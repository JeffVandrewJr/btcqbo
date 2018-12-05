import click
import os
from app.qbo import refresh_stored_tokens
from getpass import getpass
from app.utils import save, wipe, fetch
from werkzeug.security import generate_password_hash


@click.group()
def cli():
    pass


@cli.command()
def refresh():
    click.echo(refresh_stored_tokens())


@cli.command()
def printqb():
    click.echo(fetch('qb_id'))
    click.echo(fetch('qb_secret'))
    click.echo(fetch('qb_sandbox'))
    click.echo(os.getenv('CALLBACK_URL'))


@cli.command()
def setlogin():
    username = input("Choose a username: ")
    pswd = getpass("Choose a password: ")
    hash = generate_password_hash(pswd)
    save('hash', hash)
    save('username', username)


@cli.command()
def deletelogin():
    wipe('hash')
    wipe('username')


@cli.command()
def deletekeys():
    wipe('qb_id')
    wipe('qb_secret')
    wipe('qb_sandbox')


if __name__ == '__main__':
    cli()
