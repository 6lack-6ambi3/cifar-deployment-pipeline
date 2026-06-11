# CIFAR-10 Automated Deployment Pipeline

An end-to-end CI/CD and infrastructure-as-code pipeline for a machine learning
inference service. A PyTorch image classifier is served via FastAPI, containerised
with Docker, automatically tested and published by GitHub Actions, and deployed
through Terraform and Ansible.

This project demonstrates the full path from application code to automated,
reproducible deployment — the core workflow of DevOps and SRE roles.

## Architecture

```
  ┌──────────────┐     push      ┌──────────────────┐
  │   Developer  │ ────────────► │  GitHub Actions  │
  └──────────────┘               │     CI/CD        │
                                 │                  │
                                 │  1. Run pytest   │
                                 │  2. Build image  │
                                 │  3. Push to Hub  │
                                 └────────┬─────────┘
                                          │ push image
                                          ▼
                                 ┌──────────────────┐
                                 │   Docker Hub     │
                                 │ 6lack6ambi3/     │
                                 │   cifar-api      │
                                 └────────┬─────────┘
                                          │ pull image
                          ┌───────────────┴───────────────┐
                          ▼                                ▼
                 ┌──────────────────┐           ┌──────────────────┐
                 │   Terraform      │           │     Ansible      │
                 │ (provision +     │           │ (install Docker, │
                 │  run container)  │           │  deploy on host) │
                 └──────────────────┘           └──────────────────┘
```

## Tech stack

| Layer              | Tool                              |
|--------------------|-----------------------------------|
| ML model           | PyTorch (CNN, 83% val accuracy)   |
| API                | FastAPI + Uvicorn                 |
| Containerisation   | Docker (non-root, healthcheck)    |
| CI/CD              | GitHub Actions                    |
| Image registry     | Docker Hub                        |
| Infrastructure     | Terraform (Docker provider)       |
| Config management  | Ansible                           |

## The pipeline

**On every push to `main`:**

1. **Test** — GitHub Actions runs the pytest suite (root, health, and predict endpoints). If any test fails, the pipeline stops here.
2. **Build & Push** — on success, Docker builds the image (with layer caching) and pushes it to Docker Hub tagged with both `latest` and the git SHA for traceability.

**Deployment (infrastructure-as-code):**

- **Terraform** provisions and runs the container declaratively (`init` → `plan` → `apply` → `destroy`). Verified working end-to-end locally.
- **Ansible** installs Docker and deploys the container on any fresh Ubuntu host, with an idempotent playbook and a health-check wait.

## Running it

### The API (locally)

```bash
docker run -p 8000:8000 6lack6ambi3/cifar-api:latest
curl http://localhost:8000/health
```

### Deploy with Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply      # deploys the container
terraform destroy    # tears it down
```

### Deploy with Ansible

```bash
cd ansible
pip install ansible
ansible-galaxy collection install community.docker
# edit inventory.ini with your host's IP
ansible-playbook -i inventory.ini deploy.yml
```

## API endpoints

| Method | Path       | Description                                    |
|--------|------------|------------------------------------------------|
| GET    | `/`        | Service metadata                               |
| GET    | `/health`  | Liveness check (used by Docker/orchestrators)  |
| POST   | `/predict` | Upload an image, get top-3 predictions         |

### Example prediction

```bash
curl -X POST http://localhost:8000/predict -F "file=@image.png"
```

```json
{
  "filename": "image.png",
  "predictions": [
    {"rank": 1, "class": "cat",  "probability": 0.78},
    {"rank": 2, "class": "dog",  "probability": 0.10},
    {"rank": 3, "class": "frog", "probability": 0.07}
  ]
}
```

## Project structure

```
cifar-deployment-pipeline/
├── app/                      FastAPI application
│   ├── main.py               routes: /, /health, /predict
│   └── model.py              CNN definition + inference
├── model/
│   └── best_cifar10_model.pth
├── tests/
│   └── test_api.py           pytest suite (gates the pipeline)
├── .github/workflows/
│   └── ci-cd.yml             test → build → push
├── terraform/
│   ├── main.tf               image + container resources
│   ├── variables.tf          configurable inputs
│   └── outputs.tf            deployment outputs
├── ansible/
│   ├── deploy.yml            install Docker + deploy container
│   ├── inventory.ini         target hosts
│   └── README.md
├── Dockerfile                production image (non-root, healthcheck)
├── .dockerignore
└── requirements.txt
```

## What I'd improve

- **Multi-architecture images** — the CI build currently targets `linux/amd64`; adding `linux/arm64` would let it run natively on Apple Silicon and ARM servers without emulation.
- **Deploy stage in CI** — extend the pipeline to SSH into a server and run the Ansible playbook automatically on each merge.
- **Cloud target** — point Terraform at an AWS EC2 instance instead of local Docker to demonstrate cloud provisioning (the provider swaps; the workflow stays the same).
- **Monitoring** — add Prometheus metrics and a Grafana dashboard for request latency and model inference time.

## Notes

The Terraform deploy targets the local Docker daemon, demonstrating the full
`init/plan/apply/destroy` lifecycle. The same workflow applies to cloud providers
by swapping the provider block. The Ansible playbook is ready to run against any
SSH-accessible Ubuntu host.
