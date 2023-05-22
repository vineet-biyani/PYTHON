from bs4 import BeautifulSoup
import requests
import csv

fname = input("Enter file name: ")
if len(fname) < 1 :
    fname = 'brownells.txt'
fhandle = open(fname)

name_list = dict()

for url in fhandle :
    if url.startswith('https') :
        url = url.strip()
        urlhandle = requests.get(url).text
        soup = BeautifulSoup(urlhandle, 'html.parser')
        spans = soup('span', {'itemprop' : 'name'})
        tags = soup('span', {'itemprop' : 'availability'})
        if len(spans) > 0 and len(tags) > 0 :
            for span in spans :
                for tag in tags :
                    if 'unavailable' in tag.text or 'Alternatives' in tag.text or 'Out of Stock' in tag.text :
                        name_list[span.text] = 'Out of Stock'
                    elif 'Pre-Order' in tag.text :
                        name_list[span.text] = 'Pre-Order'
                    else :
                        name_list[span.text] = 'In Stock'
                    tags.remove(tag)
                    break
        else :
            spans = soup.findAll('h1', {'class' : 'mbm'})
            tags = spans[0].findAll('span')
            full_name = tags[-1]
            name_list[full_name.text.replace('\r\n','').strip()] = 'Out of Stock'

file_name = 'main.csv'

fields = ['Product Title', 'Stock Status']

rows = name_list.items()

with open(file_name, 'w') as csvfile :
    writer = csv.writer(csvfile)
    writer.writerow(fields)
    writer.writerows(rows)
