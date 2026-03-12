#!/bin/bash

echo "🏪 UrbanStreet Retail AI Demo - Destroy Script"
echo "=============================================="
echo ""
echo "⚠️  WARNING: This will destroy all Confluent Cloud resources!"
echo ""

# Confirmation prompt
read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Destroy cancelled"
    exit 0
fi

echo ""

# Load environment variables from .env
source .env

cd terraform
echo ""
echo "Destroying Confluent Cloud infrastructure with Terraform..."
terraform destroy -auto-approve \
    -var="aws_access_key_id=$AWS_ACCESS_KEY_ID" \
    -var="aws_secret_access_key=$AWS_SECRET_ACCESS_KEY"
if [ $? -ne 0 ]; then
    echo "❌ Terraform destroy failed"
    exit 1
fi

cd ..
echo "✅ Confluent Cloud infrastructure destroyed"
echo "✅ Configuration file deleted: backend/utils/config/cflt-cloud-credentials.ini"
echo ""

echo "✅ Confluent Cloud resources have been cleaned up. You can now safely delete the .env file if you wish."
echo ""
