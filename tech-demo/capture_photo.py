import cv2
import requests
import base64
import time

# Capture an image with preview
def capture_image():
    cap = cv2.VideoCapture(0) # Attempt to open the webcam
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None
    
    print("Camera preview started. Press 'c' to capture, 'q' to quit.")
    captured_frame = None

    while True:
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            print("Error: Failed to read a valid frame.")
            continue  # Optionally add a timeout or a maximum number of retries

        cv2.imshow("Camera Preview", frame)
        key = cv2.waitKey(1) & 0xFF

        # If user input is detected, process it
        if key == ord('c'):
            captured_frame = frame.copy()
            print("Image captured!")
            break
        elif key == ord('q'):
            print("Exiting without capturing.")
            break
    
    # Kill all subprocesses and return the image captured
    cap.release()
    cv2.destroyAllWindows()
    return captured_frame

def send_to_api(image, api_url):
    # Encode image as JPEG
    ret, buffer = cv2.imencode('.jpg', image)
    if not ret: # Check to ensure the image encoded properly
        print("Error encoding image.")
        return None
    # Encode bytes to Base64 for transport
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    # Attempt to upload the image to the AWS cloud, WAS THIS payload = {'image': image_base64}
    payload = {
        'image': image_base64,
        'imageId': str(int(time.time()))
        }
    try:
        response = requests.post(api_url, json=payload)
        return response.json()
    except Exception as e:
        print("Error sending request:", e)
        return None

def main():
    api_url = "https://pfmthlmvvh.execute-api.us-east-1.amazonaws.com/prod/rekognition/latest"
    image = capture_image()
    if image is None:
        return
    
    # Show the captured image briefly
    cv2.imshow("Captured Image", image)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()

    result = send_to_api(image, api_url)
    if result:
        print("Rekognition Response:")
        print(result)
    else:
        print("No response received")

if __name__ == "__main__":
    main()