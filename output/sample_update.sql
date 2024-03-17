 SELECT
    *,
    CASE
        WHEN employee_id = 1234 THEN salary * 1.05
        ELSE salary
    END AS salary,
    SYSDATE AS last_update
FROM employees;