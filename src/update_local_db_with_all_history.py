from dataHolder.aggregate_data import aggregateData
from db_server import dBServer
from api_reader import LaunchSyncManager
from dataHolder.models import Launch, Payload
import time

tables_required = [Launch,
                   Payload,
                   aggregateData]

def main():
    db_writer = dBServer()
    db_writer._drop_table_if_exists(Launch.table_name)
    db_writer._drop_table_if_exists(Payload.table_name)
    db_writer._drop_table_if_exists(aggregateData.table_name)


    data_aggregator = aggregateData()
    api_reader = LaunchSyncManager(db_writer=db_writer)
    db_writer.create_tables(tables_required)

    for data_dict in api_reader.launches_generator():
        launch = data_dict["launch"]
        if launch:
            aggregation_data = data_aggregator.extract_data_from_launch_and_update(data_dict)
            print(aggregation_data["values"][3])
            print(aggregation_data["values"][4])
            db_writer.insert_data_into_table(aggregation_data, use_ignore_conflicts=False)
        time.sleep(1.0)


if __name__ == "__main__":
    main()
