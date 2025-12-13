# 🚀 Oracle Cloud Free Tier Deployment

Deploy Unitasa to Oracle Cloud Free Tier with automated scripts. **Zero cost** deployment using Oracle's Always Free resources.

## 📋 Prerequisites

- Oracle Cloud Free Tier account
- Domain name (optional but recommended)
- SSH key pair
- 30 minutes of setup time

## 🌍 Region Selection (Important!)

**Choose your home region carefully** - you cannot change it later!

### ✅ Recommended Regions (A1 Available)
- **US East (Ashburn)** - `us-ashburn-1`
- **US West (Phoenix)** - `us-phoenix-1`
- **Germany Central (Frankfurt)** - `eu-frankfurt-1`
- **UK South (London)** - `uk-london-1`
- **Canada Southeast (Montreal)** - `ca-montreal-1`

### ❌ Avoid These Regions (Limited A1)
- **South Korea Central (Seoul)** - `ap-seoul-1` ⛔
- **Japan East (Tokyo)** - `ap-tokyo-1` ⛔

### Why Region Matters
- **A1 instances** (ARM-based, our choice) have limited availability in Asia Pacific regions
- Your **home region** determines where your resources are created
- **Cannot be changed** after account creation
- Choose a region close to your users for better performance

### How to Choose Region
1. During Oracle Cloud signup, select your home region
2. Pick from the ✅ recommended list above
3. Consider proximity to your target audience
4. All recommended regions offer the same Free Tier benefits

## 🎯 Quick Start (3 Steps)

### Step 1: Oracle Cloud Setup
1. Create Oracle Cloud account at [oracle.com/cloud/free](https://www.oracle.com/cloud/free)
2. Launch Ubuntu 22.04 VM (VM.Standard.A1.Flex - 1 OCPU, 6GB RAM)
3. Note your **Public IP Address**

### Step 2: Initial Server Setup
```bash
# Connect to your VM
ssh -i your-key ubuntu@<PUBLIC_IP>

# Download and run quick setup
curl -O https://raw.githubusercontent.com/yourusername/unitasa/main/oracle-quick-setup.sh
chmod +x oracle-quick-setup.sh
./oracle-quick-setup.sh

# Logout and reconnect for Docker group
exit
ssh -i your-key ubuntu@<PUBLIC_IP>
```

### Step 3: Deploy Application
```bash
# Download deployment script
curl -O https://raw.githubusercontent.com/yourusername/unitasa/main/deploy-oracle.sh
chmod +x deploy-oracle.sh

# Run deployment (will prompt for configuration)
./deploy-oracle.sh
```

**That's it!** Your app will be live at `https://yourdomain.com`

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `docs/oracle-cloud-deployment-guide.md` | Detailed step-by-step guide |
| `deploy-oracle.sh` | Main automated deployment script |
| `oracle-config.env` | Configuration template |
| `oracle-quick-setup.sh` | Initial server setup script |
| `ORACLE_DEPLOY_README.md` | This quick start guide |

## ⚙️ Configuration

### Option 1: Interactive Setup
Run `./deploy-oracle.sh` and enter values when prompted.

### Option 2: Pre-configured Setup
```bash
# Edit configuration
cp oracle-config.env my-config.env
nano my-config.env  # Edit your values

# Run with config
source my-config.env && ./deploy-oracle.sh
```

### Required Configuration
```bash
DOMAIN_NAME=yourdomain.com
DB_PASSWORD=your_secure_password
SMTP_USERNAME=support@yourdomain.com
SMTP_PASSWORD=your_smtp_password
```

## 🏗️ Architecture

```
Oracle Cloud VM (Free Tier)
├── Ubuntu 22.04
├── Docker + Docker Compose
├── PostgreSQL Database
├── Nginx Reverse Proxy
├── SSL (Let's Encrypt)
└── Unitasa Application
    ├── FastAPI Backend
    └── React Frontend
```

## 📊 Resources Used (All Free)

- **VM**: 1 OCPU ARM64, 6GB RAM
- **Storage**: 200GB block storage
- **Network**: Unlimited inbound/outbound
- **Load Balancer**: 1 instance free
- **SSL**: Let's Encrypt (free)

## 🔧 Management Commands

```bash
# View application logs
docker-compose logs -f

# Restart application
docker-compose restart

# Update application
cd unitasa
git pull origin main
docker-compose build
docker-compose up -d

# Check backups
ls -la /home/ubuntu/backups/

# Monitor resources
htop
docker stats
```

## 🔒 Security Features

- ✅ SSH key authentication only
- ✅ UFW firewall configured
- ✅ Fail2ban intrusion prevention
- ✅ SSL/TLS encryption
- ✅ Security headers configured
- ✅ Automated security updates

## 📈 Monitoring & Backups

- ✅ **Prometheus** node exporter for metrics
- ✅ **Automated daily backups** (keeps 7 days)
- ✅ **Log rotation** configured
- ✅ **Health checks** enabled

## 🚨 Troubleshooting

### Application not starting
```bash
docker-compose logs
docker-compose ps
```

### Database connection issues
```bash
sudo -u postgres psql -c "SELECT version();"
```

### SSL certificate issues
```bash
sudo certbot certificates
sudo certbot renew --dry-run
```

### Port already in use
```bash
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

## 🔄 Updates

To update your application:
```bash
cd unitasa
git pull origin main
docker-compose build
docker-compose up -d
```

## 📞 Support

- Check `docs/oracle-cloud-deployment-guide.md` for detailed instructions
- Monitor logs: `docker-compose logs -f`
- Check Oracle Cloud console for VM status

## 🎉 Success Metrics

After deployment, you should have:
- ✅ HTTPS website at your domain
- ✅ Working user registration/login
- ✅ Database with proper schema
- ✅ Automated backups
- ✅ SSL certificate
- ✅ Monitoring enabled

**Total deployment time: ~30 minutes**
**Monthly cost: $0.00** 🎊