import asyncio
import os
from utils.core.telegram import Accounts
from utils.starter import start, stats
from data import config


async def main():
    print("Soft's author: https://t.me/ApeCryptor")
    print("Fixed by BOTPROD: @botpr0d\n")

    actions = {
        0: about_soft,
        1: start_soft,
        2: get_statistics,
        3: create_sessions
    }

    try:
        action = int(input("Select action:\n0. About soft\n1. Start soft\n2. Get statistics\n3. Create sessions\n\n> "))
    except ValueError:
        print("Invalid input. Please enter a number between 0 and 3.")
        return

    if action in actions:
        await actions[action]()
    else:
        print("Invalid action selected.")


async def about_soft():
    print(config.SOFT_INFO)


async def start_soft():
    if not os.path.exists('sessions'):
        os.mkdir('sessions')

    if config.PROXY['USE_PROXY_FROM_FILE']:
        ensure_file_exists(config.PROXY['PROXY_PATH'])
    else:
        ensure_file_exists('sessions/accounts.json')

    accounts = await Accounts().get_accounts()
    tasks = [
        start(session_name=acc['session_name'], phone_number=acc['phone_number'], thread=thread, proxy=acc['proxy'])
        for thread, acc in enumerate(accounts)
    ]
    await asyncio.gather(*tasks)


async def get_statistics():
    await stats()


async def create_sessions():
    if not os.path.exists('sessions'):
        os.mkdir('sessions')
    await Accounts().create_sessions()


def ensure_file_exists(path: str):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write("")


if __name__ == '__main__':
    asyncio.run(main())
