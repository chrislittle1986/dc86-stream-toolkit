output "ec2_public_ip" {
  description = "Oeffentliche IP der EC2 Instance"
  value       = aws_instance.dc86.public_ip
}

output "ec2_public_dns" {
  description = "Oeffentlicher DNS der EC2 Instance"
  value       = aws_instance.dc86.public_dns
}

output "ecr_frontend_url" {
  description = "ECR URL fuer Frontend Image"
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecr_backend_url" {
  description = "ECR URL fuer Backend Image"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_bot_url" {
  description = "ECR URL fuer Bot Image"
  value       = aws_ecr_repository.bot.repository_url
}