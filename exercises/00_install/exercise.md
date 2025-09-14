# Elasticsearch & Kibana Installation Exercise

## Overview
This exercise will guide you through installing Elasticsearch and Kibana on Linux using three different methods:
1. APT Package Manager
2. Docker Compose
3. Direct Download (Archive)

For each method, you'll learn how to:
- Install both Elasticsearch and Kibana
- Verify the installation
- Uninstall cleanly

## Prerequisites

Before starting, ensure you have:
- Ubuntu 20.04+ or Debian-based Linux distribution
- At least 4GB RAM (8GB recommended)
- 20GB free disk space
- Terminal access with sudo privileges
- Internet connection

Update your system:
```bash
sudo apt update && sudo apt upgrade -y
```

---

## Method 1: APT Package Manager Installation

### Step 1.1: Install Dependencies
```bash
# Install required packages
sudo apt install -y wget apt-transport-https ca-certificates gnupg
```

### Step 1.2: Add Elasticsearch Repository
```bash
# Import the Elasticsearch GPG key
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | \
sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg

# Add the repository
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] \
https://artifacts.elastic.co/packages/8.x/apt stable main" | \
sudo tee /etc/apt/sources.list.d/elastic-8.x.list

# Update package list
sudo apt update
```

### Step 1.3: Install Elasticsearch
```bash
# Install Elasticsearch
sudo apt install -y elasticsearch

# IMPORTANT: Save the generated password and enrollment token shown during installation!
# If you miss it, reset the password:
sudo /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

### Step 1.4: Configure and Start Elasticsearch
```bash
# Enable and start Elasticsearch
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

# Check status
sudo systemctl status elasticsearch
```

### Step 1.5: Install Kibana
```bash
# Install Kibana
sudo apt install -y kibana

# Configure Kibana (if you have the enrollment token)
sudo /usr/share/kibana/bin/kibana-setup --enrollment-token <your-token>

# Or manually configure by editing:
sudo nano /etc/kibana/kibana.yml
# Set: server.host: "0.0.0.0" for external access
```

### Step 1.6: Start Kibana
```bash
# Enable and start Kibana
sudo systemctl daemon-reload
sudo systemctl enable kibana
sudo systemctl start kibana

# Check status
sudo systemctl status kibana
```

### Verification (APT Method)
```bash
# Test Elasticsearch (replace <password> with your elastic user password)
curl -X GET "https://localhost:9200" -k -u elastic:<password>

# Access Kibana
echo "Open browser: http://localhost:5601"
echo "Login with username: elastic"
echo "Password: <the password from Elasticsearch installation>"
```

### Uninstallation (APT Method)
```bash
# Stop services
sudo systemctl stop kibana
sudo systemctl stop elasticsearch

# Disable services
sudo systemctl disable kibana
sudo systemctl disable elasticsearch

# Remove packages
sudo apt remove --purge -y elasticsearch kibana

# Remove data directories (WARNING: This deletes all data!)
sudo rm -rf /var/lib/elasticsearch
sudo rm -rf /var/lib/kibana

# Remove configuration
sudo rm -rf /etc/elasticsearch
sudo rm -rf /etc/kibana

# Remove repository
sudo rm /etc/apt/sources.list.d/elastic-8.x.list
sudo rm /usr/share/keyrings/elasticsearch-keyring.gpg
sudo apt update
```

---

## Method 2: Docker Compose Installation

### Step 2.1: Install Docker and Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker Compose is installed
docker compose version
```

### Step 2.2: Create Project Directory
```bash
# Create and enter project directory
mkdir -p ~/elastic-docker && cd ~/elastic-docker
```

