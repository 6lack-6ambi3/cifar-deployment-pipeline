# Terraform configuration to deploy the CIFAR-10 API container.
# Uses the Docker provider - provisions the running container as
# infrastructure-as-code, the same lifecycle (init/plan/apply/destroy)
# you'd use against AWS, GCP or a VM.

terraform {
    required_providers {
        docker = {
            source = "kreuzwerker/docker" 
            version = "~> 3.0"
        }
    }
}
provider "docker" {}

# Pull the image published by the CI/CD pipeline 

resource "docker_image" "cifar_api" {
    name = "${var.dockerhub_username}/cifar-api:${var.image_tag}" 
    keep_locally = true
    platform = "linux/amd64"
}

# Run the container that was built

resource "docker_container" "cifar_api" {
    name = "cifar-api" 
    image = docker_image.cifar_api.image_id 
    ports { 
        internal = 8000 
        external = var.host_port
    }
    restart = "unless-stopped"
    healthcheck {
        test = ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
        interval = "30s"
        timeout = "5s"
        retries = 3
    }
}
