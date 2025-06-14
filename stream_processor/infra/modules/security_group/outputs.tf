output "stream_processor_sg_id" {
  description = "ID of the stream-processor SG"
  value       = aws_security_group.stream_processor.id
}