### Step 2.3: Create docker-compose.yml
```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    container_name: elasticsearch
    environment:
      - node.name=elasticsearch
      - cluster.name=docker-cluster
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - xpack.security.enabled=true
      - xpack.security.enrollment.enabled=true
      - ELASTIC_PASSWORD=changeme123
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - esdata:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
      - "9300:9300"
    networks:
      - elastic
    healthcheck:
      test: ["CMD-SHELL", "curl -s -k https://localhost:9200 -u elastic:changeme123 | grep -q 'cluster_name'"]
      interval: 30s
      timeout: 10s
      retries: 5

  kibana:
    image: docker.elastic.co/kibana/kibana:8.15.0
    container_name: kibana
    environment:
      - SERVERNAME=kibana
      - ELASTICSEARCH_HOSTS=https://elasticsearch:9200
      - ELASTICSEARCH_USERNAME=kibana_system
      - ELASTICSEARCH_PASSWORD=changeme123
      - ELASTICSEARCH_SSL_VERIFICATIONMODE=none
    ports:
      - "5601:5601"
    networks:
      - elastic
    depends_on:
      elasticsearch:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:5601/api/status | grep -q 'available'"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  esdata:
    driver: local

networks:
  elastic:
    driver: bridge
EOF
```

### Step 2.4: Start Services
```bash
# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Wait for services to be healthy
docker compose ps
```

### Step 2.5: Set up Kibana System User
```bash
# Generate password for kibana_system user
docker exec -it elasticsearch /usr/share/elasticsearch/bin/elasticsearch-reset-password \
-u kibana_system -b

# Update the ELASTICSEARCH_PASSWORD in docker-compose.yml with the new password
# Then restart Kibana
docker compose restart kibana
```

### Verification (Docker Compose Method)
```bash
# Test Elasticsearch
curl -X GET "https://localhost:9200" -k -u elastic:changeme123

# Check container status
docker compose ps

# Access Kibana
echo "Open browser: http://localhost:5601"
echo "Login with username: elastic"
echo "Password: changeme123"
```

### Uninstallation (Docker Compose Method)
```bash
# Navigate to project directory
cd ~/elastic-docker

# Stop and remove containers
docker compose down

# Remove volumes (WARNING: This deletes all data!)
docker compose down -v

# Remove images (optional)
docker rmi docker.elastic.co/elasticsearch/elasticsearch:8.15.0
docker rmi docker.elastic.co/kibana/kibana:8.15.0

# Remove project directory
cd ~ && rm -rf ~/elastic-docker
```

---

## Method 3: Direct Download (Archive) Installation

### Step 3.1: Install Java (Required for Archive Installation)
```bash
# Install OpenJDK 17
sudo apt install -y openjdk-17-jdk

# Verify Java installation
java -version
```

### Step 3.2: Create Installation Directory
```bash
# Create directory for Elastic stack
sudo mkdir -p /opt/elastic
cd /opt/elastic
```

### Step 3.3: Download and Extract Elasticsearch
```bash
# Download Elasticsearch
sudo wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.15.0-linux-x86_64.tar.gz

# Extract archive
sudo tar -xzf elasticsearch-8.15.0-linux-x86_64.tar.gz

# Create symbolic link for easier access
sudo ln -s elasticsearch-8.15.0 elasticsearch

# Set ownership
sudo chown -R $USER:$USER /opt/elastic/elasticsearch-8.15.0
```

### Step 3.4: Configure Elasticsearch
```bash
# Edit configuration
nano /opt/elastic/elasticsearch/config/elasticsearch.yml

# Add/modify these lines:
# network.host: 0.0.0.0
# http.port: 9200
# discovery.type: single-node

# Set JVM heap size (optional)
nano /opt/elastic/elasticsearch/config/jvm.options
# Modify -Xms1g and -Xmx1g based on your system
```

### Step 3.5: Start Elasticsearch
```bash
# Start Elasticsearch in the background
/opt/elastic/elasticsearch/bin/elasticsearch -d -p /tmp/elasticsearch.pid

# Note the generated password for elastic user in the output!
# If you need to reset it:
/opt/elastic/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

### Step 3.6: Download and Extract Kibana
```bash
cd /opt/elastic

