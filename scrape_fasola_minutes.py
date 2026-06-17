import requests
from bs4 import BeautifulSoup, NavigableString
import csv
import time
import re
from urllib.parse import urljoin

# --- Configuration ---
SEARCH_URL = "https://fasola.org/minutes/search/?q=&yr=2024"
BASE_URL = "https://fasola.org/minutes/search/"
OUTPUT_FILE = "minutes_page_counts_2024.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_page_counts(html_content):
    """
    Parses HTML to count page citations (e.g., '59', '49b', '49t').
    Returns: (wrapped_count, unwrapped_count)
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Regex: 1-3 digits, optional 't' or 'b', word boundaries
    page_num_pattern = r'\b\d{1,3}[tb]?\b'

    wrapped = 0
    unwrapped = 0

    # Target specific paragraphs containing minute text
    paragraphs = soup.find_all('p', class_='MinutesText')

    for p in paragraphs:
        # We must iterate over children to distinguish Text vs Tags
        for child in p.contents:

            # 1. Wrapped: It is a link <a> tag
            if child.name == 'a':
                text = child.get_text(strip=True)
                if re.fullmatch(page_num_pattern, text):
                    wrapped += 1

            # 2. Unwrapped: It is raw text (NavigableString)
            elif isinstance(child, NavigableString):
                # Find all regex matches within this text chunk
                matches = re.findall(page_num_pattern, str(child))
                unwrapped += len(matches)

    return wrapped, unwrapped

def main():
    # 1. Fetch the main list of minutes
    print(f"Fetching list from: {SEARCH_URL}")
    try:
        response = requests.get(SEARCH_URL, headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching search page: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all minute links inside 'td.MinLstItem'
    minute_links = soup.select('td.MinLstItem a')
    print(f"Found {len(minute_links)} minutes to process.")

    # 2. Prepare CSV Output
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Minute_Name', 'URL', 'Wrapped_Count', 'Unwrapped_Count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # 3. Iterate through each minute page
        for index, link in enumerate(minute_links):
            name = link.get_text(strip=True)
            href = link.get('href')
            full_url = urljoin(BASE_URL, href)

            print(f"[{index + 1}/{len(minute_links)}] Processing: {name}...", end=" ")

            try:
                # Fetch the individual minute page
                page_response = requests.get(full_url, headers=HEADERS)
                if page_response.status_code == 200:

                    # Run the Beautiful Soup Counting Logic
                    w_count, u_count = get_page_counts(page_response.text)

                    # Save to CSV
                    writer.writerow({
                        'Minute_Name': name,
                        'URL': full_url,
                        'Wrapped_Count': w_count,
                        'Unwrapped_Count': u_count
                    })
                    print(f"Done (Wrapped: {w_count}, Unwrapped: {u_count})")
                else:
                    print(f"Failed (Status {page_response.status_code})")

            except Exception as e:
                print(f"Error: {e}")

            # Polite pause to avoid hammering the server
            time.sleep(1)

    print(f"\n✅ Processing complete. Data saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
