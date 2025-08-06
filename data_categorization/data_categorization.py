import json

from langchain_openai import ChatOpenAI

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

import pandas as pd
import os

os.environ['OPENAI_API_KEY'] = ''

# Load the data entries from the JSON file
data_json_path = "./gpt_data_entries.json"
taxonomy_path = './taxonomy.csv'
result_path = './extracted_data_types.json'

if not os.path.exists(result_path):
    with open(result_path, 'w') as f:
        json.dump([], f)

class DataNameType(BaseModel):
    data_name: str = Field(description="name of the data entry")
    data_type: str = Field(description="type of the data entry")

class MyLLMChain:
    def __init__(self, categories):
        self.chat_llm = ChatOpenAI(model='gpt-4o', temperature=0.0, model_kwargs={"seed": 0})

        # Load prompt template from file
        prompt_file_path = '../prompts/data_description_classification_prompt.py'
        prompt_vars = {}
        with open(prompt_file_path, 'r') as f:
            exec(f.read(), prompt_vars)
        system_template_message = prompt_vars.get('system_template_message', '')
        output_format = prompt_vars.get('output_format', '')

        template_message = [SystemMessagePromptTemplate(prompt=PromptTemplate( \
            input_variables=['initial_taxonomy', 'categorization_rules', 'general_examples', 'output_format'], template=system_template_message)),\
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}'))]

        self.output_parser = JsonOutputParser(pydantic_object=DataNameType)

        self.template_llm = ChatPromptTemplate(
            input_variables=['output_format', 'initial_taxonomy', 'categorization_rules', 'general_examples', 'input'], 
            messages= template_message,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )

        self.template_llm = self.template_llm.partial(output_format=output_format, initial_taxonomy=categories, categorization_rules='', general_examples='')

        self.llm_chain = self.template_llm | self.chat_llm | self.output_parser

    def query_resolution(self, query): 
        result = self.llm_chain.invoke({"input": query})
        return result

def main():    
    # Load the categories from the csv file    
    categories_df = pd.read_csv(taxonomy_path)
    categories = categories_df.to_string(index=False)

    # Define LLM chain
    chain = MyLLMChain(categories)

    # Load the data entries from the JSON file 
    with open(data_json_path, 'r') as f:
        data = json.load(f)

    # Process each data entry and write back the result
    temp_list = [] 
    for index, data_item in enumerate(data): 
        if "plugin_id_filenames" in data_item:
            item_wo_id = {k: v for k, v in data_item.items() if k != "plugin_id_filenames"}
        result = chain.query_resolution(json.dumps(item_wo_id))
        print(result)

        new_data_item = data_item.copy()
        new_data_item['data_type'] = result[0]

        temp_list.append(new_data_item)

        if len(temp_list) == 10 or index == len(data) - 1: 
            with open(result_path, 'r') as f:
                updated_data = json.load(f)
            updated_data.extend(temp_list)
            with open(result_path, 'w') as f:
                json.dump(updated_data, f, indent=4)
            temp_list = []

if __name__ == '__main__':
    main()
