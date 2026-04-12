output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.main.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.main.public_dns
}

output "frontend_url" {
  description = "URL to access the frontend"
  value       = "http://${aws_instance.main.public_ip}"
}

output "backend_url" {
  description = "URL to access the backend API"
  value       = "http://${aws_instance.main.public_ip}:8000"
}

output "ssh_command" {
  description = "Command to SSH into the instance"
  value       = "ssh -i ~/.ssh/loan-risk-key ubuntu@${aws_instance.main.public_ip}"
}