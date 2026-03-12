# -------------------------------------------------------
# Confluent Cloud Organization
# -------------------------------------------------------
data "confluent_organization" "cc_org" {
    # This data source fetches the organization details
    # Ensure you have the correct permissions to access the organization
}

# -------------------------------------------------------
# Confluent Cloud Environment
# -------------------------------------------------------
resource "confluent_environment" "cc_demo_env" {
    display_name = "env-${var.demo_prefix}-${random_id.id.hex}"
    stream_governance {
        package  = var.stream_governance
    }
}
output "cc_demo_env" {
    description = "CC Environment ID"
    value       = resource.confluent_environment.cc_demo_env.id
}

# --------------------------------------------------------
# Apache Kafka Cluster and Schema Registry Cluster
# --------------------------------------------------------
resource "confluent_kafka_cluster" "cc_kafka_cluster" {
    display_name = "kafka-${var.demo_prefix}-${random_id.id.hex}"
    cloud        = var.cc_cloud_provider
    region       = var.cloud_region
    availability = var.cc_availability
    basic {}
    environment {
        id       = confluent_environment.cc_demo_env.id
    }
}
output "cc_kafka_cluster_id" {
    description  = "CC Kafka Cluster ID"
    value        = resource.confluent_kafka_cluster.cc_kafka_cluster.id
}
output "cc_kafka_cluster_bootstrap" {
    description  = "CC Kafka Cluster Bootstrap Endpoint"
    value        = resource.confluent_kafka_cluster.cc_kafka_cluster.bootstrap_endpoint
}

data "confluent_schema_registry_cluster" "sr" {
    environment {
        id     = confluent_environment.cc_demo_env.id
    }
    depends_on = [
        confluent_kafka_cluster.cc_kafka_cluster
    ]
}

# --------------------------------------------------------
# Service Account
# --------------------------------------------------------
resource "confluent_service_account" "app_main" {
    display_name = "sa-${var.demo_prefix}-${random_id.id.hex}"
    description  = "Main service account"
}

# --------------------------------------------------------
# Role Binding
# --------------------------------------------------------
resource "confluent_role_binding" "app_main_env_admin" {
    principal   = "User:${confluent_service_account.app_main.id}"
    role_name   = "EnvironmentAdmin"
    crn_pattern = confluent_environment.cc_demo_env.resource_name
}

# --------------------------------------------------------
# Credentials / API Keys
# --------------------------------------------------------
# Kafka
resource "confluent_api_key" "app_main_kafka_cluster_key" {
    display_name    = "api-key-cc-${var.demo_prefix}-${random_id.id.hex}"
    description     = "Kafka API Key for Confluent Cloud"
    owner {
        id          = confluent_service_account.app_main.id
        api_version = confluent_service_account.app_main.api_version
        kind        = confluent_service_account.app_main.kind
    }
    managed_resource {
        id          = confluent_kafka_cluster.cc_kafka_cluster.id
        api_version = confluent_kafka_cluster.cc_kafka_cluster.api_version
        kind        = confluent_kafka_cluster.cc_kafka_cluster.kind
        environment {
            id = confluent_environment.cc_demo_env.id
        }
    }
    depends_on      = [
        confluent_role_binding.app_main_env_admin
    ]
}
output "cc_cluster_key" {
    description = "Kafka API Key"
    value       = confluent_api_key.app_main_kafka_cluster_key.id
} 
output "cc_cluster_secret" {
    description = "Kafka API Key Secret"
    value       = confluent_api_key.app_main_kafka_cluster_key.secret
    sensitive   = true
} 

