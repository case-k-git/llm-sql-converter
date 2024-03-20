# llm-sql-converter(Beta)

This is a tool that uses [LangChain](https://github.com/langchain-ai/langchain) to convert PL/SQL into SparkSQL SELECT statements. The query is converted in the following steps:

1. Read the PL/SQL input, considering samples for conversion (few_shot_prompt).
2. Convert to Spark SQL SELECT statements based on the specified rules.
3. Check the syntax of the converted Spark SQL. If there are any errors, new prompt will be created using SQL and errors and passed to the LLM to fix converted SQL.Currently, it retries up to 3 times until successful.
4. Retrieve the converted results.

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
rule: "
  ### Instructions ###
  Convert the entered PL/SQL into Spark SQL following the rules below.
  1.Convert UPDATE statements into SELECT statements using CASE WHNE CONDITION.
  2.Convert INSERT statements into SELECT statements that produce the result of the INSERT operation.
  "
```

rule exmaple of input and output results

```yaml
rule_example:
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

poetry run python llm_sql_converter/poc_sample.py sample_update.sql

```

output logs

```

input: BEGIN
    UPDATE employees
    SET
        salary = salary * 1.05,
        last_update = SYSDATE
    WHERE employee_id = 1234;
    COMMIT;
END;

Spark SQL syntax and convert rule validation start ...
Spark SQL Syntax is valid:  SELECT
    *,
    CASE
        WHEN employee_id = 1234 THEN salary * 1.05
        ELSE salary
    END AS salary,
    SYSDATE AS last_update
FROM employees;

```

### 2. PL/SQL to Spark SQL ( Insert to Select )

command to execute

```

poetry run python llm_sql_converter/poc_sample.py sample_insert.sql

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

lm-sql-converter is available as open source under the terms of the MIT License. For more details, see the [LICENSE](./LICENSE.txt) file.
