import requests
import os
import json
import unicodedata
import re
import time
from dotenv import load_dotenv

load_dotenv()

ENV_XSRF_TOKEN = os.getenv('XSRF_TOKEN')
ENV_LARAVEL_SESSION = os.getenv('LARAVEL_SESSION')
ENV_LARAVEL_TOKEN = os.getenv('LARAVEL_TOKEN')
ENV_X_CSRF_TOKEN = os.getenv('X_CSRF_TOKEN')

FILE_OIL_LIST = 'oil_list.json'
FILE_COMPOUND_LIST = 'compound_list.json'

DIR_OILS = 'oils'
DIR_COMPOUNDS = 'compounds'

cookies = {
    'XSRF-TOKEN': ENV_XSRF_TOKEN,
    'laravel_session': ENV_LARAVEL_SESSION,
    'laravel_token': ENV_LARAVEL_TOKEN,
}
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'essentialoils.org',
    'Referer': 'https://essentialoils.org/db',
    'X-Csrf-Token': ENV_X_CSRF_TOKEN,
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode(
            'ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def doGetReq(url: str, params: set = None) -> str:
    # Manual delay to not DOS.
    time.sleep(1)

    resp = requests.get(url, headers=headers, cookies=cookies, params=params)
    text = resp.text

    if '<!DOCTYPE html>' in text:
        print('BAD REQUEST - TRY FIXING THE COOKIE or X-Csrf-Token')
        exit(1)

    if '{"success":false,"error":{"code":0,"message":"Unauthenticated."}}' in text:
        print('BAD REQUEST - TRY UPDATING THE COOKIE OR X-Csrf-Token')
        exit(1)

    if 'Too Many Attempts.' in text:
        print('TOO MANY ATTEMPTS - TRY CHANGING DELAY')
        exit(1)

    return resp.text


def getOilListData():
    payload = {
        'fields': 'id,name,name_sort,CAS,abstract_publication,name_botanical,name_botanical_sort',
        'pages': '*',
        'reset_cache': None,
        'synonym': None
    }

    return doGetReq('https://essentialoils.org/api/oil', payload)


def getCompoundListData():
    payload = {
        'fields': 'id,name,name_sort,CAS',
        'pages': '*',
        'reset_cache': None,
        'synonym': None
    }

    return doGetReq('https://essentialoils.org/api/compound', payload)


def getOilBreakdownData(id: int):
    return doGetReq(f'https://essentialoils.org/api/oil/{id}')


def getCompoundBreakdownData(id: int):
    return doGetReq(f'https://essentialoils.org/api/compound/{id}')


def exportLists():
    if not os.path.exists(FILE_OIL_LIST):
        print(f'PULLING NEW OIL LIST -> {FILE_OIL_LIST}')
        oilList = getOilListData()
        with open(FILE_OIL_LIST, 'w') as f:
            f.write(oilList)

    if not os.path.exists(FILE_COMPOUND_LIST):
        print(f'PULLING NEW COMPOUND LIST -> {FILE_COMPOUND_LIST}')
        compoundList = getCompoundListData()
        with open(FILE_COMPOUND_LIST, 'w') as f:
            f.write(compoundList)


def exportAllOils():
    if not os.path.exists(FILE_OIL_LIST):
        print(f'MISSING OIL LIST {FILE_OIL_LIST}')
        exit(1)

    if not os.path.exists(DIR_OILS):
        print(f'CREATING MISSING OILS DIR -> {DIR_OILS}')
        os.mkdir(DIR_OILS)

    with open(FILE_OIL_LIST) as f:
        data = json.load(f)

    for oil in data:
        id = oil['id']
        name = oil['name']

        oil_file_path = f'{DIR_OILS}/{slugify(name)}.json'
        if os.path.exists(oil_file_path):
            print(f'EXISTS\t{id}\t{name}')
            continue

        oil_data = getOilBreakdownData(id)
        with open(oil_file_path, 'w') as oilf:
            oilf.write(oil_data)

        print(f'PULLED\t{id}\t{name}')


def exportAllCompounds():
    if not os.path.exists(FILE_COMPOUND_LIST):
        print(f'MISSING COMPOUND LIST {FILE_COMPOUND_LIST}')
        exit(1)

    if not os.path.exists(DIR_COMPOUNDS):
        print(f'CREATING MISSING COMPOUNDS DIR -> {DIR_COMPOUNDS}')
        os.mkdir(DIR_COMPOUNDS)

    with open(FILE_COMPOUND_LIST) as f:
        data = json.load(f)

    for compound in data:
        id = compound['id']
        name = compound['name']

        compound_file_path = f'{DIR_COMPOUNDS}/{slugify(name)}.json'
        if os.path.exists(compound_file_path):
            print(f'EXISTS\t{id}\t{name}')
            continue

        compound_data = getCompoundBreakdownData(id)
        with open(compound_file_path, 'w') as compoundf:
            compoundf.write(compound_data)

        print(f'PULLED\t{id}\t{name}')


if __name__ == '__main__':
    exportLists()
    exportAllOils()
    exportAllCompounds()
