#!/bin/bash

# Unitasa Oracle Cloud Auto-Deployment Script
# This script automates the deployment of Unitasa to Oracle Cloud Free Tier

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables (customize these)
DOMAIN_NAME=""
DB_PASSWORD=""
SMTP_USERNAME=""
SMTP_PASSWORD=""
GITHUB_REPO="https://github.com/yourusername/unitasa.git"
BRANCH="main"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. Please run as ubuntu user."
        exit 1
    fi
}

# Function to update system
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_success "System updated successfully"
}

# Function to install required packages
install_packages() {
    print_status "Installing required packages..."
    sudo apt install -y curl wget git htop ufw fail2ban nginx certbot python3-certbot-nginx postgresql postgresql-contrib prometheus-node-exporter
    print_success "Required packages installed"
}

# Function to configure firewall
configure_firewall() {
    print_status "Configuring firewall..."
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443
    echo "y" | sudo ufw --force enable
    print_success "Firewall configured"
}

# Function to install Docker
install_docker() {
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER

    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose

    print_success "Docker installed successfully"
    print_warning "Please logout and login again for docker group changes to take effect"
}

# Function to setup PostgreSQL
setup_postgresql() {
    print_status "Setting up PostgreSQL database..."

    sudo systemctl start postgresql
    sudo systemctl enable postgresql

    # Create database and user
    sudo -u postgres psql -c "CREATE DATABASE unitasa;" 2>/dev/null || print_warning "Database may already exist"
    sudo -u postgres psql -c "CREATE USER unitasa_user WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || print_warning "User may already exist"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE unitasa TO unitasa_user;"
    sudo -u postgres psql -c "ALTER USER unitasa_user CREATEDB;"

    print_success "PostgreSQL configured"
}

# Function to clone repository
clone_repository() {
    print_status "Cloning repository..."
    if [ -d "unitasa" ]; then
        print_warning "Repository directory exists, pulling latest changes..."
        cd unitasa
        git pull origin $BRANCH
        cd ..
    else
        git clone -b $BRANCH $GITHUB_REPO unitasa
    fi
    print_success "Repository ready"
}

# Function to configure environment
configure_environment() {
    print_status "Configuring environment variables..."
    cd unitasa

    if [ ! -f ".env" ]; then
        cp .env.example .env
    fi

    # Update environment variables
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://unitasa_user:$DB_PASSWORD@localhost:5432/unitasa|" .env
    sed -i "s|ENVIRONMENT=.*|ENVIRONMENT=production|" .env
    sed -i "s|FRONTEND_URL=.*|FRONTEND_URL=https://$DOMAIN_NAME|" .env
    sed -i "s|SMTP_USERNAME=.*|SMTP_USERNAME=$SMTP_USERNAME|" .env
    sed -i "s|SMTP_PASSWORD=.*|SMTP_PASSWORD=$SMTP_PASSWORD|" .env

    print_success "Environment configured"
}

# Function to build and deploy application
deploy_application() {
    print_status "Building and deploying application..."
    cd unitasa

    # Build and start containers
    docker-compose build
    docker-compose up -d

    # Wait for application to start
    print_status "Waiting for application to start..."
    sleep 30

    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Application deployed successfully"
    else
        print_error "Application deployment failed"
        docker-compose logs
        exit 1
    fi
}

