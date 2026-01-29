# V&A Sculpture Data Download Script

This folder contains my script for downloading sculpture objects from the V&A Collections API. I used this to reproduce the same search I first did on the V&A website, but at scale, without needing to manually download CSV files page by page.

## What the script does

The script `va_sculpture_download.py` automates the following steps:

1. **Recreates my website search using the API**
   - Search term: `sculpture`
   - Filter: items on display at V&A South Kensington (`on_display_at=southken`)

2. **Asks the API how many results there are**
   - It makes a JSON request to find out the total number of objects and how many pages we need to fetch.

3. **Downloads each page as CSV**
   - The V&A API supports `response_format=csv`
   - I set `page_size=100` because this is the maximum allowed
   - The script loops from page 1 to the final page

4. **Loads each page into pandas**
   - Each CSV is read into a DataFrame
   - All pages are combined into one large DataFrame

5. **Removes any duplicates**
   - Uses the `systemNumber` field (the V&A unique object ID)

6. **Saves one complete combined file**
   - The final output is saved as  
     `va_full_results_sculpture_display.csv`  
   - This appears in the **project root** folder, not inside this folder

## Why I wrote this

The V&A website lets you download only one page of results at a time. My search returned many pages of sculpture objects. The API provides the same information in a structured and machine readable way, so the script allows me to fetch all records in one go, which is faster and more reproducible for my group project.

## How to run the script

From the **root of the repository**, not inside this folder:

```bash
python nicky_va_api/va_sculpture_download.py
```

You will see progress messages such as:
- Getting total number of records and pages from the V&A API
- Requesting page X from the V&A API
- Downloaded page X with Y rows
- After combining pages there are Z rows in total
- Saved all results to va_full_results_sculpture_display.csv

The combined CSV will appear in the root of the repository (*Museum_Project/*)


## API documentation used

I followed the official V&A Collections API documentation:

- API introduction
https://developers.vam.ac.uk/guide/v2/welcome.html

- Searching with q
https://developers.vam.ac.uk/guide/v2/search/introduction.html

- Filtering including on_display_at
https://developers.vam.ac.uk/guide/v2/filter/introduction.html

- CSV output format
https://developers.vam.ac.uk/guide/v2/results/introduction.html

These pages explain the structure of the API, how text search works, how to apply filters, and how to request CSV output.

## Notes for the group

- The script uses standard libraries (requests, pandas).
- The script also uses `StringIO` to treat the CSV text returned by the API as if it were a file, which allows pandas to read it directly without saving a temporary file.
- It doesn't scrape the website. It uses the official V&A API.
- The code includes clear comments so you can see which part of the API if being used and why.
- You can adapt the search parameters if we later choose a different object type or venue. 
