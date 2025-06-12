// Table storing information on any cameras currently attached to an ECS container
resource "aws_dynamodb_table" "camera_streams" {
    name         = "CameraStreams-${var.environment}"
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
    attribute {
        name = "assignedAt" // Timestamp that the stream was picked up
        type = "N"
    }

    tags = {
        Name = "CameraStreams"
    }
}

resource "aws_dynamodb_table" "free_streams" {
    name         = "FreeStreams-${var.environment}"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "instanceId"

    attribute {
        name = "instanceId" // ECS instance that "discovered" the free stream
        type = "S"
    }
    attribute {
        name = "freeStreams" // Array storing all the streams found by that instance
        type = "S"           // Actually an array, not a string (store as JSON instead)
    }
    attribute {
        name = "updatedAt" // Timestamp that the stream was found
        type = "N"
    }

    tags = {
        Name = "FreeStreams"
    }
}