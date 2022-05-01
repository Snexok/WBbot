import asyncio
from telethon import TelegramClient, events

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = 13254282
api_hash = 'd1f7738973704d2ba80a39593db47c5f'


async def main():
    client = TelegramClient('test', api_id, api_hash)
    await client.start()
    print(type(client))
    async with client.conversation("@redempt_test_2_bot", timeout=5) as conv:
        await conv.send_message("Admin")

        resp: Message = await conv.get_response()
        assert "Добро пожаловать, Лорд " in resp.raw_text
        await conv.send_message("inside")

        resp: Message = await conv.get_response()
        await conv.send_file('./../test_data/Выкупы.xlsx')


asyncio.run(main())

