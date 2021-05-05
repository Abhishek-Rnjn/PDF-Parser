# PDF-Parser
## _Description_

This project was created to enable parsing PDF documents to obtain hierarchial relations among various componnents of PDF.

- Parse PDF and obtain text and tables.
- Find headers for paras, headers for tables, page_numbers

What makes this project unique/valuable?

- While there exist many PDF parsers out there to extract table and text information we couldn't find a proper one which will associate header with each components of a PDF such as para, table. Many projects rely on finding structured information from documents, not just a dump of all the text.
- The easy to understand JSON output structure helps users use this for further tasks easily.

## Instructions for a new setup

- Clone the repository.
- Enter this branch
- Create a virtual environment, preferably outside this cloned folder.
- Upgrade pip if required.
- sudo apt-get install ghostscript
- Install the dependencies using the requirements.txt
- Run the get_results function in main.py by passing the pdf_file_path

```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install wheel
cd PDF-Parser
pip install -r requirements.txt
python main.py
```


