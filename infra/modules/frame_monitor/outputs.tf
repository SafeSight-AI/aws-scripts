# An ARN, or Amazon Resource Name, is a unique identifier used in Amazon Web Services (AWS) to specify resources unambiguously
output "task_role_arn" {
  description = "IAM Role ARN used by ECS container app"
  value       = aws_iam_role.task_role.arn
}

output "execution_role_arn" {
  description = "IAM Role ARN used by ECS agent"
  value       = aws_iam_role.execution_role.arn
}

output "newframes_queue_arn" {
  description = "ARN of the NewFrames SQS queue"
  value       = data.aws_sqs_queue.newframes.arn
}

output "newframes_queue_url" {
  description = "URL of the NewFrames SQS queue"
  value       = data.aws_sqs_queue.newframes.url
}
