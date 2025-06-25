// Create instances
resource "aws_ecs_service" "stream_processor" {
    name            = "stream-processor-service"
    cluster         = ecs_cluster.stream_processor.id
    task_definition = ecs_task_definition.stream_processor.arn
    launch_type     = "FARGATE"
    desired_count   = 1

    network_configuration {
        subnets = var.public_subnets
        assign_public_ip = true
        security_groups = [var.security_group_id]
    }

    load_balancer {
        target_group_arn = var.target_group_arn
        container_name   = "stream-processor"
        container_port   = 80
    }

    lifecycle {
        ignore_changes = [desired_count] // ignore changes to # of running ECS tasks (out of Terraform's control)
    }

    depends_on = [
        ecs_task_definition.stream_processor // Declare a dependency on ecs_task_definition
    ]
}

// Define autoscaling template
resource "aws_appautoscaling_target" "ecs_scaling_target" {
    max_capacity       = 10
    min_capacity       = 1
    resource_id        = "service/${ecs_cluster.stream_processor.name}/${ecs_service.stream_processor.name}" // ECS service to scale
    scalable_dimension = "ecs:service:DesiredCount"
    service_namespace  = "ecs"
}

// Define autoscaling rules
resource "aws_appautoscaling_policy" "cpu_policy" {
    name               = "cpu-scaling-policy"
    policy_type        = "TargetTrackingScaling"
    resource_id        = appautoscaling_target.resource_id
    scalable_dimension = appautoscaling_target.scalable_dimension
    service_namespace  = appautoscaling_target.service_namespace

    target_tracking_scaling_policy_configuration {
        target_value = 75.0
        predefined_metric_specification {
            predefined_metric_type = "ECSServiceAverageCPUUtilization"
        }
        scale_in_cooldown  = 60
        scale_out_cooldown = 60
    }
}