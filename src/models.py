from pydantic import BaseModel, ValidationError
from typing import Optional



class Models(BaseModel):
    table_name: str = ""
    columns_type: dict = {
        "data_as_json": 'JSONB NOT NULL'
    }
    _raw_json: dict

    @classmethod
    def load_from_json(cls, data_as_json: dict) -> Optional["Launch"]:
        try:
            cls._raw_json = data_as_json
            return cls.model_validate(data_as_json)
        except ValidationError as e:
            print("Models::load_from_json(), Data is not valid")
            print(e)
            return None

    def get_columns_types(self):
        return list(self.columns_type.values())
    
    def get_fields(self):
        return self.get_columns_names()

    def get_columns_names(self):
        return list(self.columns_type.keys())
    
    def get_data_to_create_sql_table(self):
        ret = {}
        ret["table_name"] = self.table_name
        ret["table_columns_names"] = self.get_columns_names()
        ret["table_columns_types"] = self.get_columns_types()
        return ret
    
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
    
    def get_data_dict_to_insert_sql_table(self) -> dict:
        ret = {}
        ret["table_name"] = self.table_name
        ret["values"] = self.get_all_values()
        ret["fields"] = self.get_fields()
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
        "data_as_json": 'JSONB NOT NULL'
    }
    id: str
    name: str
    date_utc: str
    success: bool
    rocket: str
    details: Optional[str]

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

