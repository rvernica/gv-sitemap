import logging, os, time, signal, sys
from webkit2png import WebkitRenderer
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QTimer


try:
    LOG
except NameError:
    logging.basicConfig(
        filename='%s/%s.log' %
        (os.path.dirname(os.path.realpath(__file__)),
         os.path.basename(__file__[:-3])),
        level=logging.DEBUG)
    LOG = logging.getLogger('screenshot')


from sitemapurl import SitemapUrl


class Screenshot:
    def __init__(self,
                 display=None, style=None, qtargs=None, path=''):
        '''
        Initiates the QApplication environment using the given args.
        '''
        if QApplication.instance():
            LOG.debug(
                'QApplication has already been instantiated. Ignoring ' +  
                'given arguments and returning existing QApplication.')
            return

        qtargs2 = [sys.argv[0]]
        
        if display:
            qtargs2.append('-display')
            qtargs2.append(display)
            # Also export DISPLAY var as this may be used
            # by flash plugin
            os.environ["DISPLAY"] = display

        if style:
            qtargs2.append('-style')
            qtargs2.append(style)

        qtargs2.extend(qtargs or [])

        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.app = QApplication(qtargs2)
        self.path = path

    def screenshot(self, urls, cookies=None):
        ## Initialize Qt-Application, but make this script
        ## abortable via CTRL-C
        self.urls = urls
        self.cookies = cookies
        QTimer.singleShot(0, self.__main_qt)
        return self.app.exec_()

    # Technically, this is a QtGui application, because QWebPage requires it
    # to be. But because we will have no user interaction, and rendering can
    # not start before 'app.exec_()' is called, we have to trigger our "main"
    # by a timer event.
    def __main_qt(self):
        # Render the page.
        # If this method times out or loading failed, a
        # RuntimeException is thrown
        try:
            for url in self.urls:
                # Initialize WebkitRenderer object
                renderer = WebkitRenderer()
                renderer.width = 1024
                renderer.height = 768
                renderer.logger = LOG
                if self.cookies:
                    renderer.cookies = self.cookies

                output = open(
                    os.path.join(self.path, url.pretty() + '.png'), 'w')
                renderer.render_to_file(res=url, file_object=output)
                output.close()
                
            QApplication.exit(0)
        except RuntimeError, e:
            LOG.error("__main_qt: %s" % e)
            print >> sys.stderr, e
            QApplication.exit(1)

            
if __name__ == '__main__':
    screenshot = Screenshot()
    screenshot.screenshot([
        SitemapUrl('http://www.google.com/'),
        SitemapUrl('http://www.google.com/intl/en/about/')
    ])
