# 差分とるやつ

## 準備

Python 3.10

```bash
pip install pandas
```

## 実行

```bash
$ time python nicovideo_tsv_diff.py -o temp.tsv Total_API_20240603.txt Total_API_20240610.txt
出力件数: 1251492 件 (新規投稿: 465 件)

real    1m8.128s
user    0m0.000s
sys     0m0.016s
```

```bash
$ python nicovideo_tsv_diff.py --help
usage: nicovideo_tsv_diff.py [-h] [-o OUTPUT] old_snapshot_path new_snapshot_path

スナップショットファイル間の差分を計算するスクリプト

positional arguments:
  old_snapshot_path     古いスナップショットファイルのパス
  new_snapshot_path     新しいスナップショットファイルのパス

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        結果を出力するファイルのパス
```

## ユニットテスト

```bash
python -m unittest test_nicovideo_tsv_diff.py
```