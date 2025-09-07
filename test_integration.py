import pytest
from fastapi import status

class TestSecurity:
    def test_user_isolation(self, client, auth_headers, second_user_headers, task_factory):
        # Usuario 1 crea una tarea
        task_data = {"title": "Private Task", "description": "Only for user 1"}
        response = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_id = response.json()["id"]

       
        response = client.get(f"/tasks/{task_id}", headers=second_user_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        
        update_data = {"title": "Hacked Task"}
        response = client.put(f"/tasks/{task_id}", json=update_data, headers=second_user_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        
        response = client.delete(f"/tasks/{task_id}", headers=second_user_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_protected_endpoints_require_auth(self, client, task_factory):
        task = task_factory(title="Test Task")
        
        
        endpoints = [
            ("GET", "/tasks/"),
            ("GET", f"/tasks/{task.id}"),
            ("POST", "/tasks/", {"title": "Test"}),
            ("PUT", f"/tasks/{task.id}", {"title": "Updated"}),
            ("DELETE", f"/tasks/{task.id}"),
            ("GET", "/auth/me"),
        ]
        
        for method, path, *data in endpoints:
            if method == "GET":
                response = client.get(path)
            elif method == "POST":
                response = client.post(path, json=data[0] if data else {})
            elif method == "PUT":
                response = client.put(path, json=data[0] if data else {})
            elif method == "DELETE":
                response = client.delete(path)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_rejected(self, client):
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expired_token_rejected(self, client, test_user):
        # Crear un token expirado (usando freezegun o similar)
        with pytest.MonkeyPatch().context() as m:
            m.setattr("app.auth.ACCESS_TOKEN_EXPIRE_MINUTES", -1)  # Token expirado
            from auth import create_access_token
            expired_token = create_access_token({"sub": test_user.email})
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED