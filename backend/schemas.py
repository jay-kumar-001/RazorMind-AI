from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    

class KYCCreate(BaseModel):
    aadhaar_number: str
    pan_number: str


class KYCUpdate(BaseModel):
    aadhaar_number: Optional[str] = None
    pan_number: Optional[str] = None
    verification_status: Optional[str] = None
    risk_score: Optional[float] = None


class KYCResponse(BaseModel):
    id: int
    user_id: int
    aadhaar_number: str
    pan_number: str
    verification_status: str
    risk_score: float

    class Config:
        from_attributes = True
        
        
class TransactionCreate(BaseModel):
    amount: float
    transaction_type: str


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    transaction_type: str
    risk_score: float
    status: str

    class Config:
        from_attributes = True