from dataHolder.data_holder_interface import dataHolderInterface
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar


@dataclass
class aggregateData(dataHolderInterface):
    table_name: str = "aggregate_data_table"
    columns_type: ClassVar[dict] = {
        "updated_timestamp": 'TIMESTAMPTZ PRIMARY KEY',
        "total_launches": 'INTEGER NOT NULL',
        "successful_launches": 'INTEGER NOT NULL',
        "avg_payload_mass": 'NUMERIC',
        "avg_launch_delay_minutes": 'NUMERIC',
        "last_updated_launch_date": 'TIMESTAMPTZ NOT NULL',
        "data_as_json": 'JSONB NOT NULL'
    }
    total_launches: int = 0
    total_successfull_launches: int = 0
    avg_payload_mass: float = 0.0
    avg_launch_delay: float = 0.0
    total_payload_mass: float = 0.0
    total_delay: float = 0.0
    launch_date: str = ""

    def update(self, is_successfull: bool, payload_mass: float, delay_time:float, launch_id: int, launch_date: str) -> dict:
        self.total_launches += 1
        self.total_successfull_launches += 1 if is_successfull else 0
        self.total_payload_mass += 0.0 if payload_mass is None else payload_mass
        self.total_delay += delay_time
        self.launch_date = launch_date 
        self.compute_avg_metrics()
        self.data_as_json = {
            "launch_id_updated": launch_id,
            "is_successfull": is_successfull,
            "payload_mass": payload_mass,
            "delay_time": delay_time
        }
        ret = self.get_data_dict_to_insert_sql_table()
        return ret

    def extract_data_from_launch_and_update(self, data_dict: dict) -> dict:
        launch_obj = data_dict["launch"]
        
        is_successfull = launch_obj.success
        payload_mass = data_dict["avg_pl_mass"]
        delay_time = launch_obj.get_launch_delay()
        launch_id = launch_obj.id
        launch_date = launch_obj.date_utc 
        ret = self.update(is_successfull=is_successfull,
                    payload_mass=payload_mass,
                    delay_time=delay_time,
                    launch_id=launch_id,
                    launch_date=launch_date)
        return ret

    def compute_avg_metrics(self):
        try:
            self.avg_payload_mass = self.total_payload_mass / self.total_launches
            self.avg_launch_delay = self.total_delay / self.total_launches
        except ZeroDivisionError as e:
            print("aggregateData::compute_avg_metrics(), cant compute metrics no data stored")
    
    def get_all_values(self) -> list:
        return [
            datetime.now(),
            self.total_launches,
            self.total_successfull_launches,
            self.avg_payload_mass,
            self.avg_launch_delay,
            self.launch_date,
            self.data_as_json  
        ]