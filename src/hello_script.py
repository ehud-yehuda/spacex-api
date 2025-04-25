import requests
from dataHolder.models import Launch
from dataHolder.aggregate_data import aggregateData
from typing import Optional
from db_server import dBServer

def fetch_latest_spacex_launch(url: str) -> Optional["Launch"]:
    launch = None
    response = requests.get(url)
    if response.status_code == 200:
        data: dict = response.json()
        launch = Launch.load_from_json(data)
    else:
        print("Failed to fetch SpaceX data:", response.status_code)
    return launch

def main():
    url = "https://api.spacexdata.com/v5/launches/latest"
    db_writer = dBServer()
    data_aggregator = aggregateData()

    launch = fetch_latest_spacex_launch(url=url)
    launch_table_configuration_data = launch.get_data_to_create_sql_table()

    db_writer.create_table_in_db(launch_table_configuration_data)

    data_to_store = launch.get_data_dict_to_insert_sql_table()
    db_writer.insert_data_into_table(data_to_store)

    aggregation_data = data_aggregator.extract_data_from_launch_and_update(launch)
    db_writer.insert_data_into_table(aggregation_data)


if __name__ == "__main__":
    main()
