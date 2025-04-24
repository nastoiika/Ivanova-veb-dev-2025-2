class RoleRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def get_by_id(self, role_id):
        with self.db_connector.connect() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM roles WHERE id = %s;", (role_id,))
                role = cursor.fetchone()
        return role
    
    def all(self):
        with self.db_connector.connect() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM roles;")
                roles = cursor.fetchall()
        return roles

