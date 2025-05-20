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

    ### Args passed:
    - cam_name - name of the camera in memory
    - stream_name - name of the AWS stream
    - region - AWS region the stream is stored in
    - room - name of the room camera is placed in
    - tags - rekognition tags to check for
    """
    configs = _load_configs()
    configs[args.cam_name] = {
        "stream_name": args.stream_name,
        "room": args.room,
        "rekognition_tags": args.tags,
        "aws_region": args.region
    }
    _save_configs(configs)
    print(f"Saved camera '{args.cam_name}' successfully!")

def update_camera(args):
    """
    Prompts the user to update camera configuration interactively.

    ### Args Passed
    - cam_name - name of the camera in memory
    """
    configs = _load_configs()
    name = args.cam_name
    if name not in configs:
        print(f"Error: Camera '{name}' not found")
        return
    
    camera = configs[name]
    print(f"Updating camera '{name}'. Leave responses blank to keep current values.")

    # Current values
    current_stream = camera.get('stream_name', '')
    current_room = camera.get('room', '')
    current_tags = camera.get('rekognition_tags', [])

    # Prompt for new values
    new_stream = input(f"Stream name [{current_stream}]: ") or current_stream
    new_room = input(f"Room [{current_room}]: ") or current_room
    tags_input = input(f"Tags (space-separated) [{', '.join(current_tags)}]: ")
    new_tags = tags_input.split() if tags_input.strip() else current_tags

    # Update
    camera['stream_name'] = new_stream
    camera['room'] = new_room
    camera['rekognition_tags'] = new_tags

    _save_configs(configs) # Save data to memory

    # Print updated info as validation
    print(f"Camera '{name}' updated successfully! New values")
    print(f"stream_name: {new_stream}")
    print(f"room: {new_room}")
    print(f"rekognition_tags: {new_tags}")

def delete_camera(args):
    """
    Deletes a camera from memory with cam_name as a reference

    ### Args passed
    - cam_name - name of the camera in memory
    """
    # Load the camera from memory
    configs = _load_configs()
    name = args.cam_name
    if name not in configs:
        print(f"Error: Camera '{name}' not found.")
        return
    
    # Validation check
    confirm = input(f"Are you sure you want to delete camera '{name}'? This cannot be undone. [y/n]: ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return
    
    del configs[name]
    _save_configs(configs)
    print(f"Camera '{name}' deleted successfully!")

def list_cameras(args):
    """
    List all currently saved cameras

    NOTE: No args passed
    """
    configs = _load_configs()
    if not configs:
        print("No cameras saved yet.")
    else:
        for name, data in configs.items():
            print(f"\n{name}:")
            print(f"  Stream: {data['stream_name']}")
            print(f"  Room: {data['room']}")
            print(f"  Tags: {', '.join(data['rekognition_tags'])}")