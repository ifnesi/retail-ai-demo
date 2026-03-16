# ----------------------------------------
# General variables
# ----------------------------------------
variable "demo_prefix" {
    type    = string
    default = "retail-demo"
}

# ----------------------------------------
# Confluent Cloud Kafka cluster variables
# ----------------------------------------
variable "cc_cloud_provider" {
    # IMPORTANT: Keep it in AWS, as Bedrock is only available in AWS for now.
    description = "Cloud Provider in which to create the Confluent resources."
    type    = string
    default = "AWS"
}

variable "cloud_region" {
    description = "Region in which to create the Confluent resources."
    type        = string
    default     = "eu-central-1"
}

variable "cc_availability" {
    type    = string
    default = "SINGLE_ZONE"
}

variable "stream_governance" {
    type    = string
    default = "ESSENTIALS"
}

# ----------------------------------------
# AWS LLM & Credentials (from environment)
# ----------------------------------------
variable "llm_model" {
    # IMPORTANT: Make sure this model exists on the AWS region selected.
    # You can check available models here: https://docs.aws.amazon.com/bedrock/latest/userguide/available-models.html
    type    = string
    default = "anthropic.claude-sonnet-4-5-20250929-v1:0"
}

variable "aws_access_key_id" {
    description = "AWS Access Key ID for Bedrock"
    type        = string
    sensitive   = true
}

variable "aws_secret_access_key" {
    description = "AWS Secret Access Key for Bedrock"
    type        = string
    sensitive   = true
}

variable "aws_rds_database_name" {
    description = "Database name for AWS RDS instance"
    type        = string
    default     = "postgres"
}

variable "aws_rds_username" {
    description = "Username for AWS RDS instance"
    type        = string
    default     = "postgres"
}

# --------------------------------------------------------
# This 'random_id_4' will make whatever you create (names, etc)
# unique in your account.
# --------------------------------------------------------
resource "random_id" "id" {
    byte_length = 4
}
