import lxml.html
import requests
import time
import sqlite3
import pandas as pd


def setup_db(dbpath='bvv_example_db.db'):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE matches
                 (gameNo int, teamA text, teamB text, setsA int, setsB int, date date, remark text)''')
    conn.commit()
    conn.close()


def get_wins(teamname, dbpath='bvv_example_db.db'):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    rows = c.execute('SELECT * FROM matches WHERE (teamA = ? AND (setsA > setsB)) OR (teamB = ? AND (setsB > setsA))', (teamname, teamname, ))
    i = 0
    for row in rows:
        i += 1
        print(row)
    conn.commit()
    conn.close()
    #print(str(pd.DataFrame(rows)))
    return i


def parse_url_and_update_db(url='http://www.bvv-online.de/index.php?site=1&sid=&uid=&navid=105&info=on&spiele=gespielt',
                            dbpath='bvv_example_db.db'):
    page = requests.get(url)
    tree = lxml.html.fromstring(page.content)
    tables = tree.xpath('/html/body/table/tr/td[1]/table/tr[3]/td/table/tr[2]/td/table/tr/td[2]/table[5]/tr[3]/td/table')
    table = None
    if len(tables) != 1:
        print("Parser doesnt work; more than one table found")
    else:
        table = tables[0]
    date = None
    foundDates = 0
    foundMatches = 0
    inserted = 0
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    for i, tr in enumerate(table.xpath(".//tr")):
        text = tr.text_content().strip()
        # print(text+'    ' + str(len(text)))
        # Is it a date row?
        if len(text) == 10:
            # print(' A date at line ' + str(i) + ': ' + text)
            try:
                date = time.strptime(text, '%d.%m.%Y')
                foundDates += 1
            except ValueError:
                print('Could not parse a date row')
        cols = table.xpath(".//tr[{}]/td".format(i))
        # is it a result row?
        if len(cols) == 8:
            # print('size cols {0}'.format(str(len(cols))))
            gameNumber = table.xpath(".//tr[{}]/td[2]".format(i))[0].text_content().strip()
            teamA = table.xpath(".//tr[{}]/td[4]".format(i))[0].text_content().strip()
            teamB = table.xpath(".//tr[{}]/td[6]".format(i))[0].text_content().strip()
            result = table.xpath(".//tr[{}]/td[7]".format(i))[0].text_content().strip()
            remark = table.xpath(".//tr[{}]/td[8]".format(i))[0].text_content().strip()
            if (date is not None) & \
                    (teamA is not None) & (teamA != "") & \
                    (teamB is not None) & (teamB != "") & \
                    (result is not None) & (result != ""):
                foundMatches += 1
                iso8601 = time.strftime("%Y-%m-%dT%H:%M:%S", date)
                values = (int(gameNumber), teamA, teamB, int(result[0]), int(result[len(result)-1]),
                          iso8601, remark)
                if values not in c.execute('SELECT * FROM matches'):
                    c.execute('INSERT INTO matches VALUES (?,?,?,?,?,?,?)', values)
                    inserted += 1

    conn.commit()
    conn.close()
    print('Found {0} matches from {1} dates. Inserted {2} into db'.format(foundMatches, foundDates, inserted))


if __name__ == '__main__':
    #setup_db()
    #parse_url_and_update_db()
    get_wins("Werderaner VV 1990")
