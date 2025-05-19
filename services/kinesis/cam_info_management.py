import json
import os

CAMERA_CONFIG_FILE = os.path.expanduser("./cameras.json")

# Return the data in the config file if it exists
def load_configs():
    if not os.path.exists(CAMERA_CONFIG_FILE):
        return {}
    with open(CAMERA_CONFIG_FILE, "r") as f:
        return json.load(f)

# Saves passed data to the JSON file
def save_configs(data):
    with open(CAMERA_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Saves a camera to the JSON file for future reference
# TODO save this data to s3
def save_camera(args):
    configs = load_configs()
    configs[args.cam_name] = {
        "stream_name": args.stream_name,
        "room": args.room,
        "rekognition_tags": args.tags
    }
    save_configs(configs)
    print(f"Saved camera '{args.cam_name}' successfully.")

# List all currently saved cameras
def list_cameras(args):
    configs = load_configs()
    if not configs:
        print("No cameras saved yet.")
    else:
        for name, data in configs.items():
            print(f"\n{name}:")
            print(f"  Stream: {data['stream_name']}")
            print(f"  Room: {data['room']}")
            print(f"  Tags: {', '.join(data['rekognition_tags'])}")