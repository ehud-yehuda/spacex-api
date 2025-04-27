import requests
from dataHolder.models import Launch, Payload
from db_server import dBServer
from typing import Optional
from enum import Enum

class Api(Enum):
    launch_url = "https://api.spacexdata.com/v5/launches"
    payloads_url = f"https://api.spacexdata.com/v5/payloads"

    def get(self):
        return self.value

    def add_latest(self):
        return f"{self.value}/latest"
    
    def add_id(self, _id):
        return f"{self.value}/{_id}"

    def get_model_type_by_url(self):
        if self == Api.launch_url:
            return Launch
        elif self == Api.payloads_url:
            return Payload
        else:
            raise NotImplementedError("Api::get_model_type_by_url(), Can't recognize this url")

class apiReader:
    def __init__(self, url:Api = Api.launch_url):
        self.existing_ids_list: list = []
        self.url = url

    def fetch_latest(self) -> Optional["Launch"]:
        launch = None
        url = self.url.add_latest()
        response = requests.get(url)
        
        response.raise_for_status()
        if response.status_code == 200:
            data: dict = response.json()
            obj = self.url.get_model_type_by_url()
            model_obj = obj.load_from_json(data)
        else:
            print("Failed to fetch SpaceX data:", response.status_code)
        return model_obj
    
    def fetch_by_id(self, _id: str) -> Optional[Launch]:
        url = self.url.add_id(_id)
        response = requests.get(url)
        
        if response.status_code == 404:
            print(f"❌ ID {launch_id} not found (404). Skipping.")
            return None

        if response.status_code == 200:
            data = response.json()
            obj = self.url.get_model_type_by_url()
            model_obj = obj.load_from_json(data)
            return model_obj
        else:
            print(f"❌ Failed to fetch data {launch_id}. Status code: {response.status_code}")
            return None

    def fetch_all(self) -> list[Launch]:
        url = self.url.get()
        response = requests.get(url)

        models = []
        if response.status_code == 200:
            data = response.json()
            for _data in data:
                obj = self.url.get_model_type_by_url()
                model = obj.load_from_json(_data)
                if model:
                    models.append(model)
        else:
            print(f"❌ Failed to fetch all launches. Status code: {response.status_code}")

        return models
    
class LaunchSyncManager:
    def __init__(self, db_writer: dBServer):
        self.db_writer = db_writer
        self.launch_api_reader = apiReader()
        self.payloads_api_reader = apiReader(url=Api.payloads_url)
        self.existing_ids_list: list = []
    
    def is_new_data_updated_in_api(self, existing_ids=None):
        #spacex api have no push notification or other efficient way to update the service
        if existing_ids is None:
            existing_ids = []
        self.existing_ids_list = list(set(self.existing_ids_list + existing_ids))
        launch = self.launch_api_reader.fetch_latest()
        
        if launch is None or launch.id in self.existing_ids_list:
            return None
        print(f"🚀 New launch detected: '{launch.name}' (ID: {launch.id})")
        return launch
    
    def get_all_launches_ids(self) -> list:
        table_name, query = Launch.get_all_ids_query()
        res = self.db_writer.run_query(table_name=table_name, values_as_str=query)
        if len(res):
            res = [row[0] for row in res]
        else:
            res = None
        return res
    
    def sync_latest_launch(self) -> dict:
        ret = {
            "launch": None,
            "avg_pl_mass": None
        }
        # 1. Get existing launch IDs from database
        existing_ids = self.get_all_launches_ids()

        # 2. Check if a new launch is available
        new_launch = self.is_new_data_updated_in_api(existing_ids)

        if not new_launch:
            print("✅ No new launches to sync.")
            return ret
        
        print(f"🚀 New Launch '{new_launch.name}' detected, syncing to database...")

        # 3. Insert the new launch
        data = new_launch.get_data_dict_to_insert_sql_table()
        self.db_writer.insert_data_into_table(data)

        print(f"✅ Launch '{new_launch.name}' inserted successfully.")

        # Extract payload IDs
        payload_ids = new_launch.data_as_json.get("payloads", [])
        payloads = self.fetch_payloads(payload_ids=payload_ids)
        avg_pl_mass = self.get_payloads_avg_mass(payloads)
        
        for _payload in payloads:
            _d = _payload.get_data_dict_to_insert_sql_table()
            self.db_writer.insert_data_into_table(_d)

        ret["launch"] = new_launch
        ret["avg_pl_mass"] = avg_pl_mass

        return ret

    
    def fetch_payloads(self, payload_ids: list[str]) -> list[Payload]:
        payloads = []
        for pid in payload_ids:
            payload = self.payloads_api_reader.fetch_by_id(pid)
            if payload:
                payloads.append(payload)
        return payloads
    
    def get_payloads_avg_mass(self, list_of_payloads: list[Payload]) -> float:
        if not list_of_payloads:
            return 0.0

        payload_masses = [payload.get_payload_mass() for payload in list_of_payloads]
        avg_mass = sum(payload_masses) / len(payload_masses) if payload_masses else 0.0
        return avg_mass
        
