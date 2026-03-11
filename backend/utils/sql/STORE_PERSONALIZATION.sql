CREATE MODEL STORE_PERSONALIZATION
INPUT (prompt STRING)
OUTPUT (welcome_message STRING)
WITH (
  'provider'            = 'bedrock',
  'bedrock.connection'  = 'DEMO_RETAIL_BEDROCK',
  'task'                = 'text_generation',
  'bedrock.params.max_tokens' = '2048',
  'bedrock.system_prompt' = 'Generate a personalized welcome message for a customer entering a store. Pick one or two of the store promotions based on the customer tier (BLUE, BRONZE, SILVER, GOLD, PLATINUM) and their last product viewed to create a personalised offer. Be friendly and specific as this ad is to be sent as is to the customer. Maximum 200 characters.'
);