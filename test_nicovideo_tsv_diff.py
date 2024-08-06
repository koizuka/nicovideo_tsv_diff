import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
import os
from datetime import datetime
from nicovideo_tsv_diff import custom_date_parser, parse_date_from_filename, calculate_diff

class TestCustomDateParser(unittest.TestCase):
    def test_valid_date(self):
        self.assertEqual(custom_date_parser('2010年08月12日 23:51:30'),
                         datetime(2010, 8, 12, 23, 51, 30))

    def test_invalid_date(self):
        self.assertIsNone(custom_date_parser('invalid date'))
        self.assertIsNone(custom_date_parser('2024-02-30 12:34:56'))  # 存在しない日付
        self.assertIsNone(custom_date_parser('2010年08月12日23:51:30'))  # 不正な形式
        self.assertIsNone(custom_date_parser('2010/08/12 23:51:30'))  # 不正な形式

    def test_colon_conversion(self):
        self.assertEqual(custom_date_parser('2010年08月12日 23：51：30'),
                         datetime(2010, 8, 12, 23, 51, 30))

class TestParseDateFromFilename(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(parse_date_from_filename('Total_API_20240603.txt'),
                         datetime(2024, 6, 3))
        self.assertEqual(parse_date_from_filename('sm32103696_20240610.txt'),
                         datetime(2024, 6, 10))

    def test_invalid_filename(self):
        with self.assertRaises(ValueError):
            parse_date_from_filename('invalid_filename.txt')
        with self.assertRaises(ValueError):
            parse_date_from_filename('20240603_Total_API.txt')

class TestCalculateDiff(unittest.TestCase):
    def setUp(self):
        self.old_file = 'temp_20240601.txt'
        self.new_file = 'temp_20240610.txt'
        old_cutoff_date = '2024年06月01日 05：00：00'
        new_post_date = '2024年06月02日 10：00：00'
        removed_before_cutoff_date = '2024年05月31日 23：59：59'

        old_data = pd.DataFrame({
            0: ['id1', 'id2', 'id3', 'id6'],  # 動画ID id6が新規に追加
            1: ['dummy'] * 4,          # ダミーデータ
            2: ['1,000', '2,000', '3,000', '4,000'],  # 差分を計算するフィールド
            3: ['4,000', '5,000', '6,000', '7,000'],
            4: ['7,000', '8,000', '9,000', '10,000'],
            5: ['dummy'] * 4,
            6: ['dummy'] * 4,
            7: ['string1', 'string2', 'string3', 'string6'],
            8: ['dummy'] * 4,
            9: [old_cutoff_date, '2024年06月01日 06：00：00', '2024年06月01日 07：00：00', '2024年06月01日 08：00：00'],  # 投稿日時
            10: ['dummy'] * 4,
            11: ['dummy'] * 4,
            12: ['dummy'] * 4,
            13: ['10,000', '11,000', '12,000', '13,000']
        })

        new_data = pd.DataFrame({
            0: ['id1', 'id3', 'id4', 'id5'],  # 動画ID id6は含まれない
            1: ['dummy'] * 4,          # ダミーデータ
            2: ['1,100', '3,200', '1,000', '500'],  # 差分を計算するフィールド
            3: ['4,500', '6,100', '2,000', '250'],
            4: ['7,100', '9,200', '3,000', '150'],
            5: ['dummy'] * 4,
            6: ['dummy'] * 4,
            7: ['string1_new', 'string3_new', 'string4_new', 'string5_new'],
            8: ['dummy'] * 4,
            9: [old_cutoff_date, '2024年06月01日 06：30：00', new_post_date, removed_before_cutoff_date],  # 投稿日時
            10: ['dummy'] * 4,
            11: ['dummy'] * 4,
            12: ['dummy'] * 4,
            13: ['10,100', '12,200', '5,000', '300']
        })

        old_data.to_csv(self.old_file, sep='\t', index=False, header=False)
        new_data.to_csv(self.new_file, sep='\t', index=False, header=False)

    def tearDown(self):
        os.remove(self.old_file)
        os.remove(self.new_file)

    def test_calculate_diff(self):
        cutoff_date = datetime(2024, 6, 1, 5, 0, 0)
        result_data, new_entries_count = calculate_diff(self.old_file, self.new_file, cutoff_date)

        expected_data = pd.DataFrame({
            0: ['id1', 'id3', 'id4'],  # id5はcutoff_dateより古いので含まれない
            1: ['dummy'] * 3,
            2: [100, 200, 1000],  # 差分: 1100-1000, 3200-3000, 1000
            3: [500, 100, 2000],  # 差分: 4500-4000, 6100-6000, 2000
            4: [100, 200, 3000],  # 差分: 7100-7000, 9200-9000, 3000
            5: ['dummy'] * 3,
            6: ['dummy'] * 3,
            7: ['string1_new', 'string3_new', 'string4_new'],
            8: ['dummy'] * 3,
            9: ['2024年06月01日 05：00：00', '2024年06月01日 06：30：00', '2024年06月02日 10：00：00'],
            10: ['dummy'] * 3,
            11: ['dummy'] * 3,
            12: ['dummy'] * 3,
            13: [100, 200, 5000]   # 差分: 10100-10000, 12200-12000, 5000
        })
        expected_data.set_index(0, inplace=True)
        expected_data.columns = expected_data.columns.astype(object)

        # データフレームを比較
        try:
            assert_frame_equal(result_data, expected_data, check_dtype=False)
        except AssertionError as e:
            # ここで詳細な違いを表示
            print("DataFrames are not equal!")
            print("Expected:")
            print(expected_data)
            print("Result:")
            print(result_data)
            print("\nDifferences:")
            print(result_data.compare(expected_data))
            raise e  # エラーを再度投げてテストを失敗させる

        self.assertEqual(new_entries_count, 1)

if __name__ == '__main__':
    unittest.main()
