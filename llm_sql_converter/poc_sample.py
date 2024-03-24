# from langchain.llms import OpenAI
from langchain_community.llms import OpenAI
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from pyspark.sql import SparkSession
import yaml
import sys

spark = SparkSession.builder.getOrCreate()

def predict(input_sql: str, rule: str, rule_example: str) -> str:
    prompt = PromptTemplate(
        input_variables=["input", "output"],
        template="input: {input}\output: {output}",
    )
    few_shot_prompt = FewShotPromptTemplate(
        examples=rule_example,
        example_prompt=prompt,
        prefix=rule,
        suffix="input：{input_sql}\output:",
        input_variables=["input_sql"],
    )
    # TODO: support multiple models
    llm = OpenAI(model="gpt-3.5-turbo-instruct",temperature=0)
    formated_prompt = few_shot_prompt.format(
        input_sql=input_sql
    )
    result = llm.predict(formated_prompt)
    return result

def validate_spark_sql(sql_query: str) -> (str, bool):
    try:
        # ref https://takemikami.com/2021/06/23/pysparkSparkSQL.html
        spark._jsparkSession.sessionState().sqlParser().parsePlan(sql_query)
        return sql_query, True
    except Exception as e:
        new_prompt = f'Spark SQL parse error: {e}.Please fix.'
        print('validation failed new prompt is created:', new_prompt)
        return new_prompt, False
    
def convert_spark_sql(input_sql: str, rule: str=None, rule_sample: str=None) -> str:
    retry = 3
    for i in range(retry):
        sql = predict(input_sql, rule, rule_sample)
        input_sql, valid = validate_spark_sql(sql)
        if valid:
            print(f'Spark SQL Syntax is valid: {input_sql}')
            return input_sql
    raise Exception(f'Failed to convert SQL to Spark SQL: {input_sql}')

def main(file_name) -> str:
    input_path = f'./input/{file_name}'
    with open('./config/rule.yaml', 'r') as file:
        rules = yaml.safe_load(file)

    rule_basic = rules['rules']['rule_basic']
    rule_basic_example  = rules['rules']['rule_basic_example']
    with open(input_path, 'r') as file:
        input_sql = file.read()
    print("input:", input_sql) 
    result = convert_spark_sql(input_sql,rule_basic,rule_basic_example)

    if 'UPDATE' in result:
        rule_update = rules['rules']['rule_update']
        rule_update_example = rules['rules']['rule_update_example']
        result = convert_spark_sql(input_sql, rule_update, rule_update_example)

    if 'INSERT' in result:
        rule_update = rules['rules']['rule_insert']
        rule_update_example = rules['rules']['rule_insert_example']
        result = convert_spark_sql(input_sql, rule_update, rule_update_example)

    output_path = f'./output/{file_name}'
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(result)

if __name__ == "__main__":
    file_name = sys.argv[1]
    main(file_name)
