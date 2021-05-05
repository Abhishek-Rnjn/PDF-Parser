

def set_new_line(text, seperator='|$'):
    return [t.strip() for t in text.split(seperator)]


def generate_hierarchy(refined_data, metadata):
    hierarchial_result = {'text-blocks': [], 'tables': []}

    cur_header_hierarchy = '0'
    cur_para_order = '0'
    already_seen_table = set()
    last_seen_header = ''
    prev_tag = ''
    last_to_last_tag = ''

    def join_with_prev_para(text):
        if hierarchial_result['text-blocks'][-1]['tag'] == 'para':  # just to be sure
            hierarchial_result['text-blocks'][-1]['text'] += text

    for page_no, page in enumerate(refined_data):
        for data in page:
            tag, text = data.split('>', 1)
            tag = tag[1:]
            if tag == 'p':
                lines = text.split(' |$')
                cur_para = []
                for line in lines:
                    if line.startswith('|$'):  # case of unidentified heading or para
                        if cur_para:  # store ongoing para if any
                            if 's' in prev_tag and last_to_last_tag == 'p':
                                join_with_prev_para(cur_para)
                            else:
                                cur_para_order = str(int(cur_para_order) + 1)
                                node_hierarchy = f'{cur_header_hierarchy}.{cur_para_order}'
                                hierarchial_result['text-blocks'].append(
                                    {"tag": "para", "text": cur_para, "page_number": page_no + 1,
                                     "hierarchy": node_hierarchy})
                            last_to_last_tag = prev_tag
                            prev_tag = 'p'
                            cur_para = []
                        cur_para_order = '0'  # reset it
                        if line.isupper():  # heading in para's clothing
                            node_hierarchy = ''
                            cur_header_hierarchy = node_hierarchy
                            last_seen_header = set_new_line(line)
                            hierarchial_result['text-blocks'].append(
                                {"tag": "h", "text": last_seen_header, "page_number": page_no + 1,
                                 "hierarchy": node_hierarchy})
                        else:  # new para (was stuck with other para(s))
                            cur_para.append(line[2:].strip())  # cur_para already emptied

                    else:  # normal case (are you sure?)
                        if len(line.strip()) < 50 and line.isupper():  # abnormal case of para marked as header
                            node_hierarchy = ''
                            cur_header_hierarchy = node_hierarchy
                            cur_para_order = '0'  # reset it
                            last_seen_header = set_new_line(line)
                            hierarchial_result['text-blocks'].append(
                                {"tag": "h", "text": last_seen_header, "page_number": page_no + 1,
                                 "hierarchy": node_hierarchy})
                        else:  # totally normal para
                            cur_para.append(line.strip())

                if cur_para:  # dump whatever is left
                    if 's' in prev_tag and last_to_last_tag == 'p':
                        join_with_prev_para(cur_para)
                    else:
                        cur_para_order = str(int(cur_para_order) + 1)
                        node_hierarchy = f'{cur_header_hierarchy}.{cur_para_order}'
                        hierarchial_result['text-blocks'].append(
                            {"tag": "para", "text": cur_para, "page_number": page_no + 1, "hierarchy": node_hierarchy})

            elif 'h' in tag:  # header
                if tag == 'h':
                    node_hierarchy = ''  # undetermined
                else:
                    node_hierarchy = tag[1:]
                cur_header_hierarchy = node_hierarchy
                cur_para_order = '0'  # reset it
                last_seen_header = set_new_line(text)
                hierarchial_result['text-blocks'].append(
                    {"tag": tag, "text": set_new_line(text), "page_number": page_no + 1, "hierarchy": node_hierarchy})

            elif tag == 'tb':  # table
                if text not in already_seen_table:
                    # first add a reference in text section
                    hierarchial_result['text-blocks'].append(
                        {"tag": "Table", "page_number": page_no + 1, "last_seen_header": last_seen_header,
                         "table_name": text})
                    hierarchial_result['tables'].append(
                        {"tag": "Table", "page_number": page_no + 1, "last_seen_header": last_seen_header,
                         "data": text})
                    already_seen_table.add(text)

            elif 's' in tag:  # subscript
                hierarchial_result['text-blocks'].append(
                    {"tag": "Subscript", "text": set_new_line(text), "page_number": page_no + 1})
            if prev_tag:
                last_to_last_tag = prev_tag
                prev_tag = tag

    all_table_data = {}
    for key, value in metadata.items():
        page_no = key.split()[0]
        table_2d = []
        table_columns = value['df'].columns
        table_2d.append(list(table_columns))
        table_2d.extend(list(value['df'].values.to_list()))
        all_table_data[f'table_{key}'] = table_2d

    for i, table in enumerate(hierarchial_result['tables']):
        hierarchial_result['tables'][i]['data'] = all_table_data[hierarchial_result['tables'][i]['data']]

    return hierarchial_result