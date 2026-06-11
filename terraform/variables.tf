variable "dockerhub_username" {
    description = "Docker Hub username where the image is published"
    type = string
    default = "6lack6ambi3"
}

variable "image_tag" {
    description = "Image tag to deploy"
    type = string
    default = "latest"
}

variable "host_port" {
    description = "Port on the host to expose the API"
    type = number
    default = 8000
}