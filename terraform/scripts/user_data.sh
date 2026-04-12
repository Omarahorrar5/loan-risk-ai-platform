#!/bin/bash
set -e

# Log everything for debugging
exec > /var/log/user_data.log 2>&1
echo "=== Bootstrap started at $(date) ==="

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Install docker-compose standalone
curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 \
  -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create app directory
mkdir -p /app
cd /app

# Write docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER:     loanuser
      POSTGRES_PASSWORD: ${db_password}
      POSTGRES_DB:       loandb
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - app-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U loanuser -d loandb"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    image: ${dockerhub_username}/loan-risk-backend:latest
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://loanuser:${db_password}@db:5432/loandb
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app-net

  frontend:
    image: ${dockerhub_username}/loan-risk-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - app-net

volumes:
  pgdata:

networks:
  app-net:
    driver: bridge
EOF

# Pull and start
docker compose pull
docker compose up -d

echo "=== Bootstrap completed at $(date) ==="