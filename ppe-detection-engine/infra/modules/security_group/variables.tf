variable "vpc_id" {
  description = "The ID of the VPC in the Security Group"
  type        = string
}

variable "alb_security_group_id" {
  description = "Security group of the Application Load Balancer that sends traffic to stream-processor instances"
  type        = string
}