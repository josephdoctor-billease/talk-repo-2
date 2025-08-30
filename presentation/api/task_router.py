from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.task_dto import (
    TaskCreateDTO,
    TaskListResponseDTO,
    TaskResponseDTO,
    TaskUpdateDTO,
)
from domain.entities.task import Task
from domain.entities.user import User
from domain.value_objects.task_id import TaskId
from infrastructure.database.base import get_session
from infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
from presentation.middleware.auth import get_current_active_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_repository(
    session: AsyncSession = Depends(get_session),
) -> TaskRepositoryImpl:
    """Dependency to get task repository"""
    return TaskRepositoryImpl(session)


def task_to_response_dto(task: Task) -> TaskResponseDTO:
    """Convert Task entity to TaskResponseDTO"""
    return TaskResponseDTO(
        id=str(task.id),
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/", response_model=TaskListResponseDTO)
async def get_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    completed: bool = Query(None, description="Filter by completion status"),
    current_user: User = Depends(get_current_active_user),
    task_repository: TaskRepositoryImpl = Depends(get_task_repository),
):
    """Get user's tasks with pagination"""
    try:
        offset = (page - 1) * page_size

        if completed is not None:
            if completed:
                tasks = await task_repository.get_completed_by_user_id(
                    current_user.id, page_size, offset
                )
            else:
                tasks = await task_repository.get_pending_by_user_id(
                    current_user.id, page_size, offset
                )
        else:
            tasks = await task_repository.get_by_user_id(
                current_user.id, page_size, offset
            )

        total_count = await task_repository.count_by_user_id(current_user.id)
        has_next = offset + page_size < total_count

        task_dtos = [task_to_response_dto(task) for task in tasks]

        return TaskListResponseDTO(
            tasks=task_dtos,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=has_next,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving tasks",
        )


@router.get("/{task_id}", response_model=TaskResponseDTO)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    task_repository: TaskRepositoryImpl = Depends(get_task_repository),
):
    """Get a specific task"""
    try:
        task_id_obj = TaskId(task_id)
        task = await task_repository.get_by_id(task_id_obj)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        if not task.belongs_to_user(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        return task_to_response_dto(task)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID"
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving task",
        )


@router.post("/", response_model=TaskResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateDTO,
    current_user: User = Depends(get_current_active_user),
    task_repository: TaskRepositoryImpl = Depends(get_task_repository),
):
    """Create a new task"""
    try:
        task = Task.create(
            user_id=current_user.id,
            title=task_data.title,
            description=task_data.description,
        )

        created_task = await task_repository.create(task)
        return task_to_response_dto(created_task)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating task",
        )


@router.put("/{task_id}", response_model=TaskResponseDTO)
async def update_task(  # noqa: C901
    task_id: str,
    task_data: TaskUpdateDTO,
    current_user: User = Depends(get_current_active_user),
    task_repository: TaskRepositoryImpl = Depends(get_task_repository),
):
    """Update a task"""
    try:
        task_id_obj = TaskId(task_id)
        task = await task_repository.get_by_id(task_id_obj)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        if not task.belongs_to_user(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        # Update fields
        update_data = task_data.model_dump(exclude_unset=True)

        if "title" in update_data:
            task.update_title(update_data["title"])

        if "description" in update_data:
            task.update_description(update_data["description"])

        if "completed" in update_data:
            if update_data["completed"]:
                task.mark_completed()
            else:
                task.mark_incomplete()

        updated_task = await task_repository.update(task)
        return task_to_response_dto(updated_task)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating task",
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    task_repository: TaskRepositoryImpl = Depends(get_task_repository),
):
    """Delete a task"""
    try:
        task_id_obj = TaskId(task_id)
        task = await task_repository.get_by_id(task_id_obj)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        if not task.belongs_to_user(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        await task_repository.delete(task_id_obj)
        return None

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID"
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting task",
        )
