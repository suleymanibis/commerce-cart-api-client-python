"# Commerce Cart API Client for Python

A terminal-based Python client for browsing products, managing a shopping cart, and creating and reviewing orders through a Commerce Cart API.

The application provides an interactive menu, persists the authenticated session locally, validates JWT expiration before requests, and renders catalog, cart, and order data with Rich tables.

## Features

- Register and log in through the Commerce Cart API
- Persist the login response in `sessions.json`
- Browse the product catalog
- Add products to and remove products from the cart
- Clear the cart
- Check out with a delivery address
- View order history
- Detect expired sessions and handle unauthorized API responses

## Requirements

- Python 3.10 or newer (the project uses structural pattern matching)
- A running Commerce Cart API
- Network access to the API

The repository does not currently include a `requirements.txt`, `pyproject.toml`, or other dependency manifest. The third-party runtime dependencies imported by the application are:

- [`requests`](https://pypi.org/project/requests/) - HTTP requests and sessions
- [`questionary`](https://pypi.org/project/questionary/) - interactive terminal prompts
- [`rich`](https://pypi.org/project/rich/) - formatted terminal tables

The remaining imports use Python's standard library or modules in this repository.

## Installation

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install requests questionary rich
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install requests questionary rich
```

## Configuration

The current application entry point creates the API client with:

```python
ApiClient(session_manager=sm, base_url="http://localhost:8080")
```

The API base URL is therefore configured in `main.py`. Change that value before starting the client when the API is hosted elsewhere.

`SessionManager` stores the login response in `sessions.json` in the current working directory. The file is created after a successful login and is cleared when the API returns HTTP `401 Unauthorized`. Do not commit this file: it can contain an authentication token.

## Running the client

From the repository root, with the virtual environment activated:

```bash
python main.py
```

The interactive flow starts with registration or login. After authentication, the main menu provides access to the product catalog, cart, and order history.

## API operations used

The interactive client calls the following endpoints relative to the configured base URL:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Register a user |
| `POST` | `/api/auth/login` | Authenticate and persist the returned session data |
| `GET` | `/api/products` | Retrieve products for the catalog |
| `GET` | `/api/cart` | Retrieve the current cart |
| `POST` | `/api/cart/items` | Add a product with `productId` and `quantity` |
| `DELETE` | `/api/cart/items/{productId}` | Remove a product from the cart |
| `DELETE` | `/api/cart` | Clear the cart |
| `POST` | `/api/orders` | Create an order with `deliveryAddress` |
| `GET` | `/api/orders` | Retrieve the authenticated user's orders |

The client expects the API to return JSON. Product, cart, and order fields are read directly by the terminal UI; for example, products use `id`, `name`, `description`, `price`, and `status`, while orders use `orderId`, `deliveryAddress`, `status`, `totalAmount`, `orderDate`, and `items`.

## Using `ApiClient` directly

The lower-level client can also be used from another Python module:

```python
from api_client import ApiClient
from session_manager import SessionManager

session_manager = SessionManager()
client = ApiClient(
    session_manager=session_manager,
    base_url="http://localhost:8080",
)

products_response = client.get("/api/products")
products_response.raise_for_status()
products = products_response.json()

cart_response = client.get("/api/cart")
cart_response.raise_for_status()
cart = cart_response.json()
```

`ApiClient` exposes `get`, `post`, and `delete` methods. It checks the locally stored JWT before each request, removes the stored session after an HTTP `401`, and raises an application error when the API cannot be reached.

## Project structure

| File | Responsibility |
| --- | --- |
| `main.py` | Application entry point and API client configuration |
| `api_client.py` | HTTP session, JWT-based session handling, and API errors |
| `user_interface.py` | Interactive menus and terminal output |
| `session_manager.py` | Read, write, and clear `sessions.json` |
| `jwt_utils.py` | Decode JWT payloads and validate expiration |
| `errors.py` | JWT and application exception types |
| `menu_type.py` | Menu state enumeration |

## Validation

No automated test suite is included in the repository. A syntax/import compilation check can be run with:

```bash
python -m compileall .
```

For an end-to-end check, start the Commerce Cart API, install the dependencies, and run `python main.py`; then exercise registration, login, catalog, cart, checkout, and order-history flows against the configured API.

## Notes

- The client is intended for terminal use and clears the screen between menu states.
- Authentication state is local to the working directory and is not a replacement for secure credential storage.
- The API is responsible for authentication, authorization, validation, and persistence; this repository provides the Python client and terminal UI."
