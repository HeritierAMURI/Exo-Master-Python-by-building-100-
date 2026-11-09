from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from time import sleep

TINDOG_URL = "<PASTE YOUR PERSONAL TINDOG URL HERE>"
FACEBARK_EMAIL = "any-email@example.com"
FACEBARK_PASSWORD = "anything"

driver = webdriver.Chrome()
driver.get(TINDOG_URL)

# Step 1 — open the login modal and click Facebark
sleep(2)
driver.find_element(By.XPATH, value='//*[text()="Log in"]').click()
sleep(1)
driver.find_element(By.CLASS_NAME, value='btn-facebark').click()

# Step 2 — Facebark login in popup
sleep(2)
base_window = driver.window_handles[0]
facebark_window = driver.window_handles[1]
driver.switch_to.window(facebark_window)
print(driver.title)

email = driver.find_element(By.ID, value='email')
password = driver.find_element(By.ID, value='pass')
email.send_keys(FACEBARK_EMAIL)
password.send_keys(FACEBARK_PASSWORD)
password.send_keys(Keys.ENTER)

driver.switch_to.window(base_window)
print(driver.title)

# Step 3 — dismiss the three popups
sleep(3)
driver.find_element(By.XPATH, value='//button[text()="Allow"]').click()
sleep(1)
driver.find_element(By.XPATH, value='//button[text()="Not interested"]').click()
sleep(1)
driver.find_element(By.XPATH, value='//button[text()="I Accept"]').click()

# Step 4 — like all 20 dogs
for n in range(20):
    sleep(1)
    try:
        like_button = driver.find_element(By.CLASS_NAME, value='btn-like')
        like_button.click()
    except ElementClickInterceptedException:
        # Match popup is in the way — dismiss it and continue
        try:
            driver.find_element(By.CSS_SELECTOR, value='.match-popup a').click()
        except NoSuchElementException:
            sleep(2)
    except NoSuchElementException:
        # Like button not loaded yet OR all dogs have been swiped — wait and retry
        sleep(2)

driver.quit()