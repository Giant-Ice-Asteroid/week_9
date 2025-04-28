import json

"""
Mock/simulation of script handling user authentication

In a "real world" scenario..:

- we wouldn't store passwords in plain text/JSON files
- we would use hashning and salting to encrypt log on credentials
- users might go through a registration process
- accounts might be locked in case of many failed attempts to log on
- there might be back-up of data
- users might be logged out automatically after being inactive for x amount of time
- ...and probably more
"""

def load_user_credentials():
    """
    Function that loads user credentials from a json file
    In a real system, a more secure method for storing password would be used (hashing and salting)..
    
    Returns:
            a dict of user name and info 
    """
    
    try: 
        with open("user_credentials.json") as f:
            return json.load(f)
        
    except FileNotFoundError:
        # if no cred json file it returns default credentials
        return {
             "admin": {
                "password": "admin_pass", # in reality, we wouldn't store passwords like this (plain text)
                "role": "admin",
                "staff_id": None,
                "store_id": None,
                "customer_id": None
            },
            "executive": {
                "password": "exec_pass",
                "role": "executive",
                "staff_id": 1,
                "store_id": None,
                "customer_id": None
            },
            "store1_manager": {
                "password": "manager1_pass",
                "role": "store_manager",
                "staff_id": 2,
                "store_id": 1,
                "customer_id": None
            },
            "store2_manager": {
                "password": "manager2_pass",
                "role": "store_manager",
                "staff_id": 5,
                "store_id": 2,
                "customer_id": None
            },
            "store3_manager": {
                "password": "manager3_pass",
                "role": "store_manager",
                "staff_id": 8,
                "store_id": 3,
                "customer_id": None
            },
            "team_lead1": {
                "password": "team1_pass",
                "role": "team_lead",
                "staff_id": 3,
                "store_id": 1,
                "customer_id": None
            },
            "sales1": {
                "password": "sales1_pass",
                "role": "staff",
                "staff_id": 4,
                "store_id": 1,
                "customer_id": None
            },
            "customer1": {
                "password": "customer1_pass",
                "role": "customer",
                "staff_id": None,
                "store_id": None,
                "customer_id": 1
            }
        }

def authenticate_user(username, password):
    """
    Function that aunthenticates a user based on username and password
    
    Arguments:
            username (string): the username to be authenticated
            passwordd (string): the password to be checked
            
    Returns:
            tuple: (success, user_data), where success = a bool, and user data contains info about user role
    """
    
    #first loads the user credentials using the first function
    user_credentials = load_user_credentials()

    #checks if username passed into this function matches the loaded credentials
    if username not in user_credentials:
        return False, None
    
    #same for password
    if password != user_credentials[username]["password"]:
        return False, None
    
    # if match, success, returns True and the user data 
    return True, user_credentials[username]

# Test the authentication
if __name__ == "__main__":
    # Test with valid credentials
    success, user_data = authenticate_user("admin", "admin_pass")
    if success:
        print(f"Authentication successful for admin. Role: {user_data["role"]}")
    else:
        print("Authentication failed for admin.")
    
    # Test with invalid credentials
    success, user_data = authenticate_user("admin", "wrong_password")
    if success:
        print(f"Authentication successful for admin with wrong password. This is a bug!")
    else:
        print("Authentication correctly failed for admin with wrong password.")