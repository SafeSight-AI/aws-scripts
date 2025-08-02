resource "aws_ssm_parameter" "stream_processor_s3_bucket" {
  name        = "/stream-processor/s3_bucket_name"
  description = "S3 bucket for stream processor"
  type        = "String"
  value       = var.stream_processor_bucket_name
  tags        = var.tags
}

resource "aws_ssm_parameter" "stream_processor_tags" {
  name        = "/stream-processor/tags"
  description = "Tags for stream processor resources"
  type        = "StringList"
  value       = jsonencode(var.tags)
}

resource "aws_ssm_parameter" "stream_processor_interval_seconds" {
  name        = "/stream-processor/interval_seconds"
  description = "Interval in seconds for stream processor tasks"
  type        = "String"
  value       = var.interval_seconds
}