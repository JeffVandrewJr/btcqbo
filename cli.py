import click
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
    click.echo(refresh_stored_tokens())


@cli.command()
def printqb():
    # prints QBO API keys and token to screen
    click.echo(fetch('qb_id'))
    click.echo(fetch('qb_secret'))
    click.echo(fetch('qb_sandbox'))
    click.echo(os.getenv('CALLBACK_URL'))


@cli.command()
def deletekeys():
    # wipes all QBO API keys from redis storage
    wipe('qb_id')
    wipe('qb_secret')
    wipe('qb_sandbox')


if __name__ == '__main__':
    cli()
