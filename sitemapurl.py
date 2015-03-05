import re, urlparse

class SitemapUrl(str):
    '''
    Wrapper for strings that store URLs in order to ignote IDs when
    comparing URLs.

    '''
    enabled = True
    reobf = re.compile('/\d+(?=$|/)')

    def __init__(self, value):
        ## ignore IDs so URLs with different IDs are considered
        ## equal
        urlsplit = urlparse.urlparse(value)
        self.valueobf = urlsplit.scheme + '://' + \
                        urlsplit.netloc + urlsplit.path
        self.valueobf = SitemapUrl.reobf.sub('/0', self.valueobf) \
                        if SitemapUrl.enabled else self.valueobf
        self.valuepretty = urlparse.urlparse(
            self.valueobf).path[1:].replace('/', '_')
        if self.valuepretty.endswith('_'):
            self.valuepretty = self.valuepretty[:-1]
        if len(self.valuepretty) == 0:
            self.valuepretty = '_'

    def __eq__(self, other):
        return self.valueobf.__eq__(other.valueobf)

    def __ne__(self, other):
        return self.valueobf.__ne__(other.valueobf)

    def __hash__(self):
        return self.valueobf.__hash__()

    def pretty(self):
        '''
        Return a short nice formated string.
        '''
        return self.valuepretty
