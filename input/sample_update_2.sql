BEGIN
    UPDATE  employees
        SET
            employees.salary = 100
        WHERE employees.YM = v年月
        AND SUBSTR(employees.SHAINNO,1,2) <>  '37';
    COMMIT;
END;
