prompt_template = """
Objective:
You are a privacy policy data collection and sharing statement extractor. 

You will be given sentences from privacy policy and your goal is to identify sentences related to data collection and/or sharing. 


Some example data collection and sharing sentences:
{collection_statement_examples}

Create an output represented in JSON containing the following:
{output_format}

You MUST STRICTLY follow the above provided output example. Only answer with the specified JSON format, no other text.
"""

output_format = '''
{
	"collection_sentence": true or false,
	"sharing_sentence": true or false
}
'''