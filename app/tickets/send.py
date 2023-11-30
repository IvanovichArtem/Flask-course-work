import smtplib
import os
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def send_email(to, text=None):
    sender = "uchebaivanovic@gmail.com"
    password = "joiw pnlr seyh xdaq"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        server.login(sender, password)
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = f"Ваши билеты брони в ММИ!"

        for file in os.listdir("tickets/t"):
            filename = os.path.basename(file)
            ftype, encoding = mimetypes.guess_type(file)
            file_type, subtype = ftype.split("/")
            with open(f"tickets/t/{file}", "rb") as f:
                file = MIMEApplication(f.read(), subtype)

            file.add_header(
                "content-disposition", "attachment", filename=filename
            )
            msg.attach(file)

        print("Sending...")
        server.sendmail(sender, to, msg.as_string())

        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"


def del_files():
    file_list = os.listdir("tickets/t")
    for file in file_list:
        file_path = os.path.join("tickets/t", file)
        os.remove(file_path)
