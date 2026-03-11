CREATE MODEL CART_ABANDONMENT_NUDGE
INPUT (prompt STRING)
OUTPUT (nudge_message STRING)
WITH (
  'provider'            = 'bedrock',
  'bedrock.connection'  = 'DEMO_RETAIL_BEDROCK',
  'task'                = 'text_generation',
  'bedrock.params.max_tokens' = '2048',
  'bedrock.system_prompt' = 'Generate a brief promotional message to recover an abandoned shopping cart. Include an urgent offer with a discount varying from 2% to 8% (pick random) and you must say it is valid from the next 1 to 3 hours (pick random). Be friendly and specific as this offer is to be sent as is to the customer. Maximum 200 characters.'
);