# Schema Registry
resource "confluent_api_key" "sr_cluster_key" {
    display_name    = "api-key-sr-${var.demo_prefix}-${random_id.id.hex}"
    description     = "Schema Registry API Key for Confluent Cloud"
    owner {
        id          = confluent_service_account.app_main.id
        api_version = confluent_service_account.app_main.api_version
        kind        = confluent_service_account.app_main.kind
    }
    managed_resource {
        id          = data.confluent_schema_registry_cluster.sr.id
        api_version = data.confluent_schema_registry_cluster.sr.api_version
        kind        = data.confluent_schema_registry_cluster.sr.kind
        environment {
            id = confluent_environment.cc_demo_env.id
        }
    }
    depends_on = [
        confluent_role_binding.app_main_env_admin,
        data.confluent_schema_registry_cluster.sr
    ]
}
output "sr_cluster_key" {
    description = "Schema Registry API Key"
    value       = confluent_api_key.sr_cluster_key.id
} 
output "sr_cluster_secret" {
    description = "Schema Registry API Key Secret"
    value       = confluent_api_key.sr_cluster_key.secret
    sensitive   = true
}
output "sr_cluster_url" {
    description = "Schema Registry REST Endpoint"
    value       = data.confluent_schema_registry_cluster.sr.rest_endpoint
}

# Flink
resource "confluent_api_key" "flink_api_key" {
    display_name    = "api-key-flink-${var.demo_prefix}-key-${random_id.id.hex}"
    description     = "Flink API Key for Confluent Cloud"
    owner {
        id          = confluent_service_account.app_main.id
        api_version = confluent_service_account.app_main.api_version
        kind        = confluent_service_account.app_main.kind
    }
    managed_resource {
        id          = data.confluent_flink_region.flink_region.id
        api_version = data.confluent_flink_region.flink_region.api_version
        kind        = data.confluent_flink_region.flink_region.kind
        environment {
            id = confluent_environment.cc_demo_env.id
        }
    }
    depends_on = [
        confluent_role_binding.app_main_env_admin
    ]
}

# --------------------------------------------------------
# Kafka topics/schema
# --------------------------------------------------------
variable "topics" {
    type = map(string)
    default = {
        RETAIL_DEMO_USERS = "compact"
        RETAIL_DEMO_PRODUCTS = "compact"
        RETAIL_DEMO_STORES = "compact"
        RETAIL_DEMO_PARTNERS = "compact"
        RETAIL_DEMO_VIEW_PRODUCT = "delete"
        RETAIL_DEMO_ADD_TO_CART = "delete"
        RETAIL_DEMO_ABANDON_CART = "delete"
        RETAIL_DEMO_STORE_ENTRY = "delete"
        RETAIL_DEMO_PARTNER_BROWSE = "delete"
    }
}
resource "confluent_kafka_topic" "topics" {
    for_each = var.topics
    kafka_cluster {
        id = confluent_kafka_cluster.cc_kafka_cluster.id
    }
    topic_name         = each.key
    rest_endpoint      = confluent_kafka_cluster.cc_kafka_cluster.rest_endpoint
    credentials {
        key            = confluent_api_key.app_main_kafka_cluster_key.id
        secret         = confluent_api_key.app_main_kafka_cluster_key.secret
    }
    partitions_count   = 1
    config             = {
        "cleanup.policy"      = each.value
        "retention.ms"        = "604800000"  # 7 days
    }
}
resource "confluent_schema" "avro-schemas" {
    for_each = var.topics
    schema_registry_cluster {
        id = data.confluent_schema_registry_cluster.sr.id
    }
    rest_endpoint = data.confluent_schema_registry_cluster.sr.rest_endpoint
    subject_name  = "${each.key}-value"
    format        = "AVRO"
    schema        = file("${path.module}/../backend/utils/schemas/${each.key}.json")
    credentials {
        key       = confluent_api_key.sr_cluster_key.id
        secret    = confluent_api_key.sr_cluster_key.secret
    }
}

# --------------------------------------------------------
# Flink Compute Pool
# --------------------------------------------------------
resource "confluent_flink_compute_pool" "flink_compute_pool" {
    display_name     = "flink-${var.demo_prefix}-key-${random_id.id.hex}"
    cloud            = var.cc_cloud_provider
    region           = var.cloud_region
    max_cfu          = 50
    environment {
        id = confluent_environment.cc_demo_env.id
    }
}
data "confluent_flink_region" "flink_region" {
    cloud = var.cc_cloud_provider
    region = var.cloud_region
}

