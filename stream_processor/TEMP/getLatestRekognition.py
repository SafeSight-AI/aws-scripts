import json
import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    if not bucket_name:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'S3 bucket not configured in environment variables'})
        }
    
    try:
        # List objects in the S3 bucket and sort by LastModified timestamp
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix='rekognition_results/')

        if 'Contents' not in response or not response['Contents']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No objects found in the S3 bucket'})
            }
        
        # Find the latest file (sorted by last modified timestamp)
        latest_file = max(response['Contents'], key=lambda obj: obj['LastModified'])
        latest_file_key = latest_file['Key']

        # Fetch the latest file from S3
        file_obj = s3.get_object(Bucket=bucket_name, Key=latest_file_key)
        file_content = file_obj['Body'].read().decode('utf-8')

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': file_content
        }
    except Exception as e:
        error_msg = f"Error retrieving file: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'S3 retrieval error', 'details': error_msg})
        }
