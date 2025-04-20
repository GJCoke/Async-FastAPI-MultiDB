"""
Validate utils.

Author : Coke
Date   : 2025-03-10
"""

import re


def is_valid_password(value: str) -> bool:
    """
    Validate password strength.

    Requirements:
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one digit
    - May contain letters, digits, and special characters: @$!%*?&
    - Length between 8 and 20 characters
    """
    password_pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,20}$")
    return bool(re.match(password_pattern, value))
