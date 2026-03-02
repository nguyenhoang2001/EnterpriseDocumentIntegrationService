# Deployment Guide

## Overview

This guide covers deployment of the Enterprise Document Integration Service to AWS.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Docker installed locally
- PostgreSQL database (RDS recommended)

## Architecture

```
┌─────────────┐
│   Internet  │
└──────┬──────┘
       │
┌──────▼──────────┐
│  Load Balancer  │
│   (ALB/NLB)     │
└──────┬──────────┘
       │
┌──────▼──────────┐
│   ECS Fargate   │
│   (Container)   │
└──────┬──────────┘
       │
┌──────▼──────────┐
│   RDS Postgres  │
│   (Database)    │
└─────────────────┘
```

## Deployment Options

### Option 1: AWS ECS with Fargate (Recommended)

#### Step 1: Set Up RDS PostgreSQL

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
    --db-instance-identifier ocr-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15 \
    --master-username postgres \
    --master-user-password <your-password> \
    --allocated-storage 20 \
    --vpc-security-group-ids <security-group-id> \
    --db-subnet-group-name <subnet-group>
```

#### Step 2: Build and Push Docker Image to ECR

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name ocr-service

# Build Docker image
docker build -t ocr-service .

# Tag image
docker tag ocr-service:latest <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/ocr-service:latest

# Push to ECR
docker push <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/ocr-service:latest
```

#### Step 3: Create ECS Task Definition

Create `task-definition.json`:

```json
{
  "family": "ocr-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "ocr-service",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/ocr-service:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:password@<rds-endpoint>:5432/ocr_db"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ocr-service",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register the task:

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### Step 4: Create ECS Service

```bash
aws ecs create-service \
    --cluster <cluster-name> \
    --service-name ocr-service \
    --task-definition ocr-service \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[<subnet-1>,<subnet-2>],securityGroups=[<security-group>],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=<target-group-arn>,containerName=ocr-service,containerPort=8000"
```

### Option 2: AWS EC2 with Docker Compose

#### Step 1: Launch EC2 Instance

```bash
# Launch Ubuntu instance
aws ec2 run-instances \
    --image-id ami-xxxxxxxxx \
    --instance-type t3.medium \
    --key-name <your-key> \
    --security-group-ids <security-group>
```

#### Step 2: Install Docker and Docker Compose

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<ec2-public-ip>

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

#### Step 3: Deploy Application

```bash
# Clone repository
git clone <your-repo-url>
cd ocr

# Create .env file
cat > .env << EOF
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres:postgres@db:5432/ocr_db
LOG_LEVEL=INFO
DEBUG=False
EOF

# Start services
docker compose up -d

# Check logs
docker compose logs -f
```

### Option 3: AWS Lambda with API Gateway (Serverless)

For serverless deployment, use Mangum adapter:

1. Add to `requirements.txt`:

```
mangum==0.17.0
```

2. Create `lambda_handler.py`:

```python
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

3. Deploy with AWS SAM or Serverless Framework

## Environment Variables

Required environment variables for production:

```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:5432/dbname
APP_NAME=Enterprise Document Integration Service
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO
API_V1_PREFIX=/api/v1
```

## Security Best Practices

1. **Database Security**
   - Use RDS with encryption at rest
   - Store credentials in AWS Secrets Manager
   - Enable SSL/TLS connections

2. **API Security**
   - Enable HTTPS only (ALB with SSL certificate)
   - Implement rate limiting
   - Add API authentication (JWT/OAuth)

3. **Container Security**
   - Use non-root user in Docker
   - Scan images for vulnerabilities
   - Keep dependencies updated

4. **Network Security**
   - Use VPC with private subnets
   - Configure security groups properly
   - Enable VPC Flow Logs

## Monitoring and Logging

### CloudWatch Setup

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/ocr-service

# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
    --alarm-name ocr-service-high-cpu \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold
```

### Application Metrics

The service logs structured JSON logs. Set up log aggregation:

1. CloudWatch Logs Insights
2. ELK Stack (Elasticsearch, Logstash, Kibana)
3. Datadog / New Relic

## Scaling

### Auto Scaling (ECS)

```bash
# Create auto scaling target
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/<cluster>/<service> \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 2 \
    --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --resource-id service/<cluster>/<service> \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-name cpu-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

## Database Migrations

For schema changes, use Alembic:

```bash
# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head
```

## Health Checks

Configure load balancer health checks:

- **Path**: `/api/v1/health`
- **Interval**: 30 seconds
- **Timeout**: 5 seconds
- **Healthy threshold**: 2
- **Unhealthy threshold**: 3

## Rollback Procedure

```bash
# ECS: Update service to previous task definition
aws ecs update-service \
    --cluster <cluster> \
    --service ocr-service \
    --task-definition ocr-service:PREVIOUS_VERSION

# Docker Compose: Use previous image
docker compose down
docker compose up -d --force-recreate
```

## Cost Estimation

Monthly AWS costs (approximate):

- **ECS Fargate (2 tasks)**: $30-40
- **RDS PostgreSQL (db.t3.micro)**: $15-20
- **Application Load Balancer**: $20-25
- **Data Transfer**: $5-10
- **CloudWatch Logs**: $5

**Total**: ~$75-100/month for low-medium traffic

## Support

For deployment issues:

1. Check CloudWatch logs
2. Review ECS task events
3. Verify security group rules
4. Test database connectivity
