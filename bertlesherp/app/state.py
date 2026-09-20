from typing import (
    Optional,
)

from .user import User

USERS_BY_TOKEN = dict()
USER_NAMES_TO_TOKENS = dict()


def lookup_user(token: str) -> Optional[User]:
    global USERS_BY_TOKEN
    return USERS_BY_TOKEN.get(token)


def lookup_token(name: str) -> Optional[str]:
    global USER_NAMES_TO_TOKENS
    return USER_NAMES_TO_TOKENS.get(name)


def persist_user(name: str, token: str) -> User:
    global USERS_BY_TOKEN
    global USER_NAMES_TO_TOKENS

    user = User(name, token)
    USERS_BY_TOKEN[token] = user
    USER_NAMES_TO_TOKENS[name] = token
    return user


def purge_user(user: User):
    global USERS_BY_TOKEN
    global USER_NAMES_TO_TOKENS

    del USER_NAMES_TO_TOKENS[user.name]
    del USERS_BY_TOKEN[user.token]
