"""
This script contains all the camera information methods
No other file should interact directly with the cameras.json file
All interactions with the cameras.json file will happen here

TODO save camera data to AWS and use that instead of a local json file
"""
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CAMERA_CONFIG_FILE = os.path.join(SCRIPT_DIR, "./cameras.json")

def _load_configs():
    """
    PRIVATE METHOD

    Returns the existing json file if it exists. If it does not
    exist, then it returns empty
    """
    if not os.path.exists(CAMERA_CONFIG_FILE):
        return {}
    with open(CAMERA_CONFIG_FILE, "r") as f:
        return json.load(f)

def _save_configs(data):
    """
    PRIVATE METHOD
    
    Saves passed data to the json file
    """
    with open(CAMERA_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# TODO save this data to s3
def save_camera(args):
    """
    Saves a camera to memory
    """
    configs = _load_configs()
    configs[args.cam_name] = {
        "stream_name": args.stream_name,
        "room": args.room,
        "rekognition_tags": args.tags,
        "aws_region": args.region
    }
    _save_configs(configs)
    print(f"Saved camera '{args.cam_name}' successfully.")

# List all currently saved cameras
def list_cameras(args):
    configs = _load_configs()
    if not configs:
        print("No cameras saved yet.")
    else:
        for name, data in configs.items():
            print(f"\n{name}:")
            print(f"  Stream: {data['stream_name']}")
            print(f"  Room: {data['room']}")
            print(f"  Tags: {', '.join(data['rekognition_tags'])}")