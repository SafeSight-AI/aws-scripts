module "dynamodb" {
  source      = "./modules/dynamodb"
  environment = var.environment
  tags        = var.tags
}

module "stream_processor_sg" {
  source      = "./modules/security_group"
  vpc_id      = var.vpc_id
  environment = var.environment
  tags        = var.tags
}

module "ecs" {
  source              = "./modules/ecs"
  environment         = var.environment
  public_subnets      = var.subnet_ids
  security_group_id   = module.stream_processor_sg.security_group_id
  ecr_image_url       = var.container_image
  tags                = var.tags
}

module "s3" {
  source      = "./modules/s3"
  name        = "safesightai-stream-processor-${var.environment}"
  tags        = var.tags
  environment = var.environment
}