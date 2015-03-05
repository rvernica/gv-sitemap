'''
Create a sitemap image using Graphviz
'''
import argparse, ast, json, logging, os, requests, sys, urlparse
from bs4 import BeautifulSoup
from graphviz import Digraph

try:
    LOG
except NameError:
    logging.basicConfig(
        filename='%s/%s.log' %
        (os.path.dirname(os.path.realpath(__file__)),
         os.path.basename(__file__[:-3])),
        level=logging.DEBUG)
    LOG = logging.getLogger('sitemap')


from screenshot import Screenshot
from sitemapurl import SitemapUrl


class Sitemap(object):
    '''
    Crawl the given website and output a DOT structure.
    '''
    screenshot_dir = 'screenshots'

    def __init__(self, baseurl, authurl=None, authpayload=None,
                 skipself=False, skipbase=False, skipbaseback=False,
                 skipauth=None, skipdownload=None, skipscreenshot=None,
                 getscreenshots=False):
        if baseurl.endswith('/'):
            self.baseurl = SitemapUrl(baseurl)
        else:
            self.baseurl = SitemapUrl(baseurl + '/')
        self.sitemap = {}
        self.cookies = None
        ## Auth if necessary
        if authurl and authpayload:
            response = requests.post(
                authurl, data=authpayload, allow_redirects=False)
            self.cookies = response.cookies
        self.skipself = skipself
        self.skipbase = skipbase
        self.skipbaseback = skipbaseback
        self.skipauth = skipauth
        self.skipdownload = skipdownload
        self.skipscreenshot = skipscreenshot
        self.getscreenshots = getscreenshots

    def get_urls_from_response(self, url, response):
        '''
        Extract URLs from response
        '''
        soup = BeautifulSoup(response.text)
        urls = [link.get('href') for link in soup.find_all('a')]
        urls = self.clean_urls(urls)
        urlresp = SitemapUrl(response.url)
        if url != urlresp:
            self.sitemap[url] = {'outgoing': [urlresp]}
        urlsout = [u for u in set(urls) \
                   if (not self.skipself or u != url)
                   and (not self.skipbaseback or u != self.baseurl)
                   and ('auth' not in u)]
        self.sitemap[urlresp] = {'outgoing': urlsout, 'image': None}
        return urls

    def clean_urls(self, urls):
        '''
        1. Add BASE_URL to relative URLs
        2. Remove URLs from other domains
        3. Remove GET parameters from URL
        '''
        urls_new = []
        for url in urls:
            if not url:
                continue
            if url.startswith('/'):
                url = self.baseurl + url[1:]
            if not url.startswith(self.baseurl):
                continue
            urls_new.append(SitemapUrl(url))
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

            if self.skipdownload and self.skipdownload in url:
                LOG.debug('Skip URL: %s', url)
                continue

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
        self.clean()

    def clean(self):
        '''
        1. Remove base URL
        2. Remove authentication URLs
        '''
        if self.skipbase:
            del self.sitemap[self.baseurl]
        if self.skipauth:
            for key in self.sitemap.keys():
                if self.skipauth in key:
                    del self.sitemap[key]
        if self.skipbase or self.skipauth:
            for (key, value) in self.sitemap.items():
                self.sitemap[key]['outgoing'] = \
                    [u for u in value['outgoing']
                     if (self.skipbase and not u == self.baseurl)
                     or (self.skipauth and not self.skipauth in u)]

    def screenshots(self):
        '''
        Take screenshots of all the pages in sitemap.
        '''
        if not os.path.exists(Sitemap.screenshot_dir):
            os.makedirs(Sitemap.screenshot_dir)

        cookies_list = []
        for (key, value) in self.cookies.items():
            cookies_list.append(key + '=' + value)

        urls = []
        for url in self.sitemap.keys():
            if not self.skipscreenshot \
               or self.skipscreenshot not in url:
                urls.append(url)
                self.sitemap[url]['image'] = os.path.join(
                    Sitemap.screenshot_dir, url.pretty() + '.png')
        screenshot = Screenshot(path=Sitemap.screenshot_dir)
        screenshot.screenshot(urls, cookies_list)

    def gen_dot(self):
        '''
        Generate the DOT file for Graphviz
        '''
        dot = Digraph(comment='Sitemap',
                      graph_attr={'splines':'ortho',
                                  'concentrate':'true'},
                      node_attr={'fontsize':'60',
                                 'labelloc':'b',
                                 'shape':'box'},
                      edge_attr={'penwidth':'10'})
        if self.getscreenshots:
            dot.node_atts['penwidth'] = '0'
        for (key, value) in self.sitemap.items():
            name = key.pretty()
            dot.node(name,
                     label=name,
                     image=value['image'])
        for (key, value) in self.sitemap.items():
            for key2 in value['outgoing']:
                dot.edge(key.pretty(), key2.pretty())
        return dot.source


if __name__ == '__main__':
    ## Argument Parser
    parser = argparse.ArgumentParser(
        description='Crawl website and output GraphViz input file '
         + 'containing sitemap.')
    parser.add_argument(
        'baseurl',
        help='Base URL of the website.')
    parser.add_argument(
        '--authurl',
        help='URL for POST authentication.')
    parser.add_argument(
        '--authpayload',
        help='Payload for the POST authentication. e.g., '
        + '\'{"username": "foo", "password": "bar"}\'',
        type=json.loads)
    parser.add_argument(
        '--ignoreid',
        help='Ignore URLs where the difference is just an integer. '
         + 'e.g., if http://foo/1/bar and http://foo/2/bar '
         + 'are both present only one of them is visited.',
        action='store_true')
    parser.add_argument(
        '--skipself',
        help='Skip edges pointing to the same pages they are originating from.',
        action='store_true')
    parser.add_argument(
        '--skipbase',
        help='Repress base URL from the sitemap',
        action='store_true')
    parser.add_argument(
        '--skipbaseback',
        help='Repress links back to base URL from the sitemap',
        action='store_true')
    parser.add_argument(
        '--skipauth',
        help='Repress authentication URLs containing the given string '
        + 'from the sitemap')
    parser.add_argument(
        '--skipdownload',
        help='Skip downloading the URLs containing the given string.')
    parser.add_argument(
        '--getscreenshots',
        help='Take screenshots of each page for use as node image.',
        action='store_true')
    parser.add_argument(
        '--skipscreenshot',
        help='Repress screenshots for URLs containing the given string.')

    if ('--authurl' in sys.argv) and ('--authpayload' not in sys.argv):
        parser.error('--authpayload needs to be set if --authurl is used')


    args = parser.parse_args()
    SitemapUrl.enabled = args.ignoreid
    sitemap = Sitemap(args.baseurl, args.authurl, args.authpayload,
                      args.skipself, args.skipbase, args.skipbaseback,
                      args.skipauth, args.skipdownload, args.skipscreenshot,
                      args.getscreenshots)
    sitemap.crawl()
    if args.getscreenshots:
        sitemap.screenshots()
    print sitemap.gen_dot()
