output "rds_endpoint" {
  value       = aws_db_instance.postgres.address
  description = "RDS hostname"
}

output "rds_port" {
  value       = aws_db_instance.postgres.port
  description = "RDS port"
}

output "lambda_function_name" {
  value       = aws_lambda_function.earthquake_job.function_name
  description = "Lambda function name"
}

output "ecs_cluster_name" {
  value       = data.aws_ecs_cluster.main.arn
  description = "ECS cluster name"
}

output "ecs_service_names" {
  value = [
    aws_ecs_service.service_2.name
  ]
  description = "ECS service names"
}

output "ecr_repository_urls" {
  description = "ECR repository URLs"
  value = {
    for k, r in aws_ecr_repository.repositories :
    k => r.repository_url
  }
}