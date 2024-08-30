import random
import datetime
import pandas as pd
import asyncio
import os
from utils.cats_gang import CatsGang
from data import config
from utils.core import logger
from utils.core.telegram import Accounts


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    cats = CatsGang(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = f"{session_name}.session"

    try:
        await cats.login()
        tasks = await cats.get_tasks()

        for task in tasks:
            if task['completed']:
                continue

            if task['type'] == 'OPEN_LINK':
                await handle_task(cats, task, thread, account)
            elif task['type'] == 'SUBSCRIBE_TO_CHANNEL' and task['allowCheck']:
                if await cats.check_task(task_id=task['id']):
                    await handle_task(cats, task, thread, account)
            await asyncio.sleep(random.uniform(*config.DELAYS['TASK']))

    except Exception as e:
        logger.error(f"Thread {thread} | {account} | Error: {e}")
    finally:
        await cats.logout()


async def handle_task(cats: CatsGang, task: dict, thread: int, account: str):
    if await cats.complete_task(task_id=task['id']):
        logger.success(f"Thread {thread} | {account} | Completed task «{task['title']}» and got {task['rewardPoints']} CATS")
    else:
        logger.warning(f"Thread {thread} | {account} | Couldn't complete task «{task['title']}»")


async def stats():
    accounts = await Accounts().get_accounts()

    tasks = [
        asyncio.create_task(CatsGang(
            session_name=acc['session_name'],
            phone_number=acc['phone_number'],
            thread=thread,
            proxy=acc['proxy']).stats())
        for thread, acc in enumerate(accounts)
    ]

    data = await asyncio.gather(*tasks)
    path = generate_statistics_path()
    columns = ['Phone number', 'Name', 'Balance', 'Leaderboard', 'Referral Link', 'Proxy (login:password@ip:port)']

    if not os.path.exists('statistics'):
        os.mkdir('statistics')

    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    logger.success(f"Saved statistics to {path}")


def generate_statistics_path() -> str:
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    return f"statistics/statistics_{timestamp}.csv"


if __name__ == "__main__":
    asyncio.run(stats())
