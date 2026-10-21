import sys
import jwt_utils as utils
import os
import questionary as quest

from api_client import ApiClient
from questionary import Choice
from menu_type import MenuType
from session_manager import SessionManager
from errors import UnauthorizedError
from rich.table import Table
from rich.console import Console

class UserInterface:
    def __init__(self, client: ApiClient):
        self.sm = SessionManager()
        self.client = client

    def __get_products(self):
        response = self.client.get("/api/products")
        data = response.json()
        
        table = Table(title="Products")
        
        if len(data) > 0:
            table.add_column("ID", style="cyan", justify="center")
            table.add_column("Name", style="cyan", justify="center")
            table.add_column("Description", style="cyan", justify="center")
            table.add_column("Price", style="green", justify="center")
            table.add_column("Status", style="green", justify="center")
            
            for product in data:
                table.add_row(
                    str(product["id"]),
                    str(product["name"]),
                    str(product["description"]),
                    str(product["price"]),
                    str(product["status"])
                )
            
        return table, data
    
    def __get_orders(self):
        print("Get orders...")
        response = self.client.get("/api/orders")
        data = response.json()
        
        table = Table(title="Order Details")
        print(len(data))
        if len(data) > 0:
            table.add_column("Order ID", style="cyan", justify="center", footer="Total Price")
            table.add_column("Delivery Address", style="cyan", justify="center")
            table.add_column("Status", style="green", justify="center")
            table.add_column("Total Price", style="cyan", justify="center")
            table.add_column("Order Date", style="blue", justify="center")
            table.add_column("Items", style="cyan", justify="center")
            
            
            for order in data:
                items = order.get("items", [])
                
                item_info = ""
                for item in items:
                    item_info += f"Name: {item['productName']} Quantity: {item['quantity']}\n"
                
                table.add_row(
                    str(order["orderId"]),
                    str(order["deliveryAddress"]),
                    str(order["status"]),
                    str(order["totalAmount"]),
                    str(order["orderDate"]),
                    item_info
                )
            
        return table, data
    
    def __add_product(self):
        table, p_data = self.__get_products()
                                    
        if len(p_data) > 0:
            console = Console()
            console.print(table)
        else:
            print("There is no product yet.")
            return MenuType.CART_PAGE
        
        product_choice_list = []
        
        for p in p_data:
            product_choice = Choice(
                title = f"{p['name'].capitalize()}",
                value = p["id"]
            )
            product_choice_list.append(product_choice)
        
        which_product = quest.select(
            "Which product do you want to add to your cart?",
            choices= product_choice_list
        ).ask()
        
        how_many = quest.select(
            "How many?",
            choices= [
                Choice(title="1 piece", value = 1),
                Choice(title="2 pieces", value = 2),
                Choice(title="3 pieces", value = 3),
                Choice(title="4 pieces", value = 4),
                Choice(title="5 pieces", value = 5),
                Choice(title="Cancel", value = "cancel"),
            ]
        ).ask()
        
        if how_many != "cancel":
            item_info = {"productId": which_product, "quantity": how_many}
            post_response = self.client.post("/api/cart/items", json=item_info)
            
            if post_response.status_code == 200:
                print("Product added successfully.")
            elif post_response.status_code == 400:
                print(post_response.json().get("message"))
            return MenuType.CART_PAGE
        else:
            return MenuType.MAIN_MENU 
    
    def __remove_product(self, data):
        item_choice_list = []
                                                
        for i in data:
            item_choice = Choice(
                title = f"{i['productName'].capitalize()}",
                value = i["productId"]
            )
            item_choice_list.append(item_choice)
        
        item_id = quest.select(
            "Which product do you want to remove from your cart?",
            choices= item_choice_list
        ).ask()
        
        del_response = self.client.delete(f"/api/cart/items/{item_id}")
        
        if del_response.status_code == 200:
            print("Product removed successfully.")
        else:
            print(del_response.json().get('message'))
        
        return MenuType.CART_PAGE
    
    def __clear_products(self):
        is_confirmed = quest.confirm("Are you sure to clear your cart?").ask()
                            
        if is_confirmed:
            del_response = self.client.delete("/api/cart")
            
            if del_response.status_code == 200:
                print("Cart cleared successfully.")
            else:
                print(del_response.json().get('message'))
        else:
            print("Cart not cleared.")
        
        return MenuType.CART_PAGE
    
    def __checkout(self):
        address = quest.text("Enter your address: ").ask().strip()
        
        if not address:
            print("Address cannot be empty.")
            quest.press_any_key_to_continue().ask()
            return MenuType.MAIN_MENU
        
        request_json = {
            "deliveryAddress": address
        }
        
        post_response = self.client.post("/api/orders", json=request_json)
        data = post_response.json()
        
        if post_response.status_code == 201:
            items = data["items"]
            
            print()
            print("Your order has been received and will be delivered as soon as possible.")
            print()
            
            table = Table(title="Order Details")
            table.add_column("Order ID", style="cyan", justify="center", footer="Total Price")
            table.add_column("Delivery Address", style="cyan", justify="center")
            table.add_column("Status", style="green", justify="center")
            table.add_column("Total Price", style="cyan", justify="center")
            table.add_column("Order Date", style="blue", justify="center")
            table.add_column("Items", style="cyan", justify="center")
            
            item_info = ""
            for item in items:
                item_info += f"Name: {item['productName']} | Quantity: {item['quantity']}\n"
            
            table.add_row(
                str(data["orderId"]),
                str(data["deliveryAddress"]),
                str(data["status"]),
                str(data["totalAmount"]),
                str(data["orderDate"]),
                item_info
            )
            
            console = Console()
            console.print(table)
            quest.press_any_key_to_continue().ask()
            return MenuType.MAIN_MENU
        else:
            print(data.get('message'))
            return MenuType.CART_PAGE
            
    def _start_menu(self):
        choice = quest.select(
            "Please make a choice:",
            choices=[
                Choice(title="Register", value="reg"),
                Choice(title="Login", value="log"),
                Choice(title="Exit", value="ex")
            ]
        ).ask()

        match choice:
            case "reg":
                return MenuType.REGISTER_PAGE
            case "log":
                return MenuType.LOGIN_PAGE
            case "ex":
                return MenuType.EXIT
        return None

    def _register_page(self):
        inputs = quest.form(
            firstName=quest.text("First name:"),
            lastName=quest.text("Last name:"),
            email=quest.text("Email: "),
            password=quest.password("Password: ")
        ).ask()

        response = self.client.post("api/auth/register", json=inputs)

        if response.status_code == 201:
            print("You have been registered successfully.")
            return MenuType.LOGIN_PAGE
        else:
            return MenuType.START_MENU

    def _login_page(self):
        inputs = quest.form(
            email=quest.text("Email: "),
            password=quest.password("Password: ")
        ).ask()

        response = self.client.post("api/auth/login", json=inputs)

        if response.status_code == 200:
            data = response.json()
            self.sm.write_sessions(data)
            return MenuType.MAIN_MENU
        else:
            return MenuType.START_MENU
    
    def _main_menu(self):
        choice = quest.select(
                    "Please make a choice:",
                    choices=[
                        Choice(title="Product Catalog", value="catalog"),
                        Choice(title="Your Cart", value="cart"),
                        Choice(title="Order History", value="order_history"),
                        Choice(title="Exit", value="ex")
                    ]
                ).ask()
        
        match choice:
            case "catalog":
                return MenuType.CATALOG_PAGE
            case "cart":
                return MenuType.CART_PAGE
            case "order_history":
                return MenuType.ORDERS_PAGE
            case "ex":
                return MenuType.EXIT
    
    def _catalog_page(self):
        table, data = self.__get_products()
        
        if len(data) > 0:
            console = Console()
            console.print(table)
        else:
            print("There is no product yet.")
        
        
        
        quest.press_any_key_to_continue("Press any key to main menu").ask()
        return MenuType.MAIN_MENU

    def _cart_page(self):
        response = self.client.get("/api/cart")
        data = response.json()
        items = data["cartItems"]
        total_price=data["cartTotalPrice"]
        table = Table(title="Your Cart", show_footer=True)
        
        if len(items) > 0:
            table.add_column("ID", style="cyan", justify="center", footer="Total Price")
            table.add_column("Name", style="cyan", justify="center")
            table.add_column("Price", style="green", justify="center")
            table.add_column("Quantity", style="cyan", justify="center")
            table.add_column("Total Price", style="blue", justify="right", footer=f"{total_price:.2f} TL")
            
            for item in items:
                table.add_row(
                    str(item["productId"]),
                    str(item["productName"]),
                    str(item["unitPrice"]),
                    str(item["quantity"]),
                    str(item["quantity"] * item["unitPrice"])
                )
            
            console = Console()
            console.print(table)
            
            choice = quest.select(
                        "Please make a choice:",
                        choices=[
                            Choice(title="Add Product To Cart", value="add"),
                            Choice(title="Remove Product From Cart", value="remove"),
                            Choice(title="Clear Cart", value="clear"),
                            Choice(title="Checkout", value="checkout"),
                            Choice(title="Return To Main Menu", value="return")
                        ]
                    ).ask()
        else:
            print("Your cart is empty.")
            choice = quest.select(
                        "Please make a choice:",
                        choices=[
                            Choice(title="Add Product To Cart", value="add"),
                            Choice(title="Return To Main Menu", value="return")
                        ]
                    ).ask()
        
        match choice:
            case "add":
                return self.__add_product()
            case "remove":
                return self.__remove_product(data=items)
            case "clear":
                return self.__clear_products()
            case "checkout":
                return self.__checkout()
            case "return":
                return MenuType.MAIN_MENU
        return None
    
    def _orders_page(self):
        table, data = self.__get_orders()
                
        if len(data) > 0:
            console = Console()
            console.print(table)
        else:
            print("There is no order yet.")
        
        quest.press_any_key_to_continue("Press any key to main menu").ask()
        return MenuType.MAIN_MENU
    
    def get_main_loop(self):

        data = self.sm.read_sessions()
        if "token" in data:
            token = data["token"]
            is_valid = utils.is_token_valid(token)
        else:
            is_valid = False

        if is_valid:
            next_page = MenuType.MAIN_MENU
        else:
            next_page = MenuType.START_MENU


        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            try:
                match next_page:
                    case MenuType.START_MENU:
                        next_page = self._start_menu()
                    case MenuType.REGISTER_PAGE:
                        next_page = self._register_page()
                    case MenuType.LOGIN_PAGE:
                        next_page = self._login_page()
                    case MenuType.MAIN_MENU:
                        next_page = self._main_menu()
                    case MenuType.CATALOG_PAGE:
                        next_page = self._catalog_page()
                    case MenuType.CART_PAGE:
                        next_page = self._cart_page()
                    case MenuType.ORDERS_PAGE:
                        next_page = self._orders_page()
                    case MenuType.EXIT:
                        sys.exit(1)
                    case _:
                        pass
            except UnauthorizedError:
                print("Your session was expired.")
                next_page = MenuType.START_MENU

