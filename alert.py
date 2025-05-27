#!/usr/bin/env python3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from urllib.parse import urlencode
import os
import config

alert_list = []

def send_mail(mail_text):
    SMTPServer = 'smtp.example.com'
    sender = 'monitoring@example.com'
    destination = config.alert_destination
    USERNAME = 'REGION\\unix-mars-svc'
    PASSWORD = os.environ['MAIL_PASSWORD']
    subject = "Monitoring Way4"
    text_subtype = "HTML"
    content = mail_text
    try:
        msg = MIMEText(content, text_subtype)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(destination)
        conn = smtplib.SMTP(SMTPServer, 587)
        conn.set_debuglevel(False)
        conn.starttls()
        conn.login(USERNAME, PASSWORD)
        try:
            conn.sendmail(sender, destination, msg.as_string())
        finally:
            conn.quit()
    except:
        print('mail failed')

def configure_mail_text(hostnames, time, problem_text):
    text = f"<p> Hostname: {hostnames}</p>\n<p>Time: {str(datetime.fromtimestamp(time))}</p>\n<p>Message: {str(problem_text)}</p>"
    return text

def make_url(hostnames, time):
    param = {
        'orgId': '1',  # Всегда 1 - организация и на око
        'var-nodename': hostnames,  # Если несколько серверов
        'var-nodehost': 'ALL',
        'var-diskdevices': '[a-z1-9|nvme[0-9]|n[0-9]-',  # Обязательный параметр для обнаружения дн
        'var-stype': '(btrfs|ext2|ext3|ext4|reiser|xfs|fuseblk|squashfs|nfs|ntfs|fat32|zfs)$',  # Обязательный параметр для обнаружения дн
        'var-mountpoint': '/',  # Нужно указывать нужную директорию для отображения утилизации конкретно по ней
        'from': int(time - 10800) * 1000,  # Linux-timestamp
        'to': int(time) * 1000,
    }
    query_string = urlencode(param, doseq=True)
    url = f"https://monitoring.example.com/d/dashboard?...{query_string}"
    return url

def write_to_file(hostname, time, problem_text):
    text = open(config.alert_log, 'a')
    text.write(str(hostname) + ' ' + str(datetime.fromtimestamp(time)) + ' ' + str(problem_text) + '\n')
    text.close()

def alert(hostname, time, problem_text):
    write_to_file(hostname, time, problem_text)
    global alert_list
    alert_list.append(configure_mail_text(hostname, time, problem_text))
    print(str(hostname) + ' ' + str(datetime.fromtimestamp(time)) + ' ' + str(problem_text))
    # print(make_url(hostname, time))

def send_all_alert_mail(group_name):
    global alert_list
    alert_list_unique = list(dict.fromkeys(alert_list))
    if len(alert_list_unique) > 0:
        text_mail = f"<p>Group name: {group_name}</p>" + "<br>".join(alert_list_unique)
        send_mail(text_mail)
        alert_list = []
