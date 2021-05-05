import re
from copy import deepcopy

def mtch(lo_words,search_str):
    matchers = deepcopy(lo_words)
    matchers = [m for m in matchers if m]
    matchers = [m[1:] if m[0].isupper() else m for m in matchers]
    return(all([ m in search_str for m in matchers ]))

def remove_table_contents(pages_texts,metadata):
    texts = deepcopy(pages_texts)
    #texts = [[t.split(">")[1] for t in text] for text in texts]
    for id in list(metadata.keys()):
        search_cols = [list(metadata[id]['df'].columns)]
        search_vals = list(metadata[id]['df'].values)
        search_cols.extend(search_vals)
        merge = metadata[id]['merge']
        #return search_cols
        #print(search_cols)
        #print(search_vals)
        search_cols = [list(a) for a in search_cols]
        search_cols = [[a for a in cols if a] for cols in search_cols]
        search_cols = [" ".join(a) for a in search_cols]
        search_cols = " ".join(search_cols).replace("\n","")
        search_cols = re.sub(' +', ' ', search_cols).replace(" ","")
        p_n = int(id.split("_")[0])
        #print(search_cols)
        for i in range(merge+1):
            for idx, bl in enumerate(pages_texts[p_n-1+i]):
                #print(list(bl.split("|$")))
                if len(bl.split(">")[1].strip()) <2:
                    continue
                if bl.split(">")[0] =="<tb":
                    continue
                x =list(bl.split(">")[1].split("|$"))
                x = [a.strip() for a in x]
                x = [re.sub(' +', ' ', a).replace(" ","") for a in x]
                #print(f"\nThe search items are \n{x}\n")
                if all([z in search_cols for z in x]) or mtch(x,search_cols):
                    #print(idx)
                    texts[p_n-1+i][idx] = f"<tb>table_{id}"
                    #print(idx)
                    '''
                    try:
                        pages_texts[p_n-1+i].remove(bl)
                        print(bl)
                    except:
                        pass
                    '''
            #print("+++"*15)
    return texts