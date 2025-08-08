import json
import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = os.environ.get('BUCKET_NAME')
    if not bucket_name:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'S3 bucket not configured in environment variables'})
        }
    
    try:
        # List objects in the S3 bucket
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix='rekognition_results/')

        if 'Contents' not in response or not response['Contents']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No objects found in the S3 bucket'})
            }
        
        # Retrieve all files and read their contents
        all_files_data = {}
        for obj in response['Contents']:
            file_key = obj['Key']
            file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
            file_content = file_obj['Body'].read().decode('utf-8')

            # Store content in dictionary using file name as key
            all_files_data[file_key] = json.loads(file_content)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(all_files_data)
        }
    except Exception as e:
        error_msg = f"Error retrieving files: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'S3 retrieval error', 'details': error_msg})
        }
