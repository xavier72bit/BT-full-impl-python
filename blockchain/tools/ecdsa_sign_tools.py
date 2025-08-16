# types hint
from typing import Any

# std import
import base64

# 3rd import
import ecdsa

# local import
from .hash_tools import compute_hash


class ECDSAToolNotFoundPublicKeyError(Exception): pass
class ECDSAToolNotFoundPrivateKeyError(Exception): pass


class ECDSATool:
    curve = ecdsa.SECP256k1

    @classmethod
    def generate_keys(cls) -> dict:
        """
        :return: keys info
        """
        sk = ecdsa.SigningKey.generate(curve=cls.curve)
        vk = sk.get_verifying_key()

        return {
            'pub': vk.to_string().hex(),
            'sec': sk.to_string().hex()
        }

    def __init__(self, public_key: str = None, secret_key: str = None):
        if public_key:
            self.pubkey = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=self.curve)
        else:
            self.pubkey = None

        if secret_key:
            self.seckey = ecdsa.SigningKey.from_string(bytes.fromhex(secret_key), curve=self.curve)
        else:
            self.seckey = None

    def sign_data(self, data: bytes) -> str:
        if not self.seckey:
            raise ECDSAToolNotFoundPrivateKeyError

        sk: ecdsa.SigningKey = self.seckey

        signature = sk.sign(data)
        return base64.b64encode(signature).decode()

    def verify_sign_data(self, signature_b64: str, data: bytes) -> bool:
        if not self.pubkey:
            raise ECDSAToolNotFoundPublicKeyError

        pk: ecdsa.VerifyingKey = self.pubkey

        try:
            signature = base64.b64decode(signature_b64)
            return pk.verify(signature, data)
        except ecdsa.BadSignatureError:
            return False
