# llm-sql-converter(Beta)

This is a tool that uses [LangChain](https://github.com/langchain-ai/langchain) to convert PL/SQL into SparkSQL SELECT statements. The query is converted in the following steps:

1. Convert PL/SQL to Spark SQL statements based on the specified rules and example(few_shot_prompt).
2. Check the syntax of the converted Spark SQL. If there are any errors, new prompt will be created using SQL and errors and passed to the LLM to fix converted SQL.Currently, it retries up to 3 times until successful.
3. Retrieve the converted results.

## Set Up

### API key

```
export OPENAI_API_KEY=<API_KEY>
```

### poetry

```
poetry update
```

## Sample Usage

In PL/SQL, operations can be transformed according to the method you desire, prompted by specific instructions. For example, it instructs to convert an UPDATE operation into a SELECT using a CASE statement.

input rule
`config/rule.yaml`

rule

```yaml
rule_update: "
  ### Instructions ###
  Convert the Databricks SQL following the rules below.
  1.Convert UPDATE statements into SELECT statements using CASE WHNE CONDITION.
  "
```

rule exmaple of input and output results

```yaml
rule_update_example:
  - input: |
      UPDATE employees
      SET salary = CASE
                      WHEN department_id = 1 THEN salary * 1.10
                      ELSE salary
                  END;
    output: |
      SELECT
          *,
          CASE
              WHEN department_id = 1 THEN salary * 1.10
              ELSE salary
          END AS salary
      FROM employees;
```

### 1. PL/SQL to Spark SQL ( Update to Select )

command to execute

```

poetry run python llm_sql_converter/main.py sample_update_2.sql

```

output logs

```

input: BEGIN
    UPDATE  employees
        SET
            employees.salary = 100
        WHERE employees.YM = v年月
        AND SUBSTR(employees.SHAINNO,1,2) <>  '37';
    COMMIT;
END;

Spark SQL Syntax is valid:  SELECT
    *,
    CASE
        WHEN YM = 'v年月' AND SUBSTR(SHAINNO,1,2) <> '37' THEN 100
        ELSE salary
    END AS salary
FROM employees;
```

### 2. PL/SQL to Spark SQL ( Insert to Select )

command to execute

```

poetry run python llm_sql_converter/main.py sample_insert.sql

```

output logs

```

input: INSERT INTO employees (employee_id, last_name, email, hire_date, job_id)
VALUES (207, 'Smith', 'smith@example.com', '17-JUL-2021', 'IT_PROG');

Spark SQL syntax and convert rule validation start ...
Spark SQL Syntax is valid:  SELECT
    207 AS employee_id,
    'Smith' AS last_name,
    'smith@example.com' AS email,
    '17-JUL-2021' AS hire_date,
    'IT_PROG' AS job_id
FROM employees;

```

## Contributing

Contribution is welcome from anyone. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the [Contributor Covenant](http://contributor-covenant.org/) code of conduct.

## License

llm-sql-converter is available as open source under the terms of the MIT License. For more details, see the [LICENSE](./LICENSE.txt) file.
