CREATE CONNECTION DEMO_RETAIL_BEDROCK
WITH (
  'type'          = 'bedrock',
  --'endpoint'      = 'https://bedrock-runtime.eu-central-1.amazonaws.com/model/eu.anthropic.claude-sonnet-4-5-20250929-v1:0/invoke',
  'endpoint'      = 'https://bedrock-runtime.eu-central-1.amazonaws.com/model/eu.anthropic.claude-3-5-haiku-20241022-v1:0/invoke',
  'aws-access-key' = '${aws_access_key_id}',
  'aws-secret-key' = '${aws_secret_access_key}'
);