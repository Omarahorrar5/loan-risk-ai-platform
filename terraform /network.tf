resource "aws_vpc" "main" {
    cidr_block = "10.123.0.0/16"
    enable_dns_support = true
    enable_dns_hostnames = true

    tags = {
        Name = "${var.project_name}-vpc"
        Project = var.project_name
    }
}

resource "aws_subnet" "public" {
    vpc_id = aws_vpc.main.vpc_id
    cidr_block = "10.123.1.0/24"
    map_public_ip_on_launch = true
    availability_zone = "${var.aws_region}a"

    tags = {
        Name = "${var.project_name}-public-subnet"
        Project = var.project_name
    }
}

resource "aws_internet_gateway" "main" {
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "${var.project_name}-igw"
        Project = var.project_name
    }
}

resource "aws_route_table" "public" {
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "${var.project_name}-public-rt"
        Project = var.project_name
    }
}

resource "aws_route" "default" {
    route_table_id = aws_route_table.public.id
    destination_cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
}

resource "aws_route_table_association" "public" {
    subnet_id = aws_subnet.public.id
    route_table_id = aws_route_table.public.id
}