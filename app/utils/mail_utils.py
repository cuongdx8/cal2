import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

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


# @create_mail_session
# @transaction
# def send_mail_forgot_password(email: str, session_mail: smtplib.SMTP, session: Session) -> None:
#     account = account_services.find_by_email(email, session)
#
#     mail_content = '<p>Link to change password:<br/> <a href="{}">Click to change password</a>></p>'
#     # Setup the MIME
#     message = MIMEMultipart()
#     message['From'] = sender_address
#     message['To'] = email
#     message['Subject'] = 'Reset password'  # The subject line
#     # The body and the attachments for the mail
#     message.attach(MIMEText(mail_content.
#                             format(f'http://localhost:5000/auth/forgot-password?token='
#                                    f'{jwt_utils.create_forgot_token(account)}'),
#                             'plain'))
#     # Create SMTP session for sending the mail
#
#     text = message.as_string()
#     session_mail.sendmail(sender_address, email, text)


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
# def send_mail_invite(event: DBEvent, session_mail):
#     for item in event.attendees:
#         mail_content = 'Accept: {accept} <br/>' \
#                        'Denied: {denied}'
#         # Setup the MIME
#         message = MIMEMultipart()
#         message['From'] = sender_address
#         message['To'] = item.get('email')
#         message['Subject'] = 'Invite to join event {}'.format(event.name)  # The subject line
#         # The body and the attachments for the mail
#         token_invite = jwt_utils.create_invite_token(event.id, item)
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
# def send_mail_confirm_booking(booking: Booking, session_mail):
#     for item in booking.guests:
#         mail_content = 'Content body booking'
#         # Setup the MIME
#         message = MIMEMultipart()
#         message['From'] = sender_address
#         message['To'] = item
#         match booking.is_confirm:
#             case True:
#                 message['Subject'] = '{name} has been submitted'.format(name=booking.name)  # The subject line
#             case False:
#                 message['Subject'] = '{name} is rejected'.format(name=booking.name)
#             case None:
#                 message['Subject'] = '{name} is waiting for for confirm'.format(name=booking.name)
#         message.attach(MIMEText(mail_content, 'plain'))
#         # Create SMTP session for sending the mail
#
#         text = message.as_string()
#         session_mail.sendmail(sender_address, item, text)


@create_mail_session
def send_mail_verify_email(account, session_mail):
    mail_content = '<p>Click to active account {email}</p>:{uri}'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = account.email
    message['Subject'] = 'Active account'  # The subject line
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
# def send_mail_notification_active_event(emails: [str], event: DBEvent, session_mail):
#     for item in emails:
#         mail_content = f'Event: {event.name} is active in 15 minus'
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