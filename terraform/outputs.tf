output "container_name" {
    description = "Name of the running container"
    value = docker_container.cifar_api.name
}

output "api_url" {
    description = "URL where the API is accessible"
    value = "http://localhost:${var.host_port}"
}

output "image_deployed" {
    description = "The image that was deployed"
    value = docker_image.cifar_api.name
}