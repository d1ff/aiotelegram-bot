#!/usr/bin/env python3
"""
Telegram asyncio bot
"""
import asyncio
import aiohttp
import logging
import pprint

pp = pprint.PrettyPrinter(indent=4)

TOKEN = "YOURTOKENHERE"

logger = logging.getLogger(__name__)

class TelegramApiError(Exception):
    pass

@asyncio.coroutine
def api_request(method_name, method='GET', **kwargs):
    """
    Coroutine for accessing Telegram API
    """
    url = "https://api.telegram.org/bot%s/%s" % (TOKEN, method_name)
    request = yield from aiohttp.request(method, url, params=kwargs)
    result = (yield from request.json())
    if result["ok"]:
        return result["result"]
    else:
        raise TelegramApiError()

@asyncio.coroutine
def get_updates(offset=0, limit=100, timeout=0):
    """
    getUpdates Telegram Method
    """
    print(offset)
    updates = api_request('getUpdates', offset=offset, limit=limit, timeout=timeout)
    return (yield from updates)

@asyncio.coroutine
def send_message(**kwargs):
    """
    sendMessage Telegram method
    """
    request = api_request("sendMessage", **kwargs)
    return (yield from request)

@asyncio.coroutine
def echo(message):
    """
    Echoes message back to chat
    """
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    result = yield from send_message(chat_id=chat_id,
                                     text=text,
                                     reply_to_message_id=message_id)
    return result

@asyncio.coroutine
def process_update(update):
    """
    Dispatches update
    """
    pp.pprint(update)
    pp.pprint((yield from echo(update["message"])))
    return update["update_id"]

@asyncio.coroutine
def process_updates():
    """
    Long polling for updates and processes them
    """
    offset = 0
    while True:
        updates = yield from get_updates(offset, timeout=5)
        tasks = [
            asyncio.async(process_update(update)) for update in updates
        ]
        for future in asyncio.as_completed(tasks):
            update_id = yield from future
            offset = max(offset, update_id+1)

def main():
    """
    Main bot entry point
    """
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(process_updates())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
