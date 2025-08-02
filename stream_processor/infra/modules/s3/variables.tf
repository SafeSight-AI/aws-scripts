variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)  
}

variable "name" {
  description = "Name of the S3 bucket"
  type        = string
  default = "safesightai-stream-processor"
}

variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)"
  type        = string
}