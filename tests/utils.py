"""
Author  : Coke
Date    : 2025-05-09
"""

import random
import string
import uuid
from datetime import datetime, timedelta

from beanie import PydanticObjectId
from bson import ObjectId


def random_string(
    length: int = 10,
    *,
    upper: bool = False,
    lower: bool = False,
    digits: bool = True,
    punctuation: bool = False,
) -> str:
    """
    Generate a random string with customizable character types.

    Args:
        length (int): Length of the string.
        upper (bool): Include uppercase letters.
        lower (bool): Include lowercase letters.
        digits (bool): Include digits.
        punctuation (bool): Include punctuation.

    Returns:
        str: Randomly generated string.
    """
    chars = ""
    if upper:
        chars += string.ascii_uppercase
    if lower:
        chars += string.ascii_lowercase
    if digits:
        chars += string.digits
    if punctuation:
        chars += string.punctuation

    if not chars:
        raise ValueError("At least one character type must be selected.")

    return "".join(random.choices(chars, k=length))


def random_uppercase(length: int = 8) -> str:
    """Generate a random uppercase string."""
    return "".join(random.choices(string.ascii_uppercase, k=length))


def random_lowercase(length: int = 8) -> str:
    """Generate a random lowercase string."""
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_digits(length: int = 6) -> str:
    """Generate a string of random digits."""
    return "".join(random.choices(string.digits, k=length))


def random_punctuation(length: int = 5) -> str:
    """Generate a string of random punctuation characters."""
    return "".join(random.choices(string.punctuation, k=length))


def random_email(domain: str = "example.com") -> str:
    """Generate a random email address."""
    local = random_string(8, lower=True)
    return f"{local}@{domain}"


def random_username(prefix: str = "user") -> str:
    """Generate a random username with a prefix."""
    suffix = random_string(6)
    return f"{prefix}_{suffix}"


def random_password(length: int = 12) -> str:
    """Generate a secure password."""
    return random_string(length, upper=True, lower=True, digits=True, punctuation=True)


def random_uuid() -> uuid.UUID:
    """Generate a random UUID string."""
    return uuid.uuid4()


def random_object_id() -> PydanticObjectId:
    """Generate a random object ID."""
    return PydanticObjectId(ObjectId())


def random_text(min_words: int = 5, max_words: int = 15) -> str:
    """Generate a random sentence from a fixed vocabulary."""
    words = ["alpha", "beta", "gamma", "delta", "omega", "test", "random", "value", "check", "input"]
    num_words = random.randint(min_words, max_words)
    return " ".join(random.choices(words, k=num_words)).capitalize() + "."


def random_datetime(start_days_ago: int = 30, end_days_ago: int = 0) -> datetime:
    """
    Generate a random datetime between two past days.

    Args:
        start_days_ago (int): Max age in days.
        end_days_ago (int): Min age in days.

    Returns:
        datetime: A datetime object.
    """
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    return start + (end - start) * random.random()
