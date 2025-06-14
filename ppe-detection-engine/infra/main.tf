module "dynamodb" {
  source      = "./modules/dynamodb"
  environment = var.environment
}

module "stream_processor_sg" {
  source      = "./modules/security_group"
  vpc_id      = var.vpc_id
  environment = var.environment
}