# Share Dividend Scraper

Python utility to scrape ASX listed share dividends from http://www.sharedividends.com.au 

## Example Usage

First install required packages:
``` bash
pip install -r requirements.txt
```

Dividends for just `VAS`
``` python
from share_dividends import ShareDividends

dividends = ShareDividends()
dividends.parse("VAS")
```

Dividends for big 4 banks
``` python
from share_dividends import ShareDividends

banks = ["CBA","ANZ","NAB","WBC"]
dividends = ShareDividends()
dividends.parse(banks)

# or with multi-threading
dividends.parse(banks, multi_threading=True, nthreads=4)
```