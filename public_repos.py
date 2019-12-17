#!/usr/bin/env python3
import json, requests
import pandas
import csv
from bs4 import BeautifulSoup

access_token = 'd6d8da9dd28ba665cb402d02350418635baf98b6'

def get_last_id():
    try:
        df = pandas.read_csv('repo_lang2.csv', usecols=['id'])[-1:]
        last_id = df.at[df.index.item(), 'id']
    except FileNotFoundError:
        last_id = 0
    return last_id

def get_repo_language(df):
  repo_data = []
  df_id = pandas.DataFrame(df['id'])
  for language in df['languages_url']:
    r = requests.get(language, params={
      'access_token': access_token
    })
    r = r.json()
    repo_data.append(r)
    df_repo = pandas.DataFrame(repo_data)
  df_final = df_id.join(df_repo, how='outer')
  return df_final


def get_remaining_limit():
    r = requests.get("https://api.github.com/rate_limit", params={
            'access_token': access_token
    })
    return r.json()["rate"]["remaining"]


def main():
    last_id = get_last_id()
    while(get_remaining_limit() > 0):
        r = requests.get("https://api.github.com/repositories", params={
                'since': last_id, 
                'access_token': access_token
        })
        df = pandas.read_json(r.text)
        repo_language = get_repo_language(df)
        if last_id == 0:
            repo_language.to_csv('repo_lang2.csv', index=False)
        else:
            repo_language.to_csv('repo_lang2.csv', mode='a', header=False, index=False)
        last_id = df.tail(1)['id'].item()

if __name__ == "__main__":
    main()