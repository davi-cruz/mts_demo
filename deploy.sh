#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🛡️  SecOps MTS Demo - Cloud Run Deployment${NC}"
echo "================================================"

# Check if .env file exists
ENV_FILE="/app/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: $ENV_FILE file not found!${NC}"
    echo "Please ensure $ENV_FILE exists and contains your GOOGLE_API_KEY"
    exit 1
fi

# Load environment variables from .env file
echo -e "${YELLOW}📄 Loading environment variables from $ENV_FILE...${NC}"
export $(cat "$ENV_FILE" | grep -v '^#' | grep -v '^$' | xargs)

# Validate required environment variables
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${RED}❌ Error: GOOGLE_API_KEY not found in .env file!${NC}"
    echo "Please add GOOGLE_API_KEY=your_key_here to your .env file"
    exit 1
fi

echo -e "${GREEN}✅ Environment variables loaded successfully${NC}"
echo -e "${BLUE}   API Key: ${GOOGLE_API_KEY:0:8}...${GOOGLE_API_KEY: -8}${NC}"

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI not found!${NC}"
    echo "Please install Google Cloud CLI: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1)
if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo -e "${YELLOW}🔐 Please authenticate with Google Cloud...${NC}"
    gcloud auth login
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1)
fi

echo -e "${GREEN}✅ Authenticated as: $ACTIVE_ACCOUNT${NC}"

# Set project (prompt user if needed)
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}📝 No default project set. Please set your project ID:${NC}"
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo -e "${GREEN}📦 Project: $PROJECT_ID${NC}"

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --quiet

# Deploy to Cloud Run
echo -e "${GREEN}🚀 Deploying SecOps MTS Demo to Cloud Run...${NC}"
echo -e "${BLUE}   Region: us-central1${NC}"
echo -e "${BLUE}   Service: secops-mts-demo${NC}"
echo -e "${BLUE}   Memory: 2Gi${NC}"
echo -e "${BLUE}   CPU: 2${NC}"
echo ""

gcloud run deploy secops-mts-demo \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --port 8080 \
  --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Deployment successful!${NC}"
    echo "================================================"
    echo -e "${BLUE}Your SecOps MTS Demo is now available at:${NC}"
    SERVICE_URL=$(gcloud run services describe secops-mts-demo --region us-central1 --format="value(status.url)")
    echo -e "${GREEN}🔗 $SERVICE_URL${NC}"
    echo ""
    echo -e "${BLUE}💡 You can now share this URL with others!${NC}"
else
    echo -e "${RED}❌ Deployment failed!${NC}"
    echo "Please check the error messages above and try again."
    exit 1
fi