# main.tf
# -------------------------------
# Gives real values to the frame_monitor module
# -------------------------------

provider "aws" {
  region = "us-east-1"
}

module "frame_monitor" {
  source               = "../../modules/frame_monitor"
  newframes_queue_name = "NewFrames.fifo"  # Name of the existing SQS queue
  service_name         = "frame-monitor"

  tags = {
    Project     = "SafeSight"
    Component   = "FrameMonitor"
    Environment = "dev"
  }
}
