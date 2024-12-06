import requests
import json


def grab_tax_percentage(zip_code: str):
    api_url = 'https://api.api-ninjas.com/v1/salestax?zip_code={}'.format(zip_code)
    response = requests.get(api_url, headers={'X-Api-Key': '47MKwv4ZIdKCWBMl8VkXpA==X9wjg11KK1vFRRqH'})
    if response.status_code == requests.codes.ok:
        print(json.dumps(response.json(), indent=4))
        return response.json()[0]["total_rate"]
    else:
        print("Error:", response.status_code, response.text)