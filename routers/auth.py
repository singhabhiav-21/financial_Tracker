from fastapi import APIRouter, HTTPException, Depends, Request, Response
from dependencies import get_current_user
from models.user_models import (
    LoginRequest, RegisterRequest, UpdateUserRequest, UpdatePasswordRequest
)
from databaseDAO.userDAO import logIn, register, update_userinfo, update_password

router = APIRouter()


@router.get("/auth/status")
async def auth_status(request: Request):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"authenticated": True, "user_id": user_id}


@router.post("/login")
async def login_endpoint(request: Request, response: Response, data: LoginRequest):
    success, user_id = logIn(data.email, data.password)
    if not success:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    request.session.clear()
    request.session.update({"user_id": user_id, "email": data.email})
    request.session.update(request.session)

    return {"success": True, "user_id": user_id, "message": "Login successful"}


@router.get("/me")
async def get_me(request: Request, current_user: int = Depends(get_current_user)):
    return {"user_id": current_user, "email": request.session.get("email")}


@router.post("/register")
async def register_endpoint(data: RegisterRequest):
    success, message = register(data.name, data.email, data.password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}


@router.put("/update-user")
async def update_user_endpoint(
    request: Request,
    data: UpdateUserRequest,
    current_user_id: int = Depends(get_current_user)
):
    user_email = request.session.get("email")
    result = update_userinfo(user_email, data.name, data.new_email)
    if not result:
        raise HTTPException(status_code=400, detail="Update failed")
    return {"success": True, "message": "User information updated"}


@router.put("/update-password")
async def update_password_endpoint(data: UpdatePasswordRequest):
    result = update_password(data.email, data.old_password, data.password, data.re_password)
    if not result:
        raise HTTPException(status_code=400, detail="Password update failed")
    return {"success": True, "message": "Password updated successfully"}


@router.post("/logout")
async def logout_endpoint(request: Request, response: Response):
    request.session.clear()
    response.delete_cookie(key="user_session", path="/")
    return {"success": True, "message": "Logged out successfully"}