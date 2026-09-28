import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location(
    'update_prices', Path(__file__).resolve().parents[1] / 'data/update_prices.py')
prices = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prices)


class UpdatePricesTests(unittest.TestCase):
    def archive(self, directory, name, body):
        path = directory / 'archives' / name
        path.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('prices.CSV', body)
        return 'https://example.com/' + name

    def test_merge_schema_changes_sort_filter_and_deduplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            older = self.archive(root, 'old.zip',
                'C,metadata\n'
                'I,TRADING,PRICE,2,SETTLEMENTDATE,REGIONID,RUNNO,RRP,LASTCHANGED\n'
                'D,TRADING,PRICE,2,2023/01/02 00:05:00,SA1,1,20,2023/01/02\n'
                'D,TRADING,PRICE,2,2023/01/01 00:05:00,SA1,1,-5,2023/01/01\n'
                'D,TRADING,PRICE,2,2023/01/01 00:05:00,NSW1,1,50,2023/01/01\n')
            newer = self.archive(root, 'new.zip',
                'I,TRADING,PRICE,3,REGIONID,SETTLEMENTDATE,RUNNO,RRP,LASTCHANGED,EXTRA\n'
                'D,TRADING,PRICE,3,SA1,2023/01/02 00:05:00,1,25,2023/01/03,new\n'
                'D,TRADING,PRICE,3,SA1,2023/02/01 00:00:00,1,0,2023/01/31,boundary\n'
                'C,END OF REPORT\n')
            prices.update_prices([newer, older, older], root)
            output = root / 'trading-price-sa1.csv'
            with output.open() as source:
                rows = list(csv.DictReader(source))
            self.assertEqual([row['RRP'] for row in rows], ['-5', '25'])
            self.assertEqual([row['EXTRA'] for row in rows], ['', 'new'])
            with zipfile.ZipFile(root / 'trading-price-sa1.csv.zip') as archive:
                self.assertEqual(archive.read(output.name), output.read_bytes())
            before = output.read_bytes()
            prices.update_prices([newer, older], root)
            self.assertEqual(output.read_bytes(), before)

    def test_invalid_archive_preserves_existing_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / 'trading-price-sa1.csv'
            output.write_text('previous data')
            url = self.archive(root, 'bad.zip', 'C,no prices\n')
            with self.assertRaises(ValueError):
                prices.update_prices([url], root)
            self.assertEqual(output.read_text(), 'previous data')


if __name__ == '__main__':
    unittest.main()
