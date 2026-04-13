"""
AI Smart Food OS — Core API v2
FastAPI routes for food, chat, orders, profile, auth, experiments
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
import json
import random
import uuid
from datetime import datetime, timedelta
from supabase import create_client, Client
import anthropic
import razorpay

router = APIRouter()

# ──────────────────────────────────────────────
# API Configuration
# ──────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_id(request: Request) -> Optional[str]:
    """Extract user_id from session token stored in cookie."""
    token = request.cookies.get("sb_token")
    if not token:
        return None
    try:
        sb = get_supabase()
        user = sb.auth.get_user(token)
        return user.user.id if user and user.user else None
    except Exception:
        return None

# ──────────────────────────────────────────────
# PYDANTIC MODELS
# ──────────────────────────────────────────────
class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    name: str = ""

class ChatRequest(BaseModel):
    message: str
    mood: Optional[str] = None

class OrderItem(BaseModel):
    food_id: str
    qty: int

class OrderRequest(BaseModel):
    items: List[OrderItem]
    total_amount: float
    payment_method: str = "upi"
    mood: Optional[str] = None
    delivery_address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    body_type: Optional[str] = None
    fitness_goal: Optional[str] = None
    phone: Optional[str] = None

class ExperimentCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    ingredients: List[str] = []

# ──────────────────────────────────────────────
# ──────────────────────────────────────────────
# AUTH ROUTES
# ──────────────────────────────────────────────
@router.post("/api/auth/signin")
async def sign_in(data: SignInRequest):
    try:
        sb = get_supabase()
        res = sb.auth.sign_in_with_password({"email": data.email, "password": data.password})
        if not res.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        response = JSONResponse({"success": True, "user_id": res.user.id})
        # Store token in cookie (7 days)
        response.set_cookie("sb_token", res.session.access_token, max_age=604800, httponly=True, samesite="lax")
        return response
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed. Please check credentials.")


@router.post("/api/auth/signup")
async def sign_up(data: SignUpRequest):
    try:
        sb = get_supabase()
        res = sb.auth.sign_up({"email": data.email, "password": data.password})
        if not res.user:
            raise HTTPException(status_code=400, detail="Signup failed")
        # Create profile row
        try:
            sb.table("profiles").upsert({
                "id": res.user.id,
                "email": data.email,
                "name": data.name,
                "wallet_balance": 100.0,  # New user welcome bonus
                "subscription_tier": "free"
            }).execute()
        except Exception:
            pass
        response = JSONResponse({"success": True, "user_id": res.user.id})
        if res.session:
            response.set_cookie("sb_token", res.session.access_token, max_age=604800, httponly=True, samesite="lax")
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/auth/signout")
async def sign_out():
    try:
        sb = get_supabase()
        sb.auth.sign_out()
    except Exception:
        pass
    response = JSONResponse({"success": True})
    response.delete_cookie("sb_token")
    return response


@router.get("/api/auth/google")
async def google_oauth():
    try:
        sb = get_supabase()
        res = sb.auth.sign_in_with_oauth({"provider": "google", "options": {"redirect_to": f"{SUPABASE_URL}/auth/v1/callback"}})
        return {"url": res.url}
    except Exception:
        raise HTTPException(status_code=503, detail="Google OAuth unavailable")


@router.post("/api/auth/forgot")
async def forgot_password(request: Request):
    body = await request.json()
    email = body.get("email", "")
    try:
        sb = get_supabase()
        sb.auth.reset_password_email(email)
    except Exception:
        pass
    return {"success": True}

# ──────────────────────────────────────────────
# FOOD ROUTES
# ──────────────────────────────────────────────
@router.get("/api/foods")
async def get_foods(request: Request):
    """Return all food items from Supabase."""
    sb = get_supabase()
    res = sb.table("foods").select("*").execute()
    return res.data or []


@router.get("/api/recommend")
async def recommend(request: Request, mood: Optional[str] = None, budget: Optional[int] = None, health_min: Optional[int] = None):
    """AI-ranked recommendations based on mood, budget, health score."""
    items = []
    try:
        sb = get_supabase()
        db_res = sb.table("foods").select("*").execute()
        if db_res.data:
            items = db_res.data
    except Exception as e:
        print("DB Error:", e)

    # Apply filters
    if mood:
        mood_filtered = [i for i in items if mood in (i.get("mood_tags") or [])]
        items = mood_filtered if mood_filtered else items

    if budget:
        items = [i for i in items if i.get("price", 0) <= budget]

    if health_min:
        items = [i for i in items if i.get("health_score", 0) >= health_min]

    # Sort by health score
    items.sort(key=lambda x: x.get("health_score", 0), reverse=True)
    return items[:12]


@router.get("/api/foods/{food_id}")
async def get_food(food_id: str):
    try:
        sb = get_supabase()
        res = sb.table("foods").select("*").eq("id", food_id).single().execute()
        if res.data:
            return res.data
    except Exception as e:
        print("Error fetching food:", e)
    raise HTTPException(status_code=404, detail="Food item not found")

# ──────────────────────────────────────────────
# CHAT / AI CONCIERGE ROUTE
# ──────────────────────────────────────────────
@router.post("/api/chat")
async def chat_assistant(request: Request, body: ChatRequest):
    msg = body.message.strip()
    
    # Check if Claude is configured
    if not ANTHROPIC_API_KEY:
        # Fallback to smart heuristic if no key
        msg_lower = msg.lower()
        if "emergency" in msg_lower or "broke" in msg_lower or "₹50" in msg_lower or "₹80" in msg_lower:
            return {"reply": "🆘 Emergency Mode (Fallback)! Try the Emergency Poha for just ₹49. Perfect when the wallet is light! [Please configure ANTHROPIC_API_KEY for real AI]"}
        elif "protein" in msg_lower or "gym" in msg_lower:
            return {"reply": "💪 Protein mode (Fallback)! Try the Grilled Chicken or Egg White Omelette. [Please configure ANTHROPIC_API_KEY for real AI]"}
        return {"reply": "🤖 I am your AI Food Concierge! (Mock Mode - Please set ANTHROPIC_API_KEY in .env to enable the true Claude integration). Try asking for something spicy!"}

    # True Claude Integration
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Prepare context by limiting food knowledge to string items to save tokens
        sb = get_supabase()
        db_foods = sb.table("foods").select("name, price, calories, health_score, mood_tags").execute()
        food_list = db_foods.data or []
        food_context = ", ".join([f"{f['name']} (₹{f['price']}, {f['calories']}kcal, {f['health_score']}/100 Health Score, Tags: {','.join(f.get('mood_tags') or [])})" for f in food_list])
        
        system_prompt = f"""You are the AI Food Concierge for "AI Smart Food OS". 
