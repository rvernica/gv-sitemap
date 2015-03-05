# gv-sitemap

Create a sitemap image using Graphviz.

About
=====

The sitemap.py script takes an URL as input and generates a GraphViz
(.gv) graph at the output. The graph is a representation of the
website starting at the given URL. The GraphViz graph can then be
processed using the GraphViz tool set (e.g., dot) to produce an image.

The script can generate screenshots for each page using the python-webkit2png
library https://github.com/adamn/python-webkit2png which needs to be
installed separately. Use the --getscreenshots option.

Usage
=====

    python sitemap.py -h
    usage: sitemap.py [-h] [--authurl AUTHURL] [--authpayload AUTHPAYLOAD]
                      [--ignoreid] [--skipself] [--skipbase] [--skipbaseback]
                      [--skipauth SKIPAUTH] [--skipdownload SKIPDOWNLOAD]
                      [--getscreenshots] [--skipscreenshot SKIPSCREENSHOT]
                      baseurl

    Crawl website and output GraphViz input file containing sitemap.

    positional arguments:
      baseurl               Base URL of the website.

    optional arguments:
      -h, --help            show this help message and exit
      --authurl AUTHURL     URL for POST authentication.
      --authpayload AUTHPAYLOAD
                            Payload for the POST authentication. e.g.,
                            '{"username": "foo", "password": "bar"}'
      --ignoreid            Ignore URLs where the difference is just an integer.
                            e.g., if http://foo/1/bar and http://foo/2/bar are
                            both present only one of them is visited.
      --skipself            Skip edges pointing to the same pages they are
                            originating from.
      --skipbase            Repress base URL from the sitemap
      --skipbaseback        Repress links back to base URL from the sitemap
      --skipauth SKIPAUTH   Repress authentication URLs containing the given
                            string from the sitemap
      --skipdownload SKIPDOWNLOAD
                            Skip downloading the URLs containing the given string.
      --getscreenshots      Take screenshots of each page for use as node image.
      --skipscreenshot SKIPSCREENSHOT
                            Repress authentication URLs containing the given
                            string from the sitemap

Example
=======

    python sitemap.py http://www.google.com/intl/en_us/ads/ > sitemap.gv
    dot -Tpng sitemap.gv -o sitemap.png
