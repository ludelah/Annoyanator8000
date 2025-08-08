import os
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

DEBUGGING = False

# TODO: Add custom arguments on start
# TODO: Subdivide into functions &&/|| classes
# TODO: Separate into different files

# --- Load Instagram credentials ---
load_dotenv()
insta_username = os.getenv("USERNAME")
insta_password = os.getenv("PASSWORD")
group_name = os.getenv("group_name")

if DEBUGGING:
  print("ENTERING DEBUGGING MODE")
  group_name = insta_username #Debugging
  
# --- Set up persistent Chrome profile to keep session ---
profile_path = os.path.expanduser("~/.config/instagram_bot_profile")
options = Options()
if DEBUGGING:
  options.add_argument(f"--user-data-dir={profile_path}")
  options.add_argument("--window-size=1200,800")
else:
  options.add_argument("--headless=new")

# Optional: disable bot detection
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# --- Start Chrome ---
print("Starting browser...")
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

# --- Go to Instagram ---
print("Navigating to Instagram login page...")
driver.get("https://www.instagram.com/accounts/login/")

# --- Log in if not already logged in ---
try:
    wait.until(EC.presence_of_element_located((By.NAME, "username")))
    print("Logging in...")
    driver.find_element(By.NAME, "username").send_keys(insta_username)
    driver.find_element(By.NAME, "password").send_keys(insta_password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(5)
except:
    print("Already logged in or session loaded.")

# --- Handle possible popups (in English or Spanish) ---
def dismiss_popup(button_texts):
    for text in button_texts:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{text}')]"))
            )
            btn.click()
            print(f"Dismissed popup: {text}")
            break
        except:
            continue

dismiss_popup(["Not Now", "Ahora no"])
dismiss_popup(["Not Now", "Ahora no"])

# --- Go to Reels Feed ---
print("Navigating to Reels feed...")
driver.get("https://www.instagram.com/reels/")
time.sleep(13)
print("Reels feed loaded.")

# --- Main loop: send a few reels ---
max_reels = random.randint(1, 7)
print(f"Will send {max_reels} reels to '{group_name}'...")

sent_count = 0

while sent_count < max_reels:
    print(f"\n--- Processing reel #{sent_count + 1} ---")

    # Open first visible reel

    print("Waiting for reel UI...")
    time.sleep(3)

    # Try to find share/send icon
    try:
        print("Looking for share icon...")
        try:
            share_icon = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div/*[name()='svg'][@aria-label='Share']"))
            )
        except:
            share_icon = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button/*[name()='svg'][@aria-label='Share']"))
            )
        share_icon.click()
    except:
        print("⚠️ Couldn't find share icon. Skipping this reel.")
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        continue

    # Find the group and send
    print(f"Searching for group '{group_name}'...")
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
        )
        search_box.clear()
        search_box.send_keys(group_name)
        time.sleep(2)

        group_result = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[text()='{group_name}']"))
        )
        group_result.click()

        send_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Send']"))
        )
        send_button.click()

        print(f"✅ Sent reel to '{group_name}'!")
        sent_count += 1
    except:
        print("⚠️ Could not send reel. Maybe group not found.")

    # Close reel overlay
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except:
        pass

    # Scroll once to get new content
    print("Scrolling down...")
    # Try to scroll the main content area for Reels
    time.sleep(30)
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
    time.sleep(3)

    # Random wait between 1 to 8 minutes
    delay = random.randint(30, 15 * 60)
    mins = delay // 60
    secs = delay % 60
    print(f"Waiting {mins}m {secs}s before next reel...")
    if DEBUGGING:
      delay = 5
      time.sleep(delay)

print("\n✅ Done sending all reels.")
driver.quit()
