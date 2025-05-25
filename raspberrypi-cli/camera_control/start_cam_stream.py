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
from .cam_info_management import load_camera

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

    Raises:
        SystemExit:          On AWS errors, missing creds, or if stream stays non‑ACTIVE.
    """

    # Load camera config from json
    camera = load_camera(args.cam_name)
    
    stream_name = camera["stream_name"]
    region = camera["aws_region"]
    conn_type = camera["connection_type"]

    if conn_type not in ["v4l2", "rtsp"]:
        sys.exit(f"ERROR: Unsupported connection_type '{conn_type}'. Must be 'v4l2' or 'rtsp'.")

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

    # Build the appropriate GStreamer command based on connection type    
    if conn_type == "v4l2": # USB connection
        device = camera["device"] # Any v4l2 connections *should* have device info
        if not device:
            sys.exit("ERROR: No 'device' specified for v4l2 camera.")
        
        command = [
            "gst-launch-1.0", "-v",
            "v4l2src", f"device={device}", "do-timestamp=true", "!",
            "image/jpeg,width=800,height=600,framerate=15/1", "!",
            "jpegdec", "!",
            "videoconvert", "!",
            "x264enc", "tune=zerolatency", "bitrate=1000", "speed-preset=superfast", "!",
            "h264parse", "!",
            "kvssink", f"stream-name={stream_name}", f"aws-region={region}"
        ]
            
    elif conn_type == "rtsp": # Wifi connection
        uri = camera["uri"] # Any rtsp connections *should* have uri info
        if not uri:
            sys.exit("ERROR: No 'uri' specified for rtsp camera.")
        
        command = [
            "gst-launch-1.0", "-v",
            "rtspsrc", f"location={uri}", "latency=100", "!",
            "rtph264depay", "!",
            "h264parse", "!",
            "kvssink", f"stream-name={stream_name}", f"aws-region={region}"
        ]


    # Attempt to run GStreamer pipeline
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Pipeline execution failed: {e}")
    except FileNotFoundError:
        print("gst-launch-1.0 not found. Make sure GStreamer is installed and in your PATH.")
