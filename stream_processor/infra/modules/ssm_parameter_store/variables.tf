variable "stream_processor_bucket_name" {
  description = "S3 bucket for stream processor"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
}

variable "interval_seconds" {
  description = "Interval in seconds for stream processor tasks"
  type        = number
}