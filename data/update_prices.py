"""Download the archives listed by download.sh and combine their SA1 records."""

import csv
import io
import math
from pathlib import Path
import subprocess
import sys
from urllib.parse import unquote, urlparse
import zipfile


def read_prices(path):
    records = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.lower().endswith('.csv'):
                continue
            headers = {}
            with archive.open(name) as source:
                for row in csv.reader(io.TextIOWrapper(source, encoding='utf-8-sig')):
                    if len(row) < 4 or row[1:3] != ['TRADING', 'PRICE']:
                        continue
                    if row[0] == 'I':
                        headers[row[3]] = row[4:]
                    elif row[0] == 'D':
                        fields = headers.get(row[3])
                        if fields is None or len(fields) != len(row[4:]):
                            raise ValueError(f'{path}: missing header or malformed price record')
                        record = dict(zip(fields, row[4:]))
                        if record['REGIONID'] == 'SA1':
                            if not record['SETTLEMENTDATE'] or not math.isfinite(float(record['RRP'])):
                                raise ValueError(f'{path}: invalid SA1 timestamp or price')
                            records.append(record)
    if not records:
        raise ValueError(f'{path}: no SA1 trading prices found')
    return records


def update_prices(urls, data_dir):
    if not urls:
        raise ValueError('No monthly archive URLs configured')
    cache = data_dir / 'archives'
    cache.mkdir(parents=True, exist_ok=True)
    prices = {}
    fields = []
    for url in urls:
        path = cache / Path(unquote(urlparse(url).path)).name
        if not path.exists():
            partial = path.with_suffix('.part')
            try:
                print(f'Downloading {url}', flush=True)
                subprocess.run(['curl', '--fail', '--location', '--retry', '3',
                                '--connect-timeout', '30', '--max-time', '300',
                                '--silent', '--show-error', '--output', str(partial), url], check=True)
                records = read_prices(partial)
                partial.replace(path)
            finally:
                partial.unlink(missing_ok=True)
        else:
            print(f'Using cached {path.name}', flush=True)
            records = read_prices(path)
        for record in records:
            for field in record:
                if field not in fields:
                    fields.append(field)
            key = (record['SETTLEMENTDATE'], record['REGIONID'], record['RUNNO'])
            previous = prices.get(key)
            if previous is None or record.get('LASTCHANGED', '') > previous.get('LASTCHANGED', ''):
                prices[key] = record

    # Monthly archives end at midnight on the first day of the next month.
    # Omit that trailing interval so it cannot create a near-zero extra month.
    final_timestamp = max(key[0] for key in prices)
    if final_timestamp.endswith('/01 00:00:00'):
        prices = {key: record for key, record in prices.items()
                  if key[0] != final_timestamp}

    output = data_dir / 'trading-price-sa1.csv'
    temporary = output.with_suffix('.csv.tmp')
    zipped = data_dir / 'trading-price-sa1.csv.zip'
    temporary_zip = zipped.with_suffix('.zip.tmp')
    try:
        with temporary.open('w', newline='') as target:
            writer = csv.DictWriter(target, fieldnames=fields)
            writer.writeheader()
            writer.writerows(prices[key] for key in sorted(prices))
        with zipfile.ZipFile(temporary_zip, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.write(temporary, output.name)
        temporary.replace(output)
        temporary_zip.replace(zipped)
    finally:
        temporary.unlink(missing_ok=True)
        temporary_zip.unlink(missing_ok=True)
    print(f'Wrote {len(prices):,} SA1 records to {output}', flush=True)


if __name__ == '__main__':
    update_prices(sys.argv[1:], Path(__file__).resolve().parent)
