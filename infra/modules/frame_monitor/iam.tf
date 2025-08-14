# This sets up:
# 1. IAM role for your ECS container to access SQS
# 2. IAM execution role for ECS agent (logging, pulling image)
# -------------------------------

# Look up the existing SQS queue by name ("NewFrames")
data "aws_sqs_queue" "newframes" {
  name = var.newframes_queue_name 
}

# Allow ECS to assume the task role
# This role is used by the ECS task to access AWS resources
# like !SQS!, DynamoDB, etc.
data "aws_iam_policy_document" "task_trust" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# Create the actual task role
resource "aws_iam_role" "task_role" {
  name               = "${var.service_name}-task-role"
  assume_role_policy = data.aws_iam_policy_document.task_trust.json
  tags               = var.tags
}

# Create a policy that allows reading from NewFrames ONLY
data "aws_iam_policy_document" "sqs_consume" {
  statement {
    sid    = "AllowReadAndDeleteFromNewFrames"
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",            # read from the queue
      "sqs:DeleteMessage",             # remove after success
      "sqs:GetQueueAttributes",        # needed for config
      "sqs:GetQueueUrl",               # needed to resolve by name
      "sqs:ChangeMessageVisibility"    # needed for retry logic
    ]
    resources = [data.aws_sqs_queue.newframes.arn]
  }
}

# Attach that policy to the task role
resource "aws_iam_policy" "sqs_consume_policy" {
  name   = "${var.service_name}-sqs-consume"
  policy = data.aws_iam_policy_document.sqs_consume.json
  tags   = var.tags
}

resource "aws_iam_role_policy_attachment" "attach_sqs_policy" {
  role       = aws_iam_role.task_role.name
  policy_arn = aws_iam_policy.sqs_consume_policy.arn
}



# ---- Execution Role (used by ECS agent) ----
# This role is used by the ECS agent to pull images, log to CloudWatch, etc.

# Trust relationship for ECS to assume exec role
data "aws_iam_policy_document" "exec_trust" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# Create the execution role
resource "aws_iam_role" "execution_role" {
  name               = "${var.service_name}-exec-role"
  assume_role_policy = data.aws_iam_policy_document.exec_trust.json
  tags               = var.tags
}

# Attach managed AWS policy for logging + image pull
resource "aws_iam_role_policy_attachment" "exec_attach" {
  role       = aws_iam_role.execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