# Download Kibana
sudo wget https://artifacts.elastic.co/downloads/kibana/kibana-8.15.0-linux-x86_64.tar.gz

# Extract archive
sudo tar -xzf kibana-8.15.0-linux-x86_64.tar.gz

# Create symbolic link
sudo ln -s kibana-8.15.0 kibana

# Set ownership
sudo chown -R $USER:$USER /opt/elastic/kibana-8.15.0
```

### Step 3.7: Configure Kibana
```bash
# Generate enrollment token for Kibana
/opt/elastic/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana

# Configure Kibana with the token
/opt/elastic/kibana/bin/kibana-setup --enrollment-token <your-token>

# Or manually edit configuration
nano /opt/elastic/kibana/config/kibana.yml
# Set: server.host: "0.0.0.0"
```

### Step 3.8: Start Kibana
```bash
# Start Kibana in the background
nohup /opt/elastic/kibana/bin/kibana > /tmp/kibana.log 2>&1 &

# Save the PID
echo $! > /tmp/kibana.pid
```

### Step 3.9: Create Systemd Services (Optional but Recommended)

**Elasticsearch Service:**
```bash
sudo tee /etc/systemd/system/elasticsearch-archive.service > /dev/null << 'EOF'
[Unit]
Description=Elasticsearch (Archive Installation)
Documentation=https://www.elastic.co
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
ExecStart=/opt/elastic/elasticsearch/bin/elasticsearch
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

**Kibana Service:**
```bash
sudo tee /etc/systemd/system/kibana-archive.service > /dev/null << 'EOF'
[Unit]
Description=Kibana (Archive Installation)
Documentation=https://www.elastic.co
Wants=network-online.target
After=network-online.target elasticsearch-archive.service

[Service]
Type=simple
User=$USER
Group=$USER
ExecStart=/opt/elastic/kibana/bin/kibana
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

Enable services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch-archive
sudo systemctl enable kibana-archive
```

### Verification (Archive Method)
```bash
# Check if processes are running
ps aux | grep elasticsearch
ps aux | grep kibana

# Test Elasticsearch
curl -X GET "https://localhost:9200" -k -u elastic:<your-password>

# Access Kibana
echo "Open browser: http://localhost:5601"
echo "Login with username: elastic"
echo "Password: <password from Elasticsearch startup>"
```

### Uninstallation (Archive Method)
```bash
# Stop processes
if [ -f /tmp/elasticsearch.pid ]; then
    kill $(cat /tmp/elasticsearch.pid)
fi
if [ -f /tmp/kibana.pid ]; then
    kill $(cat /tmp/kibana.pid)
fi

# Or if using systemd services
sudo systemctl stop elasticsearch-archive
sudo systemctl stop kibana-archive
sudo systemctl disable elasticsearch-archive
sudo systemctl disable kibana-archive
sudo rm /etc/systemd/system/elasticsearch-archive.service
sudo rm /etc/systemd/system/kibana-archive.service

# Remove installation directory (WARNING: This deletes all data!)
sudo rm -rf /opt/elastic

# Remove PID files
rm -f /tmp/elasticsearch.pid /tmp/kibana.pid
```

---

## Verification Commands (All Methods)

### Check Elasticsearch Status
```bash
# Basic health check
curl -X GET "https://localhost:9200/_cluster/health?pretty" -k -u elastic:<password>

# Get cluster information
curl -X GET "https://localhost:9200" -k -u elastic:<password>

# List indices
curl -X GET "https://localhost:9200/_cat/indices?v" -k -u elastic:<password>
```

### Check Kibana Status
```bash
# Check Kibana API status
curl -X GET "http://localhost:5601/api/status"

# Verify in browser
# Navigate to: http://localhost:5601 or http://<your-server-ip>:5601
# You should see the Kibana login page
```

