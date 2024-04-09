from pydantic import BaseModel
from abc import ABC, abstractmethod

from src.database.db import Base


class BaseFilterData(ABC):
    model: Base = None

    @abstractmethod
    def get_filter_data(self):
        ...
