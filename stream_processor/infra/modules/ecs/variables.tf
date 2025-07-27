variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)"
  type        = string
}

variable "public_subnets" {
  description = "List of public subnet IDs for the ECS service"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group ID for the ECS service"
  type        = string
}

variable "ecr_image_url" {
  description = "ECR image URL for the ECS task"
  type        = string
}