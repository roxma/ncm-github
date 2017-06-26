# -*- coding: utf-8 -*-

from cm import register_source, Base
register_source(name='github-emoji',
        abbreviation='emoji',
        scopes=['gitcommit', 'markdown', 'magit'],
        word_pattern = r':[\w+\-]*',
        cm_refresh_length=2,
        priority=8)

from .emoji.codes import CODES

class Source(Base):
    def cm_refresh(self,info,ctx):
        matches = [':'+k+':' for k in CODES.keys()]
        self.complete(info, ctx, ctx['startcol'], matches)
