## Deploying pdf2markdown to AWS ECR

### Prerequisites

- An **AWS Account** with admin access
- **AWS CLI** installed and configured (`aws configure`)
- **Docker** installed locally
- The **pdf2markdown** application is Dockerized (Dockerfile present)

---

### 1. Create an ECR Repository

Create a repository in Amazon ECR to store the pdf2markdown Docker image:

```bash
aws ecr create-repository --repository-name pdf2markdown
```

---

### 2. Authenticate Docker to ECR

Log in to your ECR registry using the AWS CLI:

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
```

Example:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 831928063164.dkr.ecr.us-east-1.amazonaws.com
```

---

### 3. Build and Tag the Docker Image

Build the Docker image for pdf2markdown and tag it for your ECR repository:

```bash
docker build -t pdf2markdown:latest .
docker tag pdf2markdown:latest <account-id>.dkr.ecr.<region>.amazonaws.com/pdf2markdown:latest
```

Example:

```bash
docker tag pdf2markdown:latest 831928063164.dkr.ecr.us-east-1.amazonaws.com/pdf2markdown:latest
```

---

### 4. Push the Image to ECR

Push the tagged image to your ECR repository:

```bash
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/pdf2markdown:latest
```

Example:

```bash
docker push 831928063164.dkr.ecr.us-east-1.amazonaws.com/pdf2markdown:latest
```
