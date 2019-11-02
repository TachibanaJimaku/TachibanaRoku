import argparse
import asyncio
import datetime
import json
import os
import random
import time
import urllib.request

import danmaku
import modules
from module.logger import Logger

CHUNK_SIZE = 16 * 1024

parser = argparse.ArgumentParser()
parser.add_argument("--room-id", action="store", dest="room_id", type=int, required=True)
parser.add_argument("--savepath", action="store", dest="savepath", required=True)
parser.add_argument("--time-format", action="store", dest="time_format", default='%Y-%m-%d_%H-%M-%S')
for name, params in modules.request_args.items():
    parser.add_argument(name, **params)
args = parser.parse_args()

original_room_id = room_id = args.room_id
savepath = args.savepath
start_time = datetime.datetime.now().strftime(args.time_format)
log = Logger(f"{room_id} 录播模块")


def get_json_from(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as conn:
        response = conn.read()
        text = response.decode("utf-8")
        infoa = json.loads(text)
        return infoa


def get_info(uid):
    roomInitRes = get_json_from(f"https://api.live.bilibili.com/room/v1/Room/room_init?id={uid}")
    if roomInitRes["msg"] != "ok":
        raise RuntimeError("读取 room_init 文件错误，请检查网络设置。")
    room_id = roomInitRes["data"]["room_id"]
    log.info("直播间号: " + str(room_id))
    playUrlRes = get_json_from(f"https://api.live.bilibili.com/room/v1/Room/playUrl?cid={room_id}&qn=0&platform=web")

    if 'message' in playUrlRes:
        log.error(playUrlRes['message'])
        playUrlRes = json.loads(str(input(
            '请用浏览器打开' + f"  https://api.live.bilibili.com/room/v1/Room/playUrl?cid={room_id}&qn=0&platform=web  "
            + '然后将内容全部粘贴到这里: ')))

    baseInfoRes = get_json_from(f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={room_id}&from=room")
    return {'roomInitRes': roomInitRes, 'playUrlRes': playUrlRes, 'baseInfoRes': baseInfoRes}


async def download_flv(flv_url):
    total_downloaded = 0
    req = urllib.request.Request(
        flv_url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3497.100 Safari/537.36',
        }
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                raise RuntimeError("文件结束，这通常不是错误。")
            modules.on_chunk(chunk)
            total_downloaded += CHUNK_SIZE
            await asyncio.sleep(0)


log.verbose("开始中...")
info = get_info(room_id)
room_id = info['roomInitRes']['data']['room_id']
short_id = info['roomInitRes']['data']['short_id']
uid = info['roomInitRes']['data']['uid']
is_living = info['baseInfoRes']['data']['live_status'] == 1
flv_url = random.choice(info['playUrlRes']['data']["durl"])["url"] if "playUrlRes" in info else None
current_qn = info['playUrlRes']['data']["current_qn"] if "playUrlRes" in info else None
title = info['baseInfoRes']['data']['title'].replace('/', 'or').replace(' ', '_')
log.info(f"房间号: {room_id}, 标题: {title}, QN: {current_qn}, 地址: {flv_url}")

start_timestamp = time.time()
savepath = savepath.format(**globals())
os.makedirs(os.path.dirname(savepath), exist_ok=True)
log.info("保存路径: %s" % savepath)
modules.on_start(**globals())

if not is_living:
    loop = asyncio.get_event_loop()
    loop.close()


async def main():
    danmaku_task = asyncio.create_task(danmaku.connect(room_id, modules.on_danmaku))
    try:
        await download_flv(flv_url)
        danmaku_task.cancel()
        log.error("这个不可能出现的啊。。。。")
    except Exception as e:
        raise
    finally:
        danmaku_task.cancel()
        modules.on_end()
        log.info("关闭。")
