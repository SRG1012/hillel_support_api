from dataclasses import dataclass
from datetime import datetime


STORAGE = {
    "users": [...],
    "dishes": [...],
    "orders": [...]
}


@dataclass
class Dish:
    id: int
    name: str
    details: str
    price: int


# @dataclass
# class User:
#     id: int
#     first_name: str
#     last_name: str
#     email: str
#     password: str
#     bday: datetime
#     male: int


#     def register(self):
#         STORAGE[1] = User(...)


# class AuthorizationService:
#     def __init__(self, user: User) -> None:
#         pass

#     def authorize(self):
#         pas