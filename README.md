# gv-sitemap

Create a sitemap image using Graphviz

Usage
=====

    python sitemap.py -h
    usage: sitemap.py [-h] [--authurl AUTHURL] [--authpayload AUTHPAYLOAD]
                      [--ignoreid] [--skipbaseback] [--skipbase]
                      [--skipauth SKIPAUTH]
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
      --skipbaseback        Repress links back to base URL from the sitemap
      --skipbase            Repress base URL from the sitemap
      --skipauth SKIPAUTH   Repress authenticaiton URLs containing the given
                            string from the sitemap

Example
=======

    python sitemap.py http://www.google.com/intl/en_us/ads/ >! sitemap.gv
    dot -Tpng sitemap.gv -o sitemap.png
    twopi -Tpng sitemap.gv -o sitemap.png
