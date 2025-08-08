// Create an iam role allowing execution of ecs
resource "aws_iam_role" "stream_processor_task_execution_role" {
    name = "ecsTaskExecutionRole-${var.environment}"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
            Effect = "Allow"
            Principal = {
                Service = "ecs-tasks.amazonaws.com"
            }
            Action = "sts:AssumeRole"
        }]
    })

    tags = merge(
        var.tags
    )
}

// Attach custom permissions to the iam role
resource "aws_iam_role_policy" "stream_proessor_permissions" {
    name = "stream-processor-permissions-${var.environment}"
    role = aws_iam_role.stream_processor_task_execution_role.id

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "kinesisvideo:GetDataEndpoint",
                    "kinesis-video-media:GetMedia",
                    "dynamodb:GetItem",
                    "s3:PutObject"
                ]
                Resource = "*"
            }
        ]
    })
}

// Attach that role
resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
    role       = aws_iam_role.stream_processor_task_execution_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

// Define the size of ecs instances
resource "aws_ecs_task_definition" "stream_processor" {
    family                   = "stream-processor-task"
    requires_compatibilities = ["FARGATE"] // Deploy via fargate
    cpu                      = "1024" // 1 vCPU
    memory                   = "2048" // 2GB
    network_mode             = "awsvpc"
    execution_role_arn       = aws_iam_role.stream_processor_task_execution_role.arn

    container_definitions = jsonencode([{
        name         = "stream-processor" // Container name
        image        = var.ecr_image_url  // Docker image location
        essential    = true
        portMappings = [
            {
                containerPort = 80
                hostPort      = 80
            }
        ],
        environment = [
            { name = "ENVIRONMENT", value = var.environment }
        ]
    }])
}