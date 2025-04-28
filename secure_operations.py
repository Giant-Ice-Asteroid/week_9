from secure_db import SecureDatabaseAccess
from db_logger import log_database_access

class SecureOperations(SecureDatabaseAccess):
    """
    Class which inherits from SecureDatabaseAcces to provide a means of database operations
    Handles basic SQL operations:
    
    -SELECT
    -INSERT
    -UPDATE
    -DELETE
    
    Applies security checks before executing SQL queries
    """
    
    # SELECT
    def select(self, table, columns=None, condition=None, limit=None):
        """
        Selects(=reads) data from a table if permitted
        
        Arguments:
                table (string): the table to be queried
                columns (list): the specific columns to be retrieved (default to None meaning all allowed)
                condition (string): Additional WHERE clauses
                limit (int): Maximum number of rows to return
                
        Returns: 
                list: the query result as a list of dicts
                
        
        Raises:
                PermissionError: if the user doesn't have the neccessary permission for the operation
        """
        
        #checks if the user has permission to select from the spexcific table
        if not self.has_table_permission(table, "SELECT"):
            error_message = f"Access denied!!: {self.role} is not permitted to SELECT from {table}!!!!"
            print(error_message)
            raise PermissionError(error_message)
        
        #applies column restrictions depending on role
        allowed_columns = self.get_allowed_columns(table)
        
        #determine which columns to select and show
        if allowed_columns == ["*"]: # no restriction columns
            cols_to_select = "*" if not columns else ", ".join(columns)
        else:
            # in case of restrictions
            if not columns:
                # if no specific columns requested in the query, select all allowed columns
                cols_to_select = ", ".join(allowed_columns)
            else:
                # if specific columns queried for, filter for allowed columns and raise error if not permitted
                filtered_columns = [col for col in columns if col in allowed_columns]     
                if not filtered_columns:
                    raise PermissionError(f"Requested columns not accesible for {self.role}")  
                cols_to_select = ", ".join(filtered_columns)         
                
                
        #next restriction are checked for/applied at row-level
        row_restriction = self.get_row_restriction(table)
        
        # do that by building a WHERE clause in sql
        where_clauses = []
        if condition:
            where_clauses.append(f"({condition})")                
        if row_restriction:
            where_clauses.append(f"({row_restriction})")
            
        where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        limit_clause = f" LIMIT {limit}" if limit is not None else ""
        
        # build final query
        query = f"SELECT {cols_to_select} FROM {table}{where_clause}{limit_clause}"
        
        #log the access
        log_database_access(self.username, self.role, "SELECT", table, query)
        
        #connect to database if not already connected
        if not self.connection:
            self.connect()
            
        #create cursor and execute the query built
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"SELECT query executed: {query}")
            print(f"Retrieved {len(results)} rows")
            return results
        except Exception as e:
            print(f"Error executing the following SELECT query: {e}")
            raise
        finally:
            cursor.close()
            
    # INSERT
    
    def insert(self, table, data): 
        """
        Inserts data into a table if permitted
        
        Arguments:
                table (string): the table to have data inserted
                data (dict): The data to be inserted, organised as column-value pairs
                
        Returns: 
                int: ID of the newly inserted row
                
        
        Raises:
                PermissionError: if the user doesn't have the neccessary permission for the operation
        """
        
        # first check if user has permission to INSERT into the table
        if not self.has_table_permission(table, "INSERT"):
            error_message= f"Access denied!! {self.role} not permitted to INSERT into {table}"
            print(error_message)
            raise PermissionError(error_message)
        
        #for tables with store_id or customer_id constraints, ensure that user may only insert data for user's own context
        context_columns = {"store_id", "customer_id", "staff_id"}
        for col in context_columns.intersection(data.keys()):
            context_value = self.context.get(col)
            if context_value is not None and data[col] != context_value:
                error_message = f"Access denied!! Current user cannot insert {col}={data[col]} - must be {context_value}"
                print(error_message)
                raise PermissionError(error_message)
            
        #building the insert query
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        #logging it
        log_database_access(self.username, self.role, "INSERT", table, f"{query} - {values}")
        
        # Connect to the database if not already connected
        if not self.connection:
            self.connect()
            
        # Execute the query
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values)
            self.connection.commit()
            last_id = cursor.lastrowid
            print(f"INSERT query execute: {query}")
            print(f"Inserted row with ID: {last_id}")
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error when executing INSERT query: {e}")
            raise
        finally:
            cursor.close()
            
    #UPDATE
    
    def update(self, table, data, condition): 
        
        """
        Updates data inside a table if permitted
        
        Arguments:
                table (string): the table to update
                data (dict): The data to be updated, organised as column-value pairs
                condition (string): the WHERE condition
                
        Returns: 
                int: numbers of rows updated
                
        
        Raises:
                PermissionError: if the user doesn't have the neccessary permission for the operation
                ValueError: if no condition is provided
        """
        
        # again, check if user has permission for this operation - update
        if not self.has_table_permission(table, "UPDATE"):
            error_message= f"Access denied!! {self.role} not permitted to UPDATE {table}"
            print(error_message)
            raise PermissionError(error_message)
        
        #require condition for all updates
        if not condition:
            raise ValueError("UPDATE operation requires a condition argument!!")
        
        #application of row-lvel restrictions
        row_restriction = self.get_row_restriction(table)
        
        #then building the WHERE clause..
        where_clauses = [f"({condition})"]
        if row_restriction:
            where_clauses.append(f"{row_restriction}")
            
        where_clause = " WHERE " + " AND ".join(where_clauses)
        
        #building SET clause
        set_clause = ", ".join([f"{col} = %s" for col in data.keys()])
        values = list(data.values())
        
        #building the final query...:
        query = f"UPDATE {table} SET {set_clause}{where_clause}"
        
        #log it
        log_database_access(self.username, self.role, 'UPDATE', table, f"{query} - {values}")
        
        # Connect to the database if not already connected
        if not self.connection:
            self.connect()
            
        # Execute the query
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values)
            self.connection.commit()
            rows_affected = cursor.rowcount
            print(f"UPDATE query executed: {query}")
            print(f"Updated {rows_affected} rows")
            return rows_affected
        except Exception as e:
            self.connection.rollback()
            print(f"Error when executing UPDATE query: {e}")
            raise
        finally:
            cursor.close()
            
    #DELETE
    
    def delete(self, table, condition):
        """
        Deletes data inside a table if permitted
        
        Arguments:
                table (string): the table to delete data from
                condition (string): the WHERE condition
                
        Returns: 
                int: numbers of rows updated
                
        
        Raises:
                PermissionError: if the user doesn't have the neccessary permission for the operation
                ValueError: if no condition is provided
        """
        # check if the user has permission to DELETE from this table
        if not self.has_table_permission(table, 'DELETE'):
            error_msg = f"Access denied: {self.role} cannot DELETE from {table}"
            print(error_msg)
            raise PermissionError(error_msg)
        
        # Require a condition for all deletes for safety
        if not condition:
            raise ValueError("DELETE requires a condition")
        
        # Apply row-level restrictions
        row_restriction = self.get_row_restriction(table)
        
        # Build the WHERE clause
        where_clauses = [f"({condition})"]
        if row_restriction:
            where_clauses.append(f"({row_restriction})")
            
        where_clause = " WHERE " + " AND ".join(where_clauses)
        
        # Build the final query
        query = f"DELETE FROM {table}{where_clause}"
        
        # Log the access
        log_database_access(self.username, self.role, 'DELETE', table, query)
        
        # Connect to the database if not already connected
        if not self.connection:
            self.connect()
            
        # Execute the query
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            rows_affected = cursor.rowcount
            print(f"DELETE query executed: {query}")
            print(f"Deleted {rows_affected} rows")
            return rows_affected
        except Exception as e:
            self.connection.rollback()
            print(f"Error executing DELETE query: {e}")
            raise
        finally:
            cursor.close()