import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from app.users.users import User
from app.constants import Constants
from app.utils import jwt_utils
from app.utils.database_utils import transaction

sender_address = os.environ['MAIL_USERNAME']
sender_pass = os.environ['APP_PASSWORD']
mail_server = os.environ['MAIL_SERVER']
mail_port = os.environ['MAIL_PORT']


def create_mail_session(func):

    def wrapper(*args, **kwargs):
        session = smtplib.SMTP_SSL(mail_server, int(mail_port))  # use gmail with port
        session.login(sender_address, sender_pass)  # login with mail_id and password
        func(*args, **kwargs, session_mail=session)
        session.quit()

    wrapper.__name__ = func.__name__
    return wrapper


@create_mail_session
def send_mail_forgot_password(account: User, session_mail: smtplib.SMTP) -> None:

    mail_content = '<p>Link to change password:<br/> <a href="{}">Click to change password</a>></p>'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = account.email
    message['Subject'] = 'Reset password'  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content.
                            format(f'{Constants.APP_HOST}/auths/forgot-password?token='
                                   f'{jwt_utils.create_forgot_token(account)}'),
                            'plain'))
    # Create SMTP session for sending the mail

    text = message.as_string()
    session_mail.sendmail(sender_address, account.email, text)


@create_mail_session
def send_mail_reset_password(account, session_mail):
    mail_content = '<p>New password is: {}</p>'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = account.email
    message['Subject'] = 'Reset password'  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content.format(account.password),
                            'plain'))
    # Create SMTP session for sending the mail

    text = message.as_string()
    session_mail.sendmail(sender_address, account.email, text)


# @create_mail_session
# def send_mail_invite(events: DBEvent, session_mail):
#     for item in events.attendees:
#         mail_content = 'Accept: {accept} <br/>' \
#                        'Denied: {denied}'
#         # Setup the MIME
#         message = MIMEMultipart()
#         message['From'] = sender_address
#         message['To'] = item.get('email')
#         message['Subject'] = 'Invite to join events {}'.format(events.name)  # The subject line
#         # The body and the attachments for the mail
#         token_invite = jwt_utils.create_invite_token(events.id, item)
#         uri = 'http://localhost:5000/event/invite?status={status}&token={token_invite}'
#         message.attach(MIMEText(mail_content.format(accept=uri.format(status='accepted', token_invite=token_invite),
#                                                     denied=uri.format(status='declined', token_invite=token_invite)),
#                                 'plain'))
#         # Create SMTP session for sending the mail
#
#         text = message.as_string()
#         session_mail.sendmail(sender_address, item.get('email'), text)
#
#
# @create_mail_session
# def send_mail_confirm_booking(bookings: Booking, session_mail):
#     for item in bookings.guests:
#         mail_content = 'Content body bookings'
#         # Setup the MIME
#         message = MIMEMultipart()
#         message['From'] = sender_address
#         message['To'] = item
#         match bookings.is_confirm:
#             case True:
#                 message['Subject'] = '{name} has been submitted'.format(name=bookings.name)  # The subject line
#             case False:
#                 message['Subject'] = '{name} is rejected'.format(name=bookings.name)
#             case None:
#                 message['Subject'] = '{name} is waiting for for confirm'.format(name=bookings.name)
#         message.attach(MIMEText(mail_content, 'plain'))
#         # Create SMTP session for sending the mail
#
#         text = message.as_string()
#         session_mail.sendmail(sender_address, item, text)


@create_mail_session
def send_mail_verify_email(account, session_mail):
    mail_content = '<p>Click to active users {email}</p>:{uri}'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = account.email
    message['Subject'] = 'Active users'  # The subject line
    token = jwt_utils.create_active_token(account.id)
    uri = 'http://localhost:5000/auth/active?token={token}'.format(token=token)
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content.format(email=account.email, uri=uri),
                            'plain'))
    # Create SMTP session for sending the mail

    text = message.as_string()
    session_mail.sendmail(sender_address, account.email, text)

#
# @create_mail_session
# def send_mail_notification_active_event(emails: [str], events: DBEvent, session_mail):
#     for item in emails:
#         mail_content = f'Event: {events.name} is active in 15 minus'
#         # Setup the MIME
#         message = MIMEMultipart()
#         message['From'] = sender_address
#         message['To'] = item
#         message['Subject'] = 'Event notification active'  # The subject line
#         message.attach(MIMEText(mail_content, 'plain'))
#         # Create SMTP session for sending the mail
#
#         text = message.as_string()
#         session_mail.sendmail(sender_address, item, text)
