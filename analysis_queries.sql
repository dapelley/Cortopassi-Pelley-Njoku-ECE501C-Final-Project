-- analysis_queries.sql (historical_data adaptation)

-- 1. Average subtotal per restaurant (order value)
SELECT restaurant_id, AVG(subtotal) AS avg_order_value, COUNT(*) AS total_orders
FROM orders
GROUP BY restaurant_id
ORDER BY avg_order_value DESC
LIMIT 20;

-- 2. Fastest restaurants by average delivery time (minutes)
SELECT restaurant_id,
       AVG((julianday(delivery_time) - julianday(order_datetime)) * 24 * 60) AS avg_delivery_min
FROM orders
WHERE delivery_time IS NOT NULL
GROUP BY restaurant_id
HAVING COUNT(*) > 50
ORDER BY avg_delivery_min ASC
LIMIT 20;

-- 3. Average dasher load per market
SELECT location, AVG(total_busy_dashers) AS avg_busy, AVG(total_onshift_dashers) AS avg_onshift
FROM restaurants r
JOIN orders o ON r.restaurant_id = o.restaurant_id
GROUP BY location
ORDER BY avg_busy DESC;

-- 4. Correlation-style insight: high dashers vs. low delivery time
SELECT restaurant_id,
       AVG(total_onshift_dashers) AS avg_dashers,
       AVG((julianday(delivery_time) - julianday(order_datetime)) * 24 * 60) AS avg_delivery_time
FROM orders
WHERE delivery_time IS NOT NULL
GROUP BY restaurant_id
ORDER BY avg_dashers DESC
LIMIT 20;
