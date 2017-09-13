import lxml.html
import requests
import time

url = 'http://www.bvv-online.de/index.php?site=1&sid=&uid=&navid=105&info=on&spiele=gespielt'
page = requests.get(url)
tree = lxml.html.fromstring(page.content)
tables = tree.xpath('/html/body/table/tr/td[1]/table/tr[3]/td/table/tr[2]/td/table/tr/td[2]/table[5]/tr[3]/td/table')
table = None
if len(tables) != 1:
    print("Parser doesnt work; more than one table found")
else:
    table = tables[0]
date = None
for i, tr in enumerate(table.xpath(".//tr")):
    text = tr.text_content().strip()
    # print(text+'    ' + str(len(text)))
    # Is it a date row?
    if len(text) == 10:
        print(' A date at line ' + str(i) + ': ' + text)
        try:
            date = time.strptime(text, '%d.%m.%Y')
        except ValueError:
            print('Could not parse a date row')
    cols = table.xpath(".//tr[{}]/td".format(i))
    # is it a result row?
    if len(cols) == 8:
        print('size cols {0}'.format(str(len(cols))))
        gameNumber = table.xpath(".//tr[{}]/td[2]".format(i))[0].text_content().strip()
        teamA = table.xpath(".//tr[{}]/td[4]".format(i))[0].text_content().strip()
        teamB = table.xpath(".//tr[{}]/td[6]".format(i))[0].text_content().strip()
        result = table.xpath(".//tr[{}]/td[7]".format(i))[0].text_content().strip()
        remark = table.xpath(".//tr[{}]/td[8]".format(i))[0].text_content().strip()
        if (date is not None) & \
                (teamA is not None) & (teamA != "") & \
                (teamB is not None) & (teamB != "") & \
                (result is not None) & (result != ""):
            print('found a result')
