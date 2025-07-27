module "dynamodb" {
  source      = "./modules/dynamodb"
  environment = var.environment
}

module "stream_processor_sg" {
  source      = "./modules/security_group"
  vpc_id      = var.vpc_id
  environment = var.environment
}

# TODO - ensure this works
module "ecs" {
  source              = "./modules/ecs"
  environment         = var.environment
  public_subnets      = var.subnet_ids
  security_group_id   = module.stream_processor_sg.security_group_id
  ecr_image_url       = var.container_image
}