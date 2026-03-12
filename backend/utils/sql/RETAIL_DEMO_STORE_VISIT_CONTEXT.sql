CREATE TABLE RETAIL_DEMO_STORE_VISIT_CONTEXT AS
SELECT
  s.username,
  s.customer_tier,
  s.store_id,
  s.store_name,
  s.location,
  CAST(FROM_UNIXTIME(s.`timestamp` / 1000) AS TIMESTAMP) as visit_time,
  s.last_product_viewed,
  s.last_product_category,
  s.last_product_price,
  s.promotions,
  p.llm_output
FROM RETAIL_DEMO_STORE_ENTRY s,
LATERAL TABLE(
  ML_PREDICT(
    'STORE_PERSONALIZATION',
    CONCAT(
      'Customer ', s.username,
      ' (', s.customer_tier, ' tier)',
      ' entered ', s.store_name,
      ' at ', DATE_FORMAT(CAST(FROM_UNIXTIME(s.`timestamp` / 1000) AS TIMESTAMP), 'E dd/MMM/yyyy HH:mm'),
      '. Last product viewed: ',
      COALESCE(s.last_product_viewed, 'None'),
      ' (', COALESCE(s.last_product_category, 'N/A'),
      ' - $', COALESCE(CAST(s.last_product_price AS STRING), '0'),
      '). Store promotions: ', s.promotions
    )
  )
) AS p(llm_output);