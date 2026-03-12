CREATE TABLE RETAIL_DEMO_CART_RECOVERY_MESSAGES AS
SELECT
  a.username,
  a.cart_value,
  a.items_count,
  a.event_id,
  CAST(FROM_UNIXTIME(a.`timestamp` / 1000) AS TIMESTAMP) as abandonment_time,
  p.nudge_message
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
) AS p(nudge_message)
WHERE a.cart_value > 20;