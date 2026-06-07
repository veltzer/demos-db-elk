# Elasticsearch & Kibana Installation Exercise

## Overview

This exercise will guide you through installing Elasticsearch and Kibana on
Linux using three different methods:

- APT Package Manager
- Docker Compose
- Direct Download (Archive)

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

See [`00_install_01.sh`](./00_install_01.sh)

### Step 1.2: Add Elasticsearch Repository

See [`00_install_02.sh`](./00_install_02.sh)

### Step 1.3: Install Elasticsearch

See [`00_install_03.sh`](./00_install_03.sh)

### Step 1.4: Configure and Start Elasticsearch

See [`00_install_04.sh`](./00_install_04.sh)

### Step 1.5: Install Kibana

See [`00_install_05.sh`](./00_install_05.sh)

### Step 1.6: Start Kibana

See [`00_install_06.sh`](./00_install_06.sh)

### Verification (APT Method)

See [`00_install_07.sh`](./00_install_07.sh)

### Uninstallation (APT Method)

See [`00_install_08.sh`](./00_install_08.sh)

---

## Method 2: Docker Compose Installation

### Step 2.1: Install Docker and Docker Compose

See [`00_install_09.sh`](./00_install_09.sh)

### Step 2.2: Create Project Directory

See [`00_install_10.sh`](./00_install_10.sh)

### Step 2.3: Create docker-compose.yml

See [`00_install_11.sh`](./00_install_11.sh)

### Step 2.4: Start Services

See [`00_install_12.sh`](./00_install_12.sh)

### Step 2.5: Kibana System User (not required — security disabled)

See [`00_install_13.sh`](./00_install_13.sh)

### Verification (Docker Compose Method)

See [`00_install_14.sh`](./00_install_14.sh)

### Uninstallation (Docker Compose Method)

See [`00_install_15.sh`](./00_install_15.sh)

---

## Method 3: Direct Download (Archive) Installation

### Step 3.1: Install Java (Required for Archive Installation)

See [`00_install_16.sh`](./00_install_16.sh)

### Step 3.2: Create Installation Directory

See [`00_install_17.sh`](./00_install_17.sh)

### Step 3.3: Download and Extract Elasticsearch

See [`00_install_18.sh`](./00_install_18.sh)

### Step 3.4: Configure Elasticsearch

See [`00_install_19.sh`](./00_install_19.sh)

### Step 3.5: Start Elasticsearch

See [`00_install_20.sh`](./00_install_20.sh)

### Step 3.6: Download and Extract Kibana

See [`00_install_21.sh`](./00_install_21.sh)

### Step 3.7: Configure Kibana

See [`00_install_22.sh`](./00_install_22.sh)

### Step 3.8: Start Kibana

See [`00_install_23.sh`](./00_install_23.sh)

### Step 3.9: Create Systemd Services (Optional but Recommended)

#### Elasticsearch Service

See [`00_install_24.sh`](./00_install_24.sh)

#### Kibana Service

See [`00_install_25.sh`](./00_install_25.sh)

Enable services:
See [`00_install_26.sh`](./00_install_26.sh)

### Verification (Archive Method)

See [`00_install_27.sh`](./00_install_27.sh)

### Uninstallation (Archive Method)

See [`00_install_28.sh`](./00_install_28.sh)

---

## Verification Commands (All Methods)

### Check Elasticsearch Status

See [`00_install_29.sh`](./00_install_29.sh)

### Check Kibana Status

See [`00_install_30.sh`](./00_install_30.sh)

### Common Troubleshooting

See [`00_install_31.sh`](./00_install_31.sh)

---

## Method Comparison

### APT Package Manager

#### Advantages

- Integrated with system package management
- Automatic dependency resolution
- Easy updates via `apt upgrade`
- Systemd integration out of the box
- Follows Linux FHS (Filesystem Hierarchy Standard)
- Automatic user/group creation
- Security updates through distribution channels

#### Disadvantages

- Limited to versions in repository
- Requires root/sudo access for all operations
- System-wide installation only
- Harder to run multiple versions
- Configuration scattered across system directories
- May conflict with other system packages

**Best for:** Production servers, single-version deployments, system
administrators preferring standard Linux management

---

### Docker Compose

#### Advantages

- Complete isolation from host system
- Easy version management and switching
- Portable across different systems
- No dependency conflicts
- Easy clustering and scaling
- Simple backup (volume snapshots)
- Development/production parity
- Can run multiple instances easily
- No root access needed after Docker setup

#### Disadvantages

- Requires Docker knowledge
- Additional overhead from containerization
- More complex networking setup
- Volume management learning curve
- Slightly higher resource usage
- Need to manage container logs separately
- Security considerations with container runtime

**Best for:** Development environments, microservices architecture, CI/CD
pipelines, testing multiple versions

---

### Direct Download (Archive)

#### Advantages

- Full control over installation location
- Easy to run multiple versions side-by-side
- No root access required after initial setup
- Portable installation (can be moved)
- Self-contained in one directory
- Good for testing and development
- Can customize startup scripts
- No system service manager required

#### Disadvantages

- Manual dependency management (Java)
- No automatic updates
- Must create service files manually
- Manual user/permission management
- No automatic security updates
- More complex initial setup
- Need to manage environment variables
- Manual log rotation setup required

**Best for:** Custom deployments, testing environments, situations requiring
specific control, non-standard systems

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

For most modern deployments, Docker Compose offers the best balance of
ease-of-use, flexibility, and maintainability. However, APT remains excellent
for production servers where system integration is important, while archive
installation serves specialized needs requiring custom control.

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
</content>
</invoke>
