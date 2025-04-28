import mysql.connector
import json
from user_auth import authenticate_user
from role_definitions import role_permissions
from db_logger import log_database_access

class SecureDatabaseAccess:
    """
    Class that provides secure access to the database, access level depending on user roles
    --> It restrict what tables and operations each type of user has permission to access
    """
    
    def __init__(self, username, password):
        """
        Constructor that initalizes/instatiates and aunthenticates the user by using the authentication function
        It stores the user's role and context(id), which will be used later to grant the correct permissions/access
        
        Arguments:
                username (string)
                password (string)
        
        Raises:
                ValueError -> if authentication fails
        """
        
        #authenticate the user..
        success, user_data = authenticate_user(username, password)
        
        if not success:
            raise ValueError("Oops, authentication failed - wrong user name or password :<")
        
        #storing the user info
        self.username = username
        self.role = user_data["role"]
        self.context = {
            "staff_id": user_data.get("staff_id"),
            "store_id": user_data.get("store_id"),
            "customer_id": user_data.get("customer_id")
        }
        
        # initializes a database connection (set as None at first)
        self.connection = None
        
        print(f"User '{username} authenticated with the role: '{self.role}'")
        
    def connect(self):
        """
        method that creates a conenction to the database
        
        Returns:
                connection <-- mySQL database connection object
            
        """
        # Load database configuration
        with open("db_config.json") as f:
            config = json.load(f)
        
        # Connect to the database
        self.connection = mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"]
        )
        
        return self.connection
    
    def has_table_permission(self, table, action):
        """
        Method that checks if the user's role has permission to perform an action on a table
        
        Arguments:
                table (string): the table to be checked
                action(string): the action to be checked (i.e SELECT, DELETE etc)
                
        Returns:
                bool: True if user has permission, False if not
        
        """
        #first get the permissions for each role
        role_perms = role_permissions.get(self.role, {})
        
        #for the role defined above, get table permissions
        table_perms = role_perms.get("tables", {}).get(table, [])
        
        # check if the action on the table is permitted for that role
        return action in table_perms
    
    def get_allowed_columns(self, table):
        """
        method that gets the columns that the user is allowed to access in a table depending on their role
        
        Arguments:
                table(string): table to be checked
                
        Returns: 
                list: a list of allowed columns, or * if all columns are allowable
        """
        
        #again , start by getting role permissions
        role_perms = role_permissions.get(self.role, {})
        
        #next, gets column restrictions for this table for this role
        # here we look for the key "column_restrictions" in the role_perms dict
        # .get(table) is then called on the result of the first .get(). This looks for the table key in the "column_restrictions" dict
        column_restrictions = role_perms.get("column_restrictions", {}).get(table) 
        
        # in the case of specific column restrictions, those are returned. Else, * is returned
        return column_restrictions if column_restrictions is not None else ["*"]
    
    def get_row_restriction(self, table):
        """
        Method that gets the WHERE clause to restrict rows depending on the user's role
        
        Arguments:
                table(string): the table to get restrictions for
                
        Returns:
                string: a SQL WHERE clause in case of restrictions. Else returns None
        """
        
        #gets the role permission
        role_perms = role_permissions.get(self.role, {})
        
        #gets the row restriction for this role and table
        restriction_template = role_perms.get("row_restrictions", {}).get(table)
        
        # in case of restrictions, fill in values from context
        if restriction_template:
            try:
                #  .format() method is called on the template string, the method fills in placeholders with values
                # For example, "store_id = {store_id}" becomes "store_id = 1"
                #Python's "unpacking" operator (**) is used to convert the context dictionary into keyword arguments
                return restriction_template.format(**self.context) 
            except KeyError as e:
                # If a required context value is missing, print an error
                print(f"Error: Missing context for row restriction: {e}")
                return None
        
        # No restrictions
        return None
    
    def close(self):
        #Close the database connection if it exists
        if self.connection:
            self.connection.close()
            self.connection = None
            

# Test the secure database access
if __name__ == "__main__":
    try:
        # Create a secure database access for an admin
        secure_db = SecureDatabaseAccess("admin", "admin_pass")
        
        # Check permissions
        print(f"Admin can SELECT from customers: {secure_db.has_table_permission('customers', 'SELECT')}")
        print(f"Admin can UPDATE customers: {secure_db.has_table_permission('customers', 'UPDATE')}")
        
        # Check column restrictions
        print(f"Admin allowed columns in customers: {secure_db.get_allowed_columns('customers')}")
        
        # Check row restrictions
        print(f"Admin row restrictions on customers: {secure_db.get_row_restriction('customers')}")
        
        # Close the connection
        secure_db.close()
        
        # Try the same with a store manager
        secure_db = SecureDatabaseAccess("store1_manager", "manager1_pass")
        
        # Check permissions
        print(f"Store manager can SELECT from customers: {secure_db.has_table_permission('customers', 'SELECT')}")
        print(f"Store manager can UPDATE customers: {secure_db.has_table_permission('customers', 'UPDATE')}")
        
        # Check column restrictions
        print(f"Store manager allowed columns in customers: {secure_db.get_allowed_columns('customers')}")
        
        # Check row restrictions
        print(f"Store manager row restrictions on staffs: {secure_db.get_row_restriction('staffs')}")
        
        # Close the connection
        secure_db.close()
        
    except Exception as e:
        print(f"Error in test: {e}")