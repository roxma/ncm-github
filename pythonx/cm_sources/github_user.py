
from cm import register_source, Base, getLogger
register_source(name='github-user',
                   abbreviation='user',
                   scopes=['gitcommit', 'markdown', 'magit'],
                   word_pattern = r'\w+',
                   cm_refresh_length=-1,
                   cm_refresh_patterns=[r'github.com\/', r'@'],
                   priority=9)

from urllib.request import urlopen
from urllib.parse import urlencode
import json
from .api import create_request

logger = getLogger(__name__)

class Source(Base):

    def __init__(self,nvim):
        Base.__init__(self, nvim)

    def cm_refresh(self,info,ctx):
        query = {
                'q': ctx['base'] + ' in:login',
                }
        url = 'https://api.github.com/search/users?' + urlencode(query)
        req = create_request(url)
        logger.debug("url: %s", url)

        matches = []
        with urlopen(req, timeout=30) as f:
            rsp = f.read()
            logger.debug("rsp: %s", rsp)
            rsp = json.loads(rsp.decode())
            for item in rsp['items']:
                matches.append(item['login'])

        logger.debug("matches: %s", matches)
        self.complete(info, ctx, ctx['startcol'], matches, refresh=rsp['incomplete_results'])

