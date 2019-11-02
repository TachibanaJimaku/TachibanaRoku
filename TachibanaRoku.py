from roku import *

if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except:
            log.warning('没有在直播，程序等待10秒钟，然后重试。')
            time.sleep(10)
