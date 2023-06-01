import os 
import gevent.monkey
gevent.monkey.patch_all()
import multiprocessing

from chatgpt_wrapper.core.logger import logger

# 服务地址（adderes:port） 
port=8888
bind = f"0.0.0.0:{port}"
# bind = f"127.0.0.1:{port}"
# 启动进程数量
workers = 1
# workers = multiprocessing.cpu_count() * 2 +1
worker_class = 'gevent'
threads = 2
preload_app = True
reload = True
x_forwarded_for_header = 'X_FORWARDED-FOR'

accesslog = "-"  # log to stdout
errorlog = "-"  # log to stderr
# 使用自定义的 logger 记录访问日志
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
def access_log(app, req, res, time):
    logger.info(access_log_format % {
        'h': req.remote_addr,
        'l': '-',
        'u': getattr(req, 'user', '-'),
        't': req.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'r': req.path,
        's': res.status_code,
        'b': res.content_length,
        'f': req.headers.get('Referer', '-'),
        'a': req.headers.get('User-Agent', '-')
    })

# 使用自定义的 logger 记录错误日志
def when_ready(server):
    logger.info("gunicorn is ready")

def on_starting(server):
    logger.info("gunicorn is starting")

def on_exit(server):
    logger.info("gunicorn is exiting")

# 记录 worker 开始和结束的日志
def worker_int(worker):
    logger.info("worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    logger.info("worker aborted (pid: %s)", worker.pid)

def worker_exit(server, worker):
    logger.info("worker exited (pid: %s)", worker.pid)
# gunicorn -c gun.py main:app
# export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES on MacOS

"""
USEFUL DOCS
https://blog.51cto.com/u_15080026/3989166   https://zhuanlan.zhihu.com/p/102716258   https://blog.csdn.net/qq_38236744/article/details/119252923

CONFIGURABLE VARIABLES:
bind: 指定应用程序监听的主机和端口。可以使用 Unix 套接字路径或网络地址, 例如 127.0.0.1:8000 或 unix:/path/to/socket。
workers: 指定要使用的工作进程数。建议将工作进程数设置为 CPU 内核数的 2-4 倍。
worker_class: 指定工作进程使用的处理请求的类。默认为 sync, 也可以使用 gevent 或 eventlet。
threads: 指定每个工作进程中要使用的线程数。默认为 1。
worker_connections: 指定每个工作进程中要保持的最大打开连接数。默认为 1000。
backlog: 指定传入连接队列的大小。默认为 2048。
timeout: 指定工作进程接收请求的超时时间。默认为 30 秒。
graceful_timeout: 指定工作进程在退出前等待处理当前请求的超时时间。默认为 30 秒。
keepalive: 指定是否启用 HTTP Keep-Alive 连接。默认为 True。
accesslog: 指定访问日志文件的路径。默认为 None, 表示不记录访问日志。
errorlog: 指定错误日志文件的路径。默认为 None, 表示将错误消息输出到标准错误流中。
loglevel: 指定日志级别。默认为 "info", 也可以设置为 "debug"、"warning"、"error" 或 "critical"。
除了这些变量之外, gun.py 文件中还可以设置其他 Gunicorn 启动选项, 例如 pidfile、umask 和 daemon 等。您可以在 Gunicorn 文档中找到更多关于这些选项的详细信息。
"""