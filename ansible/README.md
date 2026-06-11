# Ansible Deployment

Configuration-management playbook that deploys the CIFAR-10 API to any fresh Ubuntu host.

## What it does
1. Updates apt and installs Docker.
2. Enables the Docker service.
3. Pulls the CI/CD-built image from Docker Hub
4. R`uns the container with a restart policy.
5. Waits for the '/heath' endpoint to confirm a successful deploy.

## Usage

```bash
# Install Ansible and the Docker collection
pip install ansible
ansible-galaxy collection install community.docker

# Edit inventory.ini with your target host's IP and SSH user, then:
ansible-playbook -i inventory.ini deploy.yml
```

## Idempotency

Re-running the playbook is safe — Ansible only changes what's needed.
If Docker is already installed and the container is running the current
image, nothing changes. This is the core principle of configuration
management: declare the desired state, and Ansible converges the host to it.