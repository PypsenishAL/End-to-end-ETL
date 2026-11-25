SELECT
    DATE_TRUNC('month', o.ordered_at) AS timing,
    o.currency,
    SUM(o.order_total) AS monthly_revenue
FROM block3_it_gorod_vozmite_pz_na_stazirovky.orders AS o
WHERE o.status = 'completed'
  AND o.ordered_at IS NOT NULL
GROUP BY DATE_TRUNC('month', o.ordered_at), o.currency
ORDER BY timing, o.currency;