# KeyCipher 🔐

KeyCipher is an **educational Python cybersecurity project** designed to understand how keylogging mechanisms work from a **defensive and learning-focused perspective**.

This project is built strictly for **cybersecurity education**, ethical awareness, and hands-on practice with Python, encryption, and system-level events.

---

## ⚠️ Disclaimer

This project is intended **only for educational and ethical purposes**.

❌ Do **NOT** use this software on systems you do not own or do not have **explicit permission** to test.  
The author is **not responsible for any misuse** of this project.

---

## 🎯 Learning Objectives

- Understand keyboard event capturing in Python  
- Learn how sensitive data can be logged and protected  
- Apply encryption using **Fernet (AES)**  
- Use multithreading for background tasks  
- Practice ethical handling of offensive security concepts  

---

## ✨ Features

- Captures keystrokes locally  
- Encrypts logged data  
- Demonstrates threading and automation  
- Designed for cybersecurity learning, **not deployment**  
- External reporting features are intentionally disabled by default  

---

## 🛠️ Technologies Used

- Python 3  
- `pynput`  
- `cryptography` (Fernet / AES)  
- `pyautogui`  
- `threading`  

---

## 🔧 Installation & Setup

It is **strongly recommended** to run this project inside a **Python virtual environment (venv)** to avoid dependency conflicts.

---

### 1️⃣ Clone the repository

bash
git clone https://github.com/Shanku02/KeyCipher.git
cd KeyCipher

2️⃣ Create a virtual environment
python3 -m venv venv

3️⃣ Activate the virtual environment

Linux / Kali / macOS
source venv/bin/activate

Windows
venv\Scripts\activate

You should now see (venv) in your terminal.

4️⃣ Install required modules
pip install pynput cryptography pyautogui

5️⃣ Run the program
python KeyCipher.py

## 🔐 Security & Ethics Note

This project intentionally avoids automatic data exfiltration and real-world abuse scenarios.
Its purpose is to help learners:
Understand how keyloggers work
Learn how to detect and defend against them
Practice secure coding habits

## 📌 Status

v1.0 — Stable educational release

## 📚 Author

Developed as part of a cybersecurity learning journey using Kali Linux and Python.
