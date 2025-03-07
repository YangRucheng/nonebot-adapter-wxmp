import base64
import hashlib
import secrets

from .utils import log

try:
    from Crypto.Cipher import AES   # type: ignore
except ImportError:
    log("ERROR", "Please install nonebot-adapter-wxmp[crypto] to enable encrypt")


def decrypt(
    encrypt_data: str,
    encoding_aes_key: str,
    appid: str,
) -> str:
    """
    解密 微信平台的消息推送
    """
    aes_key = base64.b64decode(f"{encoding_aes_key}=")
    tmp_msg = base64.b64decode(encrypt_data)

    cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
    full_str = cipher.decrypt(tmp_msg)
    pad = full_str[-1]
    full_str = full_str[:-pad]

    msg = full_str[20 : -len(appid)]
    appid = full_str[-len(appid) :]

    return msg.decode("utf-8")


def encrypt(
    msg: str,
    encoding_aes_key: str,
    appid: str,
) -> str:
    """
    加密 响应微信平台的消息推送
    """
    aes_key = base64.b64decode(f"{encoding_aes_key}=")

    full_str = (
        secrets.token_bytes(16)
        + len(msg).to_bytes(4, "big")
        + msg.encode("utf-8")
        + appid.encode("utf-8")
    )

    cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
    pad = 16 - len(full_str) % 16
    full_str += bytes([pad]) * pad
    tmp_msg = cipher.encrypt(full_str)

    encrypt = base64.b64encode(tmp_msg).decode("utf-8")
    return encrypt


def verify_signature_with_aes(
    timestamp: str,
    nonce: str,
    token: str,
    encrypt: str,
    msg_signature: str,
) -> bool:
    """
    校验签名 启用安全模式
    """
    concat_string: str = "".join(sorted([encrypt, token, timestamp, nonce]))
    sha1_signature = hashlib.sha1(concat_string.encode("utf-8")).hexdigest()
    return secrets.compare_digest(sha1_signature, msg_signature)


def verify_signature_without_aes(
    signature: str,
    timestamp: str,
    nonce: str,
    token: str,
) -> bool:
    """
    校验签名 未启用安全模式
    """
    concat_string = "".join(sorted([timestamp, nonce, token]))
    sha1_signature = hashlib.sha1(concat_string.encode("utf-8")).hexdigest()
    return secrets.compare_digest(sha1_signature, signature)
