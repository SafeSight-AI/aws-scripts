resource "aws_ecs_cluster" "stream_processor" {
    name = "stream-processor-cluster-${var.environment}"
    setting {
        name  = "containerInsights"
        value = "enabled"
    }

    tags = merge(
        var.tags
    )
}