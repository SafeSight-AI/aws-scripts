resource "aws_security_group" "stream_processor" {
  name        = "stream-processor-sg-${var.environment}"
  description = "Allow HTTP traffic to ECS stream processor tasks"
  vpc_id      = var.vpc_id

  // Ingress: allow all inbound traffic
  ingress {
    description = "Allow HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  // Egress: allow all outbound
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "stream-processor-sg-${var.environment}"
    Environment = var.environment
  }
}