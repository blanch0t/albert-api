import random
from typing import List, TYPE_CHECKING, Tuple

from app.helpers.models.routers.strategies import BaseRoutingStrategy


if TYPE_CHECKING:
    # only for type‐checkers and linters, not at runtime
    # Used to break circular import
    from app.clients.model import BaseModelClient


class ShuffleRoutingStrategy(BaseRoutingStrategy):
    def __init__(self, clients: List["BaseModelClient"]) -> None:
        super().__init__(clients)

    async def choose_model_client(self) -> Tuple["BaseModelClient", float | None]:
        return random.choice(self.clients), None
