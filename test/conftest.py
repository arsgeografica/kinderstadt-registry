import pytest
from flask.ext import migrate as migrate_extension
import testing.postgresql
from registry.app import factory


@pytest.fixture(scope="session")
def database(request):
    # Create PostgreSQL server on the fly
    postgresql = testing.postgresql.Postgresql()

    def fin():
        postgresql.stop()

    request.addfinalizer(fin)

    return postgresql


@pytest.fixture
def app(request, database):
    # And override the database URL
    app = factory('registry.config.testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = database.url()

    # Set up schema
    with app.app_context():
        migrate_extension.upgrade(revision='head')

    def fin():
        with app.app_context():
            migrate_extension.downgrade(revision='base')

    request.addfinalizer(fin)

    return app
