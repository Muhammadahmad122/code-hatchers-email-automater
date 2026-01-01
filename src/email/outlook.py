import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from imap_tools import MailBox, AND
import os
import uuid

class EmailHandler:
    def __init__(self):
        self.email = os.getenv("EMAIL_HOST_USER")
        self.password = os.getenv("EMAIL_HOST_PASSWORD")
        self.smtp_server = "smtp.office365.com"
        self.smtp_port = 587
        self.imap_server = "outlook.office365.com"

    def send_email(self, to_email, subject, body, tracking_id=None):
        """
        Sends an email via Outlook SMTP.
        Adds a tracking pixel if tracking_id is provided.
        Body should be HTML content.
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add Tracking Pixel
            if tracking_id:
                # Tracking domain should be configured in .env, defaulting to localhost for dev
                tracking_domain = os.getenv("TRACKING_DOMAIN", "http://localhost:8000")
                tracking_url = f"{tracking_domain}/track/open/{tracking_id}"
                pixel_html = f'<img src="{tracking_url}" width="1" height="1" style="display:none;" />'
                body += f"<br>{pixel_html}"

            # Attach HTML body
            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(self.email, to_email, msg.as_string())
            server.quit()
            
            print(f"[+] Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"[-] Error sending email: {e}")
            return False

    def check_replies(self, prospect_email):
        """
        Checks for unseen replies from a specific prospect.
        Returns list of reply objects.
        """
        replies = []
        try:
            # Login to IMAP
            with MailBox(self.imap_server).login(self.email, self.password) as mailbox:
                # Search for unread emails from the prospect
                for msg in mailbox.fetch(AND(from_=prospect_email, seen=False)):
                    replies.append({
                        "id": msg.uid,
                        "subject": msg.subject,
                        "body": msg.text or msg.html,
                        "date": msg.date
                    })
            return replies
        except Exception as e:
            print(f"[-] Error checking replies: {e}")
            return []

    def generate_tracking_id(self):
        return str(uuid.uuid4())
