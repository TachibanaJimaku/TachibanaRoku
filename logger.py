import datetime

VERBOSE = False


def time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Logger:
    def __init__(self, name):
        self.name = name

    def verbose(self, msg):
        if VERBOSE:
            print(f"{time()} 详细内容 {self.name}: {msg}")

    def info(self, msg):
        print(f"{time()} 信息 {self.name}: {msg}")

    def error(self, msg):
        print(f"{time()} 错误 {self.name}: {msg}")

    def warning(self, msg):
        print(f"{time()} 警告 {self.name}: {msg}")
