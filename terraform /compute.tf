resource "aws_key_pair" "main" {
    key_name = "${var.project_name}-key"
    public_key = file(var.ssh_public_key_path)

    tags = {
        Project = var.project_name
    }
}

resource "aws_instance" "main" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.main.key_name
  vpc_security_group_ids = [aws_security_group.main.id]
  subnet_id              = aws_subnet.public.id

  user_data = templatefile("${path.module}/scripts/user_data.sh", {
    dockerhub_username = var.dockerhub_username
    db_password        = var.db_password
  })

  user_data_replace_on_change = true

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name    = "${var.project_name}-server"
    Project = var.project_name
  }
}