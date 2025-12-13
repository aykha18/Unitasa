#!/bin/bash

# Oracle Cloud Quick Setup Script
# Run this first on your fresh Oracle Cloud Ubuntu instance

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Oracle Cloud Quick Setup${NC}"
echo "================================"

# Update system
echo -e "${YELLOW}Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo -e "${YELLOW}Installing essential packages...${NC}"
sudo apt install -y curl wget git htop ufw fail2ban

# Configure firewall
echo -e "${YELLOW}Configuring firewall...${NC}"
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
echo "y" | sudo ufw --force enable

# Install Docker
echo -e "${YELLOW}Installing Docker...${NC}"
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo -e "${YELLOW}Installing Docker Compose...${NC}"
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install PostgreSQL
echo -e "${YELLOW}Installing PostgreSQL...${NC}"
sudo apt install -y postgresql postgresql-contrib

# Install Nginx and SSL tools
echo -e "${YELLOW}Installing Nginx and SSL tools...${NC}"
sudo apt install -y nginx certbot python3-certbot-nginx

# Install monitoring
echo -e "${YELLOW}Installing monitoring tools...${NC}"
sudo apt install -y prometheus-node-exporter

echo -e "${GREEN}✅ Quick setup completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Logout and login again (for Docker group)"
echo "2. Run the main deployment script:"
echo "   ./deploy-oracle.sh"
echo ""
echo "Or run with custom config:"
echo "   source oracle-config.env && ./deploy-oracle.sh"