CREATE CONNECTION DEMO_RETAIL_BEDROCK
WITH (
  'type'          = 'bedrock',
  'endpoint'      = 'https://bedrock-runtime.${aws_region}.amazonaws.com/model/${model_prefix}.${llm_model}/invoke',
  'aws-access-key' = '${aws_access_key_id}',
  'aws-secret-key' = '${aws_secret_access_key}'
);