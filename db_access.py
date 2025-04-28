import mysql.connector
import json

def connect_to_database():
    """
    Creates and returns a connection to the BikeCorpDB database
    
    Returns:
            connection -> MySQL connection object
    """
    
    # load the database config from the db_config file
    with open("db_config.json") as config_file:
        config = json.load(config_file)
        
    # using this config , we can then create a connection
    connection = mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )
    
    return connection

def test_connection():
    """ 
    Function that tests the database connection by attempting to retrieve a small amount(5 rows) of data
    """
    
    try:
        # get the connection
        connection = connect_to_database()
        
        #cursor for executing the query
        cursor = connection.cursor()
        
        #basic query for testing
        cursor.execute("SELECT * FROM brands LIMIT 5")
        
        #fetch the results in a variable
        results = cursor.fetchall()
        
        #print it
        print(f"Successfully connected to database. When looking up 5 rows from the brands table: Found {len(results)} rows from the brands table")
        
        #closing cursor and connection
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error when attempting to connect to database: {e}")
        
if __name__ == "__main__":
    # If this file is run directly, test the connection
    test_connection()