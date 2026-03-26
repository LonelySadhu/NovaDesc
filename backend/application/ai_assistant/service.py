from typing import AsyncIterator, Optional
from uuid import UUID

from domain.ai_assistant.entities import AIQuery
from domain.ai_assistant.ports import AIProviderPort
from domain.equipment.repositories import EquipmentRepository
from domain.work_orders.repositories import WorkOrderRepository
from application.knowledge_base.search_chunks import SearchChunksUseCase


class AIAssistantService:
    def __init__(
        self,
        ai_provider: AIProviderPort,
        equipment_repo: EquipmentRepository,
        work_order_repo: WorkOrderRepository,
        search_chunks: Optional[SearchChunksUseCase] = None,
    ):
        self._ai = ai_provider
        self._equipment_repo = equipment_repo
        self._work_order_repo = work_order_repo
        self._search_chunks = search_chunks

    async def ask(
        self,
        user_id: UUID,
        question: str,
        equipment_id: Optional[UUID] = None,
        work_order_id: Optional[UUID] = None,
    ) -> AIQuery:
        context = await self._build_context(question, equipment_id, work_order_id)
        answer = await self._ai.ask(question, context)

        query = AIQuery(
            user_id=user_id,
            question=question,
            context_equipment_id=equipment_id,
            context_work_order_id=work_order_id,
        )
        query.set_answer(answer=answer, model="unknown", tokens=0)
        return query

    async def ask_stream(
        self,
        user_id: UUID,
        question: str,
        equipment_id: Optional[UUID] = None,
        work_order_id: Optional[UUID] = None,
    ) -> AsyncIterator[str]:
        context = await self._build_context(question, equipment_id, work_order_id)
        async for chunk in self._ai.ask_stream(question, context):
            yield chunk

    async def _build_context(
        self,
        question: str,
        equipment_id: Optional[UUID],
        work_order_id: Optional[UUID],
    ) -> str:
        parts = []

        if equipment_id:
            equipment = await self._equipment_repo.get_by_id(equipment_id)
            if equipment:
                parts.append(
                    f"Equipment: {equipment.name}, Model: {equipment.model}, "
                    f"Manufacturer: {equipment.manufacturer}, "
                    f"Serial: {equipment.serial_number}, "
                    f"Location: {equipment.location}, "
                    f"Status: {equipment.status}"
                )

        if work_order_id:
            work_order = await self._work_order_repo.get_by_id(work_order_id)
            if work_order:
                parts.append(
                    f"Work Order: {work_order.title}, "
                    f"Type: {work_order.order_type}, "
                    f"Priority: {work_order.priority}, "
                    f"Status: {work_order.status}, "
                    f"Description: {work_order.description}"
                )

        # RAG: retrieve relevant document chunks and prepend to context
        if self._search_chunks:
            rag_context = await self._search_chunks.build_context(
                query=question,
                equipment_id=equipment_id,
            )
            if rag_context:
                parts.insert(0, f"Relevant documentation:\n{rag_context}")

        return "\n".join(parts)
