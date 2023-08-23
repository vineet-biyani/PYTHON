from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from urllib.parse import unquote
import pandas as pd
import random


class AmazonScraper:
    def __init__(self) -> None:
        self.hrefs = []
        self.session = HTMLSession()
        with open("U_A.txt", "r") as file:
            values_list = file.readlines()
        values_list = [value.strip() for value in values_list]
        self.user_agents = values_list

    def initiate_selenium_driver(self) -> webdriver:
        """This function will return a selenium driver."""
        co = Options()
        # co.add_argument('headless')
        # co.add_argument('--disable-gpu')
        co.add_argument('--disable-infobars')
        co.add_argument(f'--user-agent={random.choice(self.user_agents)}')
        co.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        co.incognito = True
        co.headless = False
        web_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=co)
        web_driver.implicitly_wait(5)
        return web_driver

    @staticmethod
    def search_results(driver, base_url, search_term) -> None:
        """This function will show you the desired search results."""
        driver.get(base_url)
        driver.maximize_window()
        search_bar = driver.find_element(by=By.ID, value='twotabsearchtextbox')
        search_bar.send_keys(search_term)
        search_bar.send_keys(Keys.RETURN)

    def paginator(self, driver, page_limit) -> None:
        """This function surfs through all the pages within the page limit provided, to get all the product links."""
        x = 0
        while x < page_limit:
            self.product_link_scraper(driver)
            is_page_available = self.next_page(driver)
            if not is_page_available:
                break
            x += 1
            time.sleep(2)
            break

    def product_link_scraper(self, driver) -> None:
        """This function scrapes all the product links."""
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        divs = soup.find('div', {'class': 's-main-slot'}).findAll("div", {"class": "template=SEARCH_RESULTS"})
        for div in divs:
            h_ref = div.h2.find('a', {'class': 'a-link-normal'}).get('href', None)
            if h_ref:
                h_ref = unquote(h_ref)
                if "url=" in h_ref:
                    h_ref = h_ref.split("url=")[1]
                self.hrefs.append(h_ref.split("ref=")[0])

    @staticmethod
    def next_page(driver) -> bool:
        """This function checks if pagination is possible or not and then loads the next page."""
        is_next_page = True
        try:
            pager = driver.find_element(by=By.CLASS_NAME, value='s-pagination-next')
        except:
            is_next_page = False
            print("No pages left...")
        else:
            pager.click()
        finally:
            return is_next_page

    def product_data_scraper(self, base_url) -> list:
        """This function makes a request to each product page and scrapes the product information
        and finally returns the list of data of all the products."""
        final_data_list = []
        for href in self.hrefs:
            req_limit = 0
            product_url = base_url + href
            while req_limit < 10:
                time.sleep(10)
                headers = {
                    'user-agent': random.choice(self.user_agents),
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,'
                              '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
                }
                res = self.session.get(product_url, headers=headers)
                soup = BeautifulSoup(res.content, "html.parser")
                div = soup.find("div", {'id': 'titleBlockRightSection'})
                if div:
                    product_name = self.get_product_name(div)
                    product_rating, product_reviews = self.get_product_ratings_and_reviews(div)
                    product_price = self.get_product_price(soup)
                    product_asin = self.get_product_asin(soup)
                    product_description = self.get_product_description(soup)
                    product_manufacturer = self.get_product_manufacturer(soup)
                    final_data_list.append([product_url, product_name, product_price, product_rating, product_reviews,
                                            product_asin, product_description, product_manufacturer])
                    break
                req_limit += 1
        self.session.close()
        return final_data_list

    @staticmethod
    def get_product_name(div) -> str:
        """This function returns the product title."""
        title_div = div.find("div", {'id': "titleSection"})
        product_name = title_div.find('span', {'id': "productTitle"}).text.strip()
        return product_name

    @staticmethod
    def get_product_ratings_and_reviews(div) -> (str, str):
        """This function returns the number of reviews present and overall product rating."""
        rating_div = div.find("div", {'id': "averageCustomerReviews_feature_div"})
        rating_span = rating_div.find("span", {'class': 'reviewCountTextLinkedHistogram'}).find("span").\
            find("a").find("span")
        review_span = rating_div.find('span', {'id': 'acrCustomerReviewText'})
        product_rating = rating_span.text.strip()
        product_reviews = review_span.text.split("rating")[0].strip()
        return product_rating, product_reviews

    @staticmethod
    def get_product_price(soup) -> str:
        """This function returns the product price."""
        price_div = soup.find("div", {'id': 'corePriceDisplay_desktop_feature_div'})
        price_span = price_div.find("span", {'class': "priceToPay"})
        product_price = price_span.span.text.strip()
        return product_price

    @staticmethod
    def get_product_asin(soup) -> str:
        """This function returns the product ASIN."""
        asin_element = soup.find(attrs={"data-asin": True})
        product_asin = asin_element["data-asin"]
        return product_asin

    @staticmethod
    def get_product_description(soup) -> str:
        """This function checks if product description is present or not and returns it."""
        product_description = ""
        try:
            paragraph = soup.find('div', {'id': 'productDescription_feature_div'}).\
                find("div", {'id': 'productDescription'}).p
            if paragraph is not None:
                product_description = paragraph.text.strip()
        except Exception as e:
            print(str(e))
        return product_description

    @staticmethod
    def get_product_manufacturer(soup) -> str:
        """This function returns the manufacturer name of the particular product."""
        product_manufacturer = ""
        try:
            detail_div = soup.find('div', {'id': 'detailBulletsWrapper_feature_div'}).\
                find('div', {'id': 'detailBullets_feature_div'})
            lis = detail_div.find('ul', {'class': 'detail-bullet-list'}).findAll("li")
            for li in lis:
                spans = li.span.findAll('span')
                if "Manufacturer" in spans[0]:
                    product_manufacturer = spans[1].text.strip()
        except Exception as e:
            print(str(e))
        return product_manufacturer

    @staticmethod
    def save_data_to_csv(csv_file_path, column_names, final_data_list) -> None:
        """This function will create a csv of the final data after scraping. The file will be generated the
        same place where code files are present."""
        df = pd.DataFrame(final_data_list, columns=column_names)
        df.to_csv(csv_file_path, index=False)
        print("CSV File Created...")
