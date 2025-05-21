import undetected_chromedriver as uc

class BinanceExchange:
    def __init__(self, url):
        self.url = url
        self.driver = uc.Chrome(headless=True)

    def get_page_html(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        html = self.driver.page_source
        print(html[:10000])  # Print part of the HTML
        self.driver.quit()


if __name__ == "__main__":
    url = "https://www.binance.com/en/support/announcement/c-48"
    BinanceExchange(url).get_page_html()
