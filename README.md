# Food Order App - Microservices

Food ordering system with microservices: **Order Service**, **Payment Service**, and **Delivery Service**.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Order Service  │─────▶│ Payment Service │─────▶│ Delivery Service│
│   (Port 8001)   │      │   (Port 8002)   │      │   (Port 8003)   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
         │                        │                         │
         │                        │                         │
         ▼                        │                         ▼
┌─────────────────┐               │                ┌─────────────────┐
│   PostgreSQL    │               │                │   PostgreSQL    │
│ (food_order_db) │               │                │  (delivery_db)  │
│   Port: 5433    │               │                │   Port: 5434    │
└─────────────────┘               │                └─────────────────┘
                                  │
         ┌────────────────────────┴─────────────────────────┐
         │                                                   │
         ▼                                                   ▼
    ┌─────────┐                                         ┌─────────┐
    │RabbitMQ │◀────────────────────────────────────────│RabbitMQ │
    └─────────┘                                         └─────────┘
```

### Workflow:

1. **Client creates order** → Order Service
2. **Order Service sends to queue** → Payment Service
3. **Payment Service processes payment** → Delivery Service
4. **Delivery Service calculates route** (Google Maps API) and updates status to "on the way"

## Getting Started

### Requirements:
- Docker & Docker Compose
- (Optional) Google Maps API Key

### Step 1: Environment Configuration

Create a `.env` file in the root directory and paste the following configuration:

```env
# PostgreSQL Database Configuration
POSTGRES_DB=food_order_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
DB_HOST=db
DB_PORT=5432

# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# RabbitMQ Configuration
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Google Maps API (Optional - if not set, distance will be simulated)
# Get your API key from: https://console.cloud.google.com/google/maps-apis
GOOGLE_MAPS_API_KEY=

# Service Configuration
# Order Service runs on port 8001
# Payment Service runs on port 8002
# Delivery Service runs on port 8003
```

**Important:** Change `POSTGRES_PASSWORD` and `SECRET_KEY` to your own values!

### Step 2: Run the project

```bash
docker-compose up --build
```

### Step 3: Access services

- **Order Service**: http://localhost:8001
- **Payment Service**: http://localhost:8002
- **Delivery Service**: http://localhost:8003
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **pgAdmin (Database Management)**: http://localhost:5050 (admin@admin.com / admin)
  - Order DB: localhost:5433
  - Delivery DB: localhost:5434

## API Endpoints

### Order Service (8001)

#### Authentication:
- `POST /register/` - User registration
- `POST /login/` - Login (JWT)
- `POST /logout/` - Logout

#### Restaurants:
- `GET /restaurants/` - List restaurants
- `GET /restaurants/{id}/` - Restaurant details
- `GET /restaurants/{slug}/products/` - Restaurant products

#### Orders:
- `POST /orders/` - Create order
- `GET /orders/` - List your orders

### Payment Service (8002)

Internal service - communicates via RabbitMQ.

### Delivery Service (8003)

- `GET /health/` - Health check
- `GET /deliveries/` - List deliveries
- `GET /deliveries/{id}/` - Delivery details
- `GET /deliveries/order/{order_id}/` - Delivery for order
- `PATCH /deliveries/{id}/status/` - Update delivery status

## Project Structure

```
food-order-app/
├── backend/
│   ├── order_service/        # Order microservice (Django REST)
│   │   ├── orders/           # Models: User, Restaurant, Product, Order
│   │   └── order_consumer/   # RabbitMQ consumer/producer
│   │
│   ├── payment_service/      # Payment microservice
│   │   └── payments/         # Payment processor
│   │
│   └── delivery_service/     # Delivery microservice (Django REST)
│       ├── delivery/         # Model: Delivery
│       │   ├── google_maps.py    # Google Maps API integration
│       │   ├── views.py
│       │   └── serializers.py
│       └── delivery_consumer/    # RabbitMQ consumer/producer
│
├── docker-compose.yml
└── .env
```

## Technologies

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL 17 (separate databases for Order and Delivery services)
- **Message Broker**: RabbitMQ
- **External API**: Google Maps Distance Matrix API
- **Containerization**: Docker & Docker Compose

## RabbitMQ Queues

| Queue | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `payment_queue` | Order Service | Payment Service | Payment request |
| `payment_success` | Payment Service | Order Service | Payment confirmation |
| `delivery_queue` | Payment Service | Delivery Service | Create delivery |
| `delivery_status` | Delivery Service | Order Service | Delivery status |

## Google Maps API

Delivery Service uses Google Maps Distance Matrix API to calculate:
- **Distance** in km from restaurant to customer
- **Delivery time** in minutes

### Configuration (optional):

1. Get API key: https://console.cloud.google.com/google/maps-apis
2. Enable "Distance Matrix API"
3. Add key to `.env`:
   ```env
   GOOGLE_MAPS_API_KEY=AIza...
   ```

**Without API key**: Distance is simulated (2-22 km).

## Testing

### Running Unit Tests

**Order Service** includes unit tests for models, views, and business logic.

Run all tests:
```bash
docker-compose exec order_service python manage.py test
```

Run specific test file:
```bash
docker-compose exec order_service python manage.py test orders.tests.test_models
docker-compose exec order_service python manage.py test orders.tests.test_views
docker-compose exec order_service python manage.py test orders.tests.test_methods
```

Run tests with verbose output:
```bash
docker-compose exec order_service python manage.py test --verbosity=2
```

### Example workflow:

1. **Register user**:
```bash
curl -X POST http://localhost:8001/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "name": "John",
    "surname": "Doe",
    "phone_number": "+48123456789"
  }'
```

2. **Login**:
```bash
curl -X POST http://localhost:8001/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

3. **Create order**:
```bash
curl -X POST http://localhost:8001/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "restaurant_id": 1,
    "items": [
      {"product_id": 1, "quantity": 2}
    ]
  }'
```

4. **Check delivery status**:
```bash
curl http://localhost:8003/deliveries/order/1/
```

## License

Educational project - Network Programming course final project.

---

**Author**: Bartosz Piróg  

