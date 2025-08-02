resource "aws_s3_bucket" "this" {
  bucket        = var.name
  force_destroy = true

  tags = var.tags
}

output "name" {
    value = aws_s3_bucket.this.bucket
}