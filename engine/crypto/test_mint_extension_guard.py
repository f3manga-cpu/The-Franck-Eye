import base64
import struct
import unittest
from mint_extension_guard import TOKEN,TOKEN_2022,decode_mint,fetch_mint

def make(owner=TOKEN, extension=b""):
    blob=bytearray(82)
    blob[44]=8
    blob[45]=1
    if extension:
        blob.extend(bytes(83))
        blob.append(1)
        blob.extend(extension)
    return {"owner":owner,"executable":False,"data":[base64.b64encode(blob).decode(),"base64"]}

class Tests(unittest.TestCase):
    def test_legacy(self):
        self.assertEqual(decode_mint(make())["decimals"],8)
    def test_extension(self):
        a=make(TOKEN_2022,struct.pack("<HH",18,2)+b"ab")
        result=decode_mint(a)
        self.assertEqual(result["extension_type_ids"],[18])
        self.assertFalse(result["economic_value_verified"])
    def test_truncated_extension(self):
        with self.assertRaises(ValueError):decode_mint(make(TOKEN_2022,struct.pack("<HH",18,5)+b"ab"))
    def test_uninitialized_mint_rejected(self):
        a=make()
        blob=bytearray(base64.b64decode(a["data"][0]))
        blob[45]=0
        a["data"][0]=base64.b64encode(blob).decode()
        with self.assertRaisesRegex(ValueError,"Invalid mint layout"):
            decode_mint(a)
    def test_duplicate_extension_rejected(self):
        ext=struct.pack("<HH",18,2)+b"ab"
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            decode_mint(make(TOKEN_2022,ext+ext))
    def test_wrong_owner(self):
        with self.assertRaises(ValueError):decode_mint(make("invalid"))
    def test_invalid_mint_before_network(self):
        with self.assertRaises(ValueError):fetch_mint("invalid")
if __name__=="__main__":unittest.main()
