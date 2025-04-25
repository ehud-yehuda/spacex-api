from pydantic import BaseModel, ValidationError
from typing import Optional
from data_holder_interface import dataHolderInterface


class Launch(dataHolderInterface, BaseModel):
    table_name: str = "launches"
    columns_type: dict = {
        "id": 'TEXT PRIMARY KEY',
        "name": 'TEXT NOT NULL',
        "date_utc": 'TIMESTAMPTZ NOT NULL',
        "success": 'BOOLEAN',
        "rocket": 'TEXT NOT NULL',
        "details": 'TEXT',
        "data_as_json": 'JSONB NOT NULL'
    }
    id: str
    name: str
    date_utc: str
    success: bool
    rocket: str
    details: Optional[str]

    @classmethod
    def load_from_json(cls, data_as_json: dict) -> Optional["Launch"]:
        try:
            cls._raw_json = data_as_json
            return cls.model_validate(data_as_json)
        except ValidationError as e:
            print("Models::load_from_json(), Data is not valid")
            print(e)
            return None

    def get_all_values(self) -> list:
        return [
            self.id,
            self.name,
            self.date_utc,
            self.success,
            self.rocket,
            self.details,
            self._raw_json  
        ]

