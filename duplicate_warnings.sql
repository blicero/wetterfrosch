-- Time-stamp: <2024-02-07 19:02:36 krylon>

WITH ranked AS (
	SELECT
		w.id,
		w.key,
		row_number() OVER win AS num
	FROM warning w
	WINDOW win AS (PARTITION BY w.key ORDER BY w.key)
)

SELECT * FROM ranked
WHERE num > 0;
-- DELETE FROM warning WHERE id IN (SELECT id FROM ranked WHERE num > 1);

-- COMMIT;
