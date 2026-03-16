# --------------------------------------------------------
# AWS Provider Configuration
# --------------------------------------------------------
provider "aws" {
    region     = var.cloud_region
    access_key = var.aws_access_key_id
    secret_key = var.aws_secret_access_key
}

# --------------------------------------------------------
# Generate Random Password for RDS
# --------------------------------------------------------
resource "random_password" "rds_password" {
    length           = 12
    special          = true
    override_special = "!#$%&*()-_=+[]{}<>:?"
    min_lower        = 2
    min_upper        = 2
    min_numeric      = 2
    min_special      = 2
}

# --------------------------------------------------------
# Security Group for RDS
# --------------------------------------------------------
resource "aws_security_group" "rds_sg" {
    name        = "rds-${var.demo_prefix}-${random_id.id.hex}-sg"
    description = "Security group for RDS Postgres instance"

    # Allow inbound PostgreSQL traffic from anywhere (for demo purposes)
    # In production, restrict this to specific IPs/CIDR blocks
    ingress {
        from_port   = 5432
        to_port     = 5432
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
        description = "PostgreSQL access"
    }

    # Allow all outbound traffic
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        description = "Allow all outbound traffic"
    }

    tags = {
        Name = "rds-${var.demo_prefix}-${random_id.id.hex}-sg"
    }
}

# --------------------------------------------------------
# RDS Postgres Database Instance (smallest size for demo)
# --------------------------------------------------------
resource "aws_db_instance" "postgres" {
    identifier             = "rds-${var.demo_prefix}-${random_id.id.hex}"
    engine                 = "postgres"
    engine_version         = "17.4"
    instance_class         = "db.t3.micro"
    allocated_storage      = 20
    storage_type           = "gp2"

    db_name                = var.aws_rds_database_name
    username               = var.aws_rds_username
    password               = random_password.rds_password.result

    publicly_accessible    = true
    skip_final_snapshot    = true
    vpc_security_group_ids = [aws_security_group.rds_sg.id]

    # Enable logical replication for CDC
    parameter_group_name    = aws_db_parameter_group.postgres_cdc.name

    # No backups needed for demo database
    backup_retention_period = 0

    tags = {
        Name = "rds-${var.demo_prefix}-${random_id.id.hex}"
    }
}

# --------------------------------------------------------
# RDS Parameter Group for CDC (Logical Replication)
# --------------------------------------------------------
resource "aws_db_parameter_group" "postgres_cdc" {
    name        = "pg-${var.demo_prefix}-${random_id.id.hex}-cdc"
    family      = "postgres17"
    description = "Parameter group for PostgreSQL CDC with logical replication"

    parameter {
        name         = "rds.logical_replication"
        value        = "1"
        apply_method = "pending-reboot"
    }

    parameter {
        name         = "wal_sender_timeout"
        value        = "0"
        apply_method = "immediate"
    }

    tags = {
        Name = "pg-${var.demo_prefix}-${random_id.id.hex}-cdc"
    }
}

# --------------------------------------------------------
# Initialize PostgreSQL Schema (create users table and publication)
# --------------------------------------------------------
resource "null_resource" "init_postgres_schema" {
    # Trigger on RDS instance changes
    triggers = {
        db_instance_id = aws_db_instance.postgres.id
    }

    # Create table and publication using Python script
    # Script will wait for RDS to be available
    provisioner "local-exec" {
        command = "python ${path.module}/scripts/init_db_schema.py"

        environment = {
            DB_HOST     = nonsensitive(aws_db_instance.postgres.address)
            DB_PORT     = nonsensitive(tostring(aws_db_instance.postgres.port))
            DB_NAME     = nonsensitive(var.aws_rds_database_name)
            DB_USER     = nonsensitive(var.aws_rds_username)
            DB_PASSWORD = nonsensitive(random_password.rds_password.result)
        }
    }

    depends_on = [
        aws_db_instance.postgres
    ]
}

# --------------------------------------------------------
# Outputs
# --------------------------------------------------------
output "rds_connection" {
    description = "RDS Postgres connection details"
    value = {
        endpoint      = aws_db_instance.postgres.endpoint
        address       = aws_db_instance.postgres.address
        port          = aws_db_instance.postgres.port
        database_name = aws_db_instance.postgres.db_name
        username      = aws_db_instance.postgres.username
        password      = random_password.rds_password.result
    }
    sensitive = true
}
