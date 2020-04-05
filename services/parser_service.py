from bs4 import BeautifulSoup
import pandas as pd

class ParserService:

    @staticmethod
    def format_table_header_column(th):
        """
        Parses a raw HTML table header column and returns formatted string

        @Params:
        th (string): TableHeader column from countries table

        @Returns:
        Table header as string
        """

        header = " ".join(th.strings)  # join strings broken by <br> tags
        # replace non-breaking space with space and remove \n
        header = header.replace(u"\xa0", u" ").replace("\n", "") 
        return header.replace(", ", "/")


    @staticmethod
    def create_df_worldometer(raw_data):
        """
        Parses the raw HTML response from Worldometer and returns a DataFrame from it

        @Params:
        raw_data (string): request.text from Worldometer

        @Returns:
        DataFrame
        """

        soup = BeautifulSoup(raw_data, features="html.parser")

        countries_table = soup.find("table", attrs={"id": "main_table_countries_today"})
        countries_table_yesterday = soup.find("table", attrs={"id": "main_table_countries_yesterday"})

        columns = [ParserService.format_table_header_column(th) for th
                   in countries_table.find("thead").findAll("th")]
        columns.append('New Recovered')

        parsed_data = []

        def sort_alphabetically(item):
            country_name = item.findAll("td")[0].get_text().replace("\n", "")
            return country_name

        country_rows = countries_table.find("tbody").find_all("tr")
        country_rows.sort(key = sort_alphabetically)
        country_rows_yesterday = countries_table_yesterday.find("tbody").find_all("tr")
        country_rows_yesterday.sort(key = sort_alphabetically)

        for country_row, country_row_yesterday in zip(country_rows, country_rows_yesterday):
            append_data = [data.get_text().replace("\n", "") for data in country_row.findAll("td")]

            if country_row.findAll("td")[5].get_text().replace("\n", "").replace(",", ""):
                today_recovered = int(country_row.findAll("td")[5].get_text().replace("\n", "").replace(",", ""))
            else:
                today_recovered = 0

            if country_row_yesterday.findAll("td")[5].get_text().replace("\n", "").replace(",", ""):
                yesterday_recovered = int(country_row_yesterday.findAll("td")[5].get_text().replace("\n", "").replace(",", ""))
            else:
                yesterday_recovered = 0

            new_recovered = today_recovered - yesterday_recovered

            append_data.append('{:,}'.format(new_recovered))            
            parsed_data.append(append_data)
        
        df = pd.DataFrame(parsed_data, columns=columns)
        return df.replace(to_replace=[""], value=0)

    @staticmethod
    def parse_last_updated(raw_data):
        """
        Parses the raw HTML response from Worldometer and returns the lastest update time from the webpage

        @Params:
        raw_data (string): request.text from Worldometer

        @Returns:
        Last updated time (string)
        """
        
        soup = BeautifulSoup(raw_data, features="html.parser")

        last_updated = soup.find("div", {"style": "font-size:13px; color:#999; text-align:center"})
        
        return last_updated.text
