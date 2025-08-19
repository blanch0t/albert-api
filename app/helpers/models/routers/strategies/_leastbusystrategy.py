from typing import List, TYPE_CHECKING, Literal, Tuple, Dict
from datetime import datetime, timedelta
import math
import random

from app.helpers.models.routers.strategies import BaseRoutingStrategy

if TYPE_CHECKING:
    # only for type‐checkers and linters, not at runtime
    # Used to break circular import
    from app.clients.model import BaseModelClient


class LeastBusyRoutingStrategy(BaseRoutingStrategy):
    def __init__(
        self, clients: List["BaseModelClient"],
        metric_type: Literal["time_to_first_token", "latency"]
    ) -> None:
        super().__init__(clients)
        self.metric_type: Literal["time_to_first_token", "latency"] = metric_type

    @staticmethod
    def get_percentile(series: List[Tuple[int, float]], percentile: float = 0.95) -> float:
        """
        Return a value such that at least 95% of series values are smaller.
        series: list of (datetime, value) tuples
        """
        if not series:
            raise ValueError("Series is empty")

        values = [v for _, v in series]
        values.sort()

        idx = math.ceil(percentile * len(values)) - 1
        return values[idx]

    async def get_server_score(self, client: "BaseModelClient") -> float:
        cutoff = datetime.now() - timedelta(hours=1)
        series = await client.get_timeseries_since(self.metric_type, cutoff)
        return LeastBusyRoutingStrategy.get_percentile(series)

    @staticmethod
    def least_busy(scores: Dict["BaseModelClient", float]) -> Tuple["BaseModelClient", float]:
        """
        scores is a dict of shape {url: score} for each server
        """
        min_value = min(scores.values())
        candidates = [k for k, v in scores.items() if v == min_value]
        return random.choice(candidates), min_value

    async def choose_model_client(self) -> Tuple["BaseModelClient", float | None]:
        scores = {}
        for client in self.clients:
           scores[client] = await self.get_server_score(client) 
        return LeastBusyRoutingStrategy.least_busy(scores)

