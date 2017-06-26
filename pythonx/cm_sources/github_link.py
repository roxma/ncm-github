
from cm import register_source, Base, getLogger
register_source(name='github-link',
                   abbreviation='link',
                   scopes=['markdown'],
                   word_pattern = r'[^)(]+',
                   cm_refresh_length=-1,
                   cm_refresh_patterns=[r'\[(\w+\/)?[\w.\-]+\]\('],
                   priority=9)

from urllib.request import urlopen
from urllib.parse import urlencode
import json
import re
from .api import create_request

logger = getLogger(__name__)

class Source(Base):

    def __init__(self, nvim):
        Base.__init__(self, nvim)

    def cm_refresh(self, info, ctx):

        # `.*` greedy match, push to the the end
        typed = ctx['typed']
        base = ctx['base']
        txt = typed[0 : len(typed)-len(base)]

        match = re.search(r'.*\[((\w+)\/)?([\w.\-]+)\]\($', txt)
        if not match:
            logger.debug("match pattern failed: %s", txt)
            return

        user = match.group(2)
        repo = match.group(3)

        query = {
                'q': repo + ' in:name',
                'sort': 'stars',
                }

        if user:
            query['q'] += ' user:' + user

        url = 'https://api.github.com/search/repositories?' + urlencode(query)
        req = create_request(url)
        logger.debug("url: %s", url)

        matches = []
        with urlopen(req, timeout=30) as f:
            rsp = f.read()
            logger.debug("rsp: %s", rsp)
            rsp = json.loads(rsp.decode())
            for item in rsp['items']:
                matches.append(dict(word=item['html_url']))

        logger.debug("matches: %s", matches)
        self.complete(info, ctx, ctx['startcol'], matches, refresh=rsp['incomplete_results'])

