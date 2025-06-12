resource "aws_s3_bucket" "iac_test_bucket" {
    bucket = var.name

    tags = {
        Name        = "IaC Test Bucket"
        Environment = "dev"
    }
}