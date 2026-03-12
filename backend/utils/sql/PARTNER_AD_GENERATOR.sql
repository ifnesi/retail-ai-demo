CREATE MODEL PARTNER_AD_GENERATOR
INPUT (prompt STRING)
OUTPUT (ad_copy STRING)
WITH (
  'provider'            = 'bedrock',
  'bedrock.connection'  = 'DEMO_RETAIL_BEDROCK',
  'task'                = 'text_generation',
  'bedrock.params.max_tokens' = '2048',
  'bedrock.system_prompt' = 'Generate a personalized advertisement (max 200 characters) for a customer visiting a partner marketplace. Pick one or two promotions based on the customer tier (BLUE, BRONZE, SILVER, GOLD, PLATINUM) and their last product viewed to create a compelling offer. If the browsing category differs from the viewed product category, suggest a new product relevant to the category browsed on the partner site. The tone must be friendly, engaging, and ready to send directly to the customer.'
);