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
    description = "Cloud Provider in which to create the Confluent resources."
    type    = string
    default = "AWS"
}

variable "cc_cloud_region" {
    description = "Region in which to create the Confluent resources."
    type        = string
    default     = "eu-west-1"
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
# AWS Credentials (from environment)
# ----------------------------------------
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

# --------------------------------------------------------
# This 'random_id_4' will make whatever you create (names, etc)
# unique in your account.
# --------------------------------------------------------
resource "random_id" "id" {
    byte_length = 4
}
