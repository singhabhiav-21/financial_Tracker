from fastapi import HTTPException, Request


def get_current_user(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401)
    return user_id
