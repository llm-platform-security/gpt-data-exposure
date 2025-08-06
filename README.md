# Data Collection in LLM App Ecosystems

This repository contains the code and data accompanying our IMC ’25 paper, [An In-Depth Investigation of Data Collection in LLM App Ecosystems](https://arxiv.org/abs/2408.13247). These artifacts support GPT metadata crawling, data-collection analysis, and privacy-policy analysis for GPTs, including those with Actions.

## Table of Contents
- [GPT Data Exposure](#openais-gpt-data-exposure-analysis)
  - [Installation](#installation)
  - [Data Categorization](#data-categorization)
    - [Standard Data Categorization](#standard-data-categorization)
    - [Non-Classifier Data Handling](#non-classifier-data-handling)
  - [Privacy Policy Analysis](#privacy-policy-analysis)
  - [GPT Crawlers](#gpt-crawlers)
  - [Contribution and Support](#contribution-and-support)
  - [Research Team](#research-team)
  - [Citation](#citation)

## Installation
To set up the environment, we suggest using Conda. See the [Miniconda installation guide](https://docs.anaconda.com/free/miniconda/miniconda-install/).

```sh
conda create -n langchain python=3.9
conda activate langchain
git clone https://github.com/llm-platform-security/gpt-data-exposure.git
cd gpt-data-exposure
pip install -r requirements.txt
```

## Data Categorization

### Standard Data Categorization
**Setup:**  
Open `data_categorization/data_categorization.py` and insert your OpenAI API key:
```python
os.environ['OPENAI_API_KEY'] = ''  # Add your API key here
```

**Running:**  
```sh
cd data_categorization
python data_categorization.py
```

**Output:**  
- `extracted_data_types.json` in the same directory, containing each entry’s assigned data type.

### Non-Classifier Data Handling
This script processes entries labeled `Other` by the standard categorizer and suggests sub-types.

**Setup:**  
Open `data_categorization/addressing_non_classifier_data_description.py` and insert your OpenAI API key:
```python
os.environ['OPENAI_API_KEY'] = ''  # Add your API key here
```

**Running:**  
```sh
cd data_categorization
python addressing_non_classifier_data_description.py
```

**Output:**  
- `addressing_non_classifier_results.json` in the same directory, containing expanded taxonomy decisions.

## Privacy Policy Analysis

**Setup:**  
Open `privacy_policy_analysis/privacy_policy_analysis.py` and insert your OpenAI API key:
```python
os.environ['OPENAI_API_KEY'] = ''  # Add your API key here
```

**Running:**  
```sh
cd privacy_policy_analysis
python privacy_policy_analysis.py
```

**Output:**  
- Structured JSON results in `final_results/`.  
- Any failures logged to `error_files/`.

## GPT Crawlers

This package provides both individual scraper modules and a metascraper to gather GPT URLs and metadata.

### Configuration
Before running any scraper, adjust credentials and settings in:
```sh
gpt_crawlers/config.py
```
Set values such as `OPENAI_BEARER_TOKEN`, SMTP/email settings, and logfile parameters.

### Running the GPT Scrapers
```sh
cd gpt_crawlers
python metascraper.py
```
To use scrapers defined in `config.json`:
```sh
python metascraper.py --use-json
```

### Output Files
- `fallback_urls.json`: A dump of all collected OpenAI chat URLs.  
- `gizmos_noref.json` / `gizmos_ref.json`: Detailed GPT metadata without/with source references.  
- `replay_file.json`: Map of failed URLs and associated error reasons.  

## Contribution and Support
We welcome contributions via pull requests. For issues or feature requests, open a GitHub issue. Feel free to reach out if you have questions or need guidance.

## Research Team 
[Yuhao Wu](https://yuhao-w.github.io) (Washington University in St. Louis)  
[Evin Jaff](https://evinjaff.github.io/) (Washington University in St. Louis)  
[Ke Yang](https://www.linkedin.com/in/ke-yang-b46432294/) (Washington University in St. Louis)  
[Ning Zhang](https://cybersecurity.seas.wustl.edu/) (Washington University in St. Louis)  
[Umar Iqbal](https://umariqbal.com) (Washington University in St. Louis)  


## Citation
```plaintext
@inproceedings{wu2025llm-data-collection,
  author    = {Yuhao Wu and Evin Jaff and Ke Yang and Ning Zhang and Umar Iqbal},
  title     = {An In-Depth Investigation of Data Collection in {LLM} App Ecosystems},
  booktitle = {Proceedings of the 2025 ACM Internet Measurement Conference (IMC '25)},
  year      = {2025}
}
```
