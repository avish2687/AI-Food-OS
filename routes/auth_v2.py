from fastapi import APIRouter, HTTPException, Request, Response, Depends
from datetime import datetime
import re
from database import supabase
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

class PhoneRequest(BaseModel):
    phone: str

class VerifyRequest(BaseModel):
    phone: str
    token: str

@router.post("/send-otp")
async def send_otp(req: PhoneRequest):
    try:
        phone = req.phone.strip()
        if not re.match(r"^\+?[1-9]\d{1,14}$", phone):
            raise HTTPException(status_code=400, detail="Invalid phone format. Use E.164 (e.g. +91...)")
            
        # In a real app, this sends SMS. In local dev, it might need config.
        res = supabase.auth.sign_in_with_otp({"phone": phone})
        return {"success": True, "message": "OTP sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-otp")
async def verify_otp(req: VerifyRequest, response: Response):
    try:
        # Demo Bypass Logic
        if req.phone == "+910000000000" and req.token == "123456":
            demo_user_id = "00000000-0000-0000-0000-000000000000"
            
            # Skip database upsert to avoid RLS policy violations
            # response.set_cookie(key="access_token", value="demo-token", httponly=True) ...
            
            # Mock session cookies
            response.set_cookie(key="access_token", value="demo-token", httponly=True)
            response.set_cookie(key="user_id", value=demo_user_id, httponly=True)
            
            return {
                "success": True, 
                "message": "Demo Mode Active!", 
                "user": {"id": demo_user_id, "phone": req.phone}
            }

        res = supabase.auth.verify_otp({"phone": req.phone, "token": req.token, "type": "sms"})
        
        if res.user:
            # Upsert profile
            supabase.table("profiles").upsert({
                "id": res.user.id,
                "phone": req.phone,
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            
            # Set cookies for the session (simplified JWT storage)
            response.set_cookie(key="access_token", value=res.session.access_token, httponly=True)
            response.set_cookie(key="user_id", value=res.user.id, httponly=True)
            
            return {"success": True, "message": "Verified!", "user": {"id": res.user.id, "phone": req.phone}}
        
        raise HTTPException(status_code=401, detail="Verification failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_me(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return {"authenticated": False}
    
    try:
        # Demo Bypass: Return static data for the demo user
        if user_id == "00000000-0000-0000-0000-000000000000":
            return {
                "authenticated": True, 
                "user": {
                    "id": user_id, 
                    "phone": "+91 00000 00000", 
                    "name": "Demo User",
                    "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Demo"
                }
            }
            
        # Get profile data
        res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return {"authenticated": True, "user": res.data}
    except:
        return {"authenticated": False}

@router.post("/signout")
async def signout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("user_id")
    return {"success": True, "message": "Logged out"}
