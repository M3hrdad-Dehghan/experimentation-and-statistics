
/* ===================================================================
SANITY CHECK 
===================================================================*/ 
-- Sample Ratio Mismatch (SRM)

WITH counts AS (
    SELECT
        variant,
        COUNT(*) AS users
    FROM ab.assignments
    GROUP BY variant
),
total AS (
    SELECT SUM(users) AS total_users FROM counts
)
SELECT
    c.variant,
    c.users,
    CAST(1.0 * c.users / t.total_users AS DECIMAL(5,4)) AS pct_users
FROM counts c
CROSS JOIN total t;

-- Temporal Balance Between Variants
WITH daily AS (
    SELECT
        CAST(assignment_ts AS DATE) AS assignment_date,
        variant,
        COUNT(*) AS users
    FROM ab.assignments
    GROUP BY CAST(assignment_ts AS DATE), variant
),
daily_total AS (
    SELECT
        assignment_date,
        SUM(users) AS total_users
    FROM daily
    GROUP BY assignment_date
)
SELECT
    d.assignment_date,
    d.variant,
    d.users,
    CAST(1.0 * d.users / t.total_users AS DECIMAL(5,4)) AS pct_users
FROM daily d
JOIN daily_total t
    ON d.assignment_date = t.assignment_date
ORDER BY d.assignment_date, d.variant;

-- Variant Exclusivity Check
SELECT
    user_id,
    COUNT(DISTINCT variant) AS variant_count
FROM ab.assignments
GROUP BY user_id
HAVING COUNT(DISTINCT variant) > 1;

-- Are there any events that occurred before variant assignment
SELECT TOP 100
    e.user_id,
    a.variant,
    a.assignment_ts,
    e.event_ts,
    e.event_name
FROM ab.events e
JOIN ab.assignments a
    ON a.user_id = e.user_id
WHERE e.event_ts < a.assignment_ts
ORDER BY e.event_ts;

-- Did any user upgrade to Premium before exposure to the experiment
SELECT TOP 100
    s.user_id,
    a.variant,
    a.assignment_ts,
    s.activated_ts
FROM ab.subscriptions s
JOIN ab.assignments a
    ON a.user_id = s.user_id
WHERE s.activated_ts IS NOT NULL
  AND s.activated_ts < a.assignment_ts
ORDER BY s.activated_ts;

-- Do all assigned users have at least one pricing_page_view event
SELECT COUNT(*) AS users_missing_pricing_view
FROM ab.assignments a
LEFT JOIN ab.events e
  ON e.user_id = a.user_id
 AND e.event_name = 'pricing_page_view'
WHERE e.user_id IS NULL;

-- Are there any users who clicked the CTA without first viewing the Pricing Page
SELECT COUNT(*) AS clicks_without_view
FROM ab.events c
WHERE c.event_name = 'click_upgrade_cta'
  AND NOT EXISTS (
      SELECT 1
      FROM ab.events v
      WHERE v.user_id = c.user_id
        AND v.event_name = 'pricing_page_view'
        AND v.event_ts <= c.event_ts
  );

  -- Are there any users who started the checkout process without clicking the CTA
SELECT COUNT(*) AS checkouts_without_click
FROM ab.events s
WHERE s.event_name = 'start_checkout'
  AND NOT EXISTS (
      SELECT 1
      FROM ab.events c
      WHERE c.user_id = s.user_id
        AND c.event_name = 'click_upgrade_cta'
        AND c.event_ts <= s.event_ts
  );

  -- For each user, does the event sequence follow the expected order: pricing_page_view → click_upgrade_cta → start_checkout?
WITH steps AS (
  SELECT
    user_id,
    MIN(CASE WHEN event_name='pricing_page_view' THEN event_ts END) AS view_ts,
    MIN(CASE WHEN event_name='click_upgrade_cta' THEN event_ts END) AS click_ts,
    MIN(CASE WHEN event_name='start_checkout' THEN event_ts END) AS checkout_ts
  FROM ab.events
  GROUP BY user_id
)
SELECT TOP 100 *
FROM steps
WHERE
  (click_ts IS NOT NULL AND view_ts IS NOT NULL AND click_ts < view_ts)
  OR
  (checkout_ts IS NOT NULL AND click_ts IS NOT NULL AND checkout_ts < click_ts)
ORDER BY user_id;

-- Is any user_id assigned more than once in the experiment assignment table
SELECT
    user_id,
    COUNT(*) AS cnt
FROM ab.assignments
GROUP BY user_id
HAVING COUNT(*) > 1;

-- Are there any events with missing critical fields such as event_ts or event_name
SELECT
    COUNT(*) AS invalid_events
FROM ab.events
WHERE event_ts IS NULL
   OR event_name IS NULL
   OR user_id IS NULL;

-- Are there any events that do not belong to a valid user
SELECT COUNT(*) AS orphan_events
FROM ab.events e
LEFT JOIN ab.assignments a
  ON a.user_id = e.user_id
WHERE a.user_id IS NULL;

-- Are there any Premium activation records (activated_ts) that do not belong to a valid user?
SELECT COUNT(*) AS orphan_subscriptions
FROM ab.subscriptions s
LEFT JOIN ab.assignments a
  ON a.user_id = s.user_id
WHERE a.user_id IS NULL;

-- Are there any users who have a cancellation or refund recorded without ever having a Premium activation?
SELECT COUNT(*) AS inconsistent_subscriptions
FROM ab.subscriptions
WHERE activated_ts IS NULL
  AND (canceled_ts IS NOT NULL OR refunded_flag = 1);
