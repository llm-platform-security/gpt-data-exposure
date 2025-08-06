import os 

import utilities

import html2text

import multiprocessing

import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

from langchain_openai import ChatOpenAI

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from langchain.prompts import PromptTemplate


from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

from typing import List

import json


os.environ['OPENAI_API_KEY'] = ''


# path to all the privacy policy files
pp_dir = './name_domain_privacy_policies/'
# path to the output file
sentence_result_path = "./sentences/"
# path to the data entities
data_entities_path = "./pp_action_data_entities.json"
# path to storing the error files
error_path = "./error_files/"
# path to the final result file
final_result_path = "./final_results/"


temp_pp_files = os.listdir(pp_dir)

pp_files = [f for f in temp_pp_files if os.path.isfile(os.path.join(pp_dir, f))]

with open(data_entities_path) as f:
    pp_action_data_entities = json.load(f)


class SentenceType(BaseModel):
    collection_sentence: bool = Field(description="Assign true or false depending on whether the sentence is related to data collection")
    sharing_sentence: bool = Field(description="Assign true or false depending on whether the sentence is related to data collection")

        
class SentenceExtracterLLMChain:
    def __init__(self):
        self.chat_llm = ChatOpenAI(model='gpt-4o', temperature=0.0, model_kwargs={"seed": 0})

        # Load prompt template from file
        prompt_file_path = '../prompts/identifying_data_collection-related_sentences_prompt.py'
        prompt_vars = {}
        with open(prompt_file_path, 'r') as f:
            exec(f.read(), prompt_vars)
        system_template_message = prompt_vars.get('prompt_template', '')
        output_format = prompt_vars.get('output_format', '')

        # Extract example collection and sharing statements from original inline prompt
        collection_sharing_examples = '''
Collection statement: "While using Our Service, We may ask You to provide Us with certain personally identifiable information that can be used to contact or identify You. Personally identifiable information may include, but is not limited to..."
Collection statement: "Gapier does not actively collect and store any personal data from users."
Collection statement: "Our website is hosted on Squarespace, which collects personal data when you visit our site. This includes information about your browser, network, and device, web pages you visited before coming to our website, and your IP address."
Collection statement: "We collect personal data to power our site analytics, including information about your browser, network, and device, web pages you visited prior to coming to our site, and your IP address"
Collection statement: "If our website includes third-party integrations like Google Maps, OpenAI's API's generative AI services or Microsoft Geospatial datasets, these services may collect information about your interaction with them."

Sharing statement: "In addition, from time to time, we may analyze the general behavior and characteristics of users of our Services and share aggregated informationlike general user statistics with third parties..."
Sharing statement: "Sometimes this data can be shared with partners who help Us deliver ads to You on Website not controlled by Us."
Sharing statement: "We do not collect, store, or share any personal data unless it's critical to the operation of our service. Any data collected is used solely for providing and improving the service, and it is not shared with any third parties except as necessary to provide the service."
Sharing statement: "We only share information with your consent, to comply with laws, to provide you with services, to protect your rights, or to fulfill business obligations"
Sharing statement: "We may share Your information with Our business partners to offer You certain products, services or promotions"
'''


        template_message = [SystemMessagePromptTemplate(prompt=PromptTemplate( \
            input_variables=['collection_statement_examples', 'output_format'], template=system_template_message)),\
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['privacy_policy'], template='Here is the privacy policy sentence: {privacy_policy}'))]

        self.output_parser = JsonOutputParser(pydantic_object=SentenceType)

        self.template_llm = ChatPromptTemplate(
            input_variables=['output_format', 'collection_statement_examples', 'privacy_policy'], 
            messages= template_message,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )

        self.template_llm = self.template_llm.partial(output_format=output_format, collection_statement_examples=collection_sharing_examples)

        self.llm_chain = self.template_llm | self.chat_llm | self.output_parser

    def query_resolution(self, query): 
        result = self.llm_chain.invoke({"privacy_policy": query})  
        return result


def get_pp_sentences(file):

    llm_chain = SentenceExtracterLLMChain()
    try:
        overall_result = {}
        overall_result['collection'] = []
        overall_result['sharing'] = []
        
        # Read the file and convert html to text
        with open(os.path.join(pp_dir, file)) as f:
            pp_path = os.path.join(pp_dir, file)
            pp_text_html = utilities.read_full_file(pp_path)
            pp_text = html2text.html2text(pp_text_html)

        sentence_tokens = sent_tokenize(pp_text)
        
        for sentence in sentence_tokens:
            result = llm_chain.query_resolution(sentence)
            
            if result['collection_sentence']:
                overall_result['collection'].append(sentence)
                
            if result['sharing_sentence']:
                overall_result['sharing'].append(sentence)
            
        overall_result['pp_length'] = len(pp_text)
            
        with open(sentence_result_path + file[:-3] + 'json', 'w') as f:
            json.dump(overall_result, f, indent=4)
    
        return True
    
    except Exception as e:
        print(e)
        return file


class LabelType(BaseModel):
    number: int = Field(description="The number of the sentence in the privacy policy sentence list")
    label: str = Field(description="Label of the data type disclosure, i.e., CLEAR, VAGUE, OMITTED, AMBIGUOUS, INCORRECT")

class LabelTypeList(BaseModel):
    items: List[LabelType] = Field(description="List of LabelType objects")

