// Auto-generated from Flink SQL CONCAT templates
// DO NOT EDIT - Run terraform/scripts/extract_prompts.py to regenerate
//
// These functions are dynamically generated from:
// - RETAIL_DEMO_CART_RECOVERY_MESSAGES.sql
// - RETAIL_DEMO_STORE_VISIT_CONTEXT.sql
// - RETAIL_DEMO_PARTNER_BROWSE_ADS.sql

export const buildCartRecoveryContext = (data) => {
  return `Customer ${data.username || 'N/A'} (${data.customer_tier || 'N/A'} tier) abandoned $${data.cart_value?.toFixed(2) || '0.00'} cart with ${data.items_count || 0} items.`;
};

export const buildStoreContext = (data) => {
  const visitTime = data.visit_time ? new Date(data.visit_time).toLocaleString('en-US', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }) : 'N/A';
  return `Customer ${data.username || 'N/A'} (${data.customer_tier || 'N/A'} tier) entered ${data.store_name || 'N/A'} at ${visitTime}. Last product viewed: ${data.last_product_viewed || 'None'} (${data.last_product_category || 'N/A'} - $${data.last_product_price?.toFixed(2) || '0'}). Store promotions: ${data.promotions || 'N/A'}`;
};

export const buildPartnerAdContext = (data) => {
  return `Customer ${data.username || 'N/A'} (${data.customer_tier || 'N/A'} tier) browsing category ${data.category || 'N/A'} on ${data.partner_name || 'N/A'}. Last product viewed: ${data.last_product_viewed || 'None'} (category: ${data.last_product_category || 'N/A'} - $${data.last_product_price?.toFixed(2) || '0'}). Partner promotions: ${data.promotions || 'N/A'}`;
};