You are highly intelligent, slightly futuristic, and focused on helping users make optimal food decisions based on their budget, mood, and health goals. 
You recommend foods off this current menu: {food_context}.
Always use a brief, punchy tone. Use emojis. If they ask for cheap/emergency meals, find things under ₹80. If they want protein, recommend high protein. Keep your answers under 3 sentences."""

        message = client.messages.create(
            model="claude-3-opus-20240229", # or sonnet, depending on speed preference
            max_tokens=150,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": msg}
            ]
        )
        return {"reply": message.content[0].text}
    except Exception as e:
        print("Claude API Error:", e)
        return {"reply": "⚠️ Neural link interrupted. My AI core is temporarily offline. Please try again! (API Error)"}

# ──────────────────────────────────────────────
# PAYMENT ROUTES (RAZORPAY)
# ──────────────────────────────────────────────
class RazorpayOrderRequest(BaseModel):
    amount: float # Final amount in INR
    receipt: str

@router.post("/api/razorpay/create_order")
async def create_razorpay_order(request: Request, body: RazorpayOrderRequest):
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        # Simulated order creation if keys are absent
        import uuid
        return {
            "id": f"order_simulated_{uuid.uuid4().hex[:8]}",
            "amount": int(body.amount * 100),
            "currency": "INR",
            "receipt": body.receipt,
            "status": "created",
            "is_simulated": True
        }
        
    try:
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        data = {
            "amount": int(body.amount * 100), # Razorpay expects amount in paise
            "currency": "INR",
            "receipt": body.receipt,
            "payment_capture": 1 # Auto-capture
        }
        razorpay_order = client.order.create(data=data)
        return razorpay_order
    except Exception as e:
        print("Razorpay API Error:", e)
        raise HTTPException(status_code=500, detail="Payment gateway error")

# ──────────────────────────────────────────────
# PROFILE ROUTES
# ──────────────────────────────────────────────
@router.get("/api/profile")
async def get_profile(request: Request):
    user_id = get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        sb = get_supabase()
        res = sb.table("profiles").select("*").eq("id", user_id).single().execute()
        if res.data:
            return res.data
        # Auto-create profile
        profile = {"id": user_id, "wallet_balance": 100.0, "subscription_tier": "free"}
        sb.table("profiles").insert(profile).execute()
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/profile")
async def update_profile(request: Request, data: ProfileUpdate):
    user_id = get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        sb = get_supabase()
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow().isoformat()
        sb.table("profiles").update(update_data).eq("id", user_id).execute()
        return {"success": True, "message": "Profile updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ──────────────────────────────────────────────
# ORDER ROUTES
# ──────────────────────────────────────────────
@router.post("/api/order")
async def place_order(request: Request, body: OrderRequest):
    user_id = get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    order_id = str(uuid.uuid4())

    try:
        sb = get_supabase()

        # Deduct from wallet if using wallet payment
        if body.payment_method == "wallet":
            profile_res = sb.table("profiles").select("wallet_balance").eq("id", user_id).single().execute()
            balance = float(profile_res.data.get("wallet_balance", 0))
            if balance < body.total_amount:
                raise HTTPException(status_code=400, detail="Insufficient wallet balance")
            sb.table("profiles").update({"wallet_balance": balance - body.total_amount}).eq("id", user_id).execute()

        # Insert order
        order_data = {
            "id": order_id,
            "user_id": user_id,
            "amount": body.total_amount,
            "payment_method": body.payment_method,
            "status": "placed",
            "mood": body.mood,
            "delivery_address": body.delivery_address,
            "lat": body.lat,
            "lng": body.lng,
            "delivery_boy_name": random.choice(["Rohan Kumar", "Aakash Singh", "Priya Sharma", "Vikram Mehta"]),
            "eta": random.randint(20, 45),
            "created_at": datetime.utcnow().isoformat()
        }
        sb.table("orders").insert(order_data).execute()

        # Log payment
        sb.table("payments").insert({
            "id": str(uuid.uuid4()),
            "order_id": order_id,
            "user_id": user_id,
            "amount": body.total_amount,
            "method": body.payment_method,
            "status": "success",
            "created_at": datetime.utcnow().isoformat()
        }).execute()

    except HTTPException:
        raise
    except Exception as e:
        # Return success even if DB fails (demo mode)
        pass

    return {"success": True, "order_id": order_id, "eta": random.randint(20, 40)}


@router.get("/api/orders")
async def get_orders(request: Request):
    user_id = get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        sb = get_supabase()
        res = sb.table("orders").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
        return res.data or []
    except Exception:
        return []


@router.get("/api/track/{order_id}")
async def track_order(order_id: str, request: Request):
    try:
        sb = get_supabase()
        res = sb.table("orders").select("*").eq("id", order_id).single().execute()
        if res.data:
            return res.data
    except Exception:
        pass
    # Demo fallback
    statuses = ["placed", "preparing", "out_for_delivery", "delivered"]
    return {
        "id": order_id,
        "status": random.choice(statuses),
        "delivery_boy_name": random.choice(["Rohan Kumar", "Aakash Singh"]),
        "eta": random.randint(5, 35)
    }

# ──────────────────────────────────────────────
# EXPERIMENTS (FOOD LAB) ROUTES
# ──────────────────────────────────────────────
@router.get("/api/experiments")
async def get_experiments(request: Request):
    try:
        sb = get_supabase()
        res = sb.table("experiments").select("*").order("votes", desc=True).limit(20).execute()
        return res.data or []
    except Exception:
        return []


@router.post("/api/experiments")
async def create_experiment(request: Request, body: ExperimentCreate):
    user_id = get_user_id(request)
    exp_id = str(uuid.uuid4())
    try:
        sb = get_supabase()
        exp_data = {
            "id": exp_id,
            "name": body.name,
            "description": body.description,
            "ingredients": body.ingredients,
            "votes": 1,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat()
        }
        sb.table("experiments").insert(exp_data).execute()
    except Exception:
        pass
    return {"id": exp_id, "success": True}


@router.post("/api/experiments/{exp_id}/vote")
async def vote_experiment(exp_id: str, request: Request):
    try:
        sb = get_supabase()
        res = sb.table("experiments").select("votes").eq("id", exp_id).single().execute()
        votes = (res.data.get("votes") or 0) + 1
        sb.table("experiments").update({"votes": votes}).eq("id", exp_id).execute()
    except Exception:
        pass
    return {"success": True}

# ──────────────────────────────────────────────
# WALLET ROUTES
# ──────────────────────────────────────────────
@router.post("/api/wallet/topup")
async def topup_wallet(request: Request):
    user_id = get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    body = await request.json()
    amount = float(body.get("amount", 0))
    if amount < 10:
        raise HTTPException(status_code=400, detail="Minimum top-up is ₹10")
    try:
        sb = get_supabase()
        profile = sb.table("profiles").select("wallet_balance").eq("id", user_id).single().execute()
        new_balance = float(profile.data.get("wallet_balance") or 0) + amount
        sb.table("profiles").update({"wallet_balance": new_balance}).eq("id", user_id).execute()
        sb.table("wallet_transactions").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "amount": amount,
            "type": "credit",
            "note": "Manual top-up",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return {"success": True, "new_balance": new_balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────
# SUBSCRIPTION ROUTE
# ──────────────────────────────────────────────
@router.post("/api/subscribe")
async def subscribe(request: Request):
    user_id = get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    body = await request.json()
    plan = body.get("plan", "pro_monthly")
    # In production: initiate Razorpay subscription flow
    try:
        sb = get_supabase()
        sb.table("profiles").update({
            "subscription_tier": "pro",
            "subscription_plan": plan
        }).eq("id", user_id).execute()
        sb.table("subscriptions").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "plan": plan,
            "status": "active",
            "started_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception:
        pass
    return {"success": True, "plan": plan}
