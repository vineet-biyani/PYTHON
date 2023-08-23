from AmazonScraper import AmazonScraper

BASE_URL = 'https://www.amazon.in'
SEARCH_TERM = "bags"
PAGE_LIMIT = 20
COLUMN_NAMES = ["PRODUCT_URL", "PRODUCT_NAME", "PRODUCT_PRICE", "RATING", "NO_OF_REVIEWS", "ASIN",
                "PRODUCT_DESCRIPTION", "MANUFACTURER"]
CSV_FILE_PATH = "AmazonProductInfo.csv"

amazon_scraper = AmazonScraper()
driver = amazon_scraper.initiate_selenium_driver()
amazon_scraper.search_results(driver, BASE_URL, SEARCH_TERM)
amazon_scraper.paginator(driver, PAGE_LIMIT)
driver.quit()

final_data_list = amazon_scraper.product_data_scraper(BASE_URL)
amazon_scraper.save_data_to_csv(CSV_FILE_PATH, COLUMN_NAMES, final_data_list)
