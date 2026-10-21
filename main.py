from user_interface import UserInterface
from api_client import ApiClient
from session_manager import SessionManager

class Main:
    def __init__(self, user_interface: UserInterface):
        self.ui = user_interface
    
    def run(self):
        self.ui.get_main_loop()


if __name__ == "__main__":
    sm = SessionManager()
    client = ApiClient(session_manager=sm, base_url="http://localhost:8080")
    ui = UserInterface(client=client)
    main = Main(user_interface=ui)
    main.run()