CREATE MODEL STORE_PERSONALIZATION
INPUT (prompt STRING)
OUTPUT (welcome_message STRING)
WITH (
  'provider'            = 'bedrock',
  'bedrock.connection'  = 'DEMO_RETAIL_BEDROCK',
  'task'                = 'text_generation',
  'bedrock.params.max_tokens' = '2048',
  'bedrock.system_prompt' = 'Generate a personalized welcome message (max 200 characters) for a customer entering a store. Randomly pick one or two promotions based on the customer tier (BLUE, BRONZE, SILVER, GOLD, PLATINUM) and their last product viewed to create a specific, engaging offer. The tone must be friendly and ready to send directly to the customer.'
);