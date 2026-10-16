import base64
import json
import random
import zlib

import dns.resolver
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

KEY = bytes.fromhex("4e5c6d1a8b3fe8137a3b9df26a9c4de195267b8e6f6c0b4e1c3ae1d27f2b4e6f")
IV = bytes.fromhex("a9c21f8d7e6b4a9db12e4f9d5c1a7b8e")

DOH_SERVERS = ["https://1.1.1.1/dns-query", "https://1.0.0.1/dns-query", "https://8.8.8.8/resolve", "https://8.8.4.4/resolve"]


def _b64(s):
    s = s.replace("-", "+").replace("_", "/")
    return base64.b64decode(s + "=" * (-len(s) % 4))


def _aes_cbc_decrypt(data):
    d = Cipher(algorithms.AES(KEY), modes.CBC(IV)).decryptor()
    pt = d.update(data) + d.finalize()
    pad = pt[-1]
    return pt[:-pad] if 1 <= pad <= 16 and pt.endswith(bytes([pad]) * pad) else pt


class OstoraTV:
    def __init__(self, timeout=15):
        self.doh = random.choice(DOH_SERVERS)
        self.timeout = timeout
        self._resolver = dns.resolver.Resolver(configure=False)
        self._resolver.nameservers = ["8.8.8.8"]
        self._resolver.lifetime = timeout

    @staticmethod
    def decrypt_string(b64):
        return _aes_cbc_decrypt(_b64(b64)).decode()

    def doh_txt(self, host):
        r = requests.get(f"{self.doh}?name={host}&type=txt", headers={"accept": "application/dns-json"}, timeout=self.timeout)
        return r.json()["Answer"][0]["data"].replace('"', "").replace(" ", "")

    def dns_txt(self, host):
        try:
            ans = self._resolver.resolve(host, "TXT")
            return "".join(s.decode() for rec in ans for s in rec.strings)
        except Exception:
            return self.doh_txt(host)

    def get_config(self):
        raw = base64.b64decode(self.doh_txt("start.ver6.top"))
        inner = base64.b64decode(_aes_cbc_decrypt(raw))
        return json.loads(zlib.decompress(inner))

    def get_website(self):
        return self.get_config()["website"]

    def get_update_url(self):
        return self.get_config()["update"]

    def get_popup_url(self):
        return base64.b64decode(self.get_config()["pml"] + "==").decode()

    def get_notifications(self):
        raw = base64.b64decode(self.dns_txt("n6.not6.top"))
        return json.loads(zlib.decompress(raw))


if __name__ == "__main__":
    tv = OstoraTV()

    print(tv.decrypt_string("lmWqTW6yPAoclJQWaBxA8w=="))
    # start.ver6.top

    print(tv.get_website())
    # https://ostora.tv

    print(tv.get_update_url())
    # https://raw.githubusercontent.com/gabar99/new/refs/heads/main/v7.0.0.apk

    print(tv.get_popup_url())
    # https://hai8g.com/4/10302446

    print(tv.get_notifications()["notifications"][0]["title"])
    # مسلسل طالع نازل: الحب اللي كان  الحلقة 4
