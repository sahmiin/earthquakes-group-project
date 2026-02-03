terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

# Provider

provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}


# Data

data "aws_vpc" "main" {
  id = var.vpc_id
}

data "aws_subnet" "selected" {
  for_each = toset(var.subnet_ids)
  id       = each.value
}

# Common locals/tags
locals {
  name_prefix = var.project_name

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.extra_tags
  )
}


# Security Groups

# RDS SG
resource "aws_security_group" "rds" {
  name        = "${local.name_prefix}-rds-sg"
  description = "RDS security group"
  vpc_id      = data.aws_vpc.main.id
  tags        = local.common_tags
}

# ECS tasks SG
resource "aws_security_group" "ecs_tasks" {
  name        = "${local.name_prefix}-ecs-tasks-sg"
  description = "ECS tasks security group"
  vpc_id      = data.aws_vpc.main.id
  tags        = local.common_tags
}

# Lambda in VPC SG
resource "aws_security_group" "lambda" {
  count       = var.lambda_vpc_enabled ? 1 : 0
  name        = "${local.name_prefix}-lambda-sg"
  description = "Lambda security group (VPC enabled)"
  vpc_id      = data.aws_vpc.main.id
  tags        = local.common_tags
}

# Egress all (ECS tasks)
resource "aws_vpc_security_group_egress_rule" "ecs_egress_all" {
  security_group_id = aws_security_group.ecs_tasks.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# Egress all (Lambda)
resource "aws_vpc_security_group_egress_rule" "lambda_egress_all" {
  count             = var.lambda_vpc_enabled ? 1 : 0
  security_group_id = aws_security_group.lambda[0].id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# Allow RDS inbound from ECS tasks SG
resource "aws_vpc_security_group_ingress_rule" "rds_from_ecs" {
  security_group_id            = aws_security_group.rds.id
  referenced_security_group_id = aws_security_group.ecs_tasks.id
  from_port                    = var.rds_port
  to_port                      = var.rds_port
  ip_protocol                  = "tcp"
}

# Allow RDS inbound from Lambda
resource "aws_vpc_security_group_ingress_rule" "rds_from_lambda" {
  count                        = var.lambda_vpc_enabled ? 1 : 0
  security_group_id            = aws_security_group.rds.id
  referenced_security_group_id = aws_security_group.lambda[0].id
  from_port                    = var.rds_port
  to_port                      = var.rds_port
  ip_protocol                  = "tcp"
}


# Postgres RDS
resource "aws_db_subnet_group" "rds" {
  name       = "${local.name_prefix}-rds-subnet-group"
  subnet_ids = var.rds_subnet_ids != null ? var.rds_subnet_ids : var.subnet_ids
  tags       = local.common_tags
}

resource "aws_db_instance" "postgres" {
  identifier                 = "${local.name_prefix}-db"
  db_name                    = var.rds_db_name
  engine                     = "postgres"
  engine_version             = var.rds_engine_version
  instance_class             = var.rds_instance_class
  allocated_storage          = var.rds_allocated_storage
  port                       = var.rds_port
  username                   = var.rds_username
  password                   = var.rds_password
  publicly_accessible        = var.rds_publicly_accessible
  skip_final_snapshot        = true
  performance_insights_enabled = false

  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  tags = local.common_tags
}


# IAM for Lambda
resource "aws_iam_role" "lambda_exec" {
  name = "${local.name_prefix}-lambda-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  count      = var.lambda_vpc_enabled ? 1 : 0
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Lambda 
resource "aws_lambda_function" "earthquake_job" {
    function_name = "c21-earthquakes-pipeline-lambda"
    role = aws_iam_role.lambda_exec.arn

    package_type = "Image"

    image_uri = var.lambda_image_uri

    timeout = 3
    memory_size = 128


}

resource "aws_cloudwatch_event_rule" "every_minute" {
  name                = "${local.name_prefix}-every-minute"
  description         = "Invoke Lambda every minute"
  schedule_expression = "cron(* * * * ? *)"
  tags                = local.common_tags
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.every_minute.name
  target_id = "lambda"
  arn       = aws_lambda_function.earthquake_job.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.earthquake_job.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_minute.arn
}


# ECS (Cluster/Task Role/Services)
data "aws_ecs_cluster" "main" {
    cluster_name = var.ecs_cluster_name 
}

# Execution role (pull image & write logs)
resource "aws_iam_role" "ecs_task_execution" {
  name = "${local.name_prefix}-ecs-task-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Task role
resource "aws_iam_role" "ecs_task_role" {
  name = "${local.name_prefix}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })

  tags = local.common_tags
}

# CloudWatch Logs groups for each service
resource "aws_cloudwatch_log_group" "svc1" {
  name              = "/ecs/${local.name_prefix}/${var.ecs_service_1.name}"
  retention_in_days = var.log_retention_days
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "svc2" {
  name              = "/ecs/${local.name_prefix}/${var.ecs_service_2.name}"
  retention_in_days = var.log_retention_days
  tags              = local.common_tags
}

# Task definition: Service 1 - Dashboard
resource "aws_ecs_task_definition" "service_1" {
  family                   = "${local.name_prefix}-${var.ecs_service_1.name}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = tostring(var.ecs_service_1.cpu)
  memory                   = tostring(var.ecs_service_1.memory)
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = var.ecs_service_1.name
      image     = var.ecs_service_1.image
      essential = true
      portMappings = var.ecs_service_1.container_port == null ? [] : [
        { containerPort = var.ecs_service_1.container_port, hostPort = var.ecs_service_1.container_port, protocol = "tcp" }
      ]
      environment = [
        { name = "RDS_HOST", value = aws_db_instance.postgres.address },
        { name = "RDS_PORT", value = tostring(var.rds_port) },
        { name = "RDS_DB",   value = var.rds_db_name }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.svc1.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  tags = local.common_tags
}

# Task definition: Service 2 - API
resource "aws_ecs_task_definition" "service_2" {
  family                   = "${local.name_prefix}-${var.ecs_service_2.name}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = tostring(var.ecs_service_2.cpu)
  memory                   = tostring(var.ecs_service_2.memory)
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = var.ecs_service_2.name
      image     = var.ecs_service_2.image
      essential = true
      portMappings = var.ecs_service_2.container_port == null ? [] : [
        { containerPort = var.ecs_service_2.container_port, hostPort = var.ecs_service_2.container_port, protocol = "tcp" }
      ]
      environment = [
        { name = "RDS_HOST", value = aws_db_instance.postgres.address },
        { name = "RDS_PORT", value = tostring(var.rds_port) },
        { name = "RDS_DB",   value = var.rds_db_name }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.svc2.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  tags = local.common_tags
}

# ECR (3 repositories)
resource "aws_ecr_repository" "repositories" {
    for_each = var.ecr_repositories

    name = "${local.name_prefix}-${each.key}"

    image_tag_mutability = each.value.mutable_tags ? "MUTABLE" : "IMMUTABLE"

    image_scanning_configuration {
      scan_on_push = each.value.scan_on_push
    }

    tags = local.common_tags
  
}

# Controls how old images are dealt with
resource "aws_ecr_lifecycle_policy" "repositories" {
    for_each = var.ecr_repositories
    repository = aws_ecr_repository.repositories[each.key].name

    policy = jsonencode({
        rules = [
            {
                rulePriority = 1
                description = "Expire old images"
                selection = {
                    tagStatus = "any"
                    countType = "imageCountMoreThan"
                    countNumber = each.value.retention_days
                }
                action = { type = "expire" }
            }
        ]
    })
  

}


# ECS Service: 1 - Dashboard
resource "aws_ecs_service" "service_1" {
  name            = "${local.name_prefix}-${var.ecs_service_1.name}"
  cluster         = data.aws_ecs_cluster.main.arn
  task_definition = aws_ecs_task_definition.service_1.arn
  desired_count   = var.ecs_service_1.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.ecs_subnet_ids != null ? var.ecs_subnet_ids : var.subnet_ids
    security_groups = [aws_security_group.ecs_tasks.id]
    assign_public_ip = var.ecs_assign_public_ip
  }

  tags = local.common_tags
}

# ECS Service: 2 - API
resource "aws_ecs_service" "service_2" {
  name            = "${local.name_prefix}-${var.ecs_service_2.name}"
  cluster         = data.aws_ecs_cluster.main.arn
  task_definition = aws_ecs_task_definition.service_2.arn
  desired_count   = var.ecs_service_2.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.ecs_subnet_ids != null ? var.ecs_subnet_ids : var.subnet_ids
    security_groups = [aws_security_group.ecs_tasks.id]
    assign_public_ip = var.ecs_assign_public_ip
  }

  tags = local.common_tags
}

# SNS (email)

resource "aws_sns_topic" "reports" {
  name = "${local.name_prefix}-weekly-reports"
  tags = local.common_tags
}

resource "aws_sns_topic_subscription" "reports_email" {
  for_each = toset(var.weekly_report_email_subscribers)
  topic_arn = aws_sns_topic.reports.arn
  protocol = "email"
  endpoint = each.value
}

# EventBridge (weekly)

resource "aws_cloudwatch_event_rule" "weekly_report" {
  name = "${local.name_prefix}-weekly-report"
  description = "Weekly report lambda"
  schedule_expression = var.weekly_schedule_expression
  tags = local.common_tags
}


resource "aws_lambda_function" "weekly_report" {
  count = var.enable_weekly_report_lambda ? 1 : 0
  function_name = "${local.name_prefix}-weekly-report-lambda"
  role = aws_iam_role.lambda_exec.arn

  package_type = "Image"
  image_uri = var.weekly_report_lambda_image_uri

  timeout = var.lambda_timeout
  memory_size = var.lambda_memory_mb

  tags = local.common_tags
  
}

resource "aws_cloudwatch_event_target" "weekly_report_target" {
  count = var.enable_weekly_report_lambda ? 1 : 0
  rule = aws_cloudwatch_event_rule.weekly_report.name
  target_id = "weekly-report-lambda"
  arn = aws_lambda_function.weekly_report[0].arn
}

resource "aws_lambda_permission" "allow_eventbridge_weekly" {
  count = var.enable_weekly_report_lambda ? 1: 0
  statement_id = "AllowWeeklyReportFromEventBridge"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weekly_report[0].function_name
  principal = "events.amazonaws.com"
  source_arn = aws_cloudwatch_event_rule.weekly_report.arn
}

# Alert Lambda

resource "aws_lambda_function" "alert" {
  count = var.enable_alert_lambda ? 1 : 0
  function_name = "${local.name_prefix}-alert-lambda"
  role = aws_iam_role.lambda_exec.arn

  package_type = "Image"
  image_uri = var.alert_lambda_image_uri

  timeout = var.lambda_timeout
  memory_size = var.lambda_memory_mb

  tags = local.common_tags
}

#  Weekly report publishing

resource "aws_iam_policy" "lambda_publish_reports" {
  name = "${local.name_prefix}-lambda-publish-reports"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["sns:Publish"]
      Resource = aws_sns_topic.reports.arn
    }]
  })
}

resource "aws_iam_policy_attachment" "lambda_publish_reports_attach" {
  name = "placeholder"
  roles = [aws_iam_role.lambda_exec.name]
  policy_arn = aws_iam_policy.lambda_publish_reports.arn
}