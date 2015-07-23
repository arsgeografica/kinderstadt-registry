from datetime import datetime, time, timedelta
import random
import click
from faker import Factory as FakerFactory
from registry.app import factory
from registry import extensions
from registry.models import Passport, Visit
from flask.ext import migrate as migrate_extension
from pgcli.main import PGCli


@click.group()
@click.option('--debug/--no-debug', default=True)
@click.option('--config', default='registry.config.development')
@click.pass_context
def cli(ctx, debug, config):
    """
    Registry Command Line Interface.
    """
    ctx.obj['DEBUG'] = debug
    ctx.obj['CONFIG'] = config


@cli.command()
@click.pass_context
def server(ctx):
    """
    Run the flask development server.
    """
    app = factory(ctx.obj['CONFIG'])
    app.run(debug=ctx.obj['DEBUG'])


@cli.command()
@click.pass_context
@click.option('--truncate', is_flag=True, default=False, help="Empty DB first")
def fake(ctx, truncate, num_passes=700):
    """
    Generate fake data
    """
    app = factory(ctx.obj['CONFIG'])
    db = extensions.db

    num_days = (app.config['END_DATE'] - app.config['START_DATE']).days + 1

    with app.app_context():
        faker = FakerFactory.create('de_DE')
        if truncate:
            Visit.query.delete()
            Passport.query.delete()
            db.session.commit()
        for i in range(num_passes):
            passport = Passport(
                pass_id=i+1,
                surname=faker.first_name(),
                name=faker.last_name(),
                age=random.randint(7, 14),
                phone=faker.phone_number()
            )
            db.session.add(passport)

            def gen_visit(passport, day, start, stop):
                a_hour = min(max(start, random.gauss(start + 2, 2)), stop)
                a = datetime.combine(app.config['START_DATE'], time()) \
                    + timedelta(days=day, hours=a_hour)
                b_hour = min(max(start, random.gauss(stop - 2, 2)), stop)
                b = datetime.combine(app.config['START_DATE'], time()) \
                    + timedelta(days=day, hours=b_hour)

                if a > b:
                    a, b = b, a
                visit = Visit(passport=passport, check_in=a, check_out=b)
                db.session.add(visit)

            # decide on first day
            first_day = int(min(max(0, random.gauss(2, 3)), num_days))
            # for each day, decide on one or two visits
            for day in range(first_day, num_days):
                if random.choice([False, True]) is True:
                    # if one, decide on entry and exit
                    gen_visit(passport, day, 9, 17)
                else:
                    # if two, decide on entry and exit for A and B
                    gen_visit(passport, day, 9, 12)
                    gen_visit(passport, day, 13, 17)
        db.session.commit()


@cli.group()
@click.pass_context
def db(ctx):
    pass


@db.command()
@click.pass_context
def shell(ctx):
    """Run database shell"""
    app = factory(ctx.obj['CONFIG'])
    with app.app_context():
        pgcli = PGCli()
        database = str(app.extensions['sqlalchemy'].db.engine.url)
        pgcli.connect_uri(database)
        pgcli.logger.debug('Launch Params: \n\tdatabase: %r', database)
        pgcli.run_cli()


@db.command()
@click.pass_context
def init(ctx):
    """Init migrations system"""
    app = factory(ctx.obj['CONFIG'])
    with app.app_context():
        migrate_extension.init()


@db.command()
@click.pass_context
@click.option('--rev-id', default=None, help='Specify a hardcoded revision '
              'id instead of generating one')
@click.option('--version-path', default=None, help='Specify specific path '
              'from config for version file')
@click.option('--branch-label', default=None, help='Specify a branch label '
              'to apply to the new revision')
@click.option('--splice', is_flag=True, default=False, help='Allow a non-head '
              'revision as the "head" to splice onto')
@click.option('--head', default='head', help='Specify head revision or '
              '<branchname>@head to base new revision on')
@click.option('--sql', is_flag=True, default=False, help="Don't emit SQL to "
              "database - dump to standard output instead")
@click.option('--autogenerate/--no-autogenerate', default=True,
              help='Populate revision script with andidate migration '
              'operatons, based on comparison of database to model')
@click.option('-m', '--message', default=None)
def revision(ctx, rev_id, version_path, branch_label, splice, head, sql,
             autogenerate, message):
    """Create database revision"""
    app = factory(ctx.obj['CONFIG'])
    with app.app_context():
        migrate_extension.revision(
            message=message,
            autogenerate=autogenerate,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id
        )


@db.command()
@click.pass_context
@click.option('--rev-id', default=None, help='Specify a hardcoded revision id '
              'instead of generating one')
@click.option('--version-path', default=None, help='Specify specific path '
              'from config for version file')
@click.option('--branch-label', default=None, help='Specify a branch label to '
              'apply to the new revision')
@click.option('--splice', is_flag=True, default=False, help='Allow a non-head '
              'revision as the "head" to splice onto')
@click.option('--head', default='head', help='Specify head revision or '
              '<branchname>@head to base new revision on')
@click.option('--sql', is_flag=True, default=False, help="Don't emit SQL to "
              "database - dump to standard output instead")
@click.option('-m', '--message', default=None)
def migrate(ctx, rev_id, version_path, branch_label, splice, head, sql,
            message):
    app = factory(ctx.obj['CONFIG'])
    with app.app_context():
        migrate_extension.migrate(
            message=message,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id)


@db.command()
@click.pass_context
@click.option('--tag', default=None, help="Arbitrary 'tag' name - can be "
              "used by custom env.py scripts")
@click.option('--sql', is_flag=True, default=False, help="Don't emit SQL to "
              "database - dump to standard output instead")
@click.argument('revision', nargs=-1)
def upgrade(ctx, tag, sql, revision):
    """Upgrade database"""
    if not len(revision):
        revision = ('head',)

    app = factory(ctx.obj['CONFIG'])
    with app.app_context():
        migrate_extension.upgrade(revision=revision, sql=sql, tag=tag)


@db.command()
@click.pass_context
@click.option('--tag', default=None, help="Arbitrary 'tag' name - can be "
              "used by custom env.py scripts")
@click.option('--sql', is_flag=True, default=False, help="Don't emit SQL to "
              "database - dump to standard output instead")
@click.argument('revision', nargs=-1)
def downgrade(ctx, tag, sql, revision):
    """Downgrade database"""
    if not len(revision):
        revision = '-1'
    app = factory(ctx.obj['CONFIG'])
    with app.app_context():
        migrate_extension.downgrade(revision=revision, sql=sql, tag=tag)


def main():
    """
    setuptools console_script entrypoint.
    """
    cli(obj={})


if __name__ == '__main__':
    main()
