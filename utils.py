import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def save_to_csv_with_sheets(dataframes, output_file, pd):
    """
    Saves a list of DataFrames into an Excel file with each DataFrame on a separate sheet.

    Args:
        dataframes (list of pd.DataFrame): List of DataFrames to save.
        output_file (str): File path for the Excel file.

    Returns:
        None
    """
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for i, df in enumerate(dataframes):
                sheet_name = f"Page_{i + 1}"  # Unique sheet name for each DataFrame
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"An error occurred while saving data: {e}")

def send_email_with_attachments(sender_email, receiver_email, subject, body, attachments, smtp_server, smtp_port, login, password):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add email body
    msg.attach(MIMEText(body, 'plain'))

    # Attach files
    for file in attachments:
        with open(file, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={file}',
        )
        msg.attach(part)

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Upgrade connection to secure
        server.login(login, password)
        server.send_message(msg)

def test_smtp():
    smtp_server = "smtp.gmail.com"  # Replace with your SMTP server
    smtp_port = 587  # Replace with your SMTP port
    sender_email = "ccarver410@gmail.com"
    password = "fyot utte dnvt xgpe"
    receiver_email = "ccarver410@gmail.com"

    try:
        print("Connecting to SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()  # Identify with the server
            server.starttls()  # Upgrade connection to secure
            server.ehlo()
            print("Logging in...")
            server.login(sender_email, password)
            print("Sending email...")
            message = "Subject: SMTP Test\n\nThis is a test email."
            server.sendmail(sender_email, receiver_email, message)
            print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
    except Exception as e:
        print(f"General error: {e}")

def wait_for_element(driver, by, value, timeout=10):
    """
    Waits for an element to be present in the DOM and visible.

    Args:
        driver: Selenium WebDriver instance.
        by: The locator strategy (e.g., By.ID, By.CLASS_NAME).
        value: The value of the locator.
        timeout (int): Maximum wait time in seconds.

    Returns:
        WebElement: The located element or None if not found.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"Timeout: Element with {by} = {value} not found within {timeout} seconds.")
        return None