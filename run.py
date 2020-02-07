import multiprocessing
import os
import re
import sys
import time
import requests
import urllib3

import utils
from Live import BiliBiliLive

urllib3.disable_warnings()


class BiliBiliLiveRecorder(BiliBiliLive):
    def __init__(self, room_id, check_interval=5 * 60):
        super().__init__(room_id)
        self.print = utils.print_log
        self.check_interval = check_interval

    def check(self, interval):
        while True:
            try:
                room_info = self.get_room_info()
                if room_info['status']:
                    self.print(self.room_id, room_info['roomname'])
                    break
                else:
                    self.print(self.room_id, '等待开播')
            except Exception as e:
                self.print(self.room_id, 'Error:' + str(e))
            time.sleep(interval)
        return self.get_live_urls()

    def record(self, record_url, output_filename):
        try:
            self.print(self.room_id, '√ 正在录制...' + self.room_id)
            headers = dict()
            headers['Accept-Encoding'] = 'identity'
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'
            headers['Referer'] = re.findall(r'(https://.*\/).*\.flv', record_url)[0]
            resp = requests.get(record_url, stream=True, headers=headers)
            with open(output_filename, "wb") as f:
                chunk_id = 0;
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk_id % 1000 == 0:
                        self.print(self.room_id, '√ 正在录制...' + self.room_id + " Chunk ID: " + str(chunk_id))
                    chunk_id += 1
                    f.write(chunk) if chunk else None
        except Exception as e:
            self.print(self.room_id, 'Error while recording:' + str(e))

    def run(self):
        while True:
            try:
                urls = input(
                    "请打开 https://api.live.bilibili.com/room/v1/Room/playUrl?cid=" + self.room_id + "&qn=0&platform=web 输入DURL: ")
                filename = utils.generate_filename(self.room_id)
                c_filename = os.path.join(os.getcwd(), 'files', filename)
                self.record(urls, c_filename)
                self.print(self.room_id, '录制完成' + c_filename)
            except Exception as e:
                self.print(self.room_id, 'Error while checking or recording: ' + str(e))


if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) == 2:
        input_id = str(sys.argv[1])
    else:
        raise ZeroDivisionError('请检查输入的命令是否正确 例如：python3 run.py 10086')

    BiliBiliLiveRecorder(input_id).run()
