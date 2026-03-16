# 🏪 UrbanStreet Retail AI Demo

An omnichannel retail AI demonstration powered by Confluent Cloud, showcasing how data streaming enables real-time customer journey personalization across online, in-store, and partner channels.

## What is This Demo About?

This demo tells the story of **Clarice**, a busy professional shopping with **UrbanStreet**, a fashion & lifestyle retailer. Follow her journey through five acts that demonstrate how a data streaming platform transforms retail AI from a buzzword into measurable revenue:

### The Reality of Modern Retail

- **Localised ads = 2x sales uplift** - When ads reflect local context (store, region, live inventory), retailers see roughly double the impact versus generic campaigns
- **4 in 5 customers change their mind mid-journey** - The battle is won or lost in the moment: comparing prices, switching from delivery to click-and-collect, swapping items at the shelf
- **80% of Netflix viewing from recommendations** - Consumers expect the same intelligence from retailers: "if you know me, show me"

### The Five Acts

**Act 1 - Online Discovery**: Clarice sees a localized ad on Instagram: "20% off trainers this weekend – pick up in 30 minutes at Oxford Street". The ad knows her city, real-time inventory, and her style preferences.

**Act 2 - Mid-Journey Cart Abandonment**: She adds trainers to cart but hesitates. Within minutes, she receives an event-driven nudge: "Still thinking? Free same-day pickup if you check out in the next 30 minutes."

**Act 3 - In-Store Experience**: Clarice visits the physical store. The app recognizes her arrival and surfaces: "Welcome back, Clarice – your size is in stock, aisle 3". Store associates see her online activity on their tablets.

**Act 4 - Partner Marketplace**: A week later, on ShopNow marketplace, she sees real-time personalized ads: "Complete your look – UrbanStreet running set, 15% off with your loyalty ID". Real-time inventory prevents promoting out-of-stock items.

**Act 5 - Analytics & Optimization**: Marketing teams see unified insights across all channels from the same streaming backbone, enabling continuous learning and improvement.

### Business Impact

- **2x sales uplift** from localized, real-time ads
- **32% conversion increase** from event-driven cart recovery
- **33% YoY basket growth** from real-time retail media
- **Seamless omnichannel** experience powered by streaming data

## Architecture

```
┌──────────────────────────────────────────────────┐
│              Infrastructure Setup                │
│                                                  │
│  ┌────────────┐         ┌──────────────────┐     │
│  │ Terraform  │────────►│ Confluent Cloud  │     │
│  └────────────┘         └──────────────────┘     │
│        │                                         │
│        │ Creates:                                │
│        ├─ Environment, Kafka cluster             │
│        ├─ Schema Registry                        │
│        ├─ Flink compute pool                     │
│        ├─ Topics with AVRO schemas               │
│        ├─ Flink SQL statements (AI)              │
│        └─ API keys → Python config file          │
└──────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│             Application Runtime                  │
│                                                  │
│  ┌─────────────────┐                             │
│  │  React Frontend │                             │
│  │  - Customer Tab │──┐                          │
│  │  - Kafka Tab    │  │                          │
│  │  - Dashboard    │  │                          │
│  └─────────────────┘  │                          │
│                       │                          │
│  ┌─────────────────┐  │                          │
│  │  Flask Backend  │◄─┘                          │
│  │  - Events API   │                             │
│  │  - Kafka client |                             │
│  │  - Session Mgmt │                             │
│  └────────┬────────┘                             │
└───────────┼──────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░ CONFLUENT CLOUD (AWS)░░░░░░░░░░░░░░░░░░░░░░│
│░░┌─────────────────────────────────┐░░┌─────────────────────┐░░│
│░░│          Kafka Topics           │─►│  Schema Registry    │░░│
│░░│  CDC (from Postgres):           │░░│  (AVRO schemas)     │░░│
│░░│    - db_public_partners         │░░└─────────────────────┘░░│
│░░│    - db_public_products         │░░░░░░░░░░ ▲░░░░░░░░░░░░░░░│
│░░│    - db_public_stores           │░░░░░░░░░░ |░░░░░░░░░░░░░░░│
│░░│    - db_public_users            │░░┌────────┴────────────┐░░|
│░░│  Clickstream Events             |░░│  Postgres CDC       │░░|
|░░|    - RETAIL_DEMO_VIEW_PRODUCT   │░░│  Connector          │░░|
|░░|    - RETAIL_DEMO_ADD_TO_CART    |░░│  (Fully Managed)    │░░|
|░░|    - RETAIL_DEMO_ABANDON_CART   |░░└────────┬────────────┘░░|
|░░|    - RETAIL_DEMO_STORE_ENTRY    |░░░░░░░░░░░│░░░░░░░░░░░░░░░|
|░░|    - RETAIL_DEMO_PARTNER_BROWSE |◄─────────────────┐░░░░░░░░|
│░░└─────────────────────────────────┘░░░░░░░░░░░|░░░░░░|░░░░░░░░│
|░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|░░░░░░|░░░░░░░░|
├───────────────────────────────────┐░░░░░░░░░░░░|░░░░░░|░░░░░░░░|
│               AWS                 |░░░░░░░░░░░░|░░░░░░|░░░░░░░░|
│  ┌─────────────────────┐          |░░░░░░░░░░░░|░░░░░░|░░░░░░░░|
│  |   AWS RDS Postgres  │◄─────────┼────────────┘░░░░░░|░░░░░░░░|
│  │   (db.t3.micro)     │          |░░░┌───────────────┴─────┐░░│                     
│  │   Logical Repl ON   │          |░░░│  Flink SQL:         │░░│
│  └─────────────────────┘          |░░░│  - AI connections   │░░│
│  ┌──────────────────┐             |░░░│  - Stream joins     │░░│
│  |    AWS Bedrock   |◄────────────┼───┤  - ML_PREDICT       │░░│
│  │  (Claude Models) │             |░░░│  - Real-time AI     │░░│
│  └──────────────────┘             |░░░└─────────────────────┘░░│
└───────────────────────────────────┴────────────────────────────┘
```

