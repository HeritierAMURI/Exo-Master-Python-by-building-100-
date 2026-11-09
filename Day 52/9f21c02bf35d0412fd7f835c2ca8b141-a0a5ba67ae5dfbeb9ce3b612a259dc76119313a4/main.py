from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
import time

SIMILAR_ACCOUNT = "chefsteps"    # the account whose followers you'll follow
USERNAME = "your-email"          # your Share-a-Naan username (your email)
PASSWORD = "your-pw"             # from your Share-a-Naan profile page

BASE_URL = "https://app.100daysofpython.dev/services/share-a-naan" 
LOGIN_URL = f"{BASE_URL}/login"


class InstaFollower:

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)  # keep the browser open
        self.driver = webdriver.Chrome(options=chrome_options)

    def login(self):
        self.driver.get(LOGIN_URL)
        time.sleep(2)

        # Dismiss a cookie banner if one is present (Share-a-Naan doesn't show one,
        # but this keeps the same code working against the real site too).
        decline = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Decline')]")
        if decline:
            decline[0].click()

        username = self.driver.find_element(By.NAME, "username")
        password = self.driver.find_element(By.NAME, "password")
        username.send_keys(USERNAME)
        password.send_keys(PASSWORD)
        time.sleep(1)
        password.send_keys(Keys.ENTER)
        time.sleep(2)

        # Dismiss "Save your login info?" → "Not now"
        save_info = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Not now')]")
        if save_info:
            save_info[0].click()
        time.sleep(1)

        # Dismiss "Turn on notifications" → "Not Now"
        notifications = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now')]")
        if notifications:
            notifications[0].click()

    def find_followers(self):
        self.driver.get(f"{BASE_URL}/u/{SIMILAR_ACCOUNT}/followers")
        time.sleep(2)

        # The scrollable element inside the followers dialog. Inspect to confirm the class.
        modal = self.driver.find_element(By.CSS_SELECTOR, ".followers-scroll")
        for _ in range(10):
            # "scroll this element to the bottom" → loads the next batch of followers
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
            time.sleep(1)

    def follow(self):
        all_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".followers-scroll button")
        for button in all_buttons:
            try:
                button.click()
                time.sleep(1)
            except ElementClickInterceptedException:
                # An "Unfollow?" dialog opened (you already follow this account).
                cancel = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
                cancel.click()


bot = InstaFollower()
bot.login()
bot.find_followers()
bot.follow()
