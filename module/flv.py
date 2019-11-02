import os

log = None
file = None
total_size = 0
savepath = None


def on_start(**kargs):
    global file, savepath
    savepath = kargs['savepath'] + 'a.flv'
    file = open(savepath, 'wb')


def on_chunk(chunk):
    global file, total_size
    file.write(chunk)
    total_size += len(chunk)


def on_end():
    global file, total_size
    file.close()

    log.info("下载完成 %d" % total_size)

    if total_size == 0:
        os.remove(savepath)
        log.info("移除以下空文件： %s" % savepath)
