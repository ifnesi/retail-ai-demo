CREATE TABLE RETAIL_DEMO_PARTNER_BROWSE_ADS AS
SELECT
  p.username,
  p.partner_name,
  p.category,
  CAST(FROM_UNIXTIME(p.`timestamp` / 1000) AS TIMESTAMP) as browse_time,
  p.last_product_viewed,
  p.last_product_category,
  p.last_product_price,
  a.ad_copy
FROM RETAIL_DEMO_PARTNER_BROWSE p,
LATERAL TABLE(
  ML_PREDICT(
    'PARTNER_AD_GENERATOR',
    CONCAT(
      'Customer ', p.username,
      ' browsing category ', p.category,
      ' on ', p.partner_name,
      '. Last product viewed: ',
      COALESCE(p.last_product_viewed, 'None'),
      ' (category: ', COALESCE(p.last_product_category, 'N/A'),
      ' - $', COALESCE(CAST(p.last_product_price AS STRING), '0'),
      '). Store promotions: ', p.promotions
    )
  )
) AS a(ad_copy);