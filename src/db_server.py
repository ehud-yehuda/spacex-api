import psycopg2

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

        
    def _run_operation_on_db(self, query: str):
        conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        cur.execute(query)
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