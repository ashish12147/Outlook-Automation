import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
import requests
import os

# -------------------------------
# CAPTCHA Solving Function
# -------------------------------
def solve_captcha(api_key, site_key, url):
    data = {
        "key": api_key,
        "method": "hcaptcha",
        "sitekey": site_key,
        "pageurl": url,
        "json": 1
    }
    response = requests.post("http://2captcha.com/in.php", data=data).json()
    if response["status"] != 1:
        messagebox.showerror("Error", "Failed to get CAPTCHA ID!")
        return None

    captcha_id = response["request"]
    time.sleep(15)  # Wait for CAPTCHA to be solved
    result = requests.get(f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}&json=1").json()
    if result["status"] != 1:
        messagebox.showerror("Error", "CAPTCHA solution failed!")
        return None

    return result["request"]

# -------------------------------
# Main Automation Function
# -------------------------------
def create_account(api_key, email, password):
    try:
        # ChromeDriver Path Setup
        chrome_driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
        service = Service(chrome_driver_path)
        
        # Launch browser
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(service=service, options=options)
        
        # Open Outlook Signup page
        driver.get("https://signup.live.com/")

        # Fill email
        driver.find_element(By.NAME, "MemberName").send_keys(email)
        driver.find_element(By.ID, "iSignupAction").click()
        time.sleep(2)

        # Fill password
        driver.find_element(By.NAME, "Password").send_keys(password)
        driver.find_element(By.ID, "iSignupAction").click()
        time.sleep(2)

        # Get CAPTCHA Site Key (manually update based on site changes)
        site_key = "site_key_found_in_page_source"

        # Solve CAPTCHA
        captcha_solution = solve_captcha(api_key, site_key, driver.current_url)
        if not captcha_solution:
            driver.quit()
            return

        # Inject CAPTCHA solution
        driver.execute_script(f'document.querySelector("[name=g-recaptcha-response]").innerHTML="{captcha_solution}"')
        driver.find_element(By.ID, "iSignupAction").click()

        time.sleep(5)
        messagebox.showinfo("Success", "Outlook account created successfully!")
        driver.quit()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        driver.quit()

# -------------------------------
# GUI Interface
# -------------------------------
def run_automation():
    api_key = api_key_entry.get()
    email = email_entry.get()
    password = password_entry.get()

    if not api_key or not email or not password:
        messagebox.showerror("Error", "All fields are required!")
        return

    create_account(api_key, email, password)

# -------------------------------
# Build GUI
# -------------------------------
root = tk.Tk()
root.title("Outlook Account Creator")
root.geometry("400x300")
root.configure(bg="#F5F5F5")

# Title Label
title_label = tk.Label(root, text="Outlook Account Creator", font=("Arial", 16, "bold"), bg="#F5F5F5")
title_label.pack(pady=10)

# API Key Field
tk.Label(root, text="2Captcha API Key:", bg="#F5F5F5").pack(anchor="w", padx=20)
api_key_entry = tk.Entry(root, width=40)
api_key_entry.pack(pady=5)

# Email Field
tk.Label(root, text="Outlook Email:", bg="#F5F5F5").pack(anchor="w", padx=20)
email_entry = tk.Entry(root, width=40)
email_entry.pack(pady=5)

# Password Field
tk.Label(root, text="Password:", bg="#F5F5F5").pack(anchor="w", padx=20)
password_entry = tk.Entry(root, show="*", width=40)
password_entry.pack(pady=5)

# Create Button
create_button = tk.Button(root, text="Create Account", command=run_automation, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
create_button.pack(pady=20)

root.mainloop()
