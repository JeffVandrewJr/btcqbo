import click
import smtplib
import os
from app.qbo import refresh_stored_tokens
from app.utils import wipe, fetch

# this is a command line tool for testing


@click.group()
def cli():
    pass


@cli.command()
def refresh():
    # manually refreshes stored QBO tokens
    data = refresh_stored_tokens()
    if 'token_type' not in data:
        click.echo('Refresh failed.')
    else:
        click.echo('Refresh success.')


@cli.command()
def printqb():
    # prints QBO API ID and token to screen
    click.echo(fetch('qb_id'))
    click.echo(fetch('qb_sandbox'))
    click.echo(os.getenv('CALLBACK_URL'))


@cli.command()
def deletekeys():
    # wipes all QBO API keys from redis storage
    wipe('qb_id')
    wipe('qb_secret')
    wipe('qb_sandbox')


@cli.command()
def mail():
    recipient = input('Enter recipient: ')
    msg = 'Subject: Hi\nHow are you?'
    click.echo(fetch('mail_on'))
    click.echo(fetch('mail_user'))
    click.echo(fetch('mail_host'))
    click.echo(fetch('mail_port'))
    click.echo(fetch('mail_from'))
    smtp = smtplib.SMTP(fetch('mail_host'), fetch('mail_port'))
    click.echo(smtp.ehlo())
    if fetch('mail_port') == 587:
        click.echo(smtp.starttls())
    click.echo(smtp.login(fetch('mail_user'), fetch('mail_pswd')))
    smtp.sendmail('test@testingsite.com', recipient, msg)


if __name__ == '__main__':
    cli()
