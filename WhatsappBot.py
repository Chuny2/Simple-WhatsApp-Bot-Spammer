import os
import socket
import tkinter as tk
from tkinter import ttk, filedialog
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, TimeoutException

class WhatsAppBot:
    def __init__(self):
        self.setup_driver()
        self.setup_ui()
        self.phone_number_list = []
        self.file_path = None

    def setup_driver(self):
        self.options = webdriver.ChromeOptions()
        username = os.getlogin()
        user_data_dir = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data"
        self.options.add_argument(f"user-data-dir={user_data_dir}")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--remote-debugging-port=9222")
        self.options.add_argument("--disable-gpu") # This disables GPU hardware acceleration
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-software-rasterizer")
        self.options.add_argument("--log-level=3")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--allow-running-insecure-content")
        #self.options.add_argument("--headless=new") # Uncomment the following line to run Chrome in headless mode(Means you don´t see the browser)

        self.service = Service(executable_path="./chromedriver")

    def setup_ui(self):
        self.master = tk.Tk()
        self.master.title("WhatsApp Bot")
        self.master.geometry("600x710")
        self.master.configure(bg='#f0f0f0')

        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)
        self.style.configure('TEntry', font=('Helvetica', 12), padding=6)
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TListbox', font=('Helvetica', 12))

        self.frame = ttk.Frame(self.master, padding="20")
        self.frame.pack(fill='both', expand=True)

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.frame, text="Enter the Message:").grid(row=0, column=0, sticky='W', pady=5)

        message_frame = ttk.Frame(self.frame)
        message_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky='EW')

        self.message_text = tk.Text(message_frame, wrap='word', width=50, height=10, font=('Helvetica', 12))
        self.message_text.pack(side='left', fill='both', expand=True)

        message_scroll = ttk.Scrollbar(message_frame, orient='vertical', command=self.message_text.yview)
        message_scroll.pack(side='right', fill='y')
        self.message_text['yscrollcommand'] = message_scroll.set

        ttk.Label(self.frame, text="Enter the Phone Number:").grid(row=2, column=0, sticky='W', pady=5)

        self.phone_entry = ttk.Entry(self.frame, width=30)
        self.phone_entry.grid(row=2, column=1, pady=5, padx=5, sticky='EW')

        ttk.Button(self.frame, text="Add", command=self.add_phone_number).grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(self.frame, text="Phone Numbers:").grid(row=3, column=0, sticky='W', pady=5)

        phone_listbox_frame = ttk.Frame(self.frame)
        phone_listbox_frame.grid(row=4, column=0, columnspan=3, pady=5, sticky='EW')

        self.phone_listbox = tk.Listbox(phone_listbox_frame, height=10, width=50, font=('Helvetica', 12))
        self.phone_listbox.pack(side='left', fill='both', expand=True)

        phone_listbox_scroll = ttk.Scrollbar(phone_listbox_frame, orient='vertical', command=self.phone_listbox.yview)
        phone_listbox_scroll.pack(side='right', fill='y')
        self.phone_listbox['yscrollcommand'] = phone_listbox_scroll.set

        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.grid(row=5, column=0, columnspan=3, pady=10)

        ttk.Button(buttons_frame, text="Send", command=self.send_messages).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Load numbers from File", command=self.load_numbers_from_file).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Select File to Send", command=self.select_file).grid(row=1, column=0, columnspan=2, pady=10)

        self.file_label = ttk.Label(self.frame, text="No file selected")
        self.file_label.grid(row=6, column=0, columnspan=3, pady=5)

    def add_phone_number(self):
        phone_number = self.phone_entry.get()
        if not phone_number.startswith('+'):
            error_label = ttk.Label(self.frame, text="ERROR: Please enter the phone number with the country code (e.g., +1234567890).", foreground="red", background='#f0f0f0')
            error_label.grid(row=8, columnspan=2)
            self.master.after(5000, error_label.destroy)# Cooldown to display error message for 5 seconds
            return
        self.phone_number_list.append(phone_number)
        self.phone_listbox.insert(tk.END, phone_number)
        self.phone_entry.delete(0, 'end')

    def load_numbers_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                for line in file:
                    phone_number = line.strip()
                    if phone_number.startswith('+') and phone_number not in self.phone_number_list:
                        self.phone_number_list.append(phone_number)
                        self.phone_listbox.insert(tk.END, phone_number)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path))

    def send_messages(self):
        message_text_content = self.message_text.get("1.0", tk.END).strip()
        if len(message_text_content) == 0:
            error_label = ttk.Label(self.frame, text="ERROR: Please fill the message.", foreground="red", background='#f0f0f0')
            error_label.grid(row=8, columnspan=2)
            self.master.after(5000, error_label.destroy)
        else:
            driver = webdriver.Chrome(service=self.service, options=self.options)
            driver.get("http://web.whatsapp.com")
            sleep(5) # Cooldown to ensure WhatsApp Web loads completely

            for mobile_no in self.phone_number_list:
                try:
                    self.send_whatsapp_msg_and_file(driver, mobile_no, message_text_content, self.file_path)
                    sleep(1) # Cooldown between sending messages to different phone numbers
                except Exception as e:
                    sleep(1) # Cooldown to avoid rapid retry in case of an exception
                    self.is_connected()

    def element_presence(self, driver, by, xpath, time):
        try:
            element_present = EC.presence_of_element_located((by, xpath))
            WebDriverWait(driver, time).until(element_present)
            return True
        except TimeoutException:
            return False

    def handle_alert(self, driver):
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            print(f"Alert accepted: {alert_text}")
        except NoAlertPresentException:
            pass

    def is_connected(self):
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except:
            return False

    def send_whatsapp_msg_and_file(self, driver, phone_no, text, file_path=None):
        driver.get(f"https://web.whatsapp.com/send?phone={phone_no}&source=&data=#")
        try:
            # Check if the message input box is present within 10 seconds
            if not self.element_presence(driver, By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div', 10):
                raise TimeoutException("Message input box not found.")

            txt_box = driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div')
            txt_box.send_keys(text)
            txt_box.send_keys("\n")

            if file_path:
                # Check if the attach button is present within 5 seconds
                if not self.element_presence(driver, By.XPATH, '//*[@title="Attach"]', 5):
                    raise TimeoutException("Attach button not found.")

                attach_button = driver.find_element(By.XPATH, '//*[@title="Attach"]')
                attach_button.click()
                sleep(1) # Cooldown to allow the attachment menu to open
                # Check if the file input is present within 5 seconds
                if not self.element_presence(driver, By.XPATH, '//input[@accept="*"]', 5):
                    raise TimeoutException("File input not found.")

                file_input = driver.find_element(By.XPATH, '//input[@accept="*"]')
                file_input.send_keys(file_path)
                sleep(1) # Cooldown to allow the file to be uploaded
                # Check if the send button for the attachment is present within 5 seconds
                if not self.element_presence(driver, By.XPATH, '//span[@data-icon="send"]', 5):
                    raise TimeoutException("Send button not found.")

                send_button = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
                send_button.click()

                #if not self.element_presence(driver, By.XPATH, '//*[contains(@aria-label, "Check mark")]', 10):
                 #   raise TimeoutException("Check mark not found.")
        except UnexpectedAlertPresentException:
            self.handle_alert(driver)
        except TimeoutException as te:
            print(f"TimeoutException: Failed to send message or file to {phone_no}")
            print(te)
        except Exception as e:
            print(f"Exception: Failed to send message or file to {phone_no}")
            print(e)

    def run(self):
        self.master.mainloop()

if __name__ == "__main__":
    bot = WhatsAppBot()
    bot.run()
