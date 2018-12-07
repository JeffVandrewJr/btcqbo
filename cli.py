import click
import os
from app.qbo import refresh_stored_tokens
from app.utils import wipe, fetch


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
def deletekeys():
    wipe('qb_id')
    wipe('qb_secret')
    wipe('qb_sandbox')


if __name__ == '__main__':
    cli()
