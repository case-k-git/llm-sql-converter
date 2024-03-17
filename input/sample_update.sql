BEGIN
    UPDATE employees
    SET
        salary = salary * 1.05,
        last_update = SYSDATE
    WHERE employee_id = 1234;
    COMMIT;
END;
