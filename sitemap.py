'''
Create a sitemap image using Graphviz
'''
import ast, logging, os,  requests, urlparse, sys
from bs4 import BeautifulSoup
from graphviz import Digraph


logging.basicConfig(
    filename='%s/%s.log' %
    (os.path.dirname(os.path.realpath(__file__)),
     os.path.basename(__file__[:-3])),
    level=logging.DEBUG)
LOG = logging.getLogger('sitemap')


ERROR_BADARGS = 85


class Sitemap(object):
    '''
    Crawl the given website and output a DOT structure.
    '''
    def __init__(self, baseurl, loginurl=None, loginpayload=None):
        self.baseurl = baseurl
        if not self.baseurl.endswith('/'):
            self.baseurl += '/'
        self.sitemap = {}
        self.cookies = None
        ## Login if necessary
        if loginurl and loginpayload:
            response = requests.post(loginurl, data=loginpayload, allow_redirects=False)
            self.cookies = response.cookies

    def get_urls_from_response(self, url, response):
        """
        Extract URLs from response
        """
        soup = BeautifulSoup(response.text)
        urls = [link.get('href') for link in soup.find_all('a')]
        urls = self.clean_urls(urls)
        if url != response.url:
            self.sitemap[url] = {'outgoing': [response.url]}
        self.sitemap[response.url] = {'outgoing': urls}
        return urls

    def clean_urls(self, urls):
        '''
        1. Add BASE_URL to relative URLs
        2. Remove URLs from other domains
        '''
        urls_new = []
        for url in urls:
            if not url:
                continue
            if url.startswith('/'):
                url = self.baseurl + url[1:]
            if not url.startswith(self.baseurl):
                continue
            urlsplit = urlparse.urlparse(url)
            urls_new.append(
                SitemapUrl(urlsplit.scheme + '://' +
                           urlsplit.netloc + urlsplit.path))
        return urls_new

    def filter_ulrs(self, urls_new, urls):
        '''
        Filter and fix URLs
        '''
        urls_filtered = []
        for url in urls_new:
            if url in self.sitemap.keys() \
               or url in urls \
               or url in urls_filtered:
                continue
            urls_filtered.append(url)
        return urls_filtered

    def crawl(self):
        '''
        Given a list of starting urls, recursively finds all descendant
        urls recursively
        '''
        urls = [self.baseurl]
        while len(urls) != 0:
            url = urls.pop(0)
            LOG.debug('Request URL: %s', url)
            LOG.debug('Remaining URLs: %s', urls)
            LOG.debug('Visited URLs: %s', self.sitemap.keys())

            response = requests.get(url, cookies=self.cookies)
            LOG.debug('Response: %s', response.__str__())
            LOG.debug('Response URL: %s', response.url)

            urls_new = self.get_urls_from_response(url, response)
            LOG.debug('Complete URLs: %s', urls_new.__str__())

            urls_new = self.filter_ulrs(urls_new, urls)
            LOG.info('Selected URLs: %s', urls_new.__str__())

            urls.extend(urls_new)

        LOG.info('Sitemap: %s', self.sitemap.__str__())

    def gen_dot(self):
        '''
        Generate the DOT file for Graphviz
        '''
        dot = Digraph(comment='Site Map')
        for key in self.sitemap.keys():
            dot.node(encode_url(key))
        for (key, value) in self.sitemap.items():
            for key2 in value['outgoing']:
                dot.edge(encode_url(key), encode_url(key2))
        return dot.source


def encode_url(url):
    '''
    map URL to a DOT accepted ID
    '''
    return urlparse.urlparse(url).path.replace('/', '_')


if __name__ == '__main__':
    if len(sys.argv) not in (2, 4):
        exampleurl = 'http://foo.bar'
        usagefile = os.path.basename(__file__)
        print 'Usage:   %s baseurl [loginurl loginpayload]' % usagefile
        print 'Example: %s %s' %  (usagefile, exampleurl)
        print 'Example: %s %s %s/login "{\'username\': \'foo\', \'password\': \'bar\'}"' \
            % (usagefile, exampleurl, exampleurl)
        sys.exit(ERROR_BADARGS)
    baseurl = sys.argv[1]
    loginurl = None
    loginpayload = None
    if len(sys.argv) == 4:
        loginurl = sys.argv[2]
        loginpayload = ast.literal_eval(sys.argv[3])
    sitemap = Sitemap(baseurl, loginurl, loginpayload)
    sitemap.crawl()
    print sitemap.gen_dot()
