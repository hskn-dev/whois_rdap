#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://pypi.org/project/ipwhois/
# https://ipwhois.readthedocs.io/en/latest/RDAP.html
from ipwhois import IPWhois

# https://github.com/tqdm/tqdm
from tqdm import tqdm

import os
import json

# ISO3166(国コード)の日本語名対応データを読み込み
# https://qiita.com/kageryosan/items/dbf91cfdb460d26368be
with open('iso3166-1.json', mode='r', encoding='utf-8') as f:
  iso3166_1 = json.load(f)

# テキストデータから IP を余分な改行を削除してリストとして読み込み
with open('ip-list', mode='r', encoding='utf-8') as f:
  ip_list = [s.strip() for s in f.readlines()]

os.makedirs("results/details", exist_ok=True)

# 進捗表示用のオブジェクトの生成
pbar = tqdm(range(len(ip_list)))

with open('results/tab.txt', mode='w', encoding='utf-8') as f1:

  # 進捗名の設定
  pbar.set_description('EXECUTED')

  # 進捗オブジェクトを使用して IP リストをループ
  # 進捗オブジェクトは、リスト要素数のレンジを保持
  for i in pbar:
    ip = ip_list[i - 1]

    # RDAPによる問い合わせ
    r = IPWhois(ip).lookup_rdap()
    countryjp = 'NoData'
    address = 'NoData'

    #
    for item in iso3166_1:

      # 国コードより日本語名を取得
      if item['alpha2'] == r['network']['country']:
        countryjp = item['companyjp']

      # 所在地(address)情報を取得
      for obj in r['objects'].values():

        # contact 以下は存在しない場合があるため、例外処理を行い続行する
        try:
          for v in obj['contact']['address']:

            # 改行と余分な空白を削除
            address = v['value'].replace('\n', ' ').strip()
        except Exception:
          continue

        # 所在地(address)情報を取得した時点で終了
        if address:
          break

    # results/tab.txt にタブ区切りで、IP、国名(日本語)、組織名、所在地を出力
    f1.write(f"{ip}\t{countryjp}\t{r['network']['name']}\t{address}\n")

    # results/details/<ip>.json 取得した json データを IP 単位で出力
    with open(f'results/details/{ip}.json', mode='w', encoding='utf-8') as f2:
      f2.write(f"{json.dumps(r, indent=2)}")

pbar.close()
