import requests
from dataHolder.models import Launch
from db_server import dBServer
from typing import Optional


url = "https://api.spacexdata.com/v5/launches"

class apiReader:
    def __init__(self, url: str):
        self.url: str = url
        self.existing_ids_list: list = []

    def fetch_latest_spacex_launch(self) -> Optional["Launch"]:
        launch = None
        url = f"{self.url}/latest"
        response = requests.get(url)
        
        response.raise_for_status()
        if response.status_code == 200:
            data: dict = response.json()
            launch = Launch.load_from_json(data)
        else:
            print("Failed to fetch SpaceX data:", response.status_code)
        return launch
    
    def fetch_launch_by_id(self, launch_id: str) -> Optional[Launch]:
        url = f"{self.url}/{launch_id}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            launch = Launch.load_from_json(data)
            return launch
        else:
            print(f"❌ Failed to fetch launch {launch_id}. Status code: {response.status_code}")
            return None

    def fetch_all_launches(self) -> list[Launch]:
        url = f"{self.url}"
        response = requests.get(url)

        launches = []
        if response.status_code == 200:
            data = response.json()
            for launch_data in data:
                launch = Launch.load_from_json(launch_data)
                if launch:
                    launches.append(launch)
        else:
            print(f"❌ Failed to fetch all launches. Status code: {response.status_code}")

        return launches
    
class LaunchSyncManager:
    def __init__(self, db_writer: dBServer):
        self.db_writer = db_writer
        self.api_reader = apiReader(url)
        self.existing_ids_list: list = []
    
    def is_new_data_updated_in_api(self, existing_ids=None):
        #spacex api have no push notification or other efficient way to update the service
        if existing_ids is None:
            existing_ids = []
        self.existing_ids_list = list(set(self.existing_ids_list + existing_ids))
        launch = self.api_reader.fetch_latest_spacex_launch()
        
        if launch is None or launch.id in self.existing_ids_list:
            return None
        print(f"🚀 New launch detected: '{launch.name}' (ID: {launch.id})")
        return launch
    
    def get_all_launches_ids(self) -> list:
        table_name, query = Launch.get_all_ids_query()
        res = self.db_writer.run_query(table_name=table_name, values_as_str=query)
        if len(res):
            res = [res[0][0]]
        else:
            res = None
        return res
    
    def sync_latest_launch(self):
        # 1. Get existing launch IDs from database
        existing_ids = self.get_all_launches_ids()

        # 2. Check if a new launch is available
        new_launch = self.is_new_data_updated_in_api(existing_ids)

        if not new_launch:
            print("✅ No new launches to sync.")
            return
        
        print(f"🚀 New Launch '{new_launch.name}' detected, syncing to database...")

        # 3. Insert the new launch
        data = new_launch.get_data_dict_to_insert_sql_table()
        self.db_writer.insert_data_into_table(data)

        print(f"✅ Launch '{new_launch.name}' inserted successfully.")
        return new_launch
        
