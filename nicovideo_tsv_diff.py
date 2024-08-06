import pandas as pd
import argparse
import os
from datetime import datetime
import re
import sys

VERSION = "1.0.0"

def parse_date_from_filename(filename):
    try:
        date_str = os.path.splitext(os.path.basename(filename))[0].split('_')[-1]
        return datetime.strptime(date_str, '%Y%m%d')
    except (IndexError, ValueError):
        raise ValueError(f"ファイル名 '{filename}' から日付を抽出できませんでした。")

def custom_date_parser(date_str):
    date_str = date_str.replace('：', ':')
    try:
        if re.match(r'^\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}:\d{2}$', date_str):
            return datetime.strptime(date_str, '%Y年%m月%d日 %H:%M:%S')
        else:
            return None
    except ValueError:
        return None

def remove_commas_and_convert(value):
    try:
        return pd.to_numeric(value.replace(',', ''), errors='coerce')
    except AttributeError:
        return value

def create_converters(fields_to_diff):
    converters = {field: remove_commas_and_convert for field in fields_to_diff}
    converters[7] = str
    return converters

def calculate_diff(old_snapshot_path, new_snapshot_path, cutoff_date):
    fields_to_diff = [2, 3, 4, 13]
    converters = create_converters(fields_to_diff)

    # old_data と new_data の読み込み、ヘッダーなし
    old_data = pd.read_csv(old_snapshot_path, sep='\t', header=None, converters=converters)
    new_data = pd.read_csv(new_snapshot_path, sep='\t', header=None, converters=converters)

    old_data.set_index(0, inplace=True)
    new_data.set_index(0, inplace=True)

    new_data['timestamp'] = new_data[9].apply(custom_date_parser)
    new_data['is_new'] = (~new_data.index.isin(old_data.index)) & (new_data['timestamp'] >= cutoff_date)
    new_entries = new_data[new_data['is_new']]

    combined_data = new_data.copy()
    combined_data = combined_data.loc[combined_data.index.isin(old_data.index) | combined_data.index.isin(new_entries.index)]

    # 共通のインデックスを持つ行を取得
    common_indices = combined_data.index.intersection(old_data.index)

    # 差分計算
    combined_data.loc[common_indices, fields_to_diff] = (
        new_data.loc[common_indices, fields_to_diff] - old_data.loc[common_indices, fields_to_diff]
    ).astype(int)

    # 一時計算カラムを削除
    combined_data = combined_data.drop(columns=['timestamp', 'is_new'], errors='ignore')

    return combined_data, len(new_entries)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='スナップショットファイル間の差分を計算するスクリプト')
    parser.add_argument('old_snapshot_path', help='古いスナップショットファイルのパス')
    parser.add_argument('new_snapshot_path', help='新しいスナップショットファイルのパス')
    parser.add_argument('-o', '--output', help='結果を出力するファイルのパス')
    parser.add_argument('-v', '--version', action='version', version=f"%(prog)s {VERSION}")
    parser.add_argument('--sort-desc', action='store_true', help='カラム2の降順でソートして出力')

    args = parser.parse_args()
    
    old_date = parse_date_from_filename(args.old_snapshot_path)
    new_date = parse_date_from_filename(args.new_snapshot_path)

    if old_date > new_date:
        old_snapshot_path, new_snapshot_path = args.new_snapshot_path, args.old_snapshot_path
        cutoff_date = new_date.replace(hour=5, minute=0, second=0, microsecond=0)
    else:
        cutoff_date = old_date.replace(hour=5, minute=0, second=0, microsecond=0)

    combined_data, new_entries_count = calculate_diff(args.old_snapshot_path, args.new_snapshot_path, cutoff_date)

    if args.sort_desc:
        combined_data.sort_values(by=2, ascending=False, inplace=True)

    if args.output:
        combined_data.to_csv(args.output, sep='\t', index=True, header=False)
        total_count = len(combined_data)
        print(f"出力件数: {total_count} 件 (新規投稿: {new_entries_count} 件)")
    else:
        combined_data.to_csv(sys.stdout, sep='\t', index=True, header=False)
