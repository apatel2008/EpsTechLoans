import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time

# --- Email credentials ---
sender_email = "apateleastsideprep@gmail.com"
sender_password = "yauy lyok yuqi tdff"

# --- Connect to DB ---
conn = sqlite3.connect("eps_tech_loans.db")
cursor = conn.cursor()

# --- Get today's date and time ---
today = datetime.today().date()
formatted_today = today.strftime("%Y-%m-%d")

# --- Query all currently borrowed items ---
cursor.execute("""
    SELECT name, email, borrow_date, return_date FROM eps_tech_loans
    WHERE status = 'borrowed'
""")
borrowed_items = cursor.fetchall()

for name, email, borrow_date_str, return_date_str in borrowed_items:
    borrow_date = datetime.strptime(borrow_date_str, "%Y-%m-%d").date()
    return_date = datetime.strptime(return_date_str, "%Y-%m-%d").date()

    days_until_due = (return_date - today).days
    days_overdue = (today - return_date).days

    # --- One-week reminder ---
    if days_until_due == 7:
        subject = "Reminder: Tech Item Return Due in One Week"
        body = f"Hi,\n\nThis is a reminder to return the item in one week:\nItem: {name}\nDue Date: {return_date_str}\n\nThanks!"
        
    elif days_until_due == 1:
        subject = "Reminder: Tech Item Return Due Tomorrow"
        body = f"Hi,\n\nThis is a reminder to return the item tomorrow:\nItem: {name}\nDue Date: {return_date_str}\n\nThanks!"

    # --- Last day reminder ---
    elif days_until_due == 0:
        subject = "Reminder: Tech Item Return Due Today"
        body = f"Hi,\n\nPlease return the following item today:\nItem: {name}\nDue Date: {return_date_str}\n\nThanks!"

    # --- Overdue reminder for every late day ---
    elif days_overdue > 0:
        subject = f"Overdue Notice: {days_overdue} Day(s) Late - Tech Item Return"
        body = f"Hi,\n\nThis item is overdue by {days_overdue} day(s):\nItem: {name}\nOriginal Due Date: {return_date_str}\n\nPlease return it ASAP.\n\nThanks!"

    else:
        continue  # No reminder needed

    # --- Send email ---
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {email}: {subject}")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")
