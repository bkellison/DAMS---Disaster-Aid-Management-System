import pytest
from disaster_relief_app import create_app

@pytest.fixture
def app():
    app = create_app()
    yield app

#client
@pytest.fixture
def client(app):
    return app.test_client()