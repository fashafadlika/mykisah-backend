from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

# Schema respons generik — semua endpoint mengembalikan format ini (success, message, data, errors).
class BaseResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[Any] = None

# Respons sukses — success=True, errors selalu None.
class SuccessResponse(BaseResponse[T]):
    success: bool = True
    errors: Optional[Any] = None

# Respons error — success=False, data selalu None.
class ErrorResponse(BaseResponse[None]):
    success: bool = False
    data: Optional[None] = None
