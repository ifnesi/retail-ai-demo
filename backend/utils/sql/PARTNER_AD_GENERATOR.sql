CREATE MODEL PARTNER_AD_GENERATOR
INPUT (prompt STRING)
OUTPUT (ad_copy STRING)
WITH (
  'provider'            = 'bedrock',
  'bedrock.connection'  = 'DEMO_RETAIL_BEDROCK',
  'task'                = 'text_generation',
  'bedrock.params.max_tokens' = '2048',
  'bedrock.system_prompt' = 'Generate a personalized advertisement for a customer visiting a partner marketplace. Pick one or two of the promotions based on the customer tier (BLUE, BRONZE, SILVER, GOLD, PLATINUM) and their last product viewed to create a compelling ad. If the browsing category does not match with the product category viewed suggest a new product based on the catehory visited on the partner. Be friendly and specific as this ad is to be sent as is to the customer. Maximum 200 characters.'
);