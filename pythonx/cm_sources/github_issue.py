
from cm import register_source, Base, getLogger

register_source(name='github-issue',
                   abbreviation='issue',
                   scopes=['gitcommit', 'markdown', 'magit'],
                   word_pattern = r'((?<!^)#\d*|#\d+)',
                   cm_refresh_length=1,
                   priority=9)

from urllib.request import urlopen
from urllib.parse import urlencode
import json
import subprocess
import re
from os.path import dirname
from .api import create_request

logger = getLogger(__name__)

class Source(Base):

    def __init__(self, nvim):
        Base.__init__(self, nvim)

    def _get_repo_user(self, cwd):
        args = ['git', 'remote', '-v']
        try:
            proc = subprocess.Popen(args=args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=cwd)
            result, errs = proc.communicate('', 10)
            result = result.decode('utf-8')
            match = re.search('github.com[\/:](\w+)\/([\w.\-]+)\.git', result)
            if not match:
                return None, None

            return match.group(1), match.group(2)
        except Exception:
            logger.exception("Failed executing _get_repo_user at cwd [%s]", cwd)
            return None, None

    def cm_refresh(self,info,ctx):

        user, repo = self._get_repo_user(dirname(ctx['filepath']))
        if not repo:
            user, repo = self._get_repo_user(self.nvim.eval('getcwd()'))

        logger.info("user [%s] repo [%s]", user, repo)

        if not repo or not user:
            return

        query = {
                'q': 'user:' + user + ' repo:' + repo,
                'sort': 'updated',
                }

        url = 'https://api.github.com/search/issues?' + urlencode(query)
        req = create_request(url)
        logger.debug("url: %s", url)

        matches = []
        with urlopen(req, timeout=30) as f:
            rsp = f.read()
            logger.debug("rsp: %s", rsp)
            rsp = json.loads(rsp.decode())
            for item in rsp['items']:
                matches.append(dict(word='#%s' % item['number'], menu=item['title']))

        logger.debug("matches: %s", matches)
        self.complete(info, ctx, ctx['startcol'], matches)

