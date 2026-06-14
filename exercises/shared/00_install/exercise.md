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

Each method is a single self-contained script with `install`, `verify` and
`uninstall` subcommands, so you can run a whole method in one go or step
through individual phases:

| Method | Script |
| --- | --- |
| APT Package Manager | [`apt_install.sh`](./apt_install.sh) |
| Docker Compose | [`docker_install.sh`](./docker_install.sh) |
| Direct Download (Archive) | [`archive_install.sh`](./archive_install.sh) |
| Podman | [`podman_install.sh`](./podman_install.sh) |
| Status / troubleshooting | [`check_status.sh`](./check_status.sh) |

> **Note:** these exercises run with security **disabled**, so no generated
> passwords or enrollment tokens are needed for any method.

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

Everything lives in [`apt_install.sh`](./apt_install.sh). Read it top to bottom:
each step (dependencies, repository, Elasticsearch, configure/start, Kibana,
start Kibana) is a separate shell function.

```bash
./apt_install.sh install     # deps, repo, install, configure and start both
./apt_install.sh verify      # test Elasticsearch and print the Kibana URL
./apt_install.sh uninstall   # stop services, purge packages, remove all data
```

---

## Method 2: Docker Compose Installation

Everything lives in [`docker_install.sh`](./docker_install.sh). It installs
Docker, writes `~/elastic-docker/docker-compose.yml` and starts the stack. No
Kibana system user setup is required because security is disabled.

```bash
./docker_install.sh install     # install Docker, write compose file, start
./docker_install.sh verify      # test Elasticsearch, show containers, Kibana URL
./docker_install.sh uninstall   # compose down -v, remove images and project dir
```

---

## Method 3: Direct Download (Archive) Installation

Everything lives in [`archive_install.sh`](./archive_install.sh). It installs
Java, downloads and extracts both archives under `/opt/elastic`, configures and
starts them. Creating systemd services is optional but recommended.

```bash
./archive_install.sh install     # Java, download, configure and start both
./archive_install.sh services    # create and enable systemd services (optional)
./archive_install.sh verify      # check processes, test Elasticsearch, Kibana URL
./archive_install.sh uninstall   # stop, remove /opt/elastic and PID files
```

---

## Method 4: Podman Installation

Podman is a daemonless, rootless-capable container engine that is compatible
with the same `docker-compose.yml` used in Method 2. It reads the compose file
through its compose provider, so the steps mirror the Docker Compose method.
Everything lives in [`podman_install.sh`](./podman_install.sh).

```bash
./podman_install.sh install     # install Podman, write compose file, start
./podman_install.sh verify      # test Elasticsearch, show containers, Kibana URL
./podman_install.sh uninstall   # compose down -v, remove images and project dir
```

---

## Verification Commands (All Methods)

Shared status and troubleshooting commands live in
[`check_status.sh`](./check_status.sh).

```bash
./check_status.sh elasticsearch   # cluster health, info and index listing
./check_status.sh kibana          # Kibana API status
./check_status.sh troubleshoot    # listening ports and per-method log locations
./check_status.sh all             # elasticsearch + kibana (default)
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
