"""
Password hashing and verification via bcrypt.

Passwords are never stored in plaintext. bcrypt automatically handles salt
generation and timing-safe comparison to prevent timing attacks.
"""

from passlib.context import CryptContext

# bcrypt with a work factor of 12 (default) is suitable for user signup
# without being prohibitively slow. Adjust upward (e.g., 14) if auth becomes
# a bottleneck and needs to be deliberately slow as a DoS mitigation.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password.

    Args:
        password: The plaintext password from user signup/reset.

    Returns:
        The bcrypt-hashed password, safe to store in the database.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password: The plaintext password from a login attempt.
        hashed_password: The bcrypt hash stored in the database.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
