from bs4 import BeautifulSoup
import pandas as pd
import re


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
        country_rows.sort(key=sort_alphabetically)
        country_rows_yesterday = countries_table_yesterday.find("tbody").find_all("tr")
        country_rows_yesterday.sort(key=sort_alphabetically)
        regex = r'(\n|\+|,)'

        def filter_by_value(seq, value):
            for el in seq:
                if el.findAll("td")[0].get_text() == value:
                    return el

        for country_row in country_rows:
            # print('country_row', country_row['style'])
            # if country_row['style'] and country_row['style'] is 'display: none':
            #     return  

            append_data = [re.sub(regex, "", data.get_text()) for data in country_row.findAll("td")]

            # print('country_row.findAll("td")[0].get_text():', country_row.findAll("td"))

            today_class_name = re.sub(regex, "", country_row.findAll("td")[0].get_text())

            if today_class_name is '':
                continue

            same_row = filter_by_value(country_rows_yesterday, today_class_name)

            # print('for country_row in country_rows:', '<<', today_class_name, '>>')

            if same_row:
                today_recovered_elem = re.sub(regex, "", country_row.findAll("td")[5].get_text())
                if today_recovered_elem and today_recovered_elem != 'N/A':
                    today_recovered = int(today_recovered_elem)
                else:
                    today_recovered = 0

                yesterday_recovered_elem = re.sub(regex, "", same_row.findAll("td")[5].get_text())
                if yesterday_recovered_elem and yesterday_recovered_elem != 'N/A':
                    yesterday_recovered = int(yesterday_recovered_elem)
                else:
                    yesterday_recovered = 0

                # print(country_row.findAll("td")[0].get_text(), today_recovered, yesterday_recovered)
                new_recovered = today_recovered - yesterday_recovered
            else:
                # print(country_row.findAll("td")[0].get_text(), 'no old data')
                new_recovered = 0

            append_data.append(new_recovered)
            parsed_data.append(append_data)

        df = pd.DataFrame(parsed_data, columns=columns)
        return df.replace(to_replace=[""], value=0)

    @staticmethod
    def create_df_worldometer_by_day(raw_data, id):
        """
        Parses the raw HTML response from Worldometer and returns a DataFrame from it
        @Params:
        raw_data (string): request.text from Worldometer
        @Returns:
        DataFrame
        """

        soup = BeautifulSoup(raw_data, features="html.parser")

        countries_table = soup.find("table", attrs={"id": id})

        columns = [ParserService.format_table_header_column(th) for th
                   in countries_table.find("thead").findAll("th")]

        del columns[0]

        parsed_data = []

        def sort_by_total_confirmed(item):
            return int(item[1])

        country_rows = countries_table.find("tbody").find_all("tr")

        regex = r'(\n|\+|,)'

        for country_row in country_rows:
            appended_data = [re.sub(regex, "", data.get_text().strip()) for data
                                in country_row.findAll("td")]
            del appended_data[0]
            parsed_data.append(appended_data)

        parsed_data.sort(key=sort_by_total_confirmed, reverse=True)

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

        _styles = "font-size:13px; color:#999; margin-top:5px; text-align:center"

        last_updated = soup.find("div", {"style": _styles})

        return last_updated.text
