import pytest
from fastapi import status

class TestTasksCRUD:
    def test_create_task_success(self, client, auth_headers):
        task_data = {
            "title": "New Task",
            "description": "Task description",
            "priority": "high"
        }
        response = client.post("/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        created_task = response.json()
        assert created_task["title"] == task_data["title"]
        assert created_task["description"] == task_data["description"]
        assert created_task["priority"] == task_data["priority"]
        assert "id" in created_task
        assert "created_at" in created_task

    def test_create_task_no_auth(self, client):
        task_data = {
            "title": "New Task",
            "description": "Task description",
            "priority": "high"
        }
        response = client.post("/tasks/", json=task_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("task_data, expected_status", [
        ({"description": "Only description"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"title": "Short", "description": "x" * 1001}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"title": "Valid", "description": "Valid", "priority": "invalid"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ])
    def test_create_task_validation_errors(self, client, auth_headers, task_data, expected_status):
        response = client.post("/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == expected_status

    def test_get_task_by_id(self, client, auth_headers, task_factory):
        task = task_factory(title="Test Task")
        
        response = client.get(f"/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        retrieved_task = response.json()
        assert retrieved_task["id"] == task.id
        assert retrieved_task["title"] == "Test Task"

    def test_get_nonexistent_task(self, client, auth_headers):
        response = client.get("/tasks/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_tasks_list(self, client, auth_headers, task_factory):
        # Crear varias tareas
        task_factory(title="Task 1")
        task_factory(title="Task 2")
        task_factory(title="Task 3")
        
        response = client.get("/tasks/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        tasks = response.json()
        assert isinstance(tasks, list)
        assert len(tasks) == 3

    def test_update_task_success(self, client, auth_headers, task_factory):
        task = task_factory(title="Original Title")
        
        update_data = {"title": "Updated Title", "description": "Updated description"}
        response = client.put(f"/tasks/{task.id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        updated_task = response.json()
        assert updated_task["title"] == update_data["title"]
        assert updated_task["description"] == update_data["description"]

    def test_update_nonexistent_task(self, client, auth_headers):
        update_data = {"title": "Updated Title"}
        response = client.put("/tasks/999", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_success(self, client, auth_headers, task_factory):
        task = task_factory(title="Task to delete")
        
        response = client.delete(f"/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verificar que la tarea fue eliminada
        response = client.get(f"/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_task(self, client, auth_headers):
        response = client.delete("/tasks/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND