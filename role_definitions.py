
# defines what each user role has permission to do with each table in the database

role_permissions = {
    
    # ADMIN - First admin - digital dictator, can do whatever!
    "admin": {
        "tables": {
            "brands": ["SELECT", "INSERT", "UPDATE", "DELETE"],
            "categories": ["SELECT", "INSERT", "UPDATE", "DELETE"],
            "customers": ["SELECT", "INSERT", "UPDATE", "DELETE"],
            "orders": ["SELECT", "INSERT", "UPDATE", "DELETE"],
            "order_items": ["SELECT", "INSERT", "UPDATE", "DELETE"],
            "products": ["SELECT", "INSERT", "UPDATE", "DELETE"],
            "staffs": ["SELECT", "INSERT", "UPDATE", "DELETE"],
            "stocks": ["SELECT", "INSERT", "UPDATE", "DELETE"],
            "stores": ["SELECT", "INSERT", "UPDATE", "DELETE"]
            
        },
        #dude got no restrictions
        "column_restrictions": {},
        "row_restrictions": {}
    },
    
    # EXECUTIVE - Executive/CEO also pretty powerful, can read everything but can't write to the database
    "executive": {
        "tables": {
            "brands": ["SELECT", "INSERT", "UPDATE"],
            "categories": ["SELECT", "INSERT", "UPDATE"],
            "customers": ["SELECT"],
            "orders": ["SELECT"],
            "order_items": ["SELECT"],
            "products": ["SELECT", "INSERT", "UPDATE"],
            "staffs": ["SELECT", "INSERT", "UPDATE"],
            "stocks": ["SELECT"],
            "stores": ["SELECT", "INSERT", "UPDATE"]
            
        },
        #no restrictions either
        "column_restrictions": {},
        "row_restrictions": {}
    },
    
    # STORE MANAGER - next up store manager, can look up info and limited updates, but only their own store
    "store_manager": {
        "tables": {
            "brands": ["SELECT"],
            "categories": ["SELECT"],
            "customers": ["SELECT"],
            "orders": ["SELECT", "UPDATE"],
            "order_items": ["SELECT"],
            "products": ["SELECT"],
            "staffs": ["SELECT", "UPDATE"],
            "stocks": ["SELECT", "UPDATE"],
            "stores": ["SELECT"] 
        },
        # store managers have limited access to customers table
        "column_restrictions": {
            "customers": ["customer_id", "first_name", "last_name", "email", "phone"]
        },
        # store managers are restricted to only see data from their own store
        "row_restrictions": {
            "orders": "store_id = {store_id}", #placeholders
            "staffs": "store_id = {store_id}",
            "stocks": "store_id = {store_id}"
        }
    },
    
    #  TEAM LEAD - team lead can access and handle sales and (some) customer data
    "team_lead": {
        "tables": {
            "brands": ["SELECT"],
            "categories": ["SELECT"],
            "customers": ["SELECT", "INSERT", "UPDATE"],
            "orders": ["SELECT", "INSERT", "UPDATE"],
            "order_items": ["SELECT", "INSERT", "UPDATE"],
            "products": ["SELECT"],
            "staffs": ["SELECT"],
            "stocks": ["SELECT"]           
        },
        # team leads have limited access to customers table as well as limited access to staff tables
        "column_restrictions": {
            "customers": ["customer_id", "first_name", "last_name", "email", "phone"],
            "staffs": ["staff_id,", "first_name", "last_name", "store_id"]
        },
        
        # they are also restricted to only see data from their own store
        "row_restrictions": {
            "orders": "store_id = {store_id}",
            "stocks": "store_id = {store_id}"
        }
    },
    
    # STAFF - regular staff have access to tables related to sales and orders
    "staff": {
        "tables": {
            "brands": ["SELECT"],
            "categories": ["SELECT"],
            "customers": ["SELECT", "INSERT"],
            "orders": ["SELECT", "INSERT"],
            "order_items": ["SELECT", "INSERT"],
            "products": ["SELECT"],
            "staffs": ["SELECT"],
            "stocks": ["SELECT"]           
        },
        # staff has limited access to customers table 
        "column_restrictions": {
            "customers": ["customer_id", "first_name", "last_name", "email", "phone"],
        },
        
        # and can only see order data from their own stores..
        "row_restrictions": {
            "orders": "store_id = {store_id}"
        }
    },
        
    # CUSTOMERS - Customers may only access (read) data related to their own orders, as well as public product and store data 
    "customer": {
            "tables": {
                "brands": ["SELECT"],
                "categories": ["SELECT"],
                "orders": ["SELECT"],
                "order_items": ["SELECT"],
                "products": ["SELECT"],
                "stores": ["SELECT"]           
        },
        # no column restrictions for customers since they can only read permitted tables
        "column_restrictions": {},
        # but may only see rows related to their own data in orders and order_items
        "row_restrictions": {
            "orders": "customer_id = {customer_id}",
            "order_items": "order_id IN (SELECT order_id FROM orders WHERE customer_id = {customer_id})"
        }
    }
}