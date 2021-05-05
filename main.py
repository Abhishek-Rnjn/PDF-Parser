from extract_tables import  return_metadata
from get_tagged_data import get_tagged_data
from remove_table_contents import remove_table_contents
from create_hierarchy import generate_hierarchy
from split_into_topics import topic_split


def get_results(pdf_path):
    pdf_result = get_tagged_data(pdf_path)
    metadata = return_metadata(pdf_path)
    if metadata:
        refined_data = remove_table_contents(pdf_result, metadata)
    else:
        refined_data = pdf_result
    final_result = generate_hierarchy(refined_data, metadata)
    topic_wise_pdf = topic_split(final_result)

    return final_result, topic_wise_pdf
