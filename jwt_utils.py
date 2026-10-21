import base64
import json
import errors
from datetime import datetime

def _decode_jwt(token:str):
    try:
        token_parts = token.split('.')

        if len(token_parts) != 3: raise ValueError("Invalid token!")

        payload_b64 = token_parts[1]
        payload_b64 = payload_b64.replace("-", "+").replace("_", "/") # convert base64url to standard base64

        rem = len(payload_b64) % 4
        if rem > 0: payload_b64 = payload_b64 + "=" * (4 - rem)

        decode_bytes = base64.b64decode(payload_b64)
        decode_str = decode_bytes.decode('utf-8')

        payload_data = json.loads(decode_str)
        return payload_data
    except Exception as e:
        print(sub_error := f"Decode error: {e}")
        return None

def is_token_valid(token:str):
    payload = _decode_jwt(token)

    if payload:
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            exp_date = datetime.fromtimestamp(exp_timestamp)

            if datetime.now() < exp_date:
                return True
            else:
                return False

        else:
            raise errors.MissingExpirationError("Token has no expiration field.")

    else:
        raise errors.MissingPayload("Token has no payload field.")