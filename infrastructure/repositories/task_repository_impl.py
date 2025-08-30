from typing import List, Optional

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.task import Task
from domain.repositories.task_repository import TaskRepository
from domain.value_objects.task_id import TaskId
from domain.value_objects.user_id import UserId
from infrastructure.database.models import TaskModel


class TaskRepositoryImpl(TaskRepository):  # pragma: no cover
    def __init__(self, session: AsyncSession):  # pragma: no cover
        self.session = session

    def _model_to_entity(self, model: TaskModel) -> Task:  # pragma: no cover
        return Task(
            id=TaskId(model.id),
            user_id=UserId(model.user_id),
            title=model.title,
            description=model.description,
            completed=model.completed,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: Task) -> TaskModel:
        return TaskModel(
            id=str(entity.id),
            user_id=str(entity.user_id),
            title=entity.title,
            description=entity.description,
            completed=entity.completed,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, task: Task) -> Task:
        model = self._entity_to_model(task)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, task_id: TaskId) -> Optional[Task]:
        stmt = select(TaskModel).where(TaskModel.id == str(task_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_user_id(
        self, user_id: UserId, limit: int = 100, offset: int = 0
    ) -> List[Task]:
        stmt = (
            select(TaskModel)
            .where(TaskModel.user_id == str(user_id))
            .order_by(TaskModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def update(self, task: Task) -> Task:
        stmt = (
            update(TaskModel)
            .where(TaskModel.id == str(task.id))
            .values(
                title=task.title,
                description=task.description,
                completed=task.completed,
                updated_at=task.updated_at,
            )
            .returning(TaskModel)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one()
        return self._model_to_entity(model)

    async def delete(self, task_id: TaskId) -> bool:
        stmt = delete(TaskModel).where(TaskModel.id == str(task_id))
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def count_by_user_id(self, user_id: UserId) -> int:
        stmt = select(func.count(TaskModel.id)).where(TaskModel.user_id == str(user_id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_completed_by_user_id(
        self, user_id: UserId, limit: int = 100, offset: int = 0
    ) -> List[Task]:
        stmt = (
            select(TaskModel)
            .where(TaskModel.user_id == str(user_id), TaskModel.completed == True)
            .order_by(TaskModel.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_pending_by_user_id(
        self, user_id: UserId, limit: int = 100, offset: int = 0
    ) -> List[Task]:
        stmt = (
            select(TaskModel)
            .where(TaskModel.user_id == str(user_id), TaskModel.completed == False)
            .order_by(TaskModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
