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

# deploys zipped python code as a Lambda function
# The Lambda function will read from an S3 bucket and return the latest Rekognition result
resource "aws_lambda_function" "get_latest_rekognition_result" {
  function_name = "getLatestRekognitionResult_TF"  # Lam function name in AWS console
  runtime       = "python3.9"      # Runtime used by your Python code
  handler       = "getLatestRekognitionResult_TF.lambda_handler" 
  # Format: <filename>.<function_name> — matches the .py file and def function
  filename         = "${path.module}/getLatestRekognitionResult_TF.zip"
  source_code_hash = filebase64sha256("${path.module}/getLatestRekognitionResult_TF.zip")
  # Required to detect code changes — forces updates when the ZIP changes
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

# ─────────────────────────────────────────────────────────────────────────────
# API Gateway Setup to Trigger Lambda Function
# This section builds a REST API endpoint (https://.../prod/latest) that calls your Lambda.
# Useful for enabling external applications or users to hit the endpoint and get Rekognition results.
# ─────────────────────────────────────────────────────────────────────────────

# Create an API Gateway REST API
# This is the entry point for your API, which will handle requests and route them to the Lambda function.
# The API will be accessible at a URL like https://<api-id>.execute-api.<
resource "aws_api_gateway_rest_api" "rekognition_api" {
  name        = "rekognition-api"
  description = "API Gateway for triggering Rekognition Lambda function"
}

# Create a resource in the API, which represents a path in the URL
# This resource will be accessible at /latest, allowing users to hit this endpoint.
resource "aws_api_gateway_resource" "rekognition_resource" {
  rest_api_id = aws_api_gateway_rest_api.rekognition_api.id              # Attach to our API
  parent_id   = aws_api_gateway_rest_api.rekognition_api.root_resource_id # Attach at root level
  path_part   = "latest"                                                 # Adds /latest to the URL
}

# Create a GET method for the /latest resource
# This method will be triggered when users access the /latest endpoint.
resource "aws_api_gateway_method" "get_latest" {
  rest_api_id   = aws_api_gateway_rest_api.rekognition_api.id
  resource_id   = aws_api_gateway_resource.rekognition_resource.id
  http_method   = "GET"
  authorization = "NONE"  # No authorization required for now so publicy accessible
  # You can change this to "AWS_IAM" or other types for security later
}

# Create an integration between the GET method and the Lambda function
# This tells API Gateway how to handle requests to /latest by invoking the Lambda function.
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.rekognition_api.id
  resource_id             = aws_api_gateway_resource.rekognition_resource.id
  http_method             = aws_api_gateway_method.get_latest.http_method
  integration_http_method = "POST"  # Must be POST for Lambda
  type                    = "AWS_PROXY"  # Full request is proxied to Lambda
  uri                     = aws_lambda_function.get_latest_rekognition_result.invoke_arn
}

# Add a permission to allow API Gateway to invoke the Lambda function
# This is necessary so that API Gateway can call the Lambda function when users hit the /latest
resource "aws_lambda_permission" "api_gw_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_latest_rekognition_result.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.rekognition_api.execution_arn}/*/*"
}

# Create a deployment for the API Gateway
# This makes the API live and accessible at a URL. The deployment is necessary to apply changes
resource "aws_api_gateway_deployment" "rekognition_deployment" {
  depends_on  = [aws_api_gateway_integration.lambda_integration]  # Ensure integration exists first
  rest_api_id = aws_api_gateway_rest_api.rekognition_api.id
}

resource "aws_api_gateway_stage" "prod_stage" {
  rest_api_id   = aws_api_gateway_rest_api.rekognition_api.id
  deployment_id = aws_api_gateway_deployment.rekognition_deployment.id
  stage_name    = "prod"
}
