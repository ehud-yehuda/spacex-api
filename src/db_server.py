import psycopg2
import json
from datetime import datetime

class dBServer:
    dbname: str="spacex_db"
    user: str="space_user"
    password: str="space_pass"
    host: str="postgres"
    port: int=5432

    
    def create_table_in_db(self, data: dict):
        table_name = data["table_name"]
        fields = data["table_columns_names"]
        types = data["table_columns_types"]
        self._create_table(table_name=table_name, fields=fields, types=types)
    
    def insert_data_into_table(self, data:dict):
        table_name = data["table_name"]
        fields = data["fields"]
        values = data["values"]
        self._write_data_in_db(table_name=table_name, fields=fields, values=values)
        return

    def _write_data_in_db(self, table_name: str, fields: list, values: list):
        placeholders = ', '.join(['%s'] * len(fields))
        columns = ', '.join(fields)

        insert_sql = f"""
        INSERT INTO {table_name} ({columns})
        VALUES ({placeholders})
        ON CONFLICT (id) DO NOTHING;
        """

        # Convert date to datetime
        if 'date_utc' in fields:
            idx = fields.index('date_utc')
            values[idx] = datetime.fromisoformat(values[idx].replace("Z", "+00:00"))

        # Convert raw JSON to string
        if 'data_as_json' in fields:
            idx = fields.index('data_as_json')
            values[idx] = json.dumps(values[idx])

        self._run_operation_on_db(insert_sql, values)
    
    def _drop_table_if_exists(self, table_name: str):
        drop_sql = f"DROP TABLE IF EXISTS {table_name};"
        self._run_operation_on_db(drop_sql)
        
    def _run_operation_on_db(self, query: str, values=None):
        conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        cur.execute(query, values)
        conn.commit()
        cur.close()
        conn.close()

    def _create_table(self, table_name:str, fields:list, types: list):
        command = ','.join([x + ' ' + y for x, y in zip(fields, types)])
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {command}
        );
        """
        self._run_operation_on_db(create_sql)
        
        print("✅ Table 'launches' ensured.")