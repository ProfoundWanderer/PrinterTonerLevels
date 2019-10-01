#!/usr/bin/python3

import config
import DataHelpers
import JsonHelper
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from logging.handlers import RotatingFileHandler
import smtplib
import ssl
import sys


def main():
    # list of rrd files that contain the toner levels
    toner_file_list = [
        "dfw-bizhub_c458_snmp_black4_61.rrd",
        "dfw-bizhub_c458_snmp_cyan1_62.rrd",
        "dfw-bizhub_c458_snmp_magenta2_63.rrd",
        "dfw-bizhub_c458_snmp_yellow3_64.rrd",
        "dfw-m521dn-checkprinter_snmp_black1_79.rrd",
        "frtx-hp570dn_snmp_black1_49.rrd",
        "frtx-hp570dn_snmp_cyan2_50.rrd",
        "frtx-hp570dn_snmp_magenta3_51.rrd",
        "frtx-hp570dn_snmp_yellow4_52.rrd",
        "hotx-hp570dn_snmp_black1_86.rrd",
        "hotx-hp570dn_snmp_cyan2_87.rrd",
        "hotx-hp570dn_snmp_magenta3_88.rrd",
        "hotx-hp570dn_snmp_yellow4_89.rrd",
        "orl-m570dn_snmp_black1_53.rrd",
        "orl-m570dn_snmp_cyan2_54.rrd",
        "orl-m570dn_snmp_magenta3_55.rrd",
        "orl-m570dn_snmp_yellow4_56.rrd",
        "sauk-m570dn_snmp_black1_57.rrd",
        "sauk-m570dn_snmp_cyan2_58.rrd",
        "sauk-m570dn_snmp_magenta3_59.rrd",
        "sauk-m570dn_snmp_yellow4_60.rrd",
    ]

    # the directory with the .rrd files
    file_directory = (
        "/var/www/cacti-1.1.38/rra"
    )

    data = DataHelpers.grab_data(file_directory, toner_file_list)
    JsonHelper.toner_history(data)

    logging.info("TonerLevels.py script has ended.")


def log_setup():
    """
    Just for a easy reminder so the file doesn't get too large over time.
    """
    logging.basicConfig(
        handlers=[RotatingFileHandler('./toner_log.log', mode='a', maxBytes=1 * 1024 * 1024, backupCount=1,
                                      encoding='utf-8', delay=0)],
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO,
    )


def send_email(low_level_message, level_increase_message):
    """
    This does the final formatting of the email and sends it
    """
    port = 587
    smtp_server = "smtp.office365.com"
    login_email = config.email_login
    from_address = "it@bedrocklogistics.com"
    to_address = ["bedrocktest@mailinator.com", "bedrocktest1@mailinator.com"]
    password = config.email_password

    # this if elif block is just to help format the email so there are not extra newlines for no reason
    if low_level_message and level_increase_message:
        subject = "Subject: Printer(s) Toner Level is Low and Increased from Yesterday!"
        body = f"{low_level_message}\n{level_increase_message}\n" \
               f"The Konica phone number is (800) 456-5664 and their website is www.mykmbs.com.\n"
    elif low_level_message and not level_increase_message:
        subject = "Subject: Printer(s) Toner Level is Low!"
        body = f"{low_level_message}\n" \
               f"The Konica phone number is (800) 456-5664 and their website is www.mykmbs.com.\n"
    elif not low_level_message and level_increase_message:
        subject = "Subject: Printer(s) Toner Level Increased from Yesterday!"
        body = f"{level_increase_message}\n" \
               f"The Konica phone number is (800) 456-5664 and their website is www.mykmbs.com.\n"
    else:  # another safety check so no blank emails are sent because I believe sometimes a stray is sent
        logging.info("low_level_message and level_increase_message are both empty")
        logging.info("TonerLevels.py script has ended.")
        sys.exit(0)

    # create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = login_email
    message["To"] = ', '.join(to_address)
    message["Subject"] = subject
    # add body to the email
    message.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        try:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(login_email, password)
            server.sendmail(from_address, to_address, message.as_string())
            logging.info("Email has successfully sent.")
        except Exception as e:
            logging.exception(e)
        finally:
            server.quit()
            logging.info("Successfully quit server.")


if __name__ == "__main__":
    log_setup()
    logging.info("TonerLevels.py script has started.")
    main()
