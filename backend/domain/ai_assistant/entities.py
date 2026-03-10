from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class AIQuery:
    user_id: UUID
    question: str
    context_equipment_id: Optional[UUID] = None
    context_work_order_id: Optional[UUID] = None
    answer: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: int = 0
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def set_answer(self, answer: str, model: str, tokens: int) -> None:
        self.answer = answer
        self.model_used = model
        self.tokens_used = tokens
