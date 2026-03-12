import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_home_page(client):
    """Test that home page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Weather Monitoring System' in response.data

def test_history_endpoint(client):
    """Test history endpoint returns JSON"""
    response = client.get('/history')
    assert response.status_code == 200
    assert response.is_json
