CREATE MODEL CART_ABANDONMENT_NUDGE
INPUT (prompt STRING)
OUTPUT (llm_output STRING)
WITH (
  'provider'            = 'bedrock',
  'bedrock.connection'  = 'DEMO_RETAIL_BEDROCK',
  'task'                = 'text_generation',
  'bedrock.params.max_tokens' = '2048',
  'bedrock.system_prompt' = 'Generate a personalized promotional message (max 200 characters) to recover an abandoned shopping cart. Randomly select a discount based on tier (BLUE:2.0-4.0%, BRONZE:3.0-5.0%, SILVER:4.0-6.0%, GOLD:5.0-7.0%, PLATINUM:6.0-8.0%) and a validity window between 30 and 180 minutes. The tone must be friendly, engaging, and specific, ready to send to the customer.'
);