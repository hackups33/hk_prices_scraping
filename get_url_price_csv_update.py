import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

df = pd.read_csv("router_price.csv")
check_row = 0

for row in df.iterrows():
    model = df.at[check_row,'model'].replace(" ","+")

    # Search the product

    url = "https://www.price.com.hk/search.php?g=A&q="+model
    print (url)
    response = requests.get(url)

    soup = BeautifulSoup (response.text,'html.parser')

    # Get the product title
    try:
        find_title = soup.find(text=re.compile("product name")).previous_element.previous_sibling
        print (find_title)

        title = find_title.text
        print (str(title))
    except:
        print (model + "search by title but not found")
        check_row = check_row + 1
        continue

    # Get the product url

    print ("find_title convert to string: ", str(find_title))
    product_id = re.search('product.php(.*)&amp;tr_so=', str(find_title))
    print (product_id.group(1))
    product_url = "https://www.price.com.hk/product.php"+product_id.group(1)
    print (product_url)


    # write product title and url to df
    df.at[check_row,'url_title'] = title
    df.at[check_row,'url'] = product_url

    print (df)

    # call get_price.py to get the 9 price of product
    response = requests.get(product_url)
    soup = BeautifulSoup (response.text,'html.parser')

    try:

        hong_img = soup.find(class_="hong_20")
        print ("main hong img span: ",hong_img)

        main_price_span = hong_img.previous_element.previous_sibling
        print ("main hong price span: ",main_price_span)
    except:
        print (model + "no hong price is found")
        check_row = check_row + 1
        continue

    count = 0

    while count < 9:
        try:
            hong_img = hong_img.find_next(class_="hong_20")
            print ("1st hong img span: ",hong_img)

            price_span1 = hong_img.previous_element.previous_sibling.find('span',class_="text-price-number")
            print (count, " hong price span: ",price_span1)
            price_span_soup = BeautifulSoup (str(price_span1),'html.parser')
            price = price_span_soup.find("span",{"class":"text-price-number"})['data-price']
            print (price)

            col_name = "price_"+str(count+1)

            df.at[check_row, col_name] = price

            count = count + 1

        except:
            count = count + 1
            print ("no price find at " + str(count) + "trial")
    check_row = check_row +1
    print (df)
    time.sleep(10)
filename_prefix = input ('Enter filename prefix (brand e.g.): ')
df.to_csv (str(filename_prefix+'_'+'router_hk_price_updated.csv'),index=False,header=True)
print (filename_prefix + " HK Price Update Mission Completed")
