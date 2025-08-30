"""
Integration tests for task endpoints.
"""

import pytest
from httpx import AsyncClient


class TestTaskEndpoints:
    """Integration tests for task API endpoints."""

    @pytest.mark.integration
    async def test_create_task_success(self, authenticated_client, task_factory):
        """Test successful task creation."""
        client, auth_data = authenticated_client
        task_data = task_factory(title="Test Task", description="This is a test task")

        response = await client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert data["updated_at"] is None

    @pytest.mark.integration
    async def test_create_task_without_description(self, authenticated_client):
        """Test creating task without description."""
        client, auth_data = authenticated_client
        task_data = {"title": "Task without description"}

        response = await client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Task without description"
        assert data["description"] is None

    @pytest.mark.integration
    async def test_create_task_unauthorized(self, client: AsyncClient, task_factory):
        """Test creating task without authentication."""
        task_data = task_factory()

        response = await client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"

    @pytest.mark.integration
    async def test_create_task_empty_title(self, authenticated_client):
        """Test creating task with empty title."""
        client, auth_data = authenticated_client
        task_data = {"title": "", "description": "Valid description"}

        response = await client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == 422  # FastAPI returns 422 for validation errors
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    async def test_create_task_title_too_long(self, authenticated_client):
        """Test creating task with title too long."""
        client, auth_data = authenticated_client
        long_title = "x" * 201  # 201 characters
        task_data = {"title": long_title, "description": "Valid description"}

        response = await client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == 422  # FastAPI returns 422 for validation errors
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    async def test_get_tasks_empty_list(self, authenticated_client):
        """Test getting tasks when user has no tasks."""
        client, auth_data = authenticated_client

        response = await client.get("/api/v1/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total_count"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["has_next"] is False

    @pytest.mark.integration
    async def test_get_tasks_with_data(self, authenticated_client, task_factory):
        """Test getting tasks when user has tasks."""
        client, auth_data = authenticated_client

        # Create a few tasks
        task_data1 = task_factory(title="Task 1")
        task_data2 = task_factory(title="Task 2")

        await client.post("/api/v1/tasks/", json=task_data1)
        await client.post("/api/v1/tasks/", json=task_data2)

        response = await client.get("/api/v1/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 2
        assert data["total_count"] == 2
        assert data["page"] == 1
        assert data["has_next"] is False

        # Check task titles (order might vary)
        task_titles = [task["title"] for task in data["tasks"]]
        assert "Task 1" in task_titles
        assert "Task 2" in task_titles

    @pytest.mark.integration
    async def test_get_tasks_pagination(self, authenticated_client, task_factory):
        """Test task pagination."""
        client, auth_data = authenticated_client

        # Create multiple tasks
        for i in range(5):
            task_data = task_factory(title=f"Task {i+1}")
            await client.post("/api/v1/tasks/", json=task_data)

        # Get first page with page_size=2
        response = await client.get("/api/v1/tasks/?page=1&page_size=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 2
        assert data["total_count"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["has_next"] is True

    @pytest.mark.integration
    async def test_get_tasks_filter_completed(self, authenticated_client, task_factory):
        """Test filtering tasks by completion status."""
        client, auth_data = authenticated_client

        # Create completed and pending tasks
        completed_task = task_factory(title="Completed Task")
        pending_task = task_factory(title="Pending Task")

        # Create tasks
        completed_response = await client.post("/api/v1/tasks/", json=completed_task)
        completed_task_id = completed_response.json()["id"]
        await client.post("/api/v1/tasks/", json=pending_task)

        # Mark one task as completed
        await client.put(f"/api/v1/tasks/{completed_task_id}", json={"completed": True})

        # Filter for completed tasks
        response = await client.get("/api/v1/tasks/?completed=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["completed"] is True

        # Filter for pending tasks
        response = await client.get("/api/v1/tasks/?completed=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["completed"] is False

    @pytest.mark.integration
    async def test_get_task_by_id_success(self, authenticated_client, task_factory):
        """Test getting specific task by ID."""
        client, auth_data = authenticated_client
        task_data = task_factory(title="Specific Task")

        create_response = await client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/tasks/{task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == task_data["title"]

    @pytest.mark.integration
    async def test_get_task_by_id_not_found(self, authenticated_client):
        """Test getting non-existent task."""
        client, auth_data = authenticated_client
        fake_task_id = "123e4567-e89b-12d3-a456-426614174000"

        response = await client.get(f"/api/v1/tasks/{fake_task_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Task not found"

    @pytest.mark.integration
    async def test_get_task_by_id_invalid_uuid(self, authenticated_client):
        """Test getting task with invalid UUID format."""
        client, auth_data = authenticated_client

        response = await client.get("/api/v1/tasks/invalid-uuid")

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Invalid task ID"

    @pytest.mark.integration
    async def test_update_task_success(self, authenticated_client, task_factory):
        """Test successful task update."""
        client, auth_data = authenticated_client
        task_data = task_factory(title="Original Title")

        create_response = await client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "completed": True,
        }

        response = await client.put(f"/api/v1/tasks/{task_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["completed"] is True
        assert data["updated_at"] is not None

    @pytest.mark.integration
    async def test_update_task_partial(self, authenticated_client, task_factory):
        """Test partial task update."""
        client, auth_data = authenticated_client
        task_data = task_factory(
            title="Original Title", description="Original description"
        )

        create_response = await client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Only update title
        update_data = {"title": "Only Title Updated"}

        response = await client.put(f"/api/v1/tasks/{task_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Only Title Updated"
        assert data["description"] == task_data["description"]  # Unchanged
        assert data["completed"] is False  # Unchanged

    @pytest.mark.integration
    async def test_update_task_not_found(self, authenticated_client):
        """Test updating non-existent task."""
        client, auth_data = authenticated_client
        fake_task_id = "123e4567-e89b-12d3-a456-426614174000"

        update_data = {"title": "Updated Title"}
        response = await client.put(f"/api/v1/tasks/{fake_task_id}", json=update_data)

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Task not found"

    @pytest.mark.integration
    async def test_delete_task_success(self, authenticated_client, task_factory):
        """Test successful task deletion."""
        client, auth_data = authenticated_client
        task_data = task_factory(title="Task to Delete")

        create_response = await client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/tasks/{task_id}")

        assert response.status_code == 204

        # Verify task is deleted
        get_response = await client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 404

    @pytest.mark.integration
    async def test_delete_task_not_found(self, authenticated_client):
        """Test deleting non-existent task."""
        client, auth_data = authenticated_client
        fake_task_id = "123e4567-e89b-12d3-a456-426614174000"

        response = await client.delete(f"/api/v1/tasks/{fake_task_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Task not found"

    @pytest.mark.integration
    async def test_task_ownership_isolation(
        self, client: AsyncClient, user_factory, task_factory
    ):
        """Test that users can only access their own tasks."""
        # Create two users
        user1_data = user_factory(email="user1@example.com", username="user1")
        user2_data = user_factory(email="user2@example.com", username="user2")

        # Sign up both users
        await client.post("/api/v1/auth/signup", json=user1_data)
        await client.post("/api/v1/auth/signup", json=user2_data)

        # Login as user1
        login1_response = await client.post(
            "/api/v1/auth/login",
            json={"email": user1_data["email"], "password": user1_data["password"]},
        )
        user1_token = login1_response.json()["tokens"]["access_token"]

        # Login as user2
        login2_response = await client.post(
            "/api/v1/auth/login",
            json={"email": user2_data["email"], "password": user2_data["password"]},
        )
        user2_token = login2_response.json()["tokens"]["access_token"]

        # Create task as user1
        client.headers.update({"Authorization": f"Bearer {user1_token}"})
        task_data = task_factory(title="User1 Task")
        create_response = await client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]

        # Try to access task as user2
        client.headers.update({"Authorization": f"Bearer {user2_token}"})

        # Should not be able to get the task
        get_response = await client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 403

        # Should not be able to update the task
        update_response = await client.put(
            f"/api/v1/tasks/{task_id}", json={"title": "Hacked"}
        )
        assert update_response.status_code == 403

        # Should not be able to delete the task
        delete_response = await client.delete(f"/api/v1/tasks/{task_id}")
        assert delete_response.status_code == 403

        # User2 should see empty task list
        list_response = await client.get("/api/v1/tasks/")
        assert list_response.status_code == 200
        assert len(list_response.json()["tasks"]) == 0
