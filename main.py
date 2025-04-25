from api_client import MyApiClient

client = MyApiClient(token="rAlqC/b1qsPJT48rwFX7aA==")

params = {
    'apiid': '1002',
    'seasonid': '17',
    'gradeid': '71374',
    'sportid': '1',
    'pagenum': '1',
    'pagesize': '500',
    'sort': '-BAAGG',
}

data = client.fetch(params)
print(data.keys())
