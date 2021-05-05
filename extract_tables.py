import camelot
import pandas as pd

def verifier(prev_page,curr_page,prev_df,curr_df):
    last_values = " ".join(list(prev_df.values[-1]))
    if curr_df.columns[0] == 0:
        first_values = " ".join(list(curr_df.values[0]))  #or list(curr_df.columns)
    else:
        first_values = " ".join(list(curr_df.columns))
    last_line = prev_page[-1]
    last_line = last_line.split(">")[1].replace("|$","")
    first_line = curr_page[0]
    first_line = first_line.split(">")[1].replace("|$","")
    '''
    print("++"*30)
    print(f"{last_values}\n\nAR\n{last_line}\n\n\n\nBR\n{first_values}\nCR\n{first_line}\n")
    print("{}"*30)
    '''
    if last_line.replace(" ","").replace("\n","") in last_values.replace(" ","").replace("\n","") and first_line.replace(" ","").replace("\n","") in first_values.replace(" ","").replace("\n",""):
        print("True")
        return True
    else:
        print("False")
        return False


def return_metadata(file_path):
    tables = camelot.read_pdf(file_path, pages="all", line_scale=65)
    pages_data = get_tagged_data(file_path)
    with open("temp.txt",'w') as f:
        for page in pages_data:
            f.write("\n".join(page))
            f.write("\nDFSJFGSJFGSFG\n")
    metadata = {}
    i = 0
    if len(tables)  == 0:
        return metadata
    for table in tables:
        passing = False
        report = table.parsing_report
        if abs(report['accuracy']) >1000:
            passing = True
        if report['accuracy'] < 35 and not passing :
            continue
        table_id = f"{report['page']}_{report['order']}"
        metadata[table_id] = {}
        df = table.df
        if len(df) > 1:
            colmns = df.iloc[0]
            df = df.iloc[1:]
            df.columns = colmns

        z = table.cols
        b = []
        for a in z:
            b.append((a[0] // 1, a[1] // 1))
        metadata[table_id]['df'] = df
        metadata[table_id]['page'] = report['page']
        metadata[table_id]['position'] = report['order']
        metadata[table_id]['confidence'] = report['accuracy']
        metadata[table_id]['cols'] = b
        metadata[table_id]['merge'] = 0

    if len(metadata) == 0:
        return metadata
    # return metadata
    all_tabs = list(metadata.keys())  # a_t
    temp_list = [{all_tabs[0]: metadata[all_tabs[0]]}]
    final_tabs = deepcopy(all_tabs)

    for a in all_tabs[1:]:
        prev_name = list(temp_list[-1].keys())[0]
        prev_data = temp_list[-1][prev_name]
        idx = 0
        if (metadata[a]['cols'] == prev_data['cols']) and (metadata[a]['page'] != prev_data['page']) and (metadata[a]['position'] ==1):
            print(f"The prev_table's page is { prev_data['page']}\n THe current table's page is {metadata[a]['page']}\n")
            if (metadata[a]['df'].columns[0] == 0) or (list(metadata[a]['df'].columns) == list(prev_data['df'].columns))or ( verifier(pages_data[prev_data['page']-1],pages_data[metadata[a]['page']-1],prev_data['df'],metadata[a]['df'])):
                # don't know if this line'll work
                prev_data['page']+=1
                # till here
                if list(metadata[a]['df'].columns) == list(prev_data['df'].columns) or (metadata[a]['df'].columns[0] == 0):
                    metadata[a]['df'].columns = prev_data['df'].columns
                    temp_df = pd.concat([prev_data['df'], metadata[a]['df']])
                    metadata[prev_name]['df'] = temp_df
                    final_tabs.remove(a)
                    metadata[prev_name]['merge']+=1
                else:
                    cls = [list(metadata[a]['df'].columns)]
                    cls.extend(list(metadata[a]['df'].values))
                    alt_df = pd.DataFrame(cls)
                    alt_df.columns = prev_data['df'].columns
                    temp_df = pd.concat([prev_data['df'], alt_df])
                    metadata[prev_name]['df'] = temp_df
                    final_tabs.remove(a)
                    metadata[prev_name]['merge']+=1


            else:
                temp_list.append({a: metadata[a]})
        else:
            temp_list.append({a: metadata[a]})
    data = {}

    for table in final_tabs:
        dx = metadata[table]['df']
        if metadata[table]['page'] != table.split("_")[0]:
            metadata[table]['page'] = int(table.split("_")[0])
        vals = list(dx.columns)
        if vals[0] == 0:
            print("\n\n\nZUP\n\n")
            temp = dx.iloc[0].values
            dx.columns = temp
            dx = dx.iloc[1:]
        metadata[table]['df'] = dx
        data[table] = metadata[table]
    #print("\nAll the tables are:\n")
    #print(data)
    return data