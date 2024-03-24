 SELECT
    *,
    CASE
        WHEN YM = 'v年月' AND SUBSTR(SHAINNO,1,2) <> '37' THEN 100
        ELSE salary
    END AS salary
FROM employees;
