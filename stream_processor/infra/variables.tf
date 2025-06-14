# --------------- General variables ---------------

variable "aws_region" { // Without this variable, terraform thinks we are in eu-central-2
  type    = string
  default = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)"
  type        = string
}

# variable "public_subnets" {
#   type = list(string)
# }

# variable "security_group_id" {
#   type = string
# }

# variable "ecr_image_url" {
#   type = string
# }

# variable "target_group_arn" {
#   type = string
# }

# --------------- Security group variables ---------------
variable "vpc_id" {
  description = "The ID of the VPC in the Security Group"
  type        = string
}