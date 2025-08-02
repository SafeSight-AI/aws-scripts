// Table storing information on any cameras currently attached to an ECS container
resource "aws_dynamodb_table" "camera_streams" {
    name         = "TEST_Cams-${var.environment}"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "instanceId"
    range_key    = "streamName"

    // Database attributes to be stored
    attribute {
        name = "instanceId" // ECS instance attached
        type = "S"
    }
    attribute {
        name = "streamName" // Name of the camera's KVS stream
        type = "S"
    }
    
    // Other attributes not part of hash_key or range_key:
    // assignedAt (number): Timestamp that the stream picked up

    tags = merge(
        { Name = "CameraStreams" },
        var.tags
    )
}