SELECT
    p.product_id,
    p.product_name,
    SUM(o.quantity) AS total_units,
    COUNT(*) AS total_orders
FROM block3_it_gorod_vozmite_pz_na_stazirovky.products AS p
JOIN block3_it_gorod_vozmite_pz_na_stazirovky.orders AS o
    ON o.product_id = p.product_id
WHERE o.status = 'completed'
GROUP BY p.product_id, p.product_name
ORDER BY total_units DESC, total_orders DESC, p.product_id;