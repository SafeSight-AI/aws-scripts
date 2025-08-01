# --------------- General variables ---------------

variable "aws_region" { // Without this variable, terraform thinks we are in eu-central-2
  type    = string
  default = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the ECS instances"
  type        = list(string)
}

variable "container_image" {
  description = "The Docker image to use for the ECS task"
  type        = string
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
}

variable "desired_count" {
  description = "Number of desired ECS tasks"
  type        = number
  default     = 1
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
}

# --------------- Security group variables ---------------
variable "vpc_id" {
  description = "The ID of the VPC in the Security Group"
  type        = string
}