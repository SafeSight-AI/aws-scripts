resource "security_group" "stream_processor" {
    name        = "stream-processor-sg-${var.environment}"
    description = "Security group for stream-processor ECS instances"
    vpc_id      = var.vpc_id
}