# --------------------------------------------------------
# Flink Statements (created in order with explicit dependencies)
# --------------------------------------------------------
# 1. DEMO_RETAIL_BEDROCK - AI Connection (must be first)
resource "confluent_flink_statement" "bedrock_connection" {
    organization {
        id = data.confluent_organization.cc_org.id
    }
    environment {
        id = confluent_environment.cc_demo_env.id
    }
    compute_pool {
        id = confluent_flink_compute_pool.flink_compute_pool.id
    }
    principal {
        id = confluent_service_account.app_main.id
    }
    statement = templatefile("${path.module}/../backend/utils/sql/DEMO_RETAIL_BEDROCK.sql", {
        aws_access_key_id     = var.aws_access_key_id
        aws_secret_access_key = var.aws_secret_access_key
        aws_region            = var.cloud_region
        llm_model             = var.llm_model
        model_prefix          = split("-", var.cloud_region)[0]
    })
    properties = {
        "sql.current-catalog"  = resource.confluent_environment.cc_demo_env.id
        "sql.current-database" = resource.confluent_kafka_cluster.cc_kafka_cluster.id
    }
    rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
    credentials {
        key    = confluent_api_key.flink_api_key.id
        secret = confluent_api_key.flink_api_key.secret
    }
    depends_on = [
        confluent_flink_compute_pool.flink_compute_pool,
        confluent_kafka_topic.topics,
        confluent_schema.avro-schemas
    ]
}

# 2. CART_ABANDONMENT_NUDGE
resource "confluent_flink_statement" "cart_abandonment_nudge" {
    organization {
        id = data.confluent_organization.cc_org.id
    }
    environment {
        id = confluent_environment.cc_demo_env.id
    }
    compute_pool {
        id = confluent_flink_compute_pool.flink_compute_pool.id
    }
    principal {
        id = confluent_service_account.app_main.id
    }
    statement = file("${path.module}/../backend/utils/sql/CART_ABANDONMENT_NUDGE.sql")
    properties = {
        "sql.current-catalog"  = resource.confluent_environment.cc_demo_env.id
        "sql.current-database" = resource.confluent_kafka_cluster.cc_kafka_cluster.id
    }
    rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
    credentials {
        key    = confluent_api_key.flink_api_key.id
        secret = confluent_api_key.flink_api_key.secret
    }
    depends_on = [
        confluent_flink_statement.bedrock_connection
    ]
}

# 3. RETAIL_DEMO_CART_RECOVERY_MESSAGES
resource "confluent_flink_statement" "cart_recovery_messages" {
    organization {
        id = data.confluent_organization.cc_org.id
    }
    environment {
        id = confluent_environment.cc_demo_env.id
    }
    compute_pool {
        id = confluent_flink_compute_pool.flink_compute_pool.id
    }
    principal {
        id = confluent_service_account.app_main.id
    }
    statement = file("${path.module}/../backend/utils/sql/RETAIL_DEMO_CART_RECOVERY_MESSAGES.sql")
    properties = {
        "sql.current-catalog"  = resource.confluent_environment.cc_demo_env.id
        "sql.current-database" = resource.confluent_kafka_cluster.cc_kafka_cluster.id
    }
    rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
    credentials {
        key    = confluent_api_key.flink_api_key.id
        secret = confluent_api_key.flink_api_key.secret
    }
    depends_on = [
        confluent_flink_statement.cart_abandonment_nudge
    ]
}

# 4. STORE_PERSONALIZATION
resource "confluent_flink_statement" "store_personalization" {
    organization {
        id = data.confluent_organization.cc_org.id
    }
    environment {
        id = confluent_environment.cc_demo_env.id
    }
    compute_pool {
        id = confluent_flink_compute_pool.flink_compute_pool.id
    }
    principal {
        id = confluent_service_account.app_main.id
    }
    statement = file("${path.module}/../backend/utils/sql/STORE_PERSONALIZATION.sql")
    properties = {
        "sql.current-catalog"  = resource.confluent_environment.cc_demo_env.id
        "sql.current-database" = resource.confluent_kafka_cluster.cc_kafka_cluster.id
    }
    rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
    credentials {
        key    = confluent_api_key.flink_api_key.id
        secret = confluent_api_key.flink_api_key.secret
    }
    depends_on = [
        confluent_flink_statement.cart_recovery_messages
    ]
}

