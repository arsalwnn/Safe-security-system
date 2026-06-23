import cv2
import os
import time
import requests
import smtplib
from email.message import EmailMessage
from config import *

class AlertSystem:
    def __init__(self):
        if not os.path.exists(EVIDENCE_DIR):
            os.makedirs(EVIDENCE_DIR)
        self._last_alert_time = 0

    def _cooldown_ok(self):
        """جلوگیری از spam alert - حداقل ALERT_COOLDOWN ثانیه بین هر alert"""
        now = time.time()
        if now - self._last_alert_time >= ALERT_COOLDOWN:
            self._last_alert_time = now
            return True
        remaining = ALERT_COOLDOWN - (now - self._last_alert_time)
        print(f"[ALERT] Cooldown active, {remaining:.0f}s remaining")
        return False

    def save_intruder(self, frame):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{EVIDENCE_DIR}/intruder_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"[ALERT] Saved: {filename}")
        return filename

    def trigger(self, frame):
        """
        یه متد واحد برای trigger کردن همه alertها
        cooldown رو هم چک می‌کنه
        """
        if not self._cooldown_ok():
            return

        image_path = self.save_intruder(frame)
        self._send_telegram(image_path)
        self._send_email(image_path)

    def _send_telegram(self, image_path):
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            with open(image_path, "rb") as img:
                response = requests.post(
                    url,
                    data={"chat_id": TELEGRAM_CHAT_ID, "caption": "🚨 Intruder detected!"},
                    files={"photo": img},
                    timeout=10
                )
            if response.status_code == 200:
                print("[ALERT] Telegram sent")
            else:
                print(f"[ALERT] Telegram failed: {response.status_code}")
        except Exception as e:
            print(f"[ALERT] Telegram error: {e}")

    def _send_email(self, image_path):
        try:
            msg = EmailMessage()
            msg["Subject"] = "🚨 Intruder Alert!"
            msg["From"] = EMAIL_SENDER
            msg["To"] = EMAIL_RECEIVER
            msg.set_content("Intruder detected near the safe!")

            with open(image_path, "rb") as f:
                msg.add_attachment(f.read(), maintype="image", subtype="jpeg", filename="intruder.jpg")

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(msg)
            print("[ALERT] Email sent")
        except Exception as e:
            print(f"[ALERT] Email error: {e}")