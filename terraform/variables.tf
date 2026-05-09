variable "aws_region" {
  default = "eu-central-1"
}

variable "db_username" {
  description = "MySQL root username"
  sensitive   = true
}

variable "db_password" {
  description = "MySQL root password"
  sensitive   = true
}

variable "image_url" {
  description = "Docker image URL from GHCR"
}