# 5. RETAIL_DEMO_STORE_VISIT_CONTEXT
resource "confluent_flink_statement" "store_visit_context" {
    organization {
        id = data.confluent_organization.cc_org.id
    }
    environment {
        id = confluent_environment.cc_demo_env.id
    }
    compute_pool {
        id = confluent_flink_compute_pool.flink_compute_pool.id
    }
    principal {
        id = confluent_service_account.app_main.id
    }
    statement = file("${path.module}/../backend/utils/sql/RETAIL_DEMO_STORE_VISIT_CONTEXT.sql")
    properties = {
        "sql.current-catalog"  = resource.confluent_environment.cc_demo_env.id
        "sql.current-database" = resource.confluent_kafka_cluster.cc_kafka_cluster.id
    }
    rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
    credentials {
        key    = confluent_api_key.flink_api_key.id
        secret = confluent_api_key.flink_api_key.secret
    }
    depends_on = [
        confluent_flink_statement.store_personalization
    ]
}

# 6. PARTNER_AD_GENERATOR
resource "confluent_flink_statement" "partner_ad_generator" {
    organization {
        id = data.confluent_organization.cc_org.id
    }
    environment {
        id = confluent_environment.cc_demo_env.id
    }
    compute_pool {
        id = confluent_flink_compute_pool.flink_compute_pool.id
    }
    principal {
        id = confluent_service_account.app_main.id
    }
    statement = file("${path.module}/../backend/utils/sql/PARTNER_AD_GENERATOR.sql")
    properties = {
        "sql.current-catalog"  = resource.confluent_environment.cc_demo_env.id
        "sql.current-database" = resource.confluent_kafka_cluster.cc_kafka_cluster.id
    }
    rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
    credentials {
        key    = confluent_api_key.flink_api_key.id
        secret = confluent_api_key.flink_api_key.secret
    }
    depends_on = [
        confluent_flink_statement.store_visit_context
    ]
}

# 7. RETAIL_DEMO_PARTNER_BROWSE_ADS
resource "confluent_flink_statement" "partner_browse_ads" {
    organization {
        id = data.confluent_organization.cc_org.id
    }
    environment {
        id = confluent_environment.cc_demo_env.id
    }
    compute_pool {
        id = confluent_flink_compute_pool.flink_compute_pool.id
    }
    principal {
        id = confluent_service_account.app_main.id
    }
    statement = file("${path.module}/../backend/utils/sql/RETAIL_DEMO_PARTNER_BROWSE_ADS.sql")
    properties = {
        "sql.current-catalog"  = resource.confluent_environment.cc_demo_env.id
        "sql.current-database" = resource.confluent_kafka_cluster.cc_kafka_cluster.id
    }
    rest_endpoint = data.confluent_flink_region.flink_region.rest_endpoint
    credentials {
        key    = confluent_api_key.flink_api_key.id
        secret = confluent_api_key.flink_api_key.secret
    }
    depends_on = [
        confluent_flink_statement.partner_ad_generator
    ]
}

# --------------------------------------------------------
# Generate Python Config File
# --------------------------------------------------------
resource "local_file" "python_config" {
    filename = "${path.module}/../backend/utils/config/cflt-cloud-credentials.ini"
    content = templatefile("${path.module}/../backend/utils/config/template.ini", {
        kafka_bootstrap_servers      = confluent_kafka_cluster.cc_kafka_cluster.bootstrap_endpoint
        kafka_api_key                = confluent_api_key.app_main_kafka_cluster_key.id
        kafka_api_secret             = confluent_api_key.app_main_kafka_cluster_key.secret
        schema_registry_url          = data.confluent_schema_registry_cluster.sr.rest_endpoint
        schema_registry_api_key      = confluent_api_key.sr_cluster_key.id
        schema_registry_api_secret   = confluent_api_key.sr_cluster_key.secret
    })
    file_permission = "0600"
    depends_on = [
        confluent_api_key.app_main_kafka_cluster_key,
        confluent_api_key.sr_cluster_key
    ]
}