# Examine whether privacy policy sentences and data entities are matching
class PolicyCheckerLLMChain:
    def __init__(self):
        self.chat_llm = ChatOpenAI(model='gpt-4o', temperature=0.0, model_kwargs={"seed": 0})

        # Load prompt template from file
        prompt_file_path = '../prompts/assigning_data_collection_consistency_prompt.py'
        prompt_vars = {}
        with open(prompt_file_path, 'r') as f:
            exec(f.read(), prompt_vars)
        system_template_message = prompt_vars.get('system_template_message', '')
        output_format = prompt_vars.get('output_format', '')

        # Extract example labels from original inline prompt
        examples = '''
Data_type_description: "The date of the poster is specified by the user, if not specified, it is an empty string."
Relevant_privacy_policy_text: "...Usage Data may include information such as Your Device's Internet Protocol address (e.g. IP address), browser type, browser version, the pages of our Service that You visit, the time and date of Your visit, the time spent on those pages, unique device identifiers and other diagnostic data..."
Label: CLEAR

Data_type_description: "End time of the query as unix timestamp. If only count is given, defaults to now."
Relevant_privacy_policy_text: "For example, we collect information ..., and a timestamp for the request."
Label: CLEAR 

Data_type_description: "City"
Relevant_privacy_policy_text: "When You access the Service by or through a mobile device, We may collect certain information automatically, including, but not limited to, the type of mobile device You use, Your mobile device unique ID, the IP address of Your mobile device, Your mobile operating system, the type of mobile Internet browser You use, unique device identifiers and other diagnostic data..."
Label: VAGUE

Data_type_description: "Script to be produced"
Relevant_privacy_policy_text: "User Data that includes data about how you use our website and any online\nservices together with any data that you post for publication on our website\nor through other online services"
Label: VAGUE

Data_type_description: "The titles of the all the gift ideas"
Relevant_privacy_policy_text: "USAGE DATA is data collected automatically either generated by the use of\nService or from Service infrastructure itself (for example, the duration of a\npage visit)"
Label: VAGUE

Data_type_description: "Your Gapier login email."
Relevant_privacy_policy_text: "Gapier does not actively collect and store any personal data from users...We use Your Personal data to provide and improve the Service."
Label: AMBIGUOUS

Data_type_description: "Your Gapier login email."
Relevant_privacy_policy_text: "We do not collect our customer's personal information or share it with unaffiliated third parties ...""
Label: INCORRECT

Data_type_description: "Your WordAi login email."
Relevant_privacy_policy_text: "We only collect user name and mailing address"
Label: OMITTED
'''


        template_message = [SystemMessagePromptTemplate(prompt=PromptTemplate( \
            input_variables=['examples', 'output_format'], template=system_template_message)),\
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['privacy_policy', 'data_entity'], template='Here is the privacy policy sentence list: {privacy_policy}\n\nHere is the data entity description: {data_entity}'))]

        self.output_parser = JsonOutputParser(pydantic_object=LabelTypeList)

        self.template_llm = ChatPromptTemplate(
            input_variables=['output_format', 'examples', 'privacy_policy', 'data_entity'], 
            messages= template_message,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )

        self.template_llm = self.template_llm.partial(output_format=output_format, examples=examples)

        self.llm_chain = self.template_llm | self.chat_llm | self.output_parser

    def query_resolution(self, privacy_policy, data_entity): 
        result = self.llm_chain.invoke({"privacy_policy": privacy_policy, 'data_entity': data_entity})  
        return result



def number_list_items_as_string_and_dict(items):
    numbered_items = [f"{index}. {item}" for index, item in enumerate(items, start=1)]
    numbered_string = '\n'.join(numbered_items)
    numbered_dict = {index: item for index, item in enumerate(items, start=1)}
    return numbered_string, numbered_dict

def pp_sentence_data_check(file):

    try:
        domain = file[:-4]
        overall_result = []
        llm_chain = PolicyCheckerLLMChain()

        with open(os.path.join(sentence_result_path, domain+".json")) as f:
            sentences = json.load(f)
        
        collection_sentences, collection_num_dict = number_list_items_as_string_and_dict(sentences['collection'])

        for data_entity in pp_action_data_entities[domain]:
            data_entity_results = data_entity
            collection_temp_results = llm_chain.query_resolution(collection_sentences, data_entity)

            # update the collection_temp_results by including the sentences
            for item in collection_temp_results:
                item['sentence'] = collection_num_dict.get(item['number'], "None")

            data_entity_results['collection'] = collection_temp_results

            overall_result.append(data_entity_results) 
        
        result_path = os.path.join(final_result_path, domain+".json")
        with open(result_path, 'w') as f:
            json.dump(overall_result, f, indent=4)

        return True
    
    except Exception as e:
        print(e)
        return file

def pp_pipeline_action(file):
    first_flag = get_pp_sentences(file)
    if first_flag != True:
        with open(error_path + "sentence_error.txt", "a") as f:
            f.write(first_flag + "\n")
    second_flag = pp_sentence_data_check(file)
    if second_flag != True:
        with open(error_path + "final_error.txt", "a") as f:
            f.write(second_flag + "\n")


def run_concurrent(pp_files, workers=8):
    with multiprocessing.Pool(workers) as pool:
        return list(pool.imap(pp_pipeline_action, pp_files, chunksize=1))

def main():
    temp_pp_files = os.listdir(pp_dir)
    pp_files = [f for f in temp_pp_files if os.path.isfile(os.path.join(pp_dir, f))]

    # create the error files if not exist
    if not os.path.exists(error_path):
        os.makedirs(error_path)
    
    if not os.path.exists(final_result_path):
        os.makedirs(final_result_path)

    results = run_concurrent(pp_files) 
    return results

    # # Read the file list from the error files
    # with open(error_path + "final_error.txt") as f:
    #     temp_pp_files = f.readlines()
    #     temp_pp_files = [f.strip() for f in temp_pp_files]
    # pp_files = [f for f in temp_pp_files if os.path.isfile(os.path.join(pp_dir, f))]
    # results = run_concurrent(pp_files) 

if __name__ == '__main__':
    main()
