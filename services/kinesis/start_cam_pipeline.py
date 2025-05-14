import subprocess
import os
import sys

def start_cam_pipeline(device):
    """
    Starts a GStreamer video streaming pipeline using the specified video device.

    This function sets the GST_DEBUG environment variable to 3 for verbose debugging output,
    then constructs and executes a GStreamer pipeline that:
    - Captures video from the given V4L2 device
    - Converts the video format
    - Resizes the video to 800x600 at 15 FPS
    - Encodes the video using H.264 with low latency settings
    - Parses the H.264 stream
    - Sends the stream to AWS Kinesis Video Streams (kvssink)

    Args:
        device (str): Path to the video device (e.g., "/dev/video0").

    Raises:
        subprocess.CalledProcessError: If the GStreamer pipeline fails to execute.
        FileNotFoundError: If `gst-launch-1.0` is not found in the system PATH.
    """
    # Set the GST_DEBUG environment variable
    os.environ["GST_DEBUG"] = "3"

    # Construct the GStreamer command
    command = [
        "gst-launch-1.0", "-v",
        "v4l2src", f"device={device}", "do-timestamp=true", "!",
        "videoconvert", "!",
        "video/x-raw,width=800,height=600,framerate=15/1", "!",
        "x264enc", "tune=zerolatency", "bitrate=1000", "speed-preset=superfast", "!",
        "h264parse", "!",
        "kvssink", "stream-name=Raspi-USB-Stream", "aws-region=us-east-1"
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Pipeline execution failed: {e}")
    except FileNotFoundError:
        print("gst-launch-1.0 not found. Make sure GStreamer is installed and in your PATH.")

if __name__ == "__main__":
    # Ensure the call has the correct amount of args
    if len(sys.argv) != 2:
        print("Usage: python3 stream.py /dev/videoX")

    # device path should be the 1st arg, set that here
    device_arg = sys.argv[1]
    start_cam_pipeline(device_arg)