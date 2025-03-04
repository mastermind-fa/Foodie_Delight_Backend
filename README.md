# Foodie Delight - Food Delivery Backend

## Overview
Foodie Delight is a Django Rest Framework-based backend for an online food delivery store. It enables users to browse food items, add them to their cart, leave reviews, and make secure payments via **SSLCommerz**.

## Features
- **User Authentication:**
  - User registration and login/logout functionality.
  - Secure authentication.
- **Food Management:**
  - Browse food items by categories and special discounts.
  - View detailed food descriptions.
- **Cart & Orders:**
  - Add food items to the cart and update quantities.
  - Secure checkout and order history.
- **Reviews & Ratings:**
  - Users can leave reviews and rate food items.
- **Payments:**
  - Integrated **SSLCommerz** for secure transactions.
- **Filtering & Sorting:**
  - Food items can be sorted by **price** and **popularity**.

## Technologies Used
- **Backend:** Django Rest Framework
- **Database:** PostgreSQL
- **Authentication:** JWT Authentication
- **Payments:** SSLCommerz
- **Deployment:** Secure hosting platform

## Installation & Setup
### Prerequisites
Ensure you have the following installed:
- Python 3.x
- PostgreSQL
- Virtual Environment (optional but recommended)

### Steps to Run the Project
1. **Clone the Repository:**
   ```sh
   git clone https://github.com/mastermind-fa/Foodie_Delight_Backend.git
   cd Foodie_Delight_Backend
   ```
2. **Create & Activate Virtual Environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate  # For Windows
   ```
3. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set Up Environment Variables:**
   - Create a `.env` file in the project root directory and add the following:
     ```env
     SECRET_KEY=<your-generated-secret-key>
     DB_NAME=<your-database-name>
     DB_USER=<your-database-user>
     DB_PASSWORD=<your-database-password>
     DB_HOST=<your-database-host>
     DB_PORT=<your-database-port>
     EMAIL=<your-email>
     PASSWORD=<your-email-app-password>
     ```
   - To generate a new Django secret key, run:
     ```sh
     python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
     ```
5. **Apply Migrations:**
   ```sh
   python manage.py migrate
   ```
6. **Create a Superuser (Admin):**
   ```sh
   python manage.py createsuperuser
   ```
7. **Run the Development Server:**
   ```sh
   python manage.py runserver
   ```

## API Endpoints
### Base URL: `http://127.0.0.1:8000/`

| Endpoint                          | Method | Description |
|------------------------------------|--------|-------------|
| `/customer/list/`                 | GET    | Fetch all customers |
| `/customer/login/`                | POST   | User login (JSON format) |
| `/customer/logout/`               | POST   | User logout |
| `/customer/register/`             | POST   | Register a new user |
| `/customer/details/<userID>/`     | GET    | Fetch user details |
| `/api/food-items/`                | GET    | Get all food items |
| `/api/categories/`                | GET    | Get all food categories |
| `/api/specials/`                  | GET    | Get special discounted food items |
| `/api/food-items/<foodID>/`       | GET    | Get details of a specific food item |
| `/api/food-items/<foodID>/reviews/` | GET    | Get all reviews for a food item |
| `/api/food-items/<foodID>/reviews/` | POST   | Post a review (authenticated users) |
| `/api/categories/<category>/food-items/` | GET | Get food items by category |
| `/api/food-items/?sort=`          | GET    | Sort food items by price and popularity |
| `/api/cart/`                      | GET    | Get cart details |
| `/api/cart/`                      | POST   | Add food item to cart |
| `/api/cart/`                      | PUT    | Update cart quantity |
| `/api/cart/<itemID>/`             | DELETE | Remove item from cart |
| `/api/orders/`                    | GET    | Get all user orders |


## Contribution
Contributions are welcome! Feel free to fork the repo and submit a pull request.

## License
This project is licensed under the MIT License.

---
Developed by **Farhana Alam**

