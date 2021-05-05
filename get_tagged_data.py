from collections import defaultdict
from operator import itemgetter
import fitz
import re
from copy import deepcopy

def pacifier(list_of_data):
    blacklist = set()
    freq = defaultdict(lambda: 0)
    for page in list_of_data:
        for line in page:
            # print(line)
            freq[line.strip()] += 1
    for i in freq:
        if freq[i] > int(len(list_of_data) / 2):
            blacklist.add(i)

    if len(list_of_data) > 2:
        for line in list_of_data[1]:

            if [line in dx for dx in list_of_data[2:]].count(True) > int(len(list_of_data) / 2):
                blacklist.add(line)
    if len(list_of_data) != 1:
        for line in list_of_data[0]:
            if all([line in dx for dx in list_of_data[1:]]):
                blacklist.add(line)
    final_data = []
    for data in list_of_data:
        page_data = []
        for line in data:
            if line in blacklist or line.split(">")[1].strip().isdigit():
                pass
            else:
                page_data.append(line)
        final_data.append(page_data)
    return final_data


def fonts(doc):
    styles = {}
    font_counts = {}

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # block contains text
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        identifier = "{0}".format(s['size'])  # currently not using font info
                        styles[identifier] = {'size': s['size'], 'font': s['font']}

                        font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

    font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

    if len(font_counts) < 1:
        raise ValueError("Zero discriminating fonts found!")

    return font_counts, styles


def font_tags(font_counts, styles):
    p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
    p_size = p_style['size']  # get the paragraph's size

    # sorting the font sizes high to low, so that we can append the right integer to each tag
    font_sizes = []
    for (font_size, count) in font_counts:
        if "_" in font_size:
            f_sz = font_size.split("_")[0]
        else:
            f_sz = font_size
        font_sizes.append(float(f_sz))
    font_sizes.sort(reverse=True)

    # aggregating the tags for each font size
    idx = 0
    size_tag = {}
    for size in font_sizes:
        idx += 1
        if size == p_size:
            idx = 0
            size_tag[size] = '<p>'
        if size > p_size:
            size_tag[size] = '<h{0}>'.format(idx)
        elif size < p_size:
            size_tag[size] = '<s{0}>'.format(idx)

    return size_tag


def headers_para(doc, size_tag):
    """Scrapes headers & paragraphs from PDF and return texts with element tags.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param size_tag: textual element tags for each size
    :type size_tag: dict
    :rtype: list
    :return: texts with pre-prended element tags
    """
    all_header_para = []  # list with headers and paragraphs
    first = True  # boolean operator for first header
    previous_s = {}  # previous span

    for page in doc:
        all_page_para = []
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            block_para = []
            if b['type'] == 0:  # this block contains text

                block_string = ""  # text found in block
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if s['text'].strip():  # removing whitespaces:
                            if first:
                                previous_s = s
                                first = False
                                block_string = size_tag[s['size']] + s['text'] + "  rGb" + str(s['font']).replace(" ",
                                                                                                                  "").replace(
                                    ",", "-") + " "
                            else:
                                if s['size'] == previous_s['size']:

                                    if block_string and all((c == "|$") for c in block_string):
                                        # block_string only contains pipes
                                        block_string = size_tag[s['size']] + s['text'] + "  rGb" + str(
                                            s['font']).replace(" ", "").replace(",", "-") + " "
                                    if block_string == "":
                                        # new block has started, so append size tag
                                        block_string = size_tag[s['size']] + s['text'] + "  rGb" + str(
                                            s['font']).replace(" ", "").replace(",", "-") + " "
                                    else:  # in the same block, so concatenate strings
                                        block_string += " " + s['text'] + "  rGb" + str(s['font']).replace(" ",
                                                                                                           "").replace(
                                            ",", "-") + " "

                                else:
                                    block_para.append(block_string)
                                    block_string = size_tag[s['size']] + s['text'] + "  rGb" + str(s['font']).replace(
                                        " ", "").replace(",", "-") + " "

                                previous_s = s
                    # print(block_string)
                    # new block started, indicating with a pipe
                    block_string += "|$"

                block_para.append(block_string)
                if block_para:
                    all_page_para.append(block_para)
        if all_page_para:
            all_header_para.append(all_page_para)
        else:
            all_header_para.append([])

    return all_header_para


def get_tagged_data(pdf_path):
    doc = fitz.open(pdf_path)

    font_counts, styles = fonts(doc)
    # print(font_counts)
    s_merge = 0
    h_merge = 0
    if len(font_counts) > 1:
        if abs(float(font_counts[0][0]) - float(font_counts[1][0])) < 0.7:
            if font_counts[0] > font_counts[1]:
                s_merge = 1
            else:
                h_merge = 1

    size_tag = font_tags(font_counts, styles)

    datas = headers_para(doc, size_tag)
    dts = []
    for data in datas:
        x = [d for e in data for d in e]
        x = [a for a in x if len(a) > 2]
        x = [a.strip(" |$") for a in x if a[0] == "<"]
        dts.append(x)

    tags = set()
    for dt in dts:
        for line in dt:
            tags.add(line.split(">")[0])
    tags = sorted(tags)
    bold_tag = None
    for i in range(len(tags)):
        if tags[i] == "<p":
            try:
                bold_tag = tags[i - 1]
            except:
                break
    print(tags)
    print(bold_tag)
    num = 1
    if bold_tag:
        num = int(bold_tag[-1]) + 1
    print(num)
    merge_tag = None
    if s_merge:
        for i in range(len(tags)):
            if tags[i] == "<p":
                try:
                    merge_tag = tags[i + 1]
                except:
                    break
    if h_merge:
        for i in range(len(tags)):
            if tags[i] == "<p":
                try:
                    merge_tag = tags[i - 1]
                except:
                    break
    print(merge_tag)
    dt = []
    for i, cs in enumerate(dts):
        pg_data = []
        for line in cs:
            if len(line.split("rGb")) == 2:
                try:
                    if line.split("rGb", 1)[1].split("-")[1].startswith("Bold") and (
                            line[1] != "h" or line.split(">", 1)[0] == merge_tag):
                        line = f"<h{num}> " + line.split(">", 1)[1]
                        if 'Invoicing Schedule' in line:
                            print(line)
                        # print(line)
                except:
                    pass
            line = re.sub(r"\brGb[a-zA-Z]*[-][a-zA-Z]*", "", line)
            line = re.sub(r"\brGb[a-zA-Z]*", "", line)
            pg_data.append(line)
        dt.append(pg_data)
    dts = deepcopy(dt)
    if not merge_tag:
        return pacifier(dts)
    dtx = []
    for data in dts:
        y = []
        for l in data:
            if 'Invoicing Schedule' in l:
                print(l, l[:len(merge_tag)], merge_tag)
            if l[:len(merge_tag)] == merge_tag:
                y.append(l.replace(merge_tag, "<p"))
            else:
                y.append(l)

        dtx.append(y)

    return pacifier(dtx)