      
import hashlib
import aiohttp
import base64
import json
from Crypto.Cipher import AES
import requests

class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b"".decode("utf-8"))
        if isinstance(data, u_type):
            return data.encode("utf-8")
        return data

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    def decrypt(self, enc):
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def decrypt_string(self, enc):
        enc = base64.b64decode(enc)
        return self.decrypt(enc).decode("utf-8")


class TokenManager(object):
    def __init__(self, app_id: str, app_secret: str) -> None:
        self.token = "an_invalid_token"
        self.url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        self.req = {
            "app_id": app_id,
            "app_secret": app_secret
        }

    def set_token(self) -> str:
        response = requests.post(
                self.url,
                headers={"Content-Type": "application/json; charset=utf-8"},
                data=json.dumps(self.req),
                timeout=5
            )
        data = response.json()
        if (data["code"] == 0):
            self.token = data["tenant_access_token"]

    async def update(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                headers={"Content-Type": "application/json; charset=utf-8"},
                data=json.dumps(self.req),
                timeout=5
            ) as response:
                data = await response.json()
                if (data["code"] == 0):
                    self.token = data["tenant_access_token"]

    def get_token(self) -> str:
        return self.token
    

class LarkTableManager(object):
    def __init__(self, token_manager: TokenManager) -> None:
        self.prefix = "https://open.feishu.cn/open-apis/contact/v3/users/"
        self.suffix = "?department_id_type=open_department_id&user_id_type=user_id"
        self.token_manager = token_manager

    async def get_records(self, app_token: str, table_id: str, page_size: int=500, page_token: str="", sorts=None, read_limits="all") -> str:
        if (page_token != ""):
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}"
        else:
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}"

        headers = {
            "Authorization": "Bearer " + self.token_manager.get_token(),
            "Content-Type": "application/json"
        }
        if sorts is None:
            payload = json.dumps({
                "sort": [{"desc": True, "field_name": "获取时间（约）"}]
            })
        else:
            payload = json.dumps({
                "sort": sorts
            })
        
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                data = await response.json()

        if (data["code"] == 99991668 or data["code"] == 99991663):
            await self.token_manager.update()
            return await self.get_records(app_token, table_id, page_size, page_token, sorts, read_limits)
        else:
            if data['data']['has_more'] and read_limits=="all":
                new_data = await self.get_records(app_token, table_id, page_size, data['data']['page_token'], sorts, read_limits)
                data["data"]["items"].extend(new_data["items"])
                data['data']['has_more'] = False
                return data["data"]

            return data["data"]

    async def modify_records(self, app_token: str, table_id: str, record_id: str, fields: dict) -> str:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"

        headers = {
            "Authorization": "Bearer " + self.token_manager.get_token(),
            "Content-Type": "application/json"
        }
        payload = json.dumps(fields)
        
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, data=payload) as response:
                data = await response.json()

        if (data["code"] == 99991668 or data["code"] == 99991663):
            await self.token_manager.update()
            return await self.modify_records(app_token, table_id, record_id, fields)
        else:
            return data["msg"]

    async def add_records(self, app_token: str, table_id: str, fields: dict) -> str:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        headers = {
            "Authorization": "Bearer " + self.token_manager.get_token(),
            "Content-Type": "application/json"
        }
        payload = json.dumps(fields)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                content_type = response.headers.get('Content-Type')
                if 'application/json' in content_type:
                    data = await response.json()
                    # Process JSON data
                else:
                    data = await response.text()
                    # Handle non-JSON response
                    print(data)
        if (data["code"] == 99991668 or data["code"] == 99991663):
            await self.token_manager.update()
            return await self.add_records(app_token, table_id, fields)
        elif (data["code"] == 0):
            return data
        else:
            return data

    async def delete_records(self, app_token:str, table_id:str, records_list:list):
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete"
        headers = {
            "Authorization": "Bearer " + self.token_manager.get_token(),
            "Content-Type": "application/json"
        }
        payload = json.dumps({
                        "records": records_list
                    })
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                content_type = response.headers.get('Content-Type')
                if 'application/json' in content_type:
                    data = await response.json()
                    # Process JSON data
                else:
                    data = await response.text()
                    # Handle non-JSON response
                    print(data)
        if (data["code"] == 99991668 or data["code"] == 99991663):
            await self.token_manager.update()
            return await self.delete_records(app_token, table_id, records_list)
        elif (data["code"] == 0):
            return data["msg"]
        else:
            pass

    async def printer(self):
        print("test")

    async def batch_add_records(self, app_token: str, table_id: str, fields: dict) -> str:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
        headers = {
            "Authorization": "Bearer " + self.token_manager.get_token(),
            "Content-Type": "application/json"
        }
        payload = json.dumps(fields)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                content_type = response.headers.get('Content-Type')
                if 'application/json' in content_type:
                    data = await response.json()
                    # Process JSON data
                else:
                    data = await response.text()
                    # Handle non-JSON response
                    print(data)
        if (data["code"] == 99991668 or data["code"] == 99991663):
            await self.token_manager.update()
            return await self.add_records(app_token, table_id, fields)
        elif (data["code"] == 0):
            return data
        else:
            return data
        
def convert_to_batch_add(dict_list: list) -> dict:
    '''
    把普通字典列表转换为方便写入飞书多维表格的数据形式
    '''
    feishu_dict = {}
    fields_list = []
    for data in dict_list:
        temp_dict = {}
        temp_dict["fields"] = data
        fields_list.append(temp_dict)
    feishu_dict["records"] = fields_list
    return feishu_dict
