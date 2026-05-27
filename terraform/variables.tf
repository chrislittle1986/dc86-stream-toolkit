variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "eu-central-1"
}

variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
  default     = "669643924496"
}

variable "project_name" {
  description = "Projektname als Prefix für alle Ressourcen"
  type        = string
  default     = "dc86"
}

variable "environment" {
  description = "Umgebung (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "ec2_instance_type" {
  description = "EC2 Instance Typ"
  type        = string
  default     = "t2.small"
}

variable "ec2_ami" {
  description = "Ubuntu 24.04 AMI ID für eu-central-1"
  type        = string
  default     = "ami-0faab6bdbac9486fb"
}

variable "ssh_key_name" {
  description = "Name des SSH Key Pairs in AWS"
  type        = string
}