import psycopg2
import json
from datetime import datetime
import pandas as pd

class dBServer:
    dbname: str="spacex_db"
    user: str="space_user"
    password: str="space_pass"
    host: str="postgres"
    port: int=5432

    def create_tables(self, list_of_table_configurations):
        for data_obj in list_of_table_configurations:
            conf = data_obj.get_data_to_create_sql_table()    
            self.create_table_in_db(conf)
        return
    
    def create_table_in_db(self, data: dict):
        table_name = data["table_name"]
        fields = data["table_columns_names"]
        types = data["table_columns_types"]
        self._create_table(table_name=table_name, fields=fields, types=types)
    
    def insert_data_into_table(self, data:dict, use_ignore_conflicts=True):
        table_name = data["table_name"]
        fields = data["fields"]
        values = data["values"]
        self._write_data_in_db(table_name=table_name, fields=fields, values=values, use_ignore_conflicts=use_ignore_conflicts)
        return

    def _write_data_in_db(self, table_name: str, fields: list, values: list, use_ignore_conflicts:bool=True):
        placeholders = ', '.join(['%s'] * len(fields))
        columns = ', '.join(fields)

        if use_ignore_conflicts:
            insert_sql = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ON CONFLICT (id) DO NOTHING;
            """
        else:
            insert_sql = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders});
            """

        # Convert date to datetime
        if 'date_utc' in fields:
            idx = fields.index('date_utc')
            values[idx] = datetime.fromisoformat(values[idx].replace("Z", "+00:00"))

        # Convert raw JSON to string
        if 'data_as_json' in fields:
            idx = fields.index('data_as_json')
            values[idx] = json.dumps(values[idx])

        self._run_write_operation_on_db(insert_sql, values)
    
    def _drop_table_if_exists(self, table_name: str):
        drop_sql = f"DROP TABLE IF EXISTS {table_name};"
        self._run_write_operation_on_db(drop_sql)
        
    def _run_write_operation_on_db(self, query: str, values=None):
        with psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
                conn.commit()
            
    
    def _run_read_operation_on_db(self, query: str, values=None) -> list:
        #only support select
        rows = None
        with psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
                rows = cur.fetchall()
        return rows

    def _create_table(self, table_name:str, fields:list, types: list):
        command = ','.join([x + ' ' + y for x, y in zip(fields, types)])
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {command}
        );
        """
        self._run_write_operation_on_db(create_sql)
        
        print(f"✅ Table {table_name} ensured.")
    
    def run_query(self, table_name: str, values_as_str) -> list:
        query = f"SELECT {values_as_str} FROM {table_name};"
        rows = self._run_read_operation_on_db(query=query)
        return rows
    
    def read_query_to_dataframe(self, query:str)-> pd.DataFrame:
        try:
            with psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            ) as conn:
                df = pd.read_sql_query(query, conn)
                return df
        except (psycopg2.OperationalError, psycopg2.ProgrammingError) as e:
            print(f"❌ Known DB error: {e}")
            return pd.DataFrame()
        except psycopg2.Error as e:
            print(f"❌ General DB error: {e}")
            return pd.DataFrame()
