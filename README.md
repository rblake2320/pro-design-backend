# Pro Design - E-Commerce Backend API

RESTful API backend for Pro Design e-commerce platform. Built with Flask, SQLAlchemy, and JWT authentication.

## 🚀 Features

- **User Authentication** - JWT-based authentication with bcrypt password hashing
- **Product Management** - CRUD operations for products and variants
- **Order Processing** - Complete order lifecycle management
- **Custom Orders** - Handle custom design requests
- **Admin Operations** - Dashboard statistics and management endpoints
- **Database ORM** - SQLAlchemy with SQLite (PostgreSQL-ready)
- **CORS Support** - Cross-origin resource sharing enabled

## 🛠️ Tech Stack

- **Flask 3.1.1** - Web framework
- **Flask-SQLAlchemy 3.1.1** - ORM
- **Flask-JWT-Extended 4.7.1** - JWT authentication
- **Flask-CORS 6.0.0** - CORS handling
- **Flask-Mail 0.10.0** - Email notifications (ready for integration)
- **Stripe 13.0.1** - Payment processing (ready for integration)
- **bcrypt 5.0.0** - Password hashing
- **SQLite** - Development database (PostgreSQL recommended for production)

## 📋 Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/rblake2320/pro-design-backend.git
cd pro-design-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_APP=src/main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///src/database/app.db

# Stripe Configuration (for payment integration)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Database Setup

```bash
# The database will be created automatically on first run
# Tables are created using SQLAlchemy models

# To reset the database (WARNING: deletes all data)
rm src/database/app.db
python src/main.py  # Will recreate tables
```

### Running the Server

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start the Flask development server
python src/main.py
```

The API will be available at `http://localhost:5000`

## 📁 Project Structure

```
src/
├── models/              # SQLAlchemy database models
│   ├── user.py         # User model with authentication
│   ├── product.py      # Product and ProductVariant models
│   └── order.py        # Order, OrderItem, CustomOrder models
├── routes/             # API route blueprints
│   ├── auth.py         # Authentication endpoints
│   ├── products.py     # Product catalog endpoints
│   ├── orders.py       # Order management endpoints
│   ├── user.py         # User profile endpoints
│   └── admin.py        # Admin-only endpoints
├── database.py         # Database configuration
├── main.py            # Application entry point
└── static/            # Static files
```

## 🔌 API Endpoints

### Authentication (`/api/auth`)

```
POST   /api/auth/register    - Register new user
POST   /api/auth/login       - Login user
GET    /api/auth/me          - Get current user (requires JWT)
POST   /api/auth/logout      - Logout user
```

### Products (`/api/products`)

```
GET    /api/products              - Get all products
GET    /api/products/:id          - Get product by ID
GET    /api/products/:id/variants - Get product variants
GET    /api/products/categories   - Get product categories
```

### Orders (`/api/orders`)

```
POST   /api/orders/create        - Create new order
GET    /api/orders               - Get user's orders (requires JWT)
GET    /api/orders/:id           - Get order by ID
GET    /api/orders/:id/track     - Track order status
POST   /api/orders/custom-quote  - Request custom design quote
```

### Admin (`/api/admin`) - Requires Admin JWT

```
GET    /api/admin/dashboard           - Dashboard statistics
GET    /api/admin/orders              - Get all orders
PUT    /api/admin/orders/:id/status   - Update order status
GET    /api/admin/products            - Get all products
POST   /api/admin/products            - Create product
PUT    /api/admin/products/:id        - Update product
DELETE /api/admin/products/:id        - Delete product
GET    /api/admin/custom-orders       - Get custom order requests
PUT    /api/admin/custom-orders/:id   - Update custom order
GET    /api/admin/customers           - Get all customers
```

## 💾 Database Models

### User
```python
- id (Integer, Primary Key)
- email (String, Unique)
- password_hash (String)
- first_name (String)
- last_name (String)
- phone (String)
- is_admin (Boolean)
- created_at (DateTime)
```

### Product
```python
- id (Integer, Primary Key)
- name (String)
- description (Text)
- category (String)
- base_price (Float)
- image_url (String)
- is_active (Boolean)
- created_at (DateTime)
- updated_at (DateTime)
```

### ProductVariant
```python
- id (Integer, Primary Key)
- product_id (Foreign Key)
- size (String)
- color (String)
- stock_quantity (Integer)
- sku (String, Unique)
```

### Order
```python
- id (Integer, Primary Key)
- user_id (Foreign Key, Optional)
- order_number (String, Unique)
- status (String)
- customer_email (String)
- customer_name (String)
- customer_phone (String)
- subtotal (Float)
- tax (Float)
- shipping (Float)
- total (Float)
- payment_status (String)
- payment_intent_id (String)
- shipping_address (JSON)
- billing_address (JSON)
- created_at (DateTime)
- updated_at (DateTime)
```

### OrderItem
```python
- id (Integer, Primary Key)
- order_id (Foreign Key)
- product_id (Foreign Key)
- variant_id (Foreign Key, Optional)
- quantity (Integer)
- price_at_purchase (Float)
- custom_text (Text)
- custom_image_url (String)
- custom_notes (Text)
```

### CustomOrder
```python
- id (Integer, Primary Key)
- user_id (Foreign Key, Optional)
- order_id (Foreign Key, Optional)
- design_type (String)
- design_data (JSON)
- front_design (String)
- back_design (String)
- notes (Text)
- status (String)
- admin_notes (Text)
- contact_email (String)
- contact_phone (String)
- created_at (DateTime)
- updated_at (DateTime)
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. User registers or logs in
2. Server returns JWT access token
3. Client includes token in `Authorization: Bearer <token>` header
4. Server validates token on protected routes

### Admin Access

Admin-only routes require:
- Valid JWT token
- User account with `is_admin=True`

## 🔧 Configuration

### CORS Configuration

CORS is configured in `main.py`:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Change to specific origins in production
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### JWT Configuration

JWT settings in `main.py`:

```python
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-this-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
```

## 🚧 Current Status

### ✅ Implemented
- User registration and authentication
- Product CRUD operations
- Order creation and retrieval
- Admin dashboard statistics
- Custom order requests
- Database models and relationships

### 🚧 In Development
- Stripe payment integration
- Email notifications
- Order status updates
- Inventory management

### 📝 Planned
- Payment webhooks
- Order tracking integration
- Advanced analytics
- Automated email notifications
- File upload for custom designs

## 🔒 Security Considerations

### Current Implementation
- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ CORS protection
- ✅ SQL injection protection (SQLAlchemy ORM)

### Production Requirements
- ⚠️ Change default secret keys
- ⚠️ Enable HTTPS/SSL
- ⚠️ Restrict CORS origins
- ⚠️ Implement rate limiting
- ⚠️ Add input validation and sanitization
- ⚠️ Set up database backups
- ⚠️ Use environment variables for all secrets

## 📦 Dependencies

See `requirements.txt` for full list. Key dependencies:

```
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.7.1
Flask-CORS==6.0.0
Flask-Mail==0.10.0
stripe==13.0.1
bcrypt==5.0.0
```

## 🚀 Deployment

### Production Checklist

1. **Database Migration**
   - Switch from SQLite to PostgreSQL
   - Set `DATABASE_URL` environment variable

2. **Environment Variables**
   - Set all secrets in production environment
   - Never commit `.env` file

3. **Security**
   - Enable HTTPS
   - Restrict CORS origins
   - Implement rate limiting
   - Set secure cookie flags

4. **Monitoring**
   - Set up error logging
   - Configure application monitoring
   - Enable database backups

### Recommended Platforms

- **Heroku** - Easy deployment with add-ons
- **Railway** - Modern platform with PostgreSQL
- **DigitalOcean** - VPS with full control
- **AWS EC2** - Scalable cloud infrastructure

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Check code coverage
pytest --cov=src
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Pro Design Contact

- **Phone:** 334-559-2010 or 334-271-4455
- **Text Orders:** 334-281-6145
- **Cash App:** $prodesigncompany

## 📄 License

This project is proprietary software. All rights reserved.

## 🔗 Related Repositories

- [Frontend Application](https://github.com/rblake2320/pro-design-frontend) - React e-commerce frontend
