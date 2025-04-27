from dataHolder.aggregate_data import aggregateData
from db_server import dBServer
from api_reader import LaunchSyncManager
from dataHolder.models import Launch
import time

tables_required = [Launch,
                   aggregateData]

def main():
    db_writer = dBServer()
    data_aggregator = aggregateData()
    api_reader = LaunchSyncManager(db_writer=db_writer)
    db_writer.create_tables(tables_required)

    while True:
        new_launch = api_reader.sync_latest_launch()
        if new_launch:
            aggregation_data = data_aggregator.extract_data_from_launch_and_update(new_launch)
            db_writer.insert_data_into_table(aggregation_data)
        time.sleep(1.0)


if __name__ == "__main__":
    main()
