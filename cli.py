import click
from app.qbo import refresh_stored_tokens
from getpass import getpass
from app.utils import save, wipe
from werkzeug.security import generate_password_hash


@click.group()
def cli():
    pass


@cli.command()
def refresh():
    click.echo(refresh_stored_tokens())


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


if __name__ == '__main__':
    cli()
