from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()
    #Thread(args).start() starts a background thread to run functions in the background

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
    #with app.app_context() manually creates app context so that it can auto pass arguments across functions, in this case it can see the email configuration values for the server

