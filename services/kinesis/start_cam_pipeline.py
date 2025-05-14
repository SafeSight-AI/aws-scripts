# Internal OS imports
import subprocess
import os
import sys
import time
import argparse

# External AWS imports
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def start_cam_pipeline(device, stream_name, region):
    """
    Ensure the given KVS stream exists & is ready, then launch the GStreamer pipeline.

    1. Describe the stream:
         - If it exists and is not 'ACTIVE', exit with error.
         - If it exists and is 'ACTIVE', proceed.
    2. If it does not exist, create it, then poll DescribeStream until it becomes 'ACTIVE'.
    3. Launch gst-launch-1.0 with the provided device and stream name.

    Args:
        device (str):        Path to the video device (e.g. '/dev/video0').
        stream_name (str):   Name of the Kinesis Video Stream.
        region (str):        AWS region (e.g. 'us-east-1').

    Raises:
        SystemExit:          On AWS errors, missing creds, or if stream stays non‑ACTIVE.
    """

    # Set debug logging for GStreamer
    os.environ["GST_DEBUG"] = "3"

    # Initialize KVS client, if user is currently authenticated through the AWS CLI
    try:
        kvs = boto3.client("kinesisvideo", region_name=region)
    except NoCredentialsError:
        sys.exit("ERROR: AWS credentials not found. Configure them and retry.")
    
    # Check for existing stream
    try:
        resp = kvs.describe_stream(StreamName=stream_name)
        status = resp["StreamInfo"]["Status"]

        # If stream is inactive, tell the user what status it is in and exit the program
        if status != "ACTIVE":
            sys.exit(f"ERROR: Stream '{stream_name}' exists but is in status '{status}'") # Quit program with error

        # else: ACTIVE -> reuse
        print(f"Re‑using existing ACTIVE stream '{stream_name}'.")
    except ClientError as e:
        code = e.response["Error"]["Code"]

        # We want a ResourceNotFoundException for the later part of this block, if it is something else, we cannot handle it here
        if code != "ResourceNotFoundException":
            sys.exit(f"AWS ClientError: {e}") # Quit program with error
        
        # If we get to this part of the block, we do have a ResourceNotFoundException
        # This means that everything else in the call should be correct, we just need to create a new stream to use
        print(f"Stream '{stream_name}' not found → creating new stream...")
        kvs.create_stream(StreamName=stream_name, DataRetentionInHours=24)

        # Wait until stream is ACTIVE
        for _ in range(30):
            time.sleep(2)

            try:
                # Get the current status of the new stream
                s = kvs.describe_stream(StreamName=stream_name)["StreamInfo"]["Status"]
                if s == "ACTIVE":
                    print(f"Stream '{stream_name}' is now ACTIVE.")
                    break
            except ClientError:
                pass
        # If the stream didn't activate in a minute, assume that it won't start
        else:
            sys.exit(f"ERROR: Stream '{stream_name}' did not become ACTIVE in time.") # Quit program with error

    # Build GStreamer pipeline
    command = [
        "gst-launch-1.0", "-v",
        "v4l2src", f"device={device}", "do-timestamp=true", "!",
        "videoconvert", "!",
        "video/x-raw,width=800,height=600,framerate=15/1", "!",
        "x264enc", "tune=zerolatency", "bitrate=1000", "speed-preset=superfast", "!",
        "h264parse", "!",
        "kvssink", "stream-name=Raspi-USB-Stream", "aws-region=us-east-1"
    ]

    # Attempt to run GStreamer pipeline
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Pipeline execution failed: {e}")
    except FileNotFoundError:
        print("gst-launch-1.0 not found. Make sure GStreamer is installed and in your PATH.")

if __name__ == "__main__":
    # Create command-line argument parser with a helpful description
    p = argparse.ArgumentParser(
        description="Start a GStreamer → AWS Kinesis Video Stream pipeline."
    )

    # Required positional argument: video device path (e.g., /dev/video0)
    p.add_argument("device",     help="Video device, e.g. /dev/video0")

    # Required positional argument: stream name (will be used or created)
    p.add_argument("stream",     help="KVS stream name to use or create")

    # Optional argument: AWS region (defaults to us-east-1 if not given)
    p.add_argument(
        "--region", "-r",
        default="us-east-1",
        help="AWS region (default: us‑east‑1)"
    )

    # Parse command-line arguments into variables
    args = p.parse_args()

    # Launch pipeline using provided values
    start_cam_pipeline(args.device, args.stream, args.region)
