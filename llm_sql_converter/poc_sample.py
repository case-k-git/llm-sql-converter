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
    print("input:", input_sql) 
    return result

def validate_spark_sql(sql_query: str) -> (str, bool):
    print('Spark SQL syntax and convert rule validation start ...')
    if 'UPDATE' in sql_query:
        new_prompt = f'UPDATE is not supported: {sql_query}. Please convert into SELECT statement.'
        print('validation failed new prompt is created:', new_prompt)
        return new_prompt, False
    if 'INSERT' in sql_query:
        new_prompt = f'INSERT is not supported: {sql_query}. Please convert into SELECT statement.'
        print('validation failed new prompt is created:', new_prompt)
        return new_prompt, False
    try:
        # ref https://takemikami.com/2021/06/23/pysparkSparkSQL.html
        spark._jsparkSession.sessionState().sqlParser().parsePlan(sql_query)
        return sql_query, True
    except Exception as e:
        new_prompt = f'Query Parse Error: {e}.Input SQL: {sql_query}.Please fix Input SQL from Query Parse Error.'
        print('validation failed new prompt is created:', new_prompt)
        return new_prompt, False
    
def main(input_sql: str,rule, rule_sample) -> str:
    retry = 3
    for i in range(retry):
        sql = predict(input_sql,rule, rule_sample)
        input_sql, valid = validate_spark_sql(sql)
        if valid:
            print(f'Spark SQL Syntax is valid: {input_sql}')
            return input_sql
    raise Exception(f'Failed to convert SQL to Spark SQL: {input_sql}')

file_name = sys.argv[1]
input_path = f'./input/{file_name}'
with open('./config/rule.yaml', 'r') as file:
    rules = yaml.safe_load(file)
rule = rules['rules']['rule']
rule_example = rules['rules']['rule_example']
with open(input_path, 'r') as file:
    input_sql = file.read()
result = main(input_sql,rule,rule_example)
output_path = f'./output/{file_name}'
with open(output_path, 'w', encoding='utf-8') as file:
    file.write(result)
