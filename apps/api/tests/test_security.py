"""Password hashing and token round-trips."""

from app.core.security import create_token, decode_token, hash_password, verify_password


def test_password_hash_round_trip():
    hashed = hash_password("correct horse battery staple")
    assert hashed != "correct horse battery staple"
    assert verify_password("correct horse battery staple", hashed)
    assert not verify_password("wrong password", hashed)


def test_token_round_trip_and_expiry():
    token = create_token("user-1")
    claims = decode_token(token)
    assert claims == {"user_id": "user-1", "exp": claims["exp"]}

    expired = create_token("user-1", expires_in=-10)
    assert decode_token(expired) is None

    tampered = token[:-1] + ("0" if token[-1] != "0" else "1")
    assert decode_token(tampered) is None
    assert decode_token("not-a-token") is None
