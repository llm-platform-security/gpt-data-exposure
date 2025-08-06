prompt_template = '''
Objective:
You are a data taxonomy expert. Your objective is to decide whether the data entities are valuable to create a new sub datatype for it and add it to the existing data taxonomy.
Attention: We want a concise data taxonomy instead of a comprehensive one. This will affect your decision!
The existing data taxonomy is as follows:
{existing_taxonomy}

Here is the format of data entity:
[
    "name : description": "data_entity_name : data_entity_description",
    "amount appears": int, //This is the number of times the data entity appears in the whole dataset.
]

Note: For whether a data entity is valuable, you should consider the following aspects:
1. It should be distinct from the existing sub data types.
2. It should provide additional value to the existing data taxonomy.
3. Bigger amount appears means the data entity is more valuable, as it appears more frequently in the dataset.

For each data entities, choose one action from the following options:
1. ['Covered', 'An existing sub datatype']. If the data entity is covered by an existing sub data type, choose this option and specify the existing sub data type.
2. ['Add', 'New sub datatype']. If the data entity is valuable and should create a new sub datatype for it, choose this option.
3. ['Combine', 'New sub datatype']. If the data entity is valuable but should be combined with other data entity to create a new sub datatype, choose this option and specify new sub data type. You can rewrite the description if necessary.
4. ['Deprecate', '']. If the data entity is not valuable and should be deprecated, choose this option.

After you have a draft of the new data taxonomy and decisions for each data entity, you need to check whether you can improve it by [Deprecate] less valuable new sub datatypes or [Combine] new sub data types to make the data taxonomy more concise. Make sure to update all the decisions accordingly.

Follow the output example below, make sure output all the decisions for each data entity in the same order as the input:
{output_format}

You MUST STRICTLY follow the above provided output example. Only answer with the specified JSON format, no other text.
'''

output_format = '''
{
    "data taxonomy": {...}, // This is the expanded data taxonomy after adding new sub data types. It should be in the same format as the existing data taxonomy.
    "decisions": {
        "0": ["Covered", "sub_data_type_name1"],
        "1": ["Add", "sub_data_type_name2"],
        "2": ["Combine", "sub_data_type_name3"],
        "3": ["Deprecate", ""],
        ...
    } // This is the decision for each data entity.
}
'''