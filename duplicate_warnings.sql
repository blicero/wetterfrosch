-- Time-stamp: <2024-02-09 17:37:17 krylon>

WITH ranked AS (
	SELECT
		w.id,
		w.key,
		row_number() OVER win AS num
	FROM warning w
	WINDOW win AS (PARTITION BY w.key ORDER BY w.key)
)

SELECT * FROM ranked
WHERE num > 1;
-- DELETE FROM warning WHERE id IN (SELECT id FROM ranked WHERE num > 1);

-- COMMIT;
