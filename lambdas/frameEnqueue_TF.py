'''
Triggered by S3 when a .jpg is uploaded.
Parses the uploaded file's S3 key to extract: ID, type, and timestamp.
Constructs a JSON message
Sends the message to NewFrames.fifo SQS queue
Handles errors and logs output
'''

import json
import boto3
import os
from datetime import datetime # may use to convert timestamp to a different format if needed

sqs = boto3.client('sqs') # allows us to send messages to SQS

def lambda_handler(event, context): # event is the S3 event data in json, context is the Lambda context i.e. metadata about the Lambda function execution
    try:
        for record in event['Records']: # loops through each record in the S3 event
            s3_bucket = record['s3']['bucket']['name'] # pulls the S3 bucket name from the event

            s3_key = record['s3']['object']['key'] # pulls the S3 object key from the event (path to the uploaded file, like cameras/cam-123/frames/2025-07-23T22:00:00.jpg)
            path_parts = s3_key.split('/') # splits the S3 key into parts using '/' as the delimiter, i.e. ['cameras', 'cam-123', 'frames', '2025-07-23T22:00:00.jpg']

            if len(path_parts) < 4: # prevent index out of range error
                raise Exception("Invalid key format. Expected cameras/{cameraId}/frames/{timestamp}.jpg")

            camera_id = path_parts[1] # extracts the camera ID from the S3 key, i.e. 'cam-123'
            timestamp_raw = path_parts[-1].replace('.jpg', '') # extracts the timestamp from the S3 key, i.e. '2025-07-23T22:00:00'
            timestamp_obj = datetime.strptime(timestamp_raw, "%Y-%m-%dT%H:%M:%S") # converts the timestamp string to a datetime object
            iso_timestamp = timestamp_obj.strftime("%Y-%m-%dT%H:%M:%SZ") # formats the datetime object to ISO 8601 format, i.e. '2025-07-23T22:00:00Z'

            message = { # constructs the message to send to SQS
                "cameraId": camera_id,
                "s3Key": s3_key,
                "timestamp": iso_timestamp
            }
  
            # Sends the message to the SQS queue.
            response = sqs.send_message(
                QueueUrl=os.environ['FRAME_QUEUE_URL'],  # pulled from the environment variable you set in Terraform
                MessageBody=json.dumps(message), # json payload as a string
                MessageGroupId="frame-events", # required for FIFO queues, all messages with this ID are delivered in order
                MessageDeduplicationId=s3_key # ensures AWS doesn't enqueue duplicate messages (idempotency, using the S3 key as a unique identifier for the message)
            )

            # Log the response from SQS
            print(f"Sent message: {response['MessageId']}")

        return { 'statusCode': 200 } # return a 200 status code to indicate success

    except Exception as e: # catch any exceptions that occur
        print(f"Error: {str(e)}")
        raise e

