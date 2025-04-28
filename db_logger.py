import logging
from datetime import datetime

# Sets up a basic logging system...

# first configure the logging per the logging module:
logging.basicConfig(
    filename="database_access.log", # the log will be written to this file
    level=logging.INFO,  # logs information as well as higher level issues
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" # the log format
)

def log_database_access(username, role, action, table, query=None):
    """
    Function that takes in information about who is accessing what inside the database
    The information is formated into a log message and written to a file
    
    Arguments:
            username (string): user name of the user performing the action 
            role (string): role of the user in question (such as admin, manager etc)
            action (string): the action/command being perfomed such as SELECT, DELETE etc
            table (string): The table that is being accessed by the user
            query (string, opt): the acutal query being executed.. 
    """
    
    #creates a log message with detailed information:
    log_message = f"USER: {username} | ROLE: {role} | ACTION: {action} | TABLE: {table}"
    
    #in case of query:
    if query:
        log_message += f"  | QUERY: {query}"
        
    # the actual writing of the message:
    logging.info(log_message)
    
# Testing the logging function
if __name__ == "__main__":
    log_database_access("test_user", "admin", "SELECT", "customers", "SELECT * FROM customers LIMIT 5")
    print("Log entry created. Check database_access.log")