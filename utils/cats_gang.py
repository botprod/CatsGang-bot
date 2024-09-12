import random
import asyncio
from urllib.parse import unquote

from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import aiohttp
from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector
from typing import Optional, List, Union

from utils.core import logger
from data import config


class CatsGang:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: Optional[str] = None):
        self.account = f"{session_name}.session"
        self.thread = thread
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy else None
        self.connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)
        self.session = self.create_session()

        proxy_details = self.parse_proxy(proxy) if proxy else None
        self.client = self.create_client(session_name, proxy_details)

    def create_session(self) -> aiohttp.ClientSession:
        headers = {
            'User-Agent': UserAgent(os='android', browsers='chrome').random,
        }
        return aiohttp.ClientSession(headers=headers, trust_env=True, connector=self.connector)

    def parse_proxy(self, proxy: str) -> dict:
        if not proxy:
            return {}

        parts = proxy.split(":")
        hostname = parts[1].split("@")[1]
        port = int(parts[2])
        username = parts[0]
        password = parts[1].split("@")[0]

        return {
            "scheme": config.PROXY['TYPE']['TG'],
            "hostname": hostname,
            "port": port,
            "username": username,
            "password": password
        }

    def create_client(self, session_name: str, proxy: Optional[dict]) -> Client:
        return Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

    async def stats(self) -> List[Union[str, int]]:
        await self.login()
        user = await self.user()

        if user is None:
            logger.error(f"Thread {self.thread} | {self.account} | Failed to retrieve user data.")
            await self.logout()
            return []

        balance = str(user.get('totalRewards'))
        referral_link = f"https://t.me/catsgang_bot/join?startapp={user.get('referrerCode')}"

        leaderboard = await self.get_leaderboard_position()

        me = await self.get_telegram_user()
        if me is None:
            logger.error(f"Thread {self.thread} | {self.account} | Failed to retrieve Telegram user data.")
            return []

        phone_number, name = me.phone_number, f"{me.first_name} {me.last_name or ''}"
        proxy = self.proxy.replace('http://', "") if self.proxy else '-'

        await self.logout()
        return [phone_number, name, balance, leaderboard, referral_link, proxy]

    async def user(self) -> Optional[dict]:
        resp = await self.session.get('https://cats-backend-cxblew-prod.up.railway.app/user')
        return await resp.json() if resp.status == 200 else None

    async def logout(self):
        await self.session.close()

    async def check_task(self, task_id: int):
        try:
            resp = await self.session.post(f'https://cats-backend-cxblew-prod.up.railway.app/tasks/{task_id}/check')
            return (await resp.json()).get('completed')
        except:
            return False

    async def complete_task(self, task_id: int):
        try:
            resp = await self.session.post(f'https://cats-backend-cxblew-prod.up.railway.app/tasks/{task_id}/complete')
            return (await resp.json()).get('success')
        except:
            return False

    async def get_tasks(self) -> Optional[List[dict]]:
        resp = await self.session.get('https://cats-backend-cxblew-prod.up.railway.app/tasks/user?group=cats')
        return (await resp.json()).get('tasks', None)
    async def register(self):
        resp = await self.session.post(
            f'https://cats-backend-cxblew-prod.up.railway.app/user/create?referral_code={config.REF}'
        )
        return resp.status == 200

    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        query = await self.get_tg_web_data()

        if not query:
            logger.error(f"Thread {self.thread} | {self.account} | Session invalid")
            await self.logout()
            return

        self.session.headers['Authorization'] = f'tma {query}'

        user_data = await self.user()
        if user_data is None or user_data.get("name") == "Error":
            if await self.register():
                logger.success(f"Thread {self.thread} | {self.account} | Registered")

    async def get_tg_web_data(self) -> Optional[str]:
        try:
            await self.client.connect()

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('catsgang_bot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('catsgang_bot'), short_name="join"),
                platform='android',
                write_allowed=True,
                start_param=config.REF
            ))

            auth_url = web_view.url
            query = unquote(auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            return query

        except Exception as e:
            logger.error(f"Thread {self.thread} | {self.account} | Error: {e}")
            return None

        finally:
            await self.client.disconnect()

    async def get_leaderboard_position(self) -> Optional[int]:
        resp = await self.session.get('https://cats-backend-cxblew-prod.up.railway.app/leaderboard')
        data = await resp.json()
        return data.get('userPlace', None)

    async def get_telegram_user(self) -> Optional[Client]:
        try:
            await self.client.connect()
            return await self.client.get_me()
        except Exception as e:
            logger.error(f"Thread {self.thread} | {self.account} | Telegram user retrieval error: {e}")
            return None
        finally:
            await self.client.disconnect()
