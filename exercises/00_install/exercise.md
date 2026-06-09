# Elasticsearch & Kibana Installation Exercise

## Overview

This exercise will guide you through installing Elasticsearch and Kibana on
Linux using four different methods:

- APT Package Manager
- Docker Compose
- Direct Download (Archive)
- Podman

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

See [`01_apt_install_dependencies.sh`](./01_apt_install_dependencies.sh)

### Step 1.2: Add Elasticsearch Repository

See [`02_apt_add_elasticsearch_repo.sh`](./02_apt_add_elasticsearch_repo.sh)

### Step 1.3: Install Elasticsearch

See [`03_apt_install_elasticsearch.sh`](./03_apt_install_elasticsearch.sh)

### Step 1.4: Configure and Start Elasticsearch

See [`04_apt_disable_security_start_elasticsearch.sh`](./04_apt_disable_security_start_elasticsearch.sh)

### Step 1.5: Install Kibana

See [`05_apt_install_kibana.sh`](./05_apt_install_kibana.sh)

### Step 1.6: Start Kibana

See [`06_apt_start_kibana.sh`](./06_apt_start_kibana.sh)

### Verification (APT Method)

See [`07_apt_verify_install.sh`](./07_apt_verify_install.sh)

### Uninstallation (APT Method)

See [`08_apt_uninstall.sh`](./08_apt_uninstall.sh)

---

## Method 2: Docker Compose Installation

### Step 2.1: Install Docker and Docker Compose

See [`09_docker_install.sh`](./09_docker_install.sh)

### Step 2.2: Create Project Directory

See [`10_docker_create_project_dir.sh`](./10_docker_create_project_dir.sh)

### Step 2.3: Create docker-compose.yml

See [`11_docker_create_compose_file.sh`](./11_docker_create_compose_file.sh)

### Step 2.4: Start Services

See [`12_docker_compose_up.sh`](./12_docker_compose_up.sh)

### Step 2.5: Kibana System User (not required — security disabled)

See [`13_docker_kibana_system_user_note.sh`](./13_docker_kibana_system_user_note.sh)

### Verification (Docker Compose Method)

See [`14_docker_verify_install.sh`](./14_docker_verify_install.sh)

### Uninstallation (Docker Compose Method)

See [`15_docker_uninstall.sh`](./15_docker_uninstall.sh)

---

## Method 3: Direct Download (Archive) Installation

### Step 3.1: Install Java (Required for Archive Installation)

See [`16_archive_install_java.sh`](./16_archive_install_java.sh)

### Step 3.2: Create Installation Directory

See [`17_archive_create_install_dir.sh`](./17_archive_create_install_dir.sh)

### Step 3.3: Download and Extract Elasticsearch

See [`18_archive_download_elasticsearch.sh`](./18_archive_download_elasticsearch.sh)

### Step 3.4: Configure Elasticsearch

See [`19_archive_configure_elasticsearch.sh`](./19_archive_configure_elasticsearch.sh)

### Step 3.5: Start Elasticsearch

See [`20_archive_start_elasticsearch.sh`](./20_archive_start_elasticsearch.sh)

### Step 3.6: Download and Extract Kibana

See [`21_archive_download_kibana.sh`](./21_archive_download_kibana.sh)

### Step 3.7: Configure Kibana

See [`22_archive_configure_kibana.sh`](./22_archive_configure_kibana.sh)

### Step 3.8: Start Kibana

See [`23_archive_start_kibana.sh`](./23_archive_start_kibana.sh)

### Step 3.9: Create Systemd Services (Optional but Recommended)

**Elasticsearch Service:**
See [`24_archive_create_elasticsearch_service.sh`](./24_archive_create_elasticsearch_service.sh)

**Kibana Service:**
See [`25_archive_create_kibana_service.sh`](./25_archive_create_kibana_service.sh)

Enable services:
See [`26_archive_enable_services.sh`](./26_archive_enable_services.sh)

### Verification (Archive Method)

See [`27_archive_verify_install.sh`](./27_archive_verify_install.sh)

### Uninstallation (Archive Method)

See [`28_archive_uninstall.sh`](./28_archive_uninstall.sh)

---

## Method 4: Podman Installation

Podman is a daemonless, rootless-capable container engine that is compatible
with the same `docker-compose.yml` used in Method 2. It reads the compose file
through its compose provider, so the steps mirror the Docker Compose method.

### Step 4.1: Install Podman

See [`32_podman_install.sh`](./32_podman_install.sh)

### Step 4.2: Create Project Directory

See [`33_podman_create_project_dir.sh`](./33_podman_create_project_dir.sh)

### Step 4.3: Create docker-compose.yml

See [`34_podman_create_compose_file.sh`](./34_podman_create_compose_file.sh)

### Step 4.4: Start Services

See [`35_podman_compose_up.sh`](./35_podman_compose_up.sh)

### Verification (Podman Method)

See [`36_podman_verify_install.sh`](./36_podman_verify_install.sh)

### Uninstallation (Podman Method)

See [`37_podman_uninstall.sh`](./37_podman_uninstall.sh)

---

## Verification Commands (All Methods)

### Check Elasticsearch Status

See [`29_check_elasticsearch_status.sh`](./29_check_elasticsearch_status.sh)

### Check Kibana Status

See [`30_check_kibana_status.sh`](./30_check_kibana_status.sh)

### Common Troubleshooting

See [`31_troubleshooting_logs.sh`](./31_troubleshooting_logs.sh)

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

**Best for:** Production servers, single-version deployments, system
administrators preferring standard Linux management

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

**Best for:** Development environments, microservices architecture, CI/CD
pipelines, testing multiple versions

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

**Best for:** Custom deployments, testing environments, situations requiring
specific control, non-standard systems

---

## Recommendations by Use Case

### Development Environment

- **Recommended: Docker Compose**
- Easy to spin up/down
- Matches production if using containers
- Clean separation from system

### Production Server (Single Node)

- **Recommended: APT Package Manager**
- Proper system integration
- Automatic updates
- Standard monitoring tools work

### Production Server (Cluster/Cloud)

- **Recommended: Docker Compose or Kubernetes**
- Better orchestration
- Easier scaling
- Container-native cloud platforms

### Testing Multiple Versions

- **Recommended: Docker Compose or Archive**
- Docker: Complete isolation
- Archive: Side-by-side installations

### Learning and Experimentation

- **Recommended: Docker Compose**
- Easy to start fresh
- No system pollution
- Quick to try different configurations

### Restricted Environments (No Root)

- **Recommended: Archive Installation**
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
1. Set up authentication and security properly
1. Configure index patterns in Kibana
1. Start ingesting data into Elasticsearch
1. Explore Kibana visualizations and dashboards
1. Learn about cluster configuration for production

## Additional Resources

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Kibana Documentation](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Elastic Stack Security](https://www.elastic.co/guide/en/elasticsearch/reference/current/security-minimal-setup.html)
