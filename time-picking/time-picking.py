# This is a script to loggin to timesheet 
# and use selenium to auto check in/out 

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
from time import sleep
import pytz
from datetime import datetime, timedelta
import pytz
import random
from dotenv import load_dotenv
import os

# init driver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)
#driver = webdriver.Chrome()
load_dotenv()
# Get check-in and check-out times from .env file
check_in_time_env = os.getenv("CHECK_IN_TIME")
check_out_time_env = os.getenv("CHECK_OUT_TIME")
# Get username and password from .env file
username_env = os.getenv("USERNAME")
password_env = os.getenv("PASSWORD")
# Get delay time from .env file
delay_time_env = os.getenv("DELAY_TIME")
timesheet_url = os.getenv("TIMESHEET_URL")
login_url = os.getenv("LOGIN_URL")
print("login_url: " + login_url)
print("timesheet_url: " + timesheet_url)

def login():
    
    print("Log in at " + datetime.now().strftime("%H:%M:%S"))
    driver.get(login_url)

    username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "_username")))
    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,"_password")))

    username.send_keys(username_env)
    password.send_keys(password_env)

    password.send_keys(Keys.RETURN)

def check_in():
    # Delay execution
    delay_random_time()

    print("Checking in at " + datetime.now().strftime("%H:%M:%S"))
    driver.get(timesheet_url)
    # Find the button by its class name
    button = driver.find_element(By.CLASS_NAME,"btn-create")
    button.click()

    # Click the dropdown to select project
    dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "select2-selection--single")))
    dropdown.click()

    # Wait for the dropdown options to be visible
    wait = WebDriverWait(driver, 10)
    options = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "select2-results__option")))

    # Click the desired option
    for option in options:
        if option.text == "Timekeeping":
            option.click()
            break

    # Click the dropdown to select activity
    # Wait for the the dropdown to select activity to be clickable and click it
    wait = WebDriverWait(driver, 10)
    dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/form/div[2]/div[3]/span/span[1]/span")))
    dropdown.click()

    # Wait for the options to be visible
    options = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "select2-results__option")))

    # Click the desired option
    for option in options:
        if option.text == "WorkRemote":
            option.click()
            break

    # Click save button
    save_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "form_modal_save")))
    save_button.click()
    # close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-dismiss='modal']")))
    # close_button.click()

def check_out():
    # Delay execution
    delay_random_time()

    print("Checking out at " + datetime.now().strftime("%H:%M:%S"))
    driver.get(timesheet_url)

    # Wait for the dropdown to be clickable and click it
    dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-default btn-sm dropdown-toggle']")))
    dropdown.click()

    # Wait for the options to be visible
    option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/api/timesheets/') and contains(text(), 'Stop')]")))
    option.click()

def delay_random_time():    
    # Generate a random delay time between 0 and delay_time_env minutes (in seconds)
    delay_time = random.randint(0, int(delay_time_env)) * 60

    print("Delaying execution for a random time between 0 and " + delay_time_env + " minutes")
    print("Delay time: " + str(delay_time) + " seconds")

    # Delay execution
    sleep(delay_time)

login()

# Define the time in GMT+7 timezone
gmt7_timezone = pytz.timezone('Etc/GMT+7') # replace with your setting timezone
check_in_time_gmt7 = datetime.strptime(check_in_time_env, "%H:%M").time()
check_out_time_gmt7 = datetime.strptime(check_out_time_env, "%H:%M").time()

# Convert the time to local timezone
local_timezone = pytz.timezone('Etc/GMT+7')  # replace with time-picking deploy machine timezone
check_in_time_local = gmt7_timezone.localize(datetime.combine(datetime.today(), check_in_time_gmt7)).astimezone(local_timezone).time()
check_out_time_local = gmt7_timezone.localize(datetime.combine(datetime.today(), check_out_time_gmt7)).astimezone(local_timezone).time()

# Schedule the tasks using the local time
schedule.every().day.at(check_in_time_local.strftime("%H:%M")).do(check_in)
schedule.every().day.at(check_out_time_local.strftime("%H:%M")).do(check_out)

while True:
    schedule.run_pending()
    print("Current time: " + datetime.now().strftime("%H:%M:%S"))
    sleep(10)

