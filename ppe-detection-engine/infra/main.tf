provider "aws" {
    region = var.aws_region
    profile = "default"
}

module "iac_bucket" {
    source = "./modules/s3"
    name   = var.iac_test_bucket_name
}

module "dynamodb" {
    source      = "./modules/dynamodb"
    environment = var.environment
}