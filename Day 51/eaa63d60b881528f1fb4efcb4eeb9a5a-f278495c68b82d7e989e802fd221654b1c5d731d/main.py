from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

PROMISED_DOWN = 1000
PROMISED_UP = 1000
Y_EMAIL = "your_email"
Y_PASSWORD = "copy_password_from_y_admin_dashboard"
Y_LOGIN_URL = "https://app.100daysofpython.dev/services/y/login"


class InternetSpeedYBot:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.down = 0
        self.up = 0

    def get_internet_speed(self):
        self.driver.get("https://www.speedtest.net/")
        time.sleep(3)
        self.driver.find_element(By.CSS_SELECTOR, value=".start-button a").click()
        time.sleep(60)
        self.down = self.driver.find_element(By.CSS_SELECTOR, value=".download-speed").text
        self.up = self.driver.find_element(By.CSS_SELECTOR, value=".upload-speed").text

    def tweet_at_provider(self):
        self.driver.get(Y_LOGIN_URL)
        time.sleep(2)

        self.driver.find_element(By.NAME, value="username").send_keys(Y_EMAIL)
        password = self.driver.find_element(By.NAME, value="password")
        password.send_keys(Y_PASSWORD)
        password.send_keys(Keys.ENTER)

        time.sleep(3)
        tweet_compose = self.driver.find_element(By.CSS_SELECTOR, value='div[aria-label="Post text"]')
        tweet = f"Hey Internet Provider, why is my speed {self.down}down/{self.up}up when I pay for {PROMISED_DOWN}down/{PROMISED_UP}up?!"
        tweet_compose.send_keys(tweet)

        time.sleep(2)
        tweet_button = self.driver.find_element(By.CSS_SELECTOR, value='.x-compose-form button')
        tweet_button.click()

        time.sleep(2)
        self.driver.quit()


bot = InternetSpeedYBot()
bot.get_internet_speed()
bot.tweet_at_provider()
