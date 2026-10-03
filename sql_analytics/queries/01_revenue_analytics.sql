-- Overall Revenue
SELECT
    SUM(gross_sales) AS total_gross_sales,
    SUM(net_sales) AS total_net_sales,
    SUM(discount_amount) AS total_discount_amount,
    SUM(quantity) AS total_units_sold,
    COUNT(DISTINCT order_id) AS total_completed_orders,
    SUM(net_sales) / NULLIF(COUNT(DISTINCT order_id), 0) AS average_order_value
FROM fact_sales
WHERE order_status != 'cancelled';
