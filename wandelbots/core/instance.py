from wandelbots.util.logger import _get_logger


class Instance:
    def __init__(self, url, user=None, password=None):
        self.user = user
        self.password = password
        self.url = self._parse_url(url)
        self.logger = _get_logger(__name__)

    def _parse_url(self, host: str) -> str:
        """remove any trailing slashes and validate scheme"""
        _url = host.rstrip("/")
        if _url.startswith("https"):
            if not self.user or not self.password:
                raise ValueError("User and password are required for https connections")
        elif _url.startswith("http"):
            if self.user or self.password:
                raise ValueError("User and password are not required for http connections")
        elif "wandelbots.io" in _url:
            _url = "https://" + _url
        else: # assume http
            _url = "http://" + _url
        return _url
            
    def _connect(self):
        self.logger.info(f"Connecting to {self.url}")
        # do some connection stuff
            
    def has_auth(self):
        return self.user and self.password