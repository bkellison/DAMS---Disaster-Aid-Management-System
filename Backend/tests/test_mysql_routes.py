from disaster_relief_app import create_app, db
from disaster_relief_app.api.mysql_routes import api_routes, SECRET_KEY
from disaster_relief_app.utils import get_db
import pytest


#do to - fix test
# def test_request_new_account_success(client, mocker):
#     """Test successful account request."""
#     mock_db = mocker.patch('disaster_relief_app.utils.get_db')
#     mock_db.session.execute.return_value.fetchone.return_value = None
#     mock_db.session.commit.return_value = None
#     #test that rollback was successful??  db.session.rollback()

#     payload = {
#         "username": "testuser",
#         "password": "password123",
#         "role": "user",
#         "email": "test@example.com"
#     }
#     response = client.post('/requestNewAccount', json=payload)
    
#     assert response.status_code == 201
#     assert response.json["message"] == "Account request created successfully"