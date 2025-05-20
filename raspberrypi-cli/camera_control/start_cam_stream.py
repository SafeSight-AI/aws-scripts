"""
This script is responsible for starting a Kinesis Video Stream
between the AWS cloud and the specified camera, using this OS
as a go-between
"""

# Internal OS imports
import subprocess
import os
import sys
import time

# External AWS imports
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Other CLI script imports
from .cam_info_management import _load_configs

# TODO ensure this works with wi-fi cameras
def start_cam_stream(args):
    """
    Ensure the given KVS stream exists & is ready, then launch the GStreamer pipeline.

    1. Describe the stream:
         - If it exists and is not 'ACTIVE', exit with error.
         - If it exists and is 'ACTIVE', proceed.
    2. If it does not exist, create it, then poll DescribeStream until it becomes 'ACTIVE'.
    3. Launch gst-launch-1.0 with the provided device and stream name.

    Args:
        args.cam_name (str):      Path or identifier for the camera (e.g. '/dev/video0').
        args.stream_name (str):   Name of the Kinesis Video Stream.
        args.region (str):        AWS region (e.g. 'us-east-1').

    Raises:
        SystemExit:          On AWS errors, missing creds, or if stream stays non‑ACTIVE.
    """

    # Load camera config from json
    configs = _load_configs()
    if args.cam_name not in configs:
        sys.exit(f"ERROR: Camera '{args.cam_name}' not found in config file.")

    cam_config = configs[args.cam_name]
    stream_name = cam_config["stream_name"]
    region = cam_config["aws_region"]
    device = args.cam_name

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
        print(f"Stream '{stream_name}' not found -> creating new stream...")
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
        "image/jpeg,width=800,height=600,framerate=15/1", "!",
        "jpegdec", "!",
        "videoconvert", "!",
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
