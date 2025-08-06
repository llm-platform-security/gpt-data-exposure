import json
import os
import pandas as pd

from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

os.environ['OPENAI_API_KEY'] = ''

existing_taxonomy_path = './taxonomy.csv'
extracted_data_types_path = './extracted_data_types.json'
result_path = './addressing_non_classifier_results.json'

if not os.path.exists(result_path):
    with open(result_path, 'w') as f:
        json.dump([], f)

class DecisionOutput(BaseModel):
    data_taxonomy: dict = Field(description="Expanded data taxonomy after adding new sub data types")
    decisions: dict = Field(description="Decision for each data entity")

class AddressingNonClassifierLLMChain:
    def __init__(self, existing_taxonomy):
        self.chat_llm = ChatOpenAI(model='gpt-4o', temperature=0.0, model_kwargs={"seed": 0})

        # Load prompt template from file
        prompt_file_path = '../prompts/addressing_non-classifier_data_description_prompt.py'
        prompt_vars = {}
        with open(prompt_file_path, 'r') as f:
            exec(f.read(), prompt_vars)
        prompt_template = prompt_vars.get('prompt_template', '')
        output_format = prompt_vars.get('output_format', '')


        template_message = [SystemMessagePromptTemplate(prompt=PromptTemplate( \
            input_variables=['existing_taxonomy', 'output_format'], template=prompt_template)),\
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}'))]

        self.output_parser = JsonOutputParser(pydantic_object=DecisionOutput)

        self.template_llm = ChatPromptTemplate(
            input_variables=['output_format', 'existing_taxonomy', 'input'], 
            messages=template_message,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )

        self.template_llm = self.template_llm.partial(output_format=output_format, existing_taxonomy=existing_taxonomy)

        self.llm_chain = self.template_llm | self.chat_llm | self.output_parser

    def query_resolution(self, query):
        result = self.llm_chain.invoke({"input": query})
        return result

def main():
    # Load existing taxonomy as string
    taxonomy_df = pd.read_csv(existing_taxonomy_path)
    existing_taxonomy_str = taxonomy_df.to_string(index=False)

    # Load data entities
    with open(extracted_data_types_path, 'r') as f:
        data_entities = json.load(f)

    # Get the data entities with 'Other' type
    data_entities = [entity for entity in data_entities if entity.get('data_type') == 'Other']

    # Initialize LLM chain
    chain = AddressingNonClassifierLLMChain(existing_taxonomy_str)

    # Process each data entity and collect results
    results = []
    for data_entity in data_entities:
        input_str = json.dumps(data_entity)
        result = chain.query_resolution(input_str)
        results.append(result)
        print(result)

    # Save results
    with open(result_path, 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == '__main__':
    main()
