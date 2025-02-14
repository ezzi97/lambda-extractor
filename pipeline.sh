#!/bin/bash
export SAM_CLI_TELEMETRY=0
set -e  # Exit on error

# Source AWS credentials if the script exists
if [ -f "./get-aws-credentials.sh" ]; then
    source ./get-aws-credentials.sh
else
    echo "get-aws-credentials.sh not found"
    exit 1
fi

# Verify AWS credentials
echo "Verifying AWS credentials..."
aws sts get-caller-identity

# Read values from samconfig.toml as defaults
DEFAULT_REGION=$(grep "region = " samconfig.toml | cut -d'"' -f2)
DEFAULT_STACK=$(grep "stack_name = " samconfig.toml | cut -d'"' -f2)
S3_BUCKET=$(grep "s3_bucket = " samconfig.toml | cut -d'"' -f2)
S3_PREFIX=$(grep "s3_prefix = " samconfig.toml | cut -d'"' -f2)

# Configuration with fallbacks
ENVIRONMENT=${1:-dev}
REGION=${AWS_REGION:-${DEFAULT_REGION}}
STACK_NAME=${2:-${DEFAULT_STACK}}

echo "Starting deployment to ${ENVIRONMENT} environment..."

# Install dependencies
echo "Installing dependencies..."
poetry install

echo "Exporting requirements..."
poetry export --without-hashes --format requirements.txt > lambda_api/requirements.txt

# Build SAM application
echo "Building application..."
sam build

# Deploy to AWS
echo "Deploying to AWS..."
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name ${STACK_NAME} \
    --region ${REGION} \
    --s3-bucket ${S3_BUCKET} \
    --s3-prefix ${S3_PREFIX} \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --no-fail-on-empty-changeset \
    --parameter-overrides Environment=${ENVIRONMENT} \
    --confirm-changeset \
    --debug

echo "Deployment completed successfully!"
