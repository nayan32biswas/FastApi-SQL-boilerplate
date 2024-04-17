from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str = Field(..., description="Email")
    full_name: str = Field(..., description="Full Name")
    image: Optional[str] = Field(..., description="Profile Image")
    is_active: bool = Field(..., description="Is Active")


class UserProfileIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str = Field(..., description="Full Name")
    image: Optional[str] = Field(..., description="Profile Image")
