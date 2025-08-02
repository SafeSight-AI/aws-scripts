resource "aws_s3_bucket" "this" {
  bucket        = var.name
  force_destroy = true

  tags = var.tags
}