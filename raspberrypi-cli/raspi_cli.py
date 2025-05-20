import argparse
from camera_control import (
    save_camera,
    update_camera,
    delete_camera,
    load_camera,
    list_cameras,
    start_cam_stream
)

def main():
    parser = argparse.ArgumentParser(description="Camera Configuration CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Stream Commands --- #
    # TODO ensure this works with wi-fi cameras too
    parser_start = subparsers.add_parser(
        "start_stream", 
        help="Start a video stream for a saved camera.",
        description="Start a video stream for a saved camera."
                    "NOTE: Camera must first be saved (see 'save_camera' command)"
    )
    parser_start.add_argument("--cam_name", required=True, help="Name of the camera to start streaming (e.g. --cam_name /dev/video0)")
    parser_start.set_defaults(func=start_cam_stream)

    # --- Camera Info Commands --- #
    parser_save = subparsers.add_parser("save_camera", help="Save a camera's to the local JSON file for later reference")
    parser_save.add_argument("--cam_name", required=True, help="Name of the camera to save")
    parser_save.add_argument("--stream_name", required=True, help="Name of the stream on AWS. Check Wiki to ensure this matches with naming convention")
    parser_save.add_argument("--room", required=True, help="Name of the room the camera is placed in")
    parser_save.add_argument("--tags", nargs="*", help="Any rekognition tags that the camera should test for (e.g. --tags hardhat safety-vest goggles)")
    parser_save.add_argument("--region", required=True, help="Which region the KVS will be located in (e.g. --region us-east-1)")
    parser_save.set_defaults(func=save_camera)

    parser_update = subparsers.add_parser("update_camera", help="Update a camera's information")
    parser_update.add_argument("--cam_name", required=True, help="Name of the camera to update")
    parser_update.set_defaults(func=update_camera)

    parser_delete = subparsers.add_parser("delete_camera", help="Delete a camera")
    parser_delete.add_argument("--cam_name", required=True, help="Name of the camera to delete")
    parser_delete.set_defaults(func=delete_camera)

    parser_load = subparsers.add_parser("load_camera", help="Load a camera's information")
    parser_load.add_argument("--cam_name", required=True, help="Name of the camera to load")
    parser_load.set_defaults(func=load_camera)
    

    parser_list = subparsers.add_parser("list_saved_cameras", help="Lists all the currently saved cameras")
    parser_list.set_defaults(func=list_cameras)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()