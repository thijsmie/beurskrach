import click
from app import create_app, default_config

app = create_app(default_config())


@app.cli.command()
def initdb():
    from app import db
    db.create_all()
    db.session.commit()
    click.echo('tables initialized')

