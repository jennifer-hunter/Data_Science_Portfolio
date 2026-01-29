"""
va_sculpture_download.py

Script for downloading V&A sculpture records using the V&A Collections API.
"""

import requests
import pandas as pd
from io import StringIO


# Base URL for the V&A Collections API search endpoint.
# Every request we make is sent to this address.
BASE_URL = "https://api.vam.ac.uk/v2/objects/search"

# How many records we want per page.
# The API allows a maximum of 100 which keeps it efficient.
PAGE_SIZE = 100

# These are the filters that control which objects we get back.
# q="sculpture" means we want anything where sculpture appears in the data.
# on_display_at="southken" means only items physically on display at V&A South Kensington.
BASE_PARAMS = {
    "q": "sculpture",
    "on_display_at": "southken",
}


def get_total_pages() -> tuple[int, int]:
    """
    Ask the V&A API how many records match our search
    and how many pages we need to download.

    This is like asking the website
    “How many total results are there for this search”  
    and  
    “How many pages of results would I need to click through”.

    We need this so that our loop knows when to stop.
    """

    print("Finding out how many pages of sculpture records exist...")

    params = BASE_PARAMS.copy()
    params["page_size"] = PAGE_SIZE

    # Ask the API for information in JSON format.
    response = requests.get(BASE_URL, params=params, timeout=20)

    # If something went wrong with the request we stop immediately.
    if response.status_code != 200:
        print("The API did not accept our request")
        print("URL:", response.url)
        print("Status:", response.status_code)
        print("Body:", response.text[:300])
        raise SystemExit("Cannot continue because the API returned an error")

    data = response.json()
    info = data["info"]

    total_records = info["record_count"]
    total_pages = info["pages"]

    print(f"The API reports {total_records} records across {total_pages} pages")

    return total_pages, total_records


def fetch_page_as_dataframe(page_number: int) -> pd.DataFrame:
    """
    Download one page of sculpture records as CSV and
    convert it into a pandas DataFrame.

    This is the part that replaces manually pressing
    “download CSV” on each page of the website.

    We set response_format=csv which tells the API
    to give us a CSV file instead of JSON.
    """

    print(f"Downloading page {page_number}...")

    params = BASE_PARAMS.copy()
    params.update(
        {
            "page_size": PAGE_SIZE,
            "page": page_number,
            "response_format": "csv",
        }
    )

    response = requests.get(BASE_URL, params=params, timeout=20)

    if response.status_code != 200:
        print(f"The API returned an error for page {page_number}")
        print("URL:", response.url)
        print("Status:", response.status_code)
        print("Body:", response.text[:300])
        raise SystemExit("Stopping because the page download failed")

    # The API gives us a long text string containing CSV data.
    csv_text = response.text

    # Read the CSV text into pandas.
    df = pd.read_csv(StringIO(csv_text))

    print(f"Page {page_number} has {len(df)} rows")

    return df


def main() -> None:
    """
    Main driver function.

    Steps:
    1. Ask the API how many pages exist.
    2. Loop through every page and download it.
    3. Combine all the pages into one DataFrame.
    4. Remove occasional duplicates based on systemNumber.
    5. Save the full dataset as a single CSV.

    This gives one clean file containing every sculpture record
    on display at V&A South Kensington.
    """

    print("Starting script...")

    total_pages, total_records = get_total_pages()

    all_frames = []

    # Loop from page 1 up to the final page.
    # Each page gets downloaded and added to a list.
    for page in range(1, total_pages + 1):
        df_page = fetch_page_as_dataframe(page)
        all_frames.append(df_page)

    # Combine all downloaded pages into one DataFrame.
    combined = pd.concat(all_frames, ignore_index=True)

    # systemNumber is the V&A's unique ID for each object.
    # If we find duplicates we remove them so the dataset is clean.
    if "systemNumber" in combined.columns:
        before = len(combined)
        combined = combined.drop_duplicates(subset="systemNumber")
        after = len(combined)
        print(f"Removed {before - after} duplicate rows")

    print(f"Final dataset contains {len(combined)} rows")

    output_name = "va_full_results_sculpture_display.csv"
    combined.to_csv(output_name, index=False)

    print(f"All records saved to {output_name}")
    print("Done.")


if __name__ == "__main__":
    main()
