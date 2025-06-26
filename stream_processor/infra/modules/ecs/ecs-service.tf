// Create instances
resource "aws_ecs_service" "stream_processor" {
    name            = "stream-processor-service"
    cluster         = aws_ecs_cluster.stream_processor.id
    task_definition = aws_ecs_task_definition.stream_processor.arn
    launch_type     = "FARGATE"
    desired_count   = 1

    network_configuration {
        subnets = var.public_subnets
        assign_public_ip = true
        security_groups = [var.security_group_id]
    }

    lifecycle {
        ignore_changes = [desired_count] // ignore changes to # of running ECS tasks (out of Terraform's control)
    }

    depends_on = [
        aws_ecs_task_definition.stream_processor // Declare a dependency on ecs_task_definition
    ]
}