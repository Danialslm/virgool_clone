import base64
import hashlib

import pyotp
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


def hash_code(code):
    return hashlib.sha256(code.encode()).hexdigest()


def create_new_otp(user_id):
    """ Generate and store a new otp code for given user_id. """

    def gen_secret():
        """ Generate a secret string encoded by base32. """
        raw = f'{user_id}{timezone.now()}{settings.SECRET_KEY}'.encode()
        return base64.b32encode(raw).decode()

    otp = pyotp.HOTP(gen_secret())
    code = otp.at(user_id)
    hashed_code = hash_code(code)

    cache.set(user_id, {'code': hashed_code}, settings.OTP_CODE_TTL)
    return code


def verify_otp(user_id, code):
    """
    Return True if the given code match by stored code for the given user_id.
    If the code is valid, it will be deleted from the cache.
    """
    hashed_code = hash_code(code)

    otp = cache.get(user_id)
    if otp:
        if hashed_code == otp['code']:
            cache.delete(user_id)
            return True
    return False
