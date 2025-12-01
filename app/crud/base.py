from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import Session


class BaseCRUD:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def wrap_element(model: type[BaseModel], result: Any) -> list[type[BaseModel]]:
        return [model.model_validate(result)]

    @staticmethod
    def wrap_elements(model: type[BaseModel], results: list) -> list[type[BaseModel]]:
        return [model.model_validate(result) for result in results]
