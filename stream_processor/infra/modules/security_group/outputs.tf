output "security_group_id" {
  description = "ID of the stream-processor SG"
  value       = aws_security_group.stream_processor.id
}