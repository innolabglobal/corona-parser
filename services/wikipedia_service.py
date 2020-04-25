from bs4 import BeautifulSoup
import requests
import os
import codecs
import re


class WikipediaService:

    @staticmethod
    def get_table():
        regex = r'\[.*\]$'
        wiki = "https://en.wikipedia.org/wiki/National_responses_to_the_2019%E2%80%9320_coronavirus_pandemic"
        header = {
            'User-Agent': 'Mozilla/5.0'
        }  # Needed to prevent 403 error on Wikipedia
        page = requests.get(wiki, headers=header)
        soup = BeautifulSoup(page.content, features="html.parser")

        tables = soup.findAll("table", {"class": "wikitable"})

        # show tables
        for i, table in enumerate(tables):
            print("#" * 10 + "Table {}".format(i) + '#' * 10)
            print(table.text[:100])
            print('.' * 80)
        print("#" * 80)

        for tn, table in enumerate(tables):

            # pre init list of lists
            rows = table.findAll("tr")
            row_lengths = [len(r.findAll(['th', 'td'])) for r in rows]
            n_cols = max(row_lengths)
            n_rows = len(rows)
            data = []
            for i in range(n_rows):
                row_d = []
                for j in range(n_cols):
                    row_d.append('')
                data.append(row_d)

            # process html
            for i in range(len(rows)):
                row = rows[i]
                row_d = []
                cells = row.findAll(["td", "th"])
                for j in range(len(cells)):
                    cell = cells[j]

                    # lots of cells span cols and rows so lets deal with that
                    c_span = int(cell.get('colspan', 1))
                    r_span = int(cell.get('rowspan', 1))
                    length = 0
                    for k in range(r_span):
                        # Shifts to the first empty cell of this row
                        while data[i + k][j + length]:
                            length += 1
                        for m in range(c_span):
                            cell_n = j + length + m
                            row_n = i + k
                            # in some cases the colspan can overflow the table, in those cases just get the last item
                            cell_n = min(cell_n, len(data[row_n]) - 1)
                            clean_text = re.sub(regex, "", cell.text)

                            clean_text = clean_text.strip() or ' '
                            data[row_n][cell_n] += clean_text
                            # print(clean_text.encode('utf-8'))

                data.append(row_d)

            # write data out to tab separated format
            # page = os.path.split(wiki)[1]
            file_name = 'lockdown.csv'
            f = codecs.open(file_name, 'w', encoding='utf-8')
            for i in range(n_rows):
                if i == 0:
                    continue

                if i == (n_rows - 1):
                    continue

                row_str = ','.join(data[i])
                row_str = row_str.replace('\n', '')
                # print(row_str.encode('utf-8'))
                f.write(row_str + '\n')

            f.close()
