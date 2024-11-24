import os

from jose import jwt, JWTError

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        # First, try to get the token from the cookies
        token = request.cookies.get("access_token")
        
        if not token:
            # If no token found in cookies, fall back to Authorization header
            credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
            if credentials:
                if credentials.scheme != "Bearer":
                    raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
                token = credentials.credentials
            else:
                raise HTTPException(status_code=403, detail="Invalid authorization code.")
        
        # After obtaining the token, verify it
        if not self.verify_jwt(token):
            raise HTTPException(status_code=403, detail="Invalid or expired token.")
        
        return token  # Return the token (or any other relevant info you need)
    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = jwt.decode(jwtoken, JWT_SECRET, algorithms=["HS256"], audience="authenticated")
            
            return True
        except JWTError as e:
            return False