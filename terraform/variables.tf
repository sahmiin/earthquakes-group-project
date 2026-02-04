
# Provider / basics
variable "aws_region" {
  type        = string
  description = "AWS region"
}

variable "aws_access_key" {
  type        = string
  description = "AWS access key"
  sensitive   = true
}

variable "aws_secret_key" {
  type        = string
  description = "AWS secret key"
  sensitive   = true
}

variable "project_name" {
  type        = string
  description = "Project name prefix for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (e.g., dev, staging, prod)"
  default     = "dev"
}

variable "extra_tags" {
  type        = map(string)
  description = "Additional tags to apply to resources"
  default     = {}
}


# Networking (existing VPC/subnets)
variable "vpc_id" {
  type        = string
  description = "Existing VPC ID"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs to use (default for ECS/Lambda/RDS if specific subnet lists not provided)"
}


# RDS

variable "rds_subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for RDS subnet group (defaults to subnet_ids if null)"
  default     = null
}

variable "rds_db_name" {
  type        = string
  description = "Initial database name"
  default     = "earthquakes"
}

variable "rds_username" {
  type        = string
  description = "RDS master username"
  sensitive   = true
}

variable "rds_password" {
  type        = string
  description = "RDS master password"
  sensitive   = true
}

variable "rds_engine_version" {
  type        = string
  description = "Postgres engine version"
  default     = "17.6"
}

variable "rds_instance_class" {
  type        = string
  description = "RDS instance class"
  default     = "db.t3.micro"
}

variable "rds_allocated_storage" {
  type        = number
  description = "Allocated storage in GB"
  default     = 20
}

variable "rds_port" {
  type        = number
  description = "Database port"
  default     = 5432
}

variable "rds_publicly_accessible" {
  type        = bool
  description = "Whether the DB is publicly accessible (generally false for production)"
  default     = false
}


# Lambda
variable "lambda_image_uri" {
  type = string
  description = "Full ECR image URI"
}

variable "lambda_timeout" {
  type        = number
  description = "Lambda timeout in seconds"
  default     = 30
}

variable "lambda_memory_mb" {
  type        = number
  description = "Lambda memory in MB"
  default     = 256
}

variable "lambda_env" {
  type        = map(string)
  description = "Additional environment variables for Lambda"
  default     = {}
}

variable "lambda_vpc_enabled" {
  type        = bool
  description = "Whether Lambda should run in the VPC (needed if it must reach private RDS)"
  default     = true
}

variable "lambda_subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for Lambda if VPC-enabled (defaults to subnet_ids if null)"
  default     = null
}


# ECS
variable "ecs_subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for ECS services (defaults to subnet_ids if null)"
  default     = null
}

variable "ecs_assign_public_ip" {
  type        = bool
  description = "Assign public IPs to Fargate tasks (true for public subnets; false for private+NAT)"
  default     = false
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch Logs retention in days"
  default     = 14
}

variable "ecs_service_2" {
  type = object({
    name           = string
    image          = string
    desired_count  = number
    cpu            = number
    memory         = number
    container_port = optional(number)
  })

  description = "Definition for ECS Fargate service 2"
}

variable "ecr_repositories" {
    description = "ECR repositories to create"
    type = map(object({
      mutable_tags = bool
      scan_on_push = bool
      force_delete = bool
      retention_days = number
    }))
    default = {
      api = {
        mutable_tags = true
        scan_on_push = true
        force_delete = true
        retention_days = 30
        }
    lambda = {
        mutable_tags = true
        scan_on_push = true
        force_delete = true
        retention_days = 30
        }
      weekly-report = {
        mutable_tags = true
        scan_on_push = true
        force_delete = true
        retention_days = 30
        }
      alerts = {
        mutable_tags = true
        scan_on_push = true
        force_delete = true
        retention_days = 30
        }
    }
}

variable "ecs_cluster_name" {
    type = string
    description = "Name of existing ECS cluster"
  
}

variable "weekly_report_email_subscribers" {
  type = list(string)
  description = "Email addresses to subscribe to weekly"
  default = []
}

variable "weekly_schedule_expression" {
  type = string
  description = "EventBridge schedule for weekly report."
  default = "cron(0 9 ? * MON *)"  
}

variable "enable_weekly_report_lambda" {
  type = bool
  description = "Create the weekly report Lambda and its trigger"
  default = false
}

variable "enable_alert_lambda" {
  type = bool
  description = "Create the alert Lambda"
  default = false
}

variable "weekly_report_lambda_image_uri" {
  type = string
  description = "ECR image URI for the weekly Lambda"
  default = ""
}

variable "alert_lambda_image_uri" {
  type = string
  description = "ECR image URI for the alert Lambda"
  default = ""
}