## What Makes This Demo Special?

**🚀 Fully Automated Infrastructure-as-Code**

This demo uses **Terraform** to automatically provision everything:

- ✅ **One Command Setup** - `./setup-demo.sh` does it all
- ✅ **Complete Infrastructure** - Environment, BASIC Kafka Clusters, ESSENTIALS Schema Registry Cluster, AWS RDS Postgres, Fully Managed CDC Connector, Kafka topics, AVRO schemas, Flink Computing Pool
- ✅ **Production-Ready Patterns** - CDC from Postgres, API key management, secret handling, GitOps workflow
- ✅ **Easy Cleanup** - `./destroy-demo.sh` removes everything

**🤖 Real AI Integration**

- AWS Bedrock (Claude models) for cart recovery, recommendations, and retail media
- Flink SQL with `ML_PREDICT` for stream processing + AI
- Live AI-generated messages visible in the dashboard

**📊 End-to-End Customer Journey**

- Complete omnichannel story from discovery to purchase
- Real metrics: 2x uplift, 32% conversion increase, 33% basket growth
- Business-focused narrative for CMOs, CDOs, and product leaders

## Prerequisites

- **Python 3.8+**
- **librdkafka (latest)**
- **PostgreSQL client libraries** - Required for `psycopg2` Python package
  - **macOS**: `brew install postgresql`
  - **Ubuntu/Debian**: `sudo apt-get install libpq-dev python3-dev`
  - **RHEL/CentOS**: `sudo yum install postgresql-devel python3-devel`
- **Node.js 16+**
- **Terraform CLI** - for infrastructure deployment
- **Confluent Cloud account** with Cloud API credentials ([create here](https://confluent.cloud/settings/api-keys))
- **AWS account** with required IAM permissions (see below)

### AWS IAM Permissions Required

Your AWS credentials must have the following IAM policies attached:

**For RDS Postgres Database Deployment:**
- `AmazonRDSFullAccess` - Create/manage RDS instances, parameter groups, and snapshots
- `AmazonRDSDataFullAccess` - Access RDS data and execute SQL operations

**For VPC and Networking:**
- `AmazonEC2FullAccess` - Create and manage security groups (required for RDS)
  - Alternative: Create a custom policy with `ec2:CreateSecurityGroup`, `ec2:AuthorizeSecurityGroupIngress`, `ec2:AuthorizeSecurityGroupEgress`, `ec2:DeleteSecurityGroup`, `ec2:DescribeSecurityGroups`

**For AI/GenAI Integration:**
- `AmazonBedrockFullAccess` - Access to Claude AI models for real-time predictions via Confluent Flink

**Minimal Custom Policy Example:**

If you prefer not to use full access policies, create a custom IAM policy with:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:CreateDBInstance",
        "rds:DeleteDBInstance",
        "rds:DescribeDBInstances",
        "rds:CreateDBParameterGroup",
        "rds:DeleteDBParameterGroup",
        "rds:DescribeDBParameterGroups",
        "rds:ModifyDBParameterGroup",
        "rds:DescribeDBParameters",
        "rds-data:*",
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup",
        "ec2:DescribeSecurityGroups",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:AuthorizeSecurityGroupEgress",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupEgress",
        "ec2:DescribeVpcs",
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

**Important Security Notes:**
- The RDS instance is created with `publicly_accessible = true` for demo purposes
- In production, restrict security group ingress to specific IP ranges
- The demo auto-generates a random RDS password (stored in Terraform state)
- Use `terraform output -raw rds_password` to retrieve the password after deployment

## Quick Start

### 1. Configure Credentials

Create a `.env` file in the project root (use `.env_example` as reference):

```bash
#!/bin/bash

# AWS credentials (for RDS Postgres deployment and Bedrock AI integration)
export AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_KEY"

# Confluent Cloud API credentials (for Terraform)
export CONFLUENT_CLOUD_API_KEY="YOUR_CONFLUENT_CLOUD_API_KEY"
export CONFLUENT_CLOUD_API_SECRET="YOUR_CONFLUENT_CLOUD_API_SECRET"
```

**Important:** These are **Cloud API Keys** for managing Confluent resources via Terraform, not Kafka cluster keys. Get them from [Confluent Cloud Settings](https://confluent.cloud/settings/api-keys).

### 2. Run Setup (One Command!)

```bash
./setup-demo.sh
```

This automated setup script will:

**✅ Validate Prerequisites**
- Check Python 3.8+, Node.js 16+, and Terraform are installed
- Validate `.env` credentials exist and are properly configured

**✅ Deploy Confluent Cloud Infrastructure with Terraform**
- Create new Confluent Cloud environment
- Create Kafka cluster (Basic tier, eu-west-1)
- Create Schema Registry (Essentials package)
- Create Flink compute pool for stream processing
- Deploy AWS RDS Postgres database (db.t3.micro) with logical replication enabled
- Create fully managed Postgres CDC connector to stream reference data:
  - `db_public_users` - User profiles from Postgres (CDC)
  - `db_public_products` - Product catalog from Postgres (CDC)
  - `db_public_stores` - Store locations from Postgres (CDC)
  - `db_public_partners` - Partner marketplaces from Postgres (CDC)
- Generate API keys for Kafka, Schema Registry, and Flink
- Create event topics with AVRO schemas:
  - `RETAIL_DEMO_VIEW_PRODUCT` - Product view events
  - `RETAIL_DEMO_ADD_TO_CART` - Cart addition events
  - `RETAIL_DEMO_ABANDON_CART` - Cart abandonment events
  - `RETAIL_DEMO_STORE_ENTRY` - Physical store visit events
  - `RETAIL_DEMO_PARTNER_BROWSE` - Partner marketplace browse events
- Deploy Flink SQL statements for AI processing (in order):
  1. Create AWS Bedrock connection
  2. Create cart abandonment AI nudge table
  3. Create cart recovery messages table
  4. Create store personalization table
  5. Create store visit context table
  6. Create partner ad generator table
  7. Create partner browse ads table
- **Auto-generate** `backend/config/cflt-cloud-credentials.ini` with all credentials

**✅ Setup Python Environment**
- Create virtual environment
- Install all Python dependencies

**✅ Setup Frontend**
- Install all npm dependencies

**✅ Initialize Demo Data**
- Deploy RDS Postgres instance with logical replication enabled
- Create database tables (users, products, stores, partners)
- Populate 5 demo users in Postgres (username: clarice, adam, megan, hemal, siri / password: secret)
- Load product catalog, store locations, and partner data into Postgres
- CDC connector automatically streams all data to Kafka topics

**Estimated time:** 5-10 minutes (depending on Confluent Cloud provisioning)

### 3. Run the Demo

```bash
./run-demo.sh
```

The application will start:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

Both services run in parallel and auto-reload on code changes.

## Using the Demo

### Customer Tab (Act 1 & 2: Discovery & Cart Abandonment)

1. **Login** with demo credentials:
   - Username: `clarice` (or any of the 4 users: `siri`, `hemal`, `adam` or `megan`)
   - Password: `secret` (the same password for all users)

2. **Browse Products** - Click "View" to generate VIEW_PRODUCT events

3. **Add to Cart** - Click "Add to Cart" to generate ADD_TO_CART events

4. **Abandon Cart** - Click "Abandon Cart" to trigger AI nudge (Act 2)
   - Check Dashboard for AI-generated recovery message
   - Expected: 32% conversion uplift

### Customer Tab (Act 3: In-Store Experience)

5. **Enter Store** - Click on a store location
   - Generates STORE_ENTRY event
   - Simulates in-store visit with online context
   - Dashboard shows personalized in-store recommendations

### Customer Tab (Act 4: Partner Experience)

6. **Browse Partner Marketplace** - Click on partner categories
   - Generates PARTNER_BROWSE events
   - Simulates retail media opportunities
   - Dashboard shows personalized ad placements

### Kafka Tab (Real-Time Events)

- View live streaming events from all topics
- Auto-refreshes every 2 seconds
- See detailed event data including:
  - Event IDs, timestamps, usernames
  - Product details, cart values
  - Store locations, partner interactions

### Dashboard Tab (Act 5: Analytics & AI Decisions)

- **Real-time Metrics**:
  - Product views, cart additions, abandonments
  - Store visits, partner browses
  - Conversion rate

- **AI Recommendations** (🤖 Live GenAI when Flink SQL is configured):
  - **Real AI-generated** cart recovery messages from Claude Sonnet
  - Static recommendations when AI tables not yet created
  - Visual distinction with glowing **🤖 LIVE AI** badge
  - In-store personalization context
  - Retail media optimization (2x sales uplift)

- **Journey Insights**:
  - Act 1: Localized ads
  - Act 2: Mid-journey nudges
  - Act 3: In-store experience
  - Act 4: Retail media

- **Platform Value**:
  - Real-time decision making
  - Unified data backbone
  - Reusable data products
  - Omnichannel intelligence

## Demo Flow (5 Acts)

### Act 1: Online Discovery
- Customer browses products
- AI-powered localized ads with real-time inventory
- **Impact**: 2x sales uplift

### Act 2: Mid-Journey Cart Abandonment
- Customer abandons cart
- Event-driven promotional nudge triggered
- **Impact**: 32% conversion increase

### Act 3: In-Store Experience
- Customer enters physical store
- Personalized service based on online activity
- **Impact**: Seamless omnichannel experience

### Act 4: Partner Marketplace
- Customer browses on partner app
- Real-time retail media placements
- **Impact**: 33% YoY basket growth

### Act 5: Analytics & Optimization
- Unified insights across all channels
- Continuous learning and improvement
- **Impact**: Reusable data products

## 🤖 Live GenAI Integration

The demo includes **real-time AI predictions** powered by AWS Bedrock (Claude models) and Flink SQL.

### Automated Setup

Terraform automatically deploys all Flink SQL statements including:

1. **AWS Bedrock Connection** - Connects Flink to AWS Bedrock API
2. **AI Processing Tables** - Using `LATERAL TABLE(ML_PREDICT(...))` for:
   - Cart abandonment recovery messages
   - Product recommendations
   - Store visit personalization
   - Partner browse ads

### How It Works

1. **Customer Actions** generate events (view, cart, abandon, etc.)
2. **Flink SQL** processes events in real-time and calls AI models
3. **AI Responses** are written to Kafka topics
4. **Backend Consumes** AI-generated messages
5. **Dashboard Shows** live predictions with **🤖 LIVE AI** badge

### Visual Experience

**Live AI Predictions:**
- Real AI-generated messages in monospace font
- Timestamp showing when AI responded
- **🤖 LIVE AI** badge indicating real-time GenAI

### Monitored AI Topics

The backend automatically consumes from:
- `RETAIL_DEMO_CART_RECOVERY_MESSAGES` - AI cart abandonment recovery
- `RETAIL_DEMO_STORE_VISIT_CONTEXT` - Enriched in-store personalization
- `RETAIL_DEMO_PARTNER_BROWSE_ADS` - Real-time retail media ads

## Kafka Topics

All topics are automatically created by Terraform with AVRO schemas:

**CDC Topics** (from Postgres via fully managed CDC connector):
- `db_public_users` - User profiles streamed from RDS Postgres
- `db_public_products` - Product catalog streamed from RDS Postgres
- `db_public_stores` - Store locations streamed from RDS Postgres
- `db_public_partners` - Partner marketplaces streamed from RDS Postgres

**Event Topics** (7-day retention):
- `RETAIL_DEMO_VIEW_PRODUCT` - Product view events
- `RETAIL_DEMO_ADD_TO_CART` - Cart addition events
- `RETAIL_DEMO_ABANDON_CART` - Cart abandonment events
- `RETAIL_DEMO_STORE_ENTRY` - Physical store visit events
- `RETAIL_DEMO_PARTNER_BROWSE` - Partner marketplace browse events

## Development

### Backend (Python/Flask)

```bash
source .venv/bin/activate
python backend/app.py
```

### Frontend (React)

```bash
cd frontend
npm start
```

## Cleanup and Teardown

When you're finished with the demo, you can destroy all Confluent Cloud resources to avoid ongoing charges.

### Destroy Infrastructure

```bash
cd terraform
source ../.env
terraform destroy \
    -var="aws_access_key_id=$AWS_ACCESS_KEY_ID" \
    -var="aws_secret_access_key=$AWS_SECRET_ACCESS_KEY"
```

This will remove:
- ✅ AWS RDS Postgres database and all data
- ✅ Postgres CDC connector
- ✅ All Kafka topics and data (including CDC topics)
- ✅ All Flink SQL statements and compute pools
- ✅ Schema Registry schemas
- ✅ API keys (Kafka, Schema Registry, Flink)
- ✅ Kafka cluster
- ✅ Confluent Cloud environment

**Important Notes:**
- Terraform will prompt for confirmation before destroying
- The operation is **irreversible** - all data will be permanently deleted
- Service accounts and API keys will be revoked
- The generated `backend/utils/config/cflt-cloud-credentials.ini` will become invalid

### Clean Up Local Files

To completely reset your local environment:

```bash
# Remove Python virtual environment
rm -rf .venv/

# Remove frontend dependencies
rm -rf frontend/node_modules/

# Remove generated config (will be recreated on next setup)
rm -f backend/utils/config/cflt-cloud-credentials.ini

# Remove Terraform state (optional, only if starting fresh)
cd terraform
rm -rf .terraform/
rm -f terraform.tfstate*
rm -f .terraform.lock.hcl
```

## Troubleshooting

### Setup fails with "Terraform not found"
- Install Terraform: `brew install terraform` (macOS) or download from [terraform.io](https://www.terraform.io/downloads)
- Verify installation: `terraform version`

### Python dependencies fail to install - psycopg2 compilation error
If `pip install -r requirements.txt` fails with errors about `psycopg2` (common on Mac M1/M2):

**Root cause**: `psycopg2` requires PostgreSQL client libraries to compile

**Solution**:
```bash
# macOS (including M1/M2)
brew install postgresql

# Ubuntu/Debian
sudo apt-get install libpq-dev python3-dev

# RHEL/CentOS
sudo yum install postgresql-devel python3-devel

# Then retry
pip install -r requirements.txt
```

**Note**: You don't need a running PostgreSQL server, just the client libraries for Python compilation.

### Setup fails with "401 Unauthorized" during Terraform apply
- Check your Confluent Cloud API credentials in `.env`
- These must be **Cloud API Keys**, not Kafka cluster keys
- Create them at [Confluent Cloud Settings](https://confluent.cloud/settings/api-keys)
- Ensure they have Organization Admin or Environment Admin permissions

### Backend won't start
- Check `backend/utils/config/cflt-cloud-credentials.ini` exists and is valid
- Verify Confluent Cloud cluster is running (check web UI)
- Ensure Python dependencies are installed: `pip install -r requirements.txt`
- Check Kafka connectivity: `telnet <bootstrap-server> 9092`

### Frontend won't start
- Verify Node.js is installed: `node --version`
- Install dependencies: `cd frontend && npm install`
- Check for port conflicts on 3000: `lsof -i :3000`

### No events showing in Kafka Tab
- Verify topics were created by Terraform (check Confluent Cloud web UI)
- Check Schema Registry is accessible
- Generate events from Customer tab first (login and click actions)
- Check browser console for API errors

### "No AI recommendations" in Dashboard
- This is expected until Flink SQL tables are created
- Flink SQL statements are automatically deployed by Terraform
- The AI connection requires valid AWS Bedrock credentials
- Check Flink SQL workspace in Confluent Cloud for statement status

### Terraform destroy fails
- Some resources may have dependencies
- Try: `terraform destroy -refresh=false`
- Manual cleanup: Delete environment from Confluent Cloud web UI

## Project Structure

```
retail-ai-demo/
├── backend/
│   ├── app.py                              # Flask backend (API, Kafka producers/consumers)
│   ├── schemas/                            # AVRO schema definitions (JSON)
│   └── config/
│       ├── cflt-cloud-credentials.ini      # Generated by Terraform
│       └── template.ini                    # Config template for Terraform
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CustomerTab.js              # Customer journey interface
│   │   │   ├── KafkaTab.js                 # Real-time event visualization
│   │   │   └── DashboardTab.js             # Analytics & AI insights
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── terraform/
│   ├── confluent.tf                        # Confluent Cloud resources
│   ├── aws.tf                              # AWS RDS Postgres + CDC setup
│   ├── providers.tf                        # Terraform providers
│   ├── vars.tf                             # Variables and defaults
│   ├── flink/                              # Flink SQL statements
│   │   ├── 01_bedrock_connection.sql       # AWS Bedrock AI connection
│   │   ├── 02_cart_abandonment_nudge.sql   # Cart recovery AI logic
│   │   ├── 03_cart_recovery_messages.sql   # AI-generated messages
│   │   ├── 04_store_personalization.sql    # In-store AI recommendations
│   │   ├── 05_store_visit_context.sql      # Store visit enrichment
│   │   ├── 06_partner_ad_generator.sql     # Partner ad AI generation
│   │   └── 07_partner_browse_ads.sql       # Partner browse ads
│   ├── scripts/
│   │   ├── init_db_schema.py               # Initialize Postgres schema & CDC
│   │   └── init_db_data.py                 # Demo data (users, products, stores, partners)
│   └── sql/
│       ├── create_users.sql                # Postgres users table DDL
│       ├── create_products.sql             # Postgres products table DDL
│       ├── create_stores.sql               # Postgres stores table DDL
│       └── create_partners.sql             # Postgres partners table DDL
├── setup-demo.sh                           # One-command setup (Terraform + dependencies)
├── run-demo.sh                             # Start backend + frontend
├── requirements.txt                        # Python dependencies
├── .env_template                           # Template for AWS & Confluent Cloud credentials
└── README.md
```

## Key Technologies

**Infrastructure & Platform:**
- **Terraform** - Infrastructure-as-Code for automated deployment
- **Confluent Cloud** - Data streaming platform (Kafka, Schema Registry, Flink)
- **Apache Kafka** - Event streaming and real-time data pipelines
- **Schema Registry** - AVRO schema management and evolution
- **Flink SQL** - Stream processing with AI integration
- **AWS RDS Postgres** - Source database for CDC (db.t3.micro with logical replication)
- **Postgres CDC Connector** - Fully managed connector for streaming database changes

**AI & Machine Learning:**
- **AWS Bedrock** - Claude AI models (Sonnet 4.5, Haiku 3.5)
- **Flink ML_PREDICT** - Real-time AI inference on streaming data

**Application:**
- **Flask** - Python backend with Kafka producers/consumers
- **React** - Frontend framework for interactive UI
- **Python** - Backend logic and Kafka client

## Business Metrics

This demo demonstrates real industry metrics:

- **Localized Ads**: 2x sales uplift from real-time context
- **Cart Recovery**: 32% conversion increase from event-driven nudges
- **Retail Media**: 33% YoY basket growth from personalized placements
- **Omnichannel Experience**: Seamless journey across web, store, and partners

## References

**Confluent Resources:**
- [Confluent Cloud Documentation](https://docs.confluent.io/cloud/current/)
- [Terraform Provider for Confluent](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs)
- [Flink SQL Reference](https://docs.confluent.io/cloud/current/flink/reference/overview.html)
- [Confluent AI/ML Integration](https://docs.confluent.io/cloud/current/ai/managed-model.html)

**AWS Resources:**
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Bedrock Supported Models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)

## Quick Command Reference

```bash
# Setup (first time)
./setup-demo.sh

# Run demo
./run-demo.sh

# Destroy infrastructure
./destroy-demo.sh

# Manual Terraform operations
cd terraform
source ../.env
terraform plan -var="aws_access_key_id=$AWS_ACCESS_KEY_ID" -var="aws_secret_access_key=$AWS_SECRET_ACCESS_KEY"
terraform apply -var="aws_access_key_id=$AWS_ACCESS_KEY_ID" -var="aws_secret_access_key=$AWS_SECRET_ACCESS_KEY"
terraform destroy -var="aws_access_key_id=$AWS_ACCESS_KEY_ID" -var="aws_secret_access_key=$AWS_SECRET_ACCESS_KEY"

# View RDS connection details (including auto-generated password)
terraform output rds_connection
terraform output -json rds_connection | jq -r '.password'
```

---

**🏪 UrbanStreet Retail AI Demo** - Powered by Confluent Cloud, AWS Bedrock, and Terraform

*Demonstrating how data streaming transforms retail AI from buzzword to measurable revenue*
