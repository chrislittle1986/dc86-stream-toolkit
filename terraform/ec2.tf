resource "aws_instance" "dc86" {
  ami                    = var.ec2_ami
  instance_type          = var.ec2_instance_type
  key_name               = var.ssh_key_name
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  vpc_security_group_ids = [aws_security_group.dc86.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp2"
  }

  user_data = <<-EOF
    #!/bin/bash
    # System updaten
    apt-get update -y
    apt-get upgrade -y

    # Docker installieren
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker ubuntu

    # Docker Compose installieren
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
      -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # AWS CLI installieren (fuer ECR Login)
    apt-get install -y awscli

    # nginx installieren
    apt-get install -y nginx
    systemctl enable nginx
  EOF

  tags = {
    Name        = "${var.project_name}-server"
    Project     = var.project_name
    Environment = var.environment
  }
}