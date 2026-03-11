terraform {
    required_version = ">= 0.14.0"
    required_providers {
        confluent = {
            source  = "confluentinc/confluent"
            version = "2.63.0"
        }
        random = {
            source  = "hashicorp/random"
            version = "~> 3.1"
        }
        local = {
            source  = "hashicorp/local"
            version = "~> 2.1"
        }
    }
}

provider "confluent" {
    # Set the environment variables CONFLUENT_CLOUD_API_KEY and CONFLUENT_CLOUD_API_SECRET on file `.env`
    # Or you can directly input your Confluent Cloud API key and secret here, but it's recommended to use environment variables for security reasons.
    # cloud_api_key    = XXXXXXXXXXXXXXXX
    # cloud_api_secret = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
}
