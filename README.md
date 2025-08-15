# SafeSight-AI AWS Scripts

This repository contains scripts and infrastructure code for SafeSight-AI's cloud-based video stream processing and PPE detection system, leveraging AWS services for scalable, real-time analytics and automation.

## Overview

- **Stream Processor**: Python code and Terraform for ingesting, processing, and storing video streams, including real-time frame capture, S3 uploads, and integration with AWS Kinesis Video Streams, DynamoDB, and SSM Parameter Store.
- **Raspberry Pi CLI**: Command-line tools for managing camera devices and streams, including local configuration and AWS Kinesis Video Stream setup.
- **Tech Demo**: Example scripts for capturing images and sending them to AWS Rekognition APIs.
- **Infrastructure**: Modular Terraform code for provisioning AWS resources (ECS, S3, DynamoDB, Security Groups, SSM Parameters).

## Directory Structure

```
aws-scripts/
├── stream_processor/
│   ├── container/         # Python code for KVS, S3, frame capture
│   ├── infra/             # Terraform modules and configs
│   ├── TEMP/              # Utility scripts
│   └── README.md          # Component documentation
├── raspberrypi-cli/       # CLI for camera management
│   ├── camera_control/    # Camera info and stream management
│   └── raspi_cli.py       # Main CLI entrypoint
├── tech-demo/             # Demo scripts for image capture and API calls
└── README.md              # (This file)
```

## Main Features

- Real-time frame capture from AWS Kinesis Video Streams
- Automated upload of frames to S3 with organized pathing
- Camera device management via CLI and local JSON
- Modular, production-ready Terraform for AWS infrastructure
- SSM Parameter Store integration for configuration
- Example code for AWS Rekognition integration

## Setup & Installation

### Prerequisites
- Python 3.11+
- AWS CLI configured
- Terraform installed

### Python Dependencies
Install required packages:
```sh
pip install boto3 opencv-python requests
```

### AWS Credentials
Configure your AWS credentials:
```sh
aws configure
```

### Terraform Infrastructure
From `stream_processor/infra`:
```sh
terraform init
terraform apply
```

## Usage

- **Stream Processor**: Run frame capture and upload scripts from `stream_processor/container/`.
- **Camera CLI**: Use `raspberrypi-cli/raspi_cli.py` to manage cameras and start streams.
- **Tech Demo**: Run `tech-demo/capture_photo.py` to test image capture and API integration.

## AWS Resources
- ECS Fargate for containerized stream processing
- S3 for frame storage
- DynamoDB for camera/stream metadata
- SSM Parameter Store for config
- Security Groups for network access

## Contributing
Contributions are welcome! Please open issues or submit pull requests.

## License
MIT License

## Contact
For questions or support, contact the SafeSight-AI team.
