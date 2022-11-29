import requests
import Error_based_attack


url = input("Enter url: ")
try:
    response = requests.get(url)
except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema, requests.exceptions.InvalidURL) as error:
    print("Enter Failed Url {}".format(error))


# First try Error based injection
# inside this we call union based attack also to figure out data from another tables (to preform Exploitation phase)
Error_based_attack.sample_Get_inj(url)


