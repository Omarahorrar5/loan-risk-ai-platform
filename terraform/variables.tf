variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for tagging and naming resources"
  type        = string
  default     = "loan-risk"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "ssh_public_key_path" {
  description = "Path to the SSH public key"
  type        = string
  default     = "~/.ssh/loan-risk-key.pub"
}

variable "allowed_ssh_cidr" {
  description = "Your IP address to allow SSH access"
  type        = string
  default     = "0.0.0.0/0"
}

variable "dockerhub_username" {
  description = "Docker Hub username to pull images from"
  type        = string
}

variable "db_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}