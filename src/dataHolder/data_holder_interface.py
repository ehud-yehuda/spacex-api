class dataHolderInterface():
    table_name: str
    columns_type: dict = {
        "data_as_json": 'JSONB NOT NULL'
    }
    _raw_json: dict

    def get_columns_types(self):
        return list(self.columns_type.values())
    
    def get_fields(self):
        return self.get_columns_names()

    def get_columns_names(self):
        return list(self.columns_type.keys())
    
    @classmethod
    def get_data_to_create_sql_table(cls):
        ret = {}
        ret["table_name"] = cls.table_name
        ret["table_columns_names"] = cls.get_columns_names(cls)
        ret["table_columns_types"] = cls.get_columns_types(cls)
        return ret
    
    def get_all_values(self) -> list:
        return [
            self._raw_json
        ]
    
    def get_data_dict_to_insert_sql_table(self) -> dict:
        ret = {}
        ret["table_name"] = self.table_name
        ret["values"] = self.get_all_values()
        ret["fields"] = self.get_fields()
        return ret

