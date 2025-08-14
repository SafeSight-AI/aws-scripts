# Variables for the Frame Monitor module

# The name of the SQS queue to which frames will be enqueued
variable "newframes_queue_name" {
  description = "The name of the existing NewFrames SQS queue"
  type        = string
}

# Used to prefix names of resources like IAM roles
variable "service_name" {
  description = "Name prefix for IAM resources"
  type        = string
  default     = "frame-monitor"
}

# Optional tagging support
variable "tags" {
  description = "Tags to apply to all resources (e.g. cost center, env)"
  type        = map(string)
  default     = {}
}
