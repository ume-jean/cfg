#!/usr/bin/python

import logging
import sys
import resolve


logging.basicConfig()
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        environ = resolve.environment()
        if len(sys.argv) > 1:
            try:
                import ujson as json
            except ImportError:
                try:
                    import simplejson as json
                except ImportError:
                    import json
            with open(sys.argv[1], 'w') as outfile:
                json.dump(environ, outfile)
        else:
            for k, v in environ.iteritems():
                line = k + "=" + v + "\n"
                sys.stdout.write(line)
    except Exception, err:
        sys.stderr.write(str(err))
        sys.exit(1)
