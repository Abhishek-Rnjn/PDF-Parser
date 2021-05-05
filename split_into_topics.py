from collections import defaultdict


def get_table_data(table_name, tables):
    _, page_no, order = table_name.split('_')
    page_no = int(page_no)
    order = int(order)
    for node in tables:
        if node['page_number'] == page_no:
            order -= 1
        if order == 0:
            return node['data']
    return []


def topic_split(hierarchical_data):
    topic_freq = defaultdict(lambda: 0)
    for node in hierarchical_data['text-blocks']:
        if 'h' in node['tag']:  # better to use re to check this...h-followed-by-number
            topic_freq[node['tag']] += 1
    most_freq_header_tag = max(topic_freq, key=topic_freq.get)
    print(most_freq_header_tag)
    topic_split = defaultdict(list)
    last_seen_header = -1
    for node_i, node in enumerate(hierarchical_data['text-blocks']):
        if node['tag'] == most_freq_header_tag:
            last_seen_header = node_i
        else:
            topic_split[last_seen_header].append(node_i)

    # replace indices with actual value
    item_header_data = []
    for topic, subitems in topic_split.items():
        if topic == -1:
            tag = 'NA'
        else:
            tag = hierarchical_data['text-blocks'][topic]['tag']
        hierarchy = {}
        hierarchy['header'] = {'tag': tag, 'text': hierarchical_data['text-blocks'][topic]['text'], 'page': hierarchical_data['text-blocks'][topic]['page_number']}
        hierarchy['sub items'] = []
        for subitem in subitems:
            subitem_info = {'tag': hierarchical_data['text-blocks'][subitem]['tag'], 'page': hierarchical_data['text-blocks'][subitem]['page_number']}
            if hierarchical_data['text-blocks'][subitem]['tag'] == 'Table':
                subitem_info['data'] = get_table_data(hierarchical_data['text-blocks'][subitem]['table_name'], hierarchical_data['tables'])
            else:
                texts = hierarchical_data['text-blocks'][subitem]['text']
                if texts[0].encode('utf-8') == b"\xe2\x80\xa2":
                    if subitem_info['tag'] == 'h':
                        subitem_info['tag'] = 'bhp'
                    subitem_info['tag'] = 'bp'
                subitem_info['data'] = texts
            hierarchy['sub items'].append(subitem_info)
        item_header_data.append(hierarchy)
    return item_header_data