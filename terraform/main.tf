# An S3 bucket is a fundamental component of Amazon S3 (Simple Storage Service), acting as a container for storing objects,
# like files or data. Think of it as a top-level folder that holds all your data within the S3 service. Each bucket has a 
# unique name and is region-specific, meaning it resides in a particular AWS region. 

#This config file tells Terraform:
#"I want to use AWS"
#"Create a private S3 bucket called zane-terraform-demo-bucket in the us-east-1 region"

provider "aws" {
  region = "us-east-1"
}

# Create an S3 bucket resource
resource "aws_s3_bucket" "my_bucket" {
  bucket = "bucket-zmc-0001"  # Must be unique across all of AWS
}

#resource "aws_s3_bucket_acl" "bucket_acl" {
#  bucket = aws_s3_bucket.my_bucket.id
#  acl    = "private"                     # Makes the bucket not public
#}

resource "aws_s3_bucket_versioning" "bucket_versioning" {
  bucket = aws_s3_bucket.my_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_object" "file_upload" {
  bucket = aws_s3_bucket.my_bucket.id    # Upload to the bucket above
  key    = "test_file.txt"               # File name in S3
  source = "${path.module}/test_file.txt" # Path to file on your machine
  acl    = "private"                     # Keep file private
}

# Lambda functions need permission to execute. This block creates a role Lambda is allowed to assume.
data "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"  # Name of the existing role in IAM
}

# Ensure the Lambda exec role always has CloudWatch logging perms
resource "aws_iam_role_policy_attachment" "lambda_basic_logs" {
  role       = data.aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# IAM policy to allow frame_enqueue_lambda to send to SQS
resource "aws_iam_policy" "sqs_enqueue_policy" {
  name = "SQSFrameEnqueuePolicy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:SendMessage"
        ],
        Resource = "arn:aws:sqs:us-east-1:528757789458:NewFrames.fifo"
      }
    ]
  })
}

# Attach the policy to the Lambda exec role
resource "aws_iam_role_policy_attachment" "attach_sqs_enqueue_policy" {
  role       = data.aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.sqs_enqueue_policy.arn
}

# deploys zipped python code as a Lambda function
# The Lambda function will read from an S3 bucket and return the latest Rekognition result
resource "aws_lambda_function" "get_latest_rekognition_result" {
  function_name = "getLatestRekognitionResult_TF"  # Lam function name in AWS console
  runtime       = "python3.9"      # Runtime used by your Python code
  handler       = "getLatestRekognitionResult_TF.lambda_handler" 
  filename         = "${path.module}/getLatestRekognitionResult_TF.zip"
  source_code_hash = filebase64sha256("${path.module}/getLatestRekognitionResult_TF.zip")
  role = data.aws_iam_role.lambda_exec_role.arn  # Link the IAM role to this Lambda function
  environment {
    variables = {
      BUCKET_NAME = "bucket-zmc-0001"   
    }
  }
}

resource "aws_lambda_function" "get_all_rekognition_result" {
  function_name = "getAllRekognitionResult_TF"
  runtime       = "python3.9"
  handler       = "getAllRekognitionResult_TF.lambda_handler"
  filename         = "${path.module}/getAllRekognitionResult_TF.zip"
  source_code_hash = filebase64sha256("${path.module}/getAllRekognitionResult_TF.zip")
  role             = data.aws_iam_role.lambda_exec_role.arn
  environment {
    variables = {
      BUCKET_NAME = "bucket-zmc-0001"
    }
  }
}

resource "aws_lambda_function" "connect_client_to_rekognition" {
  function_name = "connectClientToRekognition_TF"
  runtime       = "python3.9"
  handler       = "connectClientToRekognition_TF.lambda_handler"
  filename         = "${path.module}/connectClientToRekognition_TF.zip"
  source_code_hash = filebase64sha256("${path.module}/connectClientToRekognition_TF.zip")
  role             = data.aws_iam_role.lambda_exec_role.arn
  environment {
    variables = {
      BUCKET_NAME = "bucket-zmc-0001"
    }
  }
}

resource "aws_lambda_function" "frame_enqueue_lambda" {
  function_name = "SP-enqueue-frame-on-upload_TF"
  runtime       = "python3.12"
  handler       = "frameEnqueue_TF.lambda_handler"  # filename.function_name
  filename         = "${path.module}/frameEnqueue_TF.zip"
  source_code_hash = filebase64sha256("${path.module}/frameEnqueue_TF.zip")
  role             = data.aws_iam_role.lambda_exec_role.arn
  timeout          = 5

  environment {
    variables = {
      FRAME_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/528757789458/NewFrames.fifo"
      ENV             = "dev"
    }
  }
}

# Lambda permission to allow S3 to trigger the frame_enqueue_lambda
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.frame_enqueue_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.my_bucket.arn
}

# Set up S3 trigger for frame enqueue lambda on new .jpg file uploads in 'frames/' directory
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.my_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.frame_enqueue_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "cameras/"   # <- change from frames/ to cameras/
    filter_suffix       = ".jpg"
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}


# ─────────────────────────────────────────────────────────────────────────────
# API Gateway Setup to Trigger Lambda Function
# This section builds a REST API endpoint (https://.../prod/latest) that calls your Lambda.
# Useful for enabling external applications or users to hit the endpoint and get Rekognition results.
# ─────────────────────────────────────────────────────────────────────────────

resource "aws_api_gateway_rest_api" "rekognition_api" {
  name        = "rekognition-api"
  description = "API Gateway for triggering Rekognition Lambda function"
}

resource "aws_api_gateway_resource" "rekognition_resource" {
  rest_api_id = aws_api_gateway_rest_api.rekognition_api.id              
  parent_id   = aws_api_gateway_rest_api.rekognition_api.root_resource_id 
  path_part   = "latest"                                                 
}

resource "aws_api_gateway_method" "get_latest" {
  rest_api_id   = aws_api_gateway_rest_api.rekognition_api.id
  resource_id   = aws_api_gateway_resource.rekognition_resource.id
  http_method   = "GET"
  authorization = "NONE"  
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.rekognition_api.id
  resource_id             = aws_api_gateway_resource.rekognition_resource.id
  http_method             = aws_api_gateway_method.get_latest.http_method
  integration_http_method = "POST"  
  type                    = "AWS_PROXY"  
  uri                     = aws_lambda_function.get_latest_rekognition_result.invoke_arn
}

resource "aws_lambda_permission" "api_gw_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_latest_rekognition_result.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.rekognition_api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "rekognition_deployment" {
  depends_on  = [aws_api_gateway_integration.lambda_integration]  
  rest_api_id = aws_api_gateway_rest_api.rekognition_api.id
}

resource "aws_api_gateway_stage" "prod_stage" {
  rest_api_id   = aws_api_gateway_rest_api.rekognition_api.id
  deployment_id = aws_api_gateway_deployment.rekognition_deployment.id
  stage_name    = "prod"
}
