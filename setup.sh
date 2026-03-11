#!/bin/bash

echo "🏪 UrbanStreet Retail AI Demo - Setup Script"
echo "============================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed. Please install Terraform."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Check .env file exists
echo "Validating credentials..."
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "   Please create '.env' file with AWS and Confluent Cloud credentials, see file '.env_example' for reference"
    exit 1
fi

# Load environment variables from .env
source .env

# Check if required variables are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ AWS credentials not found in .env file"
    echo "   Required: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    echo "   Please create '.env' file with AWS and Confluent Cloud credentials, see file '.env_example' for reference"
    exit 1
fi

if [ -z "$CONFLUENT_CLOUD_API_KEY" ] || [ -z "$CONFLUENT_CLOUD_API_SECRET" ]; then
    echo "❌ Confluent Cloud credentials not found in .env file"
    echo "   Required: CONFLUENT_CLOUD_API_KEY and CONFLUENT_CLOUD_API_SECRET"
    echo "   Please create '.env' file with AWS and Confluent Cloud credentials, see file '.env_example' for reference"
    exit 1
fi

echo "✅ Credentials validated"
echo ""

# Terraform infrastructure setup
echo "Setting up Confluent Cloud infrastructure with Terraform..."
cd terraform

echo "Initializing Terraform..."
terraform init
if [ $? -ne 0 ]; then
    echo "❌ Terraform init failed"
    exit 1
fi

echo ""
echo "Planning Terraform deployment..."
terraform plan \
    -var="aws_access_key_id=$AWS_ACCESS_KEY_ID" \
    -var="aws_secret_access_key=$AWS_SECRET_ACCESS_KEY"
if [ $? -ne 0 ]; then
    echo "❌ Terraform plan failed"
    exit 1
fi

echo ""
echo "Applying Terraform configuration..."
terraform apply -auto-approve \
    -var="aws_access_key_id=$AWS_ACCESS_KEY_ID" \
    -var="aws_secret_access_key=$AWS_SECRET_ACCESS_KEY"
if [ $? -ne 0 ]; then
    echo "❌ Terraform apply failed"
    exit 1
fi

cd ..
echo "✅ Confluent Cloud infrastructure created"
echo "✅ Configuration file generated: backend/utils/config/cflt-cloud-credentials.ini"
echo ""

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python environment setup complete"
echo ""

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Frontend dependencies installed"
echo ""

# Publish required data to Kafka topics
echo "Publishing required data to Kafka topics..."
python backend/init_kafka.py

echo "✅ Setup complete!"
echo ""

echo "Next step:"
echo "Start the demo: ./run-demo.sh"
echo ""
