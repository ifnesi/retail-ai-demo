CREATE TABLE RETAIL_DEMO_CART_RECOVERY_MESSAGES AS
SELECT
  a.username,
  a.customer_tier,
  a.cart_value,
  a.items_count,
  a.event_id,
  CAST(FROM_UNIXTIME(a.`timestamp` / 1000) AS TIMESTAMP) as abandonment_time,
  p.llm_output
FROM RETAIL_DEMO_ABANDON_CART a,
LATERAL TABLE(
  ML_PREDICT(
    'CART_ABANDONMENT_NUDGE',
    CONCAT(
      'Customer ', a.username,
      ' (', a.customer_tier, ' tier)',
      ' abandoned $', CAST(a.cart_value AS STRING),
      ' cart with ', CAST(a.items_count AS STRING), ' items.'
    )
  )
) AS p(llm_output)
WHERE a.cart_value > 20;