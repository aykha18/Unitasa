# Oracle Cloud Free Tier Deployment Guide

## Overview

This guide provides step-by-step instructions to deploy the Unitasa application to Oracle Cloud Free Tier. The deployment uses Oracle's Always Free resources including Ubuntu VMs, free storage, and networking.

## Prerequisites

- Oracle Cloud account with Free Tier eligibility
- SSH key pair
- Domain name (optional, but recommended for SSL)
- GitHub repository access

## Oracle Cloud Free Tier Resources Used

- **VM.Standard.A1.Flex** (ARM-based): 1 OCPU, 6 GB RAM (free)
- **Block Storage**: 200 GB total (free)
- **Load Balancer**: 1 instance (free)
- **Network**: Free tier networking

## Step 1: Create Oracle Cloud Account & Setup

### 1.1 Create Oracle Cloud Account
1. Go to [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)
2. Click "Start for free"
3. Complete account verification
4. Add payment method (won't be charged for free tier)

### 1.2 Choose the Right Region (Critical!)

**Select your home region carefully** - this cannot be changed later!

#### ✅ Recommended Regions (A1 Available)
- **US East (Ashburn)** - `us-ashburn-1` ⭐ (Most popular, best availability)
- **US West (Phoenix)** - `us-phoenix-1`
- **Germany Central (Frankfurt)** - `eu-frankfurt-1`
- **UK South (London)** - `uk-london-1`
- **Canada Southeast (Montreal)** - `ca-montreal-1`

#### ❌ Avoid These Regions (Limited A1)
- **South Korea Central (Seoul)** - `ap-seoul-1` ⛔
- **Japan East (Tokyo)** - `ap-tokyo-1` ⛔

**Why this matters:** Due to high demand for Arm Ampere A1 Compute capacity in South Korea and Japan, A1 instance availability is limited in these regions. Your home region determines where all your resources are created and cannot be changed after account creation.

**Recommendation:** Choose **US East (Ashburn)** for the best A1 availability and performance.

### 1.3 Create Virtual Cloud Network (VCN)
1. Login to Oracle Cloud Console
2. Navigate to **Networking > Virtual Cloud Networks**
3. Click **Create VCN**
4. Configure:
   - Name: `unitasa-vcn`
   - Create in compartment: (your compartment)
   - IPv4 CIDR: `10.0.0.0/16`
   - Enable DNS resolution
5. Create default resources (Internet Gateway, Route Table, Security List)

### 1.3 Create Security List Rules
1. Go to your VCN > Security Lists
2. Click on the default security list
3. Add Ingress Rules:
   ```
   Source Type: CIDR
   Source CIDR: 0.0.0.0/0
   IP Protocol: TCP
   Destination Port Range: 22 (SSH)

   Source Type: CIDR
   Source CIDR: 0.0.0.0/0
   IP Protocol: TCP
   Destination Port Range: 80 (HTTP)

   Source Type: CIDR
   Source CIDR: 0.0.0.0/0
   IP Protocol: TCP
   Destination Port Range: 443 (HTTPS)
   ```

## Step 2: Launch Ubuntu VM

### 2.1 Create Compute Instance
1. Navigate to **Compute > Instances**
2. Click **Create Instance**
3. Configure:
   - Name: `unitasa-server`
   - Image: **Canonical Ubuntu 22.04** (latest)
   - Shape: **VM.Standard.A1.Flex**
     - OCPUs: 1
     - Memory: 6 GB
   - Network: Select your VCN
   - Subnet: Public subnet
   - Assign public IPv4 address: Yes
   - SSH keys: Add your public key

### 2.2 Wait for Instance to Run
- Status should show "Running"
- Note the **Public IP Address**

## Step 3: Initial Server Setup

### 3.1 Connect via SSH
```bash
ssh -i your-private-key ubuntu@<PUBLIC_IP>
```

### 3.2 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 3.3 Install Required Packages
```bash
sudo apt install -y curl wget git htop ufw fail2ban
```

### 3.4 Configure Firewall
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
```

### 3.5 Install Docker & Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for docker group
exit
ssh -i your-private-key ubuntu@<PUBLIC_IP>
```

## Step 4: Setup PostgreSQL Database

### 4.1 Install PostgreSQL
```bash
sudo apt install -y postgresql postgresql-contrib
```

### 4.2 Configure PostgreSQL
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE unitasa;"
sudo -u postgres psql -c "CREATE USER unitasa_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE unitasa TO unitasa_user;"
sudo -u postgres psql -c "ALTER USER unitasa_user CREATEDB;"
```

### 4.3 Configure PostgreSQL for Remote Access
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
# Add this line before the last line:
# host    unitasa         unitasa_user     127.0.0.1/32        md5

sudo nano /etc/postgresql/14/main/postgresql.conf
# Change listen_addresses:
# listen_addresses = '127.0.0.1'

sudo systemctl restart postgresql
```

## Step 5: Deploy Application

### 5.1 Clone Repository
```bash
git clone https://github.com/yourusername/unitasa.git
cd unitasa
```

### 5.2 Create Environment File
```bash
cp .env.example .env
nano .env
```

Update the following variables:
```bash
DATABASE_URL=postgresql+asyncpg://unitasa_user:your_secure_password@localhost:5432/unitasa
ENVIRONMENT=production
FRONTEND_URL=https://yourdomain.com
# Add other required environment variables
```

### 5.3 Build and Run Application
```bash
# Build the application
docker-compose build

# Start the application
docker-compose up -d
```

### 5.4 Check Application Status
```bash
docker-compose ps
docker-compose logs -f
```

## Step 6: Setup Nginx Reverse Proxy

### 6.1 Install Nginx
```bash
sudo apt install -y nginx
```

### 6.2 Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/unitasa
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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
```

### 6.3 Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/unitasa /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 7: Setup SSL Certificate (Let's Encrypt)

### 7.1 Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 7.2 Obtain SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 7.3 Configure Auto-Renewal
```bash
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## Step 8: Setup Monitoring & Backups

### 8.1 Install Monitoring Tools
```bash
sudo apt install -y prometheus-node-exporter
sudo systemctl enable prometheus-node-exporter
sudo systemctl start prometheus-node-exporter
```

### 8.2 Create Backup Script
```bash
sudo nano /usr/local/bin/backup-unitasa.sh
```

Add this content:
```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="unitasa"
DB_USER="unitasa_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/${DB_NAME}_$DATE.sql

# Compress backup
tar -czf $BACKUP_DIR/${DB_NAME}_$DATE.tar.gz -C $BACKUP_DIR ${DB_NAME}_$DATE.sql

# Remove uncompressed file
rm $BACKUP_DIR/${DB_NAME}_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/${DB_NAME}_$DATE.tar.gz"
```

### 8.3 Make Executable and Schedule
```bash
sudo chmod +x /usr/local/bin/backup-unitasa.sh
sudo crontab -e
# Add this line for daily backup at 2 AM:
# 0 2 * * * /usr/local/bin/backup-unitasa.sh
```

## Step 9: Final Configuration

### 9.1 Update Application Environment
Update your `.env` file with production URLs and secrets.

### 9.2 Test Application
```bash
curl -I https://yourdomain.com
curl https://yourdomain.com/api/v1/health
```

### 9.3 Setup Log Rotation
```bash
sudo nano /etc/logrotate.d/unitasa
```

Add:
```
/home/ubuntu/unitasa/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
```

## Troubleshooting

### Common Issues

1. **Port 80/443 already in use**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo netstat -tulpn | grep :443
   ```

2. **Docker containers not starting**
   ```bash
   docker-compose logs
   docker-compose ps
   ```

3. **Database connection issues**
   ```bash
   sudo -u postgres psql -c "SELECT version();"
   ```

4. **SSL certificate issues**
   ```bash
   sudo certbot certificates
   sudo certbot renew --dry-run
   ```

## Maintenance

### Update Application
```bash
cd /home/ubuntu/unitasa
git pull origin main
docker-compose build
docker-compose up -d
```

### Monitor Resources
```bash
htop
df -h
docker stats
```

### View Logs
```bash
docker-compose logs -f
sudo tail -f /var/log/nginx/error.log
```

## Cost Optimization

- Oracle Free Tier covers all resources used
- Monitor usage in Oracle Cloud Console
- Free tier limits: 2 VMs, 200GB storage, 10TB outbound data/month

## Security Best Practices

1. Regular system updates: `sudo apt update && sudo apt upgrade`
2. SSH key authentication only (disable password auth)
3. Fail2ban active for SSH protection
4. SSL/TLS encryption enabled
5. Regular backups scheduled
6. Minimal open ports (only 22, 80, 443)

---

**Deployment Time**: ~2-3 hours
**Monthly Cost**: $0 (Free Tier)
**Maintenance**: Minimal (automated backups and monitoring)