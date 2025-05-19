import argparse
from start_cam_pipeline import start_cam_pipeline

def main():
    parser = argparse.ArgumentParser(description="Camera Configuration CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Stream Commands --- #
    # TODO ensure this works with wi-fi cameras too
    parser_start = subparsers.add_parser("start_stream", help="Start a video stream for a specified camera")
    parser_start.add_argument("--cam_name", required=True, help="Name of the camera to start streaming (e.g. '/dev/video0')")
    parser_start.add_argument("--stream_name", required=True, help="Name of the camera on AWS. Check Wiki to ensure this matches with naming convention")
    parser_start.add_argument("--region", required=True, help="AWS Region to start the stream in (e.g. 'us-east-1')")
    parser_start.set_defaults(func=start_cam_pipeline)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()