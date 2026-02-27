#!/bin/bash
# EC2 Deployment Script
# Run this on your AWS EC2 instance after SSH-ing in:
#   ssh -i your-key.pem ec2-user@<EC2_PUBLIC_IP>
#   then: bash deploy.sh

set -e

echo "=== Step 1: Install Docker ==="
sudo yum update -y
sudo yum install -y docker git
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

echo "=== Step 2: Install Docker Compose ==="
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "=== Step 3: Clone the repository ==="
# Replace with your actual GitHub repo URL
git clone https://github.com/nguyenhoang2001/EnterpriseDocumentIntegrationService.git
cd EnterpriseDocumentIntegrationService

echo "=== Step 4: Create .env file ==="
cat > .env <<EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme_strong_password
POSTGRES_DB=ocr_db
EOF

echo "=== Step 5: Build and start containers ==="
docker-compose -f docker-compose.prod.yml up -d --build

echo "=== Step 6: Check status ==="
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "========================================"
echo " Deployment complete!"
echo " API is live at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo " Docs:           http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/docs"
echo "========================================"
