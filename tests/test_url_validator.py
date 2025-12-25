import requests
import re
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


def is_valid_youtube_channel(url: str) -> dict:
    """
    YouTube 채널 URL 유효성 검사
    """
    result = {
        'url': url,
        'is_valid': False,
        'is_channel': False,
        'status_code': None,
        'error': None
    }

    channel_patterns = [
        r'^https?://(www\.)?youtube\.com/@[\w.-]+',
        r'^https?://(www\.)?youtube\.com/channel/UC[\w-]+',
        r'^https?://(www\.)?youtube\.com/c/[\w.-]+',
        r'^https?://(www\.)?youtube\.com/user/[\w.-]+',
    ]

    is_channel_url = any(re.match(p, url) for p in channel_patterns)

    if not is_channel_url:
        result['error'] = 'Not a channel URL format'
        return result

    result['is_channel'] = True

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        result['status_code'] = response.status_code

        if response.status_code == 200:
            result['is_valid'] = True
        elif response.status_code == 404:
            result['error'] = 'Channel not found'
        else:
            result['error'] = f'HTTP {response.status_code}'

    except requests.Timeout:
        result['error'] = 'Request timeout'
    except requests.RequestException as e:
        result['error'] = str(e)

    return result


def validate_single(row_data: tuple) -> dict:
    """단일 행 검증"""
    idx, url, channel_name = row_data
    result = is_valid_youtube_channel(url)
    result['idx'] = idx
    result['channel_name'] = channel_name
    return result


def validate_output_file(filepath: str, max_workers: int = 10, save_valid: bool = False):
    """output 폴더의 CSV 파일 검증"""
    path = Path(filepath)

    if not path.exists():
        print(f"File not found: {filepath}")
        return

    df = pd.read_csv(path)

    print("=" * 60)
    print(f"Validating: {filepath}")
    print(f"Total rows: {len(df)}")
    print(f"Workers: {max_workers}")
    print("=" * 60)

    if 'channel_url' not in df.columns:
        print("Error: 'channel_url' column not found")
        return

    rows = [
        (idx, row['channel_url'], row.get('channel_name', 'N/A'))
        for idx, row in df.iterrows()
    ]

    valid_count = 0
    invalid_count = 0
    valid_urls = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(validate_single, row): row for row in rows}

        for future in as_completed(futures):
            result = future.result()

            status = "✓" if result['is_valid'] else "✗"
            print(f"{status} {result['channel_name']}: {result['url']}")

            if result['error']:
                print(f"  └─ {result['error']}")

            if result['is_valid']:
                valid_count += 1
                valid_urls.append(result['url'])
            else:
                invalid_count += 1

    print("\n" + "=" * 60)
    print(f"Valid: {valid_count} / Invalid: {invalid_count}")
    print(f"Success rate: {valid_count / len(df) * 100:.1f}%")

    if save_valid and valid_urls:
        output_path = path.parent / f"{path.stem}_validated.csv"
        valid_df = pd.DataFrame({'channel_url': valid_urls})
        valid_df.to_csv(output_path, index=False)
        print(f"Saved {len(valid_urls)} valid URLs to: {output_path}")

    return valid_urls


def get_latest_output():
    """가장 최근 output 파일 찾기"""
    output_dir = Path('output')
    if not output_dir.exists():
        return None

    csv_files = list(output_dir.glob('*.csv'))
    if not csv_files:
        return None

    return max(csv_files, key=lambda x: x.stat().st_mtime)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Validate YouTube channel URLs')
    parser.add_argument('file', nargs='?', help='CSV file to validate')
    parser.add_argument('-w', '--workers', type=int, default=10, help='Number of threads')
    parser.add_argument('-s', '--save', action='store_true', help='Save valid URLs only')

    args = parser.parse_args()

    if args.file:
        validate_output_file(args.file, max_workers=args.workers, save_valid=args.save)
    else:
        latest = get_latest_output()
        if latest:
            validate_output_file(str(latest), max_workers=args.workers, save_valid=args.save)
        else:
            print("No output files found. Run the scraper first:")
            print("  python main.py \"python programming\"")