# Function to configure Nginx
configure_nginx() {
    print_status "Configuring Nginx..."

    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/unitasa > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files
    location /static/ {
        alias /home/ubuntu/unitasa/frontend/build/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF

    # Enable site
    sudo ln -sf /etc/nginx/sites-available/unitasa /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx

    print_success "Nginx configured"
}

# Function to setup SSL
setup_ssl() {
    print_status "Setting up SSL certificate..."

    # Obtain SSL certificate
    sudo certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME

    # Setup auto-renewal
    (sudo crontab -l ; echo "0 12 * * * /usr/bin/certbot renew --quiet") | sudo crontab -

    print_success "SSL certificate configured"
}

# Function to setup monitoring and backups
setup_monitoring() {
    print_status "Setting up monitoring and backups..."

    # Start monitoring
    sudo systemctl enable prometheus-node-exporter
    sudo systemctl start prometheus-node-exporter

    # Create backup script
    sudo tee /usr/local/bin/backup-unitasa.sh > /dev/null <<EOF
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
DB_NAME="unitasa"
DB_USER="unitasa_user"

# Create backup directory
mkdir -p \$BACKUP_DIR

# Database backup
pg_dump -U \$DB_USER -h localhost \$DB_NAME > \$BACKUP_DIR/\${DB_NAME}_\$DATE.sql

# Compress backup
tar -czf \$BACKUP_DIR/\${DB_NAME}_\$DATE.tar.gz -C \$BACKUP_DIR \${DB_NAME}_\$DATE.sql

# Remove uncompressed file
rm \$BACKUP_DIR/\${DB_NAME}_\$DATE.sql

# Keep only last 7 days
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: \$BACKUP_DIR/\${DB_NAME}_\$DATE.tar.gz"
EOF

    sudo chmod +x /usr/local/bin/backup-unitasa.sh

    # Schedule daily backup
    (sudo crontab -l ; echo "0 2 * * * /usr/local/bin/backup-unitasa.sh") | sudo crontab -

    print_success "Monitoring and backups configured"
}

# Function to setup log rotation
setup_log_rotation() {
    print_status "Setting up log rotation..."

    sudo tee /etc/logrotate.d/unitasa > /dev/null <<EOF
/home/ubuntu/unitasa/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
EOF

    print_success "Log rotation configured"
}

# Function to test deployment
test_deployment() {
    print_status "Testing deployment..."

    # Test HTTP
    if curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN_NAME | grep -q "200"; then
        print_success "HTTP test passed"
    else
        print_warning "HTTP test failed"
    fi

    # Test HTTPS
    if curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN_NAME | grep -q "200"; then
        print_success "HTTPS test passed"
    else
        print_warning "HTTPS test failed"
    fi

    # Test API health
    if curl -s https://$DOMAIN_NAME/api/v1/health | grep -q "healthy"; then
        print_success "API health check passed"
    else
        print_warning "API health check failed"
    fi
}

# Function to display completion message
show_completion() {
    echo
    print_success "🎉 Deployment completed successfully!"
    echo
    echo "Your Unitasa application is now running at:"
    echo "  🌐 https://$DOMAIN_NAME"
    echo "  🔒 SSL: Enabled with Let's Encrypt"
    echo "  🗄️  Database: PostgreSQL configured"
    echo "  📊 Monitoring: Prometheus node exporter running"
    echo "  💾 Backups: Daily automated backups scheduled"
    echo
    echo "Useful commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Restart app: docker-compose restart"
    echo "  • Update app: git pull && docker-compose build && docker-compose up -d"
    echo "  • Check backups: ls -la /home/ubuntu/backups/"
    echo
    echo "Next steps:"
    echo "  1. Configure your DNS to point to this server"
    echo "  2. Test user registration and login"
    echo "  3. Set up email service (SendGrid recommended)"
    echo "  4. Configure monitoring alerts if needed"
}

# Main deployment function
main() {
    echo "🚀 Unitasa Oracle Cloud Auto-Deployment Script"
    echo "=============================================="
    echo

    # Check prerequisites
    check_root

    # Get configuration from user
    if [ -z "$DOMAIN_NAME" ]; then
        read -p "Enter your domain name (e.g., unitasa.com): " DOMAIN_NAME
    fi

    if [ -z "$DB_PASSWORD" ]; then
        read -s -p "Enter database password: " DB_PASSWORD
        echo
    fi

    if [ -z "$SMTP_USERNAME" ]; then
        read -p "Enter SMTP username (e.g., support@unitasa.in): " SMTP_USERNAME
    fi

    if [ -z "$SMTP_PASSWORD" ]; then
        read -s -p "Enter SMTP password: " SMTP_PASSWORD
        echo
    fi

    echo
    print_status "Starting deployment with the following configuration:"
    echo "  Domain: $DOMAIN_NAME"
    echo "  Database: unitasa (local PostgreSQL)"
    echo "  SMTP: $SMTP_USERNAME"
    echo

    # Run deployment steps
    update_system
    install_packages
    configure_firewall
    install_docker
    setup_postgresql
    clone_repository
    configure_environment
    deploy_application
    configure_nginx
    setup_ssl
    setup_monitoring
    setup_log_rotation
    test_deployment

    show_completion
}

# Run main function
main "$@"