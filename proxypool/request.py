from .config import HEADERS
from .dbop import RedisOperator
from requests.exceptions \
    import ProxyError, ConnectionError, Timeout, ChunkedEncodingError
import requests
import logging


class PageRequest(object):
    """爬虫类使用的解析页面的类
    支持自动切换代理
    """

    def __init__(self):
        # 存储 requests 代理参数（首次不使用代理）
        self.proxies_arg = None
        self._pool = RedisOperator()
        self._logger = logging.getLogger('root')
        self._headers = HEADERS

    def get_resp(self, url, retry=2):
        """带有重试功能的 requests
        :param url: 请求链接
        :param retry: 重试次数
        :return: requests结果
        """
        try:
            return requests.get(url, headers=self._headers, timeout=30,
                                proxies=self.proxies_arg)
        except (ProxyError, ConnectionError, Timeout,
                ChunkedEncodingError):
            if retry > 0:
                return self.get_resp(url, retry=retry - 1)
            self._logger.warning('爬虫可能被反爬，正在加载代理重试')
            # 请求失败，从池中获取代理进行重试
            self.load_proxy()
            return self.get_resp(url)

    def load_proxy(self):
        """从代理池中取一个代理用于requests"""
        self.proxies_arg = {'http': self._pool.get()}
