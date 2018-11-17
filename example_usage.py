from share_dividends import ShareDividends
dividends = ShareDividends()

# Get dividends for a single stock
dividends.parse("VAS")

# Get dividends for many stocks
banks = ["CBA","ANZ","NAB","WBC"]
dividends = ShareDividends()

# In serial
dividends.parse(banks)
# or with multi-threading
dividends.parse(banks, multi_thread=True, nthreads=4)