import requests
from bs4 import BeautifulSoup
from discord import hook
from googletrans import Translator

translator = Translator()

webhook = 'YOUR_DISCORD_WEBHOOK_LINK'

header = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}

product_id = ['160444','188097','175205','175204','187846','187828','194081','194046','187824']

serviceurl = 'https://www.innvictus.com/hombres/basket/calzado/jordan/tenis-air-jordan-1-low-triple-white/p/000000000000'

website = 'https://www.innvictus.com'


for id in product_id :
    url = serviceurl + id
    urlhandle = requests.get(url, headers = header).text
    soup = BeautifulSoup(urlhandle, 'html.parser')
    product_title = soup.find('h1', {'id' : 'productNameMobile'}).text
    price_tag = soup.find('div', {'class' : 'prices-block'}).text.replace('\n','').strip().split()
    price = price_tag[0][1:]
    img_tag = soup.find('img', {'alt' : product_title})
    image_url = website + img_tag.get('src',None)
    category_tag = soup.find('div', {'id' : 'promoFlagSection'})
    if len(category_tag.text.split()) > 0 :
        category = translator.translate(category_tag.text.replace('\r\n','').strip(), dest="en").text
    else :
        category = 'Normal'

    model_tag = soup.find('p', {'id' : 'productModel'}).text.split()
    model = model_tag[1]

    text_link = []

    ul = soup.find('ul', {'class' : 'product-size__list'})
    li = ul.findAll('li', {'class', 'product-size__option-wrapper'})
    for i in range(0, len(li)) :
        a = li[i].find('a')
        text = a.text.replace('\r\n','').strip()
        link = a.get('class',None)
        if len(link) == 1 :
            text_link.append((text,'A'))
        else :
            if 'no-stock' in link[1] :
                text_link.append((text,'N'+'/'+'A'))
            elif 'selected' in link[1] :
                text_link.append((text,'A'))

    if all(tup[1] == 'N'+'/'+'A' for tup in text_link) :
        stock_status = 'N'+'/'+'A'
    else :
        stock_status = 'A'

    size_stock = ''

    for tup in text_link :
        size_stock += tup[0] + ' ' + '-->' + ' ' + tup[1] + '\n'

    color_content = soup.find('div', {'class' : 'product-colorways__content'})
    color_tag = color_content.findAll('li', {'class' : 'product-colorways__item'})
    if len(color_tag) > 1 :
        colors = 'A'
    else :
        colors = 'N'+'/'+'A'

    hook(product_title, image_url, url, website, category, price, model, stock_status, size_stock, colors)