### Common Troubleshooting
```bash
# Check ports are listening
sudo netstat -tlnp | grep -E '9200|5601'

# Check logs (APT method)
sudo journalctl -u elasticsearch -f
sudo journalctl -u kibana -f

# Check logs (Docker method)
docker compose logs elasticsearch
docker compose logs kibana

# Check logs (Archive method)
tail -f /opt/elastic/elasticsearch/logs/*.log
tail -f /tmp/kibana.log
```

---

## Method Comparison

### APT Package Manager

**Advantages:**
- Integrated with system package management
- Automatic dependency resolution
- Easy updates via `apt upgrade`
- Systemd integration out of the box
- Follows Linux FHS (Filesystem Hierarchy Standard)
- Automatic user/group creation
- Security updates through distribution channels

**Disadvantages:**
- Limited to versions in repository
- Requires root/sudo access for all operations
- System-wide installation only
- Harder to run multiple versions
- Configuration scattered across system directories
- May conflict with other system packages

**Best for:** Production servers, single-version deployments, system administrators preferring standard Linux management

---

### Docker Compose

**Advantages:**
- Complete isolation from host system
- Easy version management and switching
- Portable across different systems
- No dependency conflicts
- Easy clustering and scaling
- Simple backup (volume snapshots)
- Development/production parity
- Can run multiple instances easily
- No root access needed after Docker setup

**Disadvantages:**
- Requires Docker knowledge
- Additional overhead from containerization
- More complex networking setup
- Volume management learning curve
- Slightly higher resource usage
- Need to manage container logs separately
- Security considerations with container runtime

**Best for:** Development environments, microservices architecture, CI/CD pipelines, testing multiple versions

---

### Direct Download (Archive)

**Advantages:**
- Full control over installation location
- Easy to run multiple versions side-by-side
- No root access required after initial setup
- Portable installation (can be moved)
- Self-contained in one directory
- Good for testing and development
- Can customize startup scripts
- No system service manager required

**Disadvantages:**
- Manual dependency management (Java)
- No automatic updates
- Must create service files manually
- Manual user/permission management
- No automatic security updates
- More complex initial setup
- Need to manage environment variables
- Manual log rotation setup required

**Best for:** Custom deployments, testing environments, situations requiring specific control, non-standard systems

---

## Recommendations by Use Case

### Development Environment
**Recommended: Docker Compose**
- Easy to spin up/down
- Matches production if using containers
- Clean separation from system

### Production Server (Single Node)
**Recommended: APT Package Manager**
- Proper system integration
- Automatic updates
- Standard monitoring tools work

### Production Server (Cluster/Cloud)
**Recommended: Docker Compose or Kubernetes**
- Better orchestration
- Easier scaling
- Container-native cloud platforms

### Testing Multiple Versions
**Recommended: Docker Compose or Archive**
- Docker: Complete isolation
- Archive: Side-by-side installations

### Learning and Experimentation
**Recommended: Docker Compose**
- Easy to start fresh
- No system pollution
- Quick to try different configurations

### Restricted Environments (No Root)
**Recommended: Archive Installation**
- Can install in user space
- No system-level changes needed

---

## Conclusion

Each installation method has its place:
- **APT** is best for traditional server deployments
- **Docker Compose** offers maximum flexibility and isolation
- **Archive** provides fine-grained control

Consider your specific needs:
- System resources
- Administrative access
- Update requirements
- Isolation needs
- Team expertise

For most modern deployments, Docker Compose offers the best balance of ease-of-use, flexibility, and maintainability. However, APT remains excellent for production servers where system integration is important, while archive installation serves specialized needs requiring custom control.

## Next Steps

After completing this exercise, you should:
1. Choose the most appropriate method for your use case
2. Set up authentication and security properly
3. Configure index patterns in Kibana
4. Start ingesting data into Elasticsearch
5. Explore Kibana visualizations and dashboards
6. Learn about cluster configuration for production

## Additional Resources

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Kibana Documentation](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Elastic Stack Security](https://www.elastic.co/guide/en/elasticsearch/reference/current/security-minimal-setup.html)