from secure_operations import SecureOperations
import time

def separator(title):
    """Print a separator with a title for better test output readability."""
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50 + "\n")

def test_admin_operations():
    """Test database operations with admin privileges."""
    separator("ADMIN USER OPERATIONS")
    
    try:
        # Login as admin
        admin = SecureOperations("admin", "admin_pass")
        print("Admin authenticated successfully")
        
        # Test SELECT - admin can see all data
        separator("Admin SELECT Test")
        customers = admin.select("customers", columns=["customer_id", "first_name", "last_name", "email", "street"], condition="customer_id < 5")
        print(f"Admin retrieved {len(customers)} customers with full details:")
        for customer in customers[:2]:  # Show just the first 2 for brevity
            print(f"  {customer}")
        
        # Test INSERT - admin can insert anywhere
        separator("Admin INSERT Test")
        # First, get the maximum category_id to avoid duplicate key errors
        max_category = admin.select("categories", columns=["MAX(category_id) as max_id"])
        new_id = 1
        if max_category and max_category[0]['max_id'] is not None:
            new_id = max_category[0]['max_id'] + 1
            
        new_category = {
            "category_id": new_id,
            "category_name": "Test Category"
        }
        try:
            admin.insert("categories", new_category)
            print(f"Admin created new category with ID: {new_id}")
            
            # Test UPDATE - admin can update anything
            separator("Admin UPDATE Test")
            update_data = {
                "category_name": "Updated Test Category"
            }
            rows_updated = admin.update("categories", update_data, f"category_id = {new_id}")
            print(f"Admin updated {rows_updated} category record(s)")
            
            # Test DELETE - admin can delete anything
            separator("Admin DELETE Test")
            rows_deleted = admin.delete("categories", f"category_id = {new_id}")
            print(f"Admin deleted {rows_deleted} category record(s)")
        except Exception as e:
            print(f"Error with category operations: {e}")
        
        # Close connection
        admin.close()
        
    except Exception as e:
        print(f"Admin test error: {e}")

def test_store_manager_operations():
    """Test database operations with store manager privileges."""
    separator("STORE MANAGER OPERATIONS")
    
    try:
        # Login as store manager
        manager = SecureOperations("store1_manager", "manager1_pass")
        print("Store Manager authenticated successfully")
        
        # Test SELECT - manager can see limited customer data
        separator("Store Manager SELECT Test")
        
        # Get customer data - should only see limited columns
        customers = manager.select("customers", columns=["customer_id", "first_name", "last_name", "email", "street"], condition="customer_id < 5")
        print(f"Store Manager retrieved {len(customers)} customers with limited details:")
        for customer in customers[:2]:
            print(f"  {customer}")
        
        # Get staff data - should only see staff in their store
        staff = manager.select("staffs")
        print(f"Store Manager can see {len(staff)} staff members in their store:")
        for s in staff[:2]:
            print(f"  {s}")
        
        # Test UPDATE - manager can update stock in their store
        separator("Store Manager UPDATE Test")
        stock_update = {
            "quantity": 50
        }
        
        # This should succeed - updating stock in their store
        rows_updated = manager.update("stocks", stock_update, "product_id = 1 AND store_id = 1")
        print(f"Store Manager updated {rows_updated} stock record(s) in their store")
        
        # This should result in 0 rows - trying to update stock in another store
        rows_updated = manager.update("stocks", stock_update, "product_id = 1 AND store_id = 2")
        print(f"Security correctly prevented update in another store: {rows_updated} rows affected")
        
        # Test INSERT - manager shouldn't be able to insert into categories
        separator("Store Manager INSERT Test")
        new_category = {
            "category_id": 999,
            "category_name": "Unauthorized Category"
        }
        try:
            category_id = manager.insert("categories", new_category)
            print(f"ERROR: Store Manager created category with ID: {category_id}")
        except PermissionError as e:
            print(f"Correctly denied: {e}")
        
        # Close connection
        manager.close()
        
    except Exception as e:
        print(f"Store Manager test error: {e}")

def test_sales_staff_operations():
    """Test database operations with sales staff privileges."""
    separator("SALES STAFF OPERATIONS")
    
    try:
        # Login as sales staff
        sales = SecureOperations("sales1", "sales1_pass")
        print("Sales Staff authenticated successfully")
        
        # Test SELECT - staff can see products
        separator("Sales Staff SELECT Test")
        products = sales.select("products", columns=["product_id", "product_name", "list_price"], condition="category_id = 1", limit=3)
        print(f"Sales Staff retrieved {len(products)} products:")
        for product in products:
            print(f"  {product}")
        
        # Test INSERT - staff can create orders
        separator("Sales Staff INSERT Test")
        
        # First, get the maximum order_id to avoid duplicate key errors
        # Query for maximum order_id across ALL stores, not just the current store
        max_order = sales.select("orders", columns=["MAX(order_id) as max_id"], 
                         condition="1=1")  # This condition is a trick to bypass row restrictions

        new_order_id = 10000  # Start with a high number
        if max_order and max_order[0]['max_id'] is not None:
            new_order_id = max(max_order[0]['max_id'] + 1, new_order_id)
            
        # Create a new order
        new_order = {
            "order_id": new_order_id,
            "customer_id": 1,
            "order_status": 1,
            "order_date": time.strftime('%Y-%m-%d'),
            "required_date": time.strftime('%Y-%m-%d', time.localtime(time.time() + 7*24*60*60)),  # 7 days later
            "store_id": 1,
            "staff_id": 4  # Their own staff ID
        }
        try:
            sales.insert("orders", new_order)
            print(f"Sales Staff created new order with ID: {new_order_id}")
            
            # Get the maximum item_id for this order
            max_item = sales.select("order_items", columns=["MAX(item_id) as max_id"], 
                                   condition=f"order_id = {new_order_id}")
            new_item_id = 1
            if max_item and max_item[0]['max_id'] is not None:
                new_item_id = max_item[0]['max_id'] + 1
            
            # Add an item to the order
            order_item = {
                "order_id": new_order_id,
                "item_id": new_item_id,
                "product_id": 1,
                "quantity": 1,
                "list_price": 599.99,
                "discount": 0
            }
            sales.insert("order_items", order_item)
            print(f"Sales Staff added item to order with ID: {new_item_id}")
        except Exception as e:
            print(f"Error creating order: {e}")
        
        # Test trying to update product prices (should fail)
        separator("Sales Staff Unauthorized Test")
        product_update = {
            "list_price": 499.99
        }
        try:
            sales.update("products", product_update, "product_id = 1")
            print("ERROR: Sales Staff should not be able to update products")
        except PermissionError as e:
            print(f"Correctly denied: {e}")
        
        # Close connection
        sales.close()
        
    except Exception as e:
        print(f"Sales Staff test error: {e}")

def test_customer_operations():
    """Test database operations with customer privileges."""
    separator("CUSTOMER OPERATIONS")
    
    try:
        # Login as customer
        customer = SecureOperations("customer1", "customer1_pass")
        print("Customer authenticated successfully")
        
        # Test SELECT - customer can see their own orders
        separator("Customer SELECT Test")
        orders = customer.select("orders")
        print(f"Customer can see {len(orders)} of their own orders:")
        for order in orders[:2]:  # Show just the first 2 for brevity
            print(f"  {order}")
        
        # Test SELECT - customer can see products
        products = customer.select("products", columns=["product_id", "product_name", "list_price"], condition="category_id = 1", limit=3)
        print(f"Customer retrieved {len(products)} products:")
        for product in products:
            print(f"  {product}")
        
        # Test trying to see other customers' data (should fail)
        separator("Customer Unauthorized Test")
        try:
            customer.select("customers")
            print("ERROR: Customer should not be able to access customer table")
        except PermissionError as e:
            print(f"Correctly denied: {e}")
        
        # Close connection
        customer.close()
        
    except Exception as e:
        print(f"Customer test error: {e}")

if __name__ == "__main__":
    # Run all tests
    try:
        test_admin_operations()
        test_store_manager_operations()
        test_sales_staff_operations()
        test_customer_operations()
        print("\nAll tests completed!")
    except Exception as e:
        print(f"Test suite error: {e}")