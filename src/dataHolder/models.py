from pydantic import BaseModel, ValidationError
from typing import Optional, ClassVar
from dataHolder.data_holder_interface import dataHolderInterface
from datetime import datetime


class Launch(dataHolderInterface, BaseModel):
    table_name: ClassVar[str] = "launches"
    columns_type: ClassVar[dict] = {
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
    data_as_json: Optional[dict] = None


    def get_launch_delay(self) -> float:
        delay_time = -1.0
        actual_time_launching = self.data_as_json.get("date_utc")
        launch_time_scheduele = self.data_as_json.get("date_local")

        if actual_time_launching and launch_time_scheduele:
            dt_utc = datetime.fromisoformat(actual_time_launching.replace("Z", "+00:00"))
            dt_local = datetime.fromisoformat(launch_time_scheduele.replace("Z", "+00:00"))
            
            delay_time = (dt_utc - dt_local).total_seconds() / 60.0  # Delay in minutes
        else:
            print("⚠️ Missing 'date_utc' or 'date_local' in API data, setting delay_time=0")
        return delay_time
    
    def get_payloads_ids(self):
        return self.data_as_json.get("payloads", [])

    @classmethod
    def load_from_json(cls, data_as_json: dict) -> Optional["Launch"]:
        try:
            obj = cls.model_validate(data_as_json)
            obj.data_as_json = data_as_json  # Attach _raw_json to the object, not class
            return obj
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
            self.data_as_json  
        ]
    
    @staticmethod
    def get_all_ids_query():
        return Launch.table_name, "id"




class Payload(dataHolderInterface, BaseModel):
    table_name: ClassVar[str] = "payloads"
    columns_type: ClassVar[dict] = {
        "id": 'TEXT PRIMARY KEY',
        "name": 'TEXT',
        "type": 'TEXT',
        "mass_kg": 'NUMERIC',
        "mass_lbs": 'NUMERIC',
        "orbit": 'TEXT',
        "data_as_json": 'JSONB NOT NULL'
    }

    id: str
    name: Optional[str]
    type: Optional[str]
    mass_kg: Optional[float]
    mass_lbs: Optional[float]
    orbit: Optional[str]
    data_as_json: Optional[dict] = None
    
    @classmethod
    def load_from_json(cls, data_as_json: dict) -> Optional["Payload"]:
        try:
            obj = cls.model_validate(data_as_json)
            obj.data_as_json = data_as_json
            return obj
        except ValidationError as e:
            print("Payload::load_from_json(), Data is not valid")
            print(e)
            return None
    
    def get_payload_mass(self, unit: str = "kg", default_value: float = 0.0) -> float:
        """
        Returns the payload mass.
        
        Args:
            unit (str): "kg" for kilograms, "lbs" for pounds.
            default_value (float): Value to return if mass is missing.
            
        Returns:
            float: Payload mass in requested unit.
        """
        if unit == "kg":
            return self.mass_kg if self.mass_kg is not None else default_value
        elif unit == "lbs":
            return self.mass_lbs if self.mass_lbs is not None else default_value
        else:
            raise ValueError(f"Unsupported mass unit: {unit}. Use 'kg' or 'lbs'.")

    @classmethod
    def load_from_json(cls, data_as_json: dict) -> Optional["Launch"]:
        try:
            obj = cls.model_validate(data_as_json)
            obj.data_as_json = data_as_json  # Attach _raw_json to the object, not class
            return obj
        except ValidationError as e:
            print("Models::load_from_json(), Data is not valid")
            print(e)
            return None
        
    def get_all_values(self) -> list:
        return [
            self.id,
            self.name,
            self.type,
            self.mass_kg,
            self.mass_lbs,
            self.orbit,
            self.data_as_json
        ]
    
    @staticmethod
    def get_all_ids_query():
        return Payload.table_name, "id"