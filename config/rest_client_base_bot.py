    @staticmethod
    def get_type(type):
        return type.entity_type if hasattr(type, "entity_type") else type


    @staticmethod
    def get_id(id):
        return id.id if hasattr(id, "id") else id
