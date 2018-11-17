import pandas as pd
import requests
from bs4 import BeautifulSoup
import bs4
import warnings
import concurrent.futures


class ShareDividends:
    """
    Parses dividend data as provided by http://www.sharedividends.com.au

    TODO:
        - Add tests
        - Add exception handling
    """

    def parse(self, ticker: str or list, multi_thread = False, nthreads = 2):
        """Primary method to orchestrate collection of dividend data
        
        Args:
            ticker (str or list): The ticker symbol or symbols to collect

        Returns:
            pandas.core.frame.DataFrame: Final Pandas dataframe containing all the dividend data
        """

        # Handle single ticker provided
        if isinstance(ticker, str):
            return self.get_dividend_data(ticker)

        elif isinstance(ticker, list):
            if multi_thread == True:
                results_list = self.multi_thread(ticker, nthreads)
            else:
                results_list = [self.get_dividend_data(x) for x in ticker]
            
            return pd.concat(results_list)


    def multi_thread(self, ticker_list: list, nthreads: int) -> list:
        """Calls the get_dividend_data method across multiple threads
        
        Args:
            ticker_list (list): List of ticker symbols to collect
            nthreads (int): Number of threads to use

         Returns:
            list: List of dataframes returned by get_dividend_data
        """

        with concurrent.futures.ThreadPoolExecutor(max_workers = nthreads) as executor:
            out = {
                executor.submit(self.get_dividend_data, ticker):
                    ticker for ticker in ticker_list
                    }

            result_set = []
            for future in concurrent.futures.as_completed(out):
                try:
                    result_set.append(future.result())
                except Exception as ex:
                    print(ex)

        return result_set
  

    def get_dividend_data(self, ticker: str) -> pd.core.frame.DataFrame:
        """Orchestrator that runs to the steps to scrape the dividend data for a given stock
        
        Args:
            ticker (str): ASX ticker symbol
        
        Returns:
            pandas.core.frame.DataFrame: Pandas dataframe containing the dividend data
        """

        # 1. Make site searchable using beautiful soup
        soup = self.get_ticker_page(ticker)

        # 2. Isolate dividends table
        table = soup.find('table')

        # 3. Extract data & return a nice table
        col_names = self.get_column_names(table)
        raw_rows = self.parse_table(table)
        results = pd.DataFrame(raw_rows, columns = col_names)
        results['symbol'] = ticker

        return results


    def get_ticker_page(self, ticker: str) -> bs4.BeautifulSoup:
        """Downloads the raw dividend page data for the ticker provided
        
        Args:
            ticker (str): ASX ticker symbol

        Returns:
            bs4.BeautifulSoup: Deserialised page as beautiful soup object
        """

        base_url = "http://www.sharedividends.com.au/"
        full_url = base_url + ticker
        page = requests.get(full_url)

        return BeautifulSoup(page.content, 'html.parser')


    def get_column_names(self, table: bs4.element.Tag) -> list:
        """Identifes & returns table header
        
        Args:
            table (bs4.element.Tag): Table object containing dividends data
        
        Returns:
            list: Table header names
        """

        header = table.find('thead')
        if header is not None:
            return [x.text.lower().replace(' ','_') for x in header.find_all('th')]
        else:
            warnings.warn("Headers not found.", Warning)


    def parse_table(self, table: bs4.element.Tag) -> list:
        """Parses the dividend data table, stripping out the desired info
        
        Args:
            table (bs4.element.Tag): Table object containing dividends data
        
        Returns:
            list: List of lists, with each containing the scraped divident data
        """
        row_data = []
        table_rows = table.find_all('tr')
        if table_rows is not None:
            for row in table_rows:
                row = [x.text.replace('\r','') for x in row.find_all('td')]
                if len(row) > 0:
                    row_data.append(row)
            return row_data
        else:
            warnings.warn("Table contains no data.", Warning)
