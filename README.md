# 差分とるやつ

大量の動画集合からつくるランキング生成のサポートツールです。

ニコニコ動画の動画情報が入ったTSVファイルを日付つきファイル名で二つ与えると、その古い方の日付の午前5時を基準時刻として、そこから新しい方への増分にしたTSVファイルを生成します。

このとき古い方にしかないものと、新しいほうにしかなくてかつ投稿日時が基準時刻より古い物は除去します。

0カラム目を動画ID, 2,3,4,13カラム目を差分対象(カンマ付き数値)、9カラム目を投稿日時(日本語表現)とします。

## 準備

Python 3.10

```bash
pip install pandas
```

## 実行

```bash
$ time python nicovideo_tsv_diff.py Total_API_20240603.txt Total_API_20240610.txt -o temp.tsv --sort-desc
出力件数: 1251492 件 (新規投稿: 465 件)

real    1m12.209s
user    0m0.015s
sys     0m0.016s
```

```bash
$ python nicovideo_tsv_diff.py --help
usage: nicovideo_tsv_diff.py [-h] [-o OUTPUT] [-v] [--sort-desc] old_snapshot_path new_snapshot_path

スナップショットファイル間の差分を計算するスクリプト

positional arguments:
  old_snapshot_path     古いスナップショットファイルのパス
  new_snapshot_path     新しいスナップショットファイルのパス

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        結果を出力するファイルのパス
  -v, --version         show program's version number and exit
  --sort-desc           カラム2の降順でソートして出力

```

```bash
$ python nicovideo_tsv_diff.py -v
nicovideo_tsv_diff.py 1.0.1
```

## ユニットテスト

```bash
python -m unittest test_nicovideo_tsv_diff.py
```
