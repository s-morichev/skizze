from uuid import UUID

from app.schemas.base_class import BaseSchema


class Token(BaseSchema):
    access_token: str
    token_type: str


class TokenPayload(BaseSchema):
    sub: UUID | None = None
