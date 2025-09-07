import pytest
from fastapi import status
# from app.models import User  # Removed unused import or fix path if needed

class TestAuth:
    def test_register_success(self, client):
        user_data = {
            "email": "test@example.com",
            "password": "securepass123",
            "full_name": "Test User"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == user_data["email"]
        assert "id" in response.json()
        assert "password" not in response.json()

    def test_register_duplicate_email(self, client, test_user):
        user_data = {
            "email": test_user.email,
            "password": "securepass123",
            "full_name": "Test User"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.parametrize("user_data, expected_error", [
        ({"email": "invalid-email", "password": "pass123", "full_name": "Test"}, "email"),
        ({"email": "test@example.com", "password": "short", "full_name": "Test"}, "password"),
        ({"email": "test@example.com", "password": "validpass123", "full_name": ""}, "full_name"),
    ])
    def test_register_validation_errors(self, client, user_data, expected_error):
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert any(expected_error in error["loc"] for error in response.json()["detail"])

    def test_login_success(self, client, test_user):
        login_data = {
            "username": test_user.email,
            "password": "testpassword"  # Contraseña por defecto del fixture
        }
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        login_data = {
            "username": "nonexistent@example.com",
            "password": "anypassword"
        }
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_get_current_user(self, client, auth_headers, test_user):
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == test_user.email
        assert response.json()["full_name"] == test_user.full_name

    def test_get_current_user_no_auth(self, client):
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED