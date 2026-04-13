# AI Smart Food OS 🍴🤖

An intelligent food ordering system with AI-powered recommendations, health scoring, and a premium multi-step checkout experience.

## Features

### 🧠 AI-Powered Menu
- Smart food recommendations based on mood, budget, and health goals
- Health scores (0-100) calculated using AI
- Macro nutrient tracking (Calories, Protein, Fat)
- Category, cuisine, and dietary filters
- Emergency budget mode for quick affordable meals

### 🛒 Smart Cart System
- Persistent cart using localStorage
- Add/remove items with quantity controls
- Cart persists across page navigation

### 📍 Multi-Step Checkout
1. **Review Cart** - View items, health summary, and macros
2. **Delivery Details** - Address input + interactive Leaflet/OpenStreetMap for pinning location
3. **Secure Payment** - Razorpay integration for UPI, Card, Wallet, COD

### 💳 Payment Integration
- Razorpay for secure payments
- Supports UPI, Credit/Debit Cards, Food Wallet, Cash on Delivery

### 🤖 AI Chat Concierge
- Interactive chatbot for personalized recommendations
- Quick suggestions based on budget and mood

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, React (via CDN/Babel)
- **Backend**: Python FastAPI
- **Database**: Supabase (PostgreSQL)
- **Maps**: Leaflet + OpenStreetMap
- **Payments**: Razorpay
- **AI**: Anthropic Claude API

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js (optional)
- Supabase account
- Razorpay account (for live payments)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/avish2687/AI-Food-OS.git
cd AI-Food-OS
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file:
```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Razorpay (optional - app works in simulated mode without these)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Anthropic AI (optional - chat won't work without this)
ANTHROPIC_API_KEY=your_anthropic_api_key
```

5. **Run the server**
```bash
python main.py
```

6. **Access the app**
```
http://localhost:8000
```

## Project Structure

```
AI-Food-OS/
├── frontend/
│   ├── index.html          # Home page
│   ├── menu.html          # AI-powered menu
│   ├── checkout.html      # Multi-step checkout
│   ├── landing.html       # Landing page
│   ├── signin.html        # Sign in
│   ├── signup.html        # Sign up
│   ├── profile.html       # User profile
│   ├── orders.html        # Order history
│   ├── health.html        # Health tracking
│   ├── tracking.html      # Order tracking
│   ├── settings.html      # Settings
│   └── static/
│       ├── css/           # Stylesheets
│       ├── js/            # JavaScript
│       └── img/           # Images
├── routes/
│   ├── api_v2.py          # API endpoints
│   └── auth_v2.py         # Authentication
├── database.py            # Database utilities
├── main.py                # FastAPI server
└── requirements.txt       # Python dependencies
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/foods` | GET | Get all food items |
| `/api/profile` | GET | Get user profile |
| `/api/order` | POST | Place order |
| `/api/razorpay/create_order` | POST | Create Razorpay order |
| `/api/chat` | POST | AI chat endpoint |

## Screenshots

- **Menu**: AI-ranked food with health scores, filters, and cart
- **Checkout**: 3-step flow with map pin selection
- **Payment**: Secure Razorpay checkout

## License

MIT License - See LICENSE file

## Author

Avishkar Kumar