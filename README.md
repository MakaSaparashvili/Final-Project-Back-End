Python 3.13.5

# Furniture Online Shop API  
**Final Project – Django & Django REST Framework**

## Project Overview
This project is a **Furniture Online Store API**, built using **Django** and **Django REST Framework (DRF)**.  
It provides core e-commerce functionalities such as product catalog, user registration and authentication, shopping cart with add/remove functions, order management, email-based password reset and implemented tasks.

---

## 🧩 Features

### 🔹 Category
- Create and manage furniture categories.
- Fields: `name`, `slug`, `description`, `image`, `is_active`, `created_at`.
- Predefined categories: Chair, Sofa, Table, Wardrobe, Bed, Cabinet, Shelf, Armchair, Outdoor Furniture.

### 🔹 Product
- List and filter available furniture products.
- Fields: `name`, `slug`, `category`, `description`, `price`, `stock`, `is_available`, `featured`, `color`, `material`, `created_at`, `updated_at`.
- 4 options of image upload support.
- Filter products by **category**, **color**, and **material**.

### 🔹 Custom User
- Extended `User` model with additional profile fields:
- `first_name`, `last_name`, `phone`, `address`, `birth_date`
- Includes helper method `get_full_name()`.

### 🔹 Cart & CartItem
- Each user has one shopping cart.
- Add or remove items and track totals.
- Methods:
  - `get_total_price()`
  - `get_total_items()`
  - `get_total_items_count()`

### 🔹 Order & OrderItem
- Create and manage orders for authenticated users.
- Order statuses: `pending`, `processing`, `shipped`, `delivered`, `cancelled`.
- Automatically transfers cart items to order.
- Calculates total price and stores snapshot product prices.

### 🔹 Celery Integration 
- `send_order_confirmation_email` — Sends a confirmation email after successful order creation.
- `update_order_status` — Automatically updates order status from **Pending → Processing** after a set delay. (Added periodic task from admin panel).

### 🔹 Password Reset 
- Custom password reset via email (without Django’s built-in views).
- Includes:
  - Request form (`/password-reset-request/`)
  - Email with reset token and link
  - Confirmation page (`/reset/<uidb64>/<token>/`)
  - Secure password update


## Django Admin Configuration

The Django Admin panel is fully customized and includes:

### CategoryAdmin
 - Search by name
 - Filter by active status (is_active)
 - Automatic slug generation from the category name

### ProductAdmin
 - Search by product name
 - Filter by category, color, and material
 - Edit price and stock directly from the list view (list_editable)

### CustomUserAdmin
 - Search by phone number and username
 - Filter by city

### CartAdmin
 - Filter by user
 - Use TabularInline to display related CartItem models within the detailed view of each Cart

### OrderAdmin
 - Search by order number (ID) and user
 - Filter by status and date
 - Use TabularInline to display related OrderItem models within the detailed view of each Order


## REST API Endpoints

| Endpoint                                        | Method   | Description                                                             |
| ----------------------------------------------- | -------- | ----------------------------------------------------------------------- |
| `/api/categories/`                              | **GET**  | Retrieve all categories                                                 |
| `/api/categories/<id>/`                         | **GET**  | Retrieve a single category                                              |
| `/api/products/`                                | **GET**  | Retrieve all products (supports filtering by category, color, material) |
| `/api/products/<id>/`                           | **GET**  | Retrieve a single product                                               |
| `/api/register/`                                | **POST** | Register a new user                                                     |
| `/api/login/`                                   | **POST** | User login (JWT authentication)                                         |
| `/api/logout/`                                  | **POST** | Logout user (JWT token blacklist)                                       |
| `/api/profile/`                                 | **GET**  | Get authenticated user profile                                          |
| `/api/cart/`                                    | **GET**  | Get user’s cart                                                         |
| `/api/cart/add/`                                | **POST** | Add a product to cart                                                   |
| `/api/cart/remove/`                             | **POST** | Remove a product from cart                                              |
| `/api/orders/`                                  | **GET**  | Get all orders (authenticated user)                                     |
| `/api/orders/<id>/`                             | **GET**  | Get a single order                                                      |
| `/api/orders/create/`                           | **POST** | Create a new order from cart                                            |
| `/api/password-reset-request/`                  | **POST** | Request password reset (sends email)                                    |
| `/api/password-reset-confirm/<uidb64>/<token>/` | **POST** | Confirm password reset and set new password                             |






---










## Tech Stack

| Component | Description |
|------------|-------------|
| **Backend** | Django, Django REST Framework |
| **Task Queue** | Celery with Redis |
| **Database** | SQLite3 (for development) |
| **Authentication** | JWT (SimpleJWT) |
| **Email Backend** | Console (for dev) / SMTP (for production) |

---

## Author
Maka Saparashvili

## Project Mentor
Mariam Kipshidze

## License
This project is for educational and demonstration purposes.
