# Create a log group so the app can send output to CloudWatch Logs
resource "aws_cloudwatch_log_group" "frame_monitor" {
  name              = "/ecs/frame-monitor"
  retention_in_days = 7
  tags              = var.tags
}

# ECS Task Definition, this will tell ECS how to run your container
# It includes the container image, resources, and environment variables
resource "aws_ecs_task_definition" "frame_monitor" {
  family                   = "${var.service_name}-task"
  cpu                      = "256"     # 0.25 vCPU
  memory                   = "512"     # 512MB memory
  network_mode             = "awsvpc"  # Needed for Fargate
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.execution_role.arn
  task_role_arn            = aws_iam_role.task_role.arn

  container_definitions = jsonencode([
    {
      name      = "frame-monitor"
      image     = "python:3.11"  # Temp image; later you'll use your own
      essential = true
      environment = [
        {
          name  = "QUEUE_URL"
          value = data.aws_sqs_queue.newframes.url
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.frame_monitor.name
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "frame-monitor"
        }
      }
    }
  ])

  tags = var.tags
}
