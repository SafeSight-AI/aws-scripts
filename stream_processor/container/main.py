from s3_uploader import run_uploader

if __name__ == "__main__":
    try:
        run_uploader()
    except KeyboardInterrupt:
        print("Shutting down.")