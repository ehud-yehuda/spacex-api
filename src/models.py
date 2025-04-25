from pydantic import BaseModel, ValidationError
from typing import Optional



class Models(BaseModel):
    table_name: str = ""
    columns_type: dict = {}

    @classmethod
    def load_from_json(cls, data_as_json: dict) -> Optional["Launch"]:
        try:
            return cls.model_validate(data_as_json)
        except ValidationError as e:
            print("Models::load_from_json(), Data is not valid")
            print(e)
            return None

    def get_columns_types(self):
        return list(self.columns_type.values())

    def get_columns_names(self):
        return list(self.columns_type.keys())
    
    def get_data_to_create_sql_table(self):
        ret = {}
        ret["table_name"] = self.table_name
        ret["table_columns_names"] = self.get_columns_names()
        ret["table_columns_types"] = self.get_columns_types()
        return ret


class Launch(Models):
    table_name: str = "launches"
    columns_type: dict = {
        "id": 'TEXT PRIMARY KEY',
        "name": 'TEXT NOT NULL',
        "date_utc": 'TIMESTAMPTZ NOT NULL',
        "success": 'BOOLEAN',
        "rocket": 'TEXT NOT NULL',
        "details": 'TEXT',
        "launch_as_json": 'JSONB NOT NULL'
    }
    id: str
    name: str
    date_utc: str
    success: bool
    rocket: str
    details: Optional[str]

