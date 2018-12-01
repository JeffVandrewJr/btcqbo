import click
from app.qbo import refresh_stored_tokens


@click.group()
def cli():
    pass


@cli.command()
def refresh():
    click.echo(refresh_stored_tokens())


if __name__ == '__main__':
    cli()
