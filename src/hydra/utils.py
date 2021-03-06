import redis
import operator
from urlparse import urlparse

from django.conf import settings
from sphinx.ext import intersphinx

from .api import RedisRedirect, RedisProject

r = redis.StrictRedis.from_url(settings.REDIS_URL)


def safe_save(project, slug, url):
    """
    Save things to Redis, but check if they exist first
    """
    obj = RedisRedirect(project=project, slug=slug)
    if not obj.exists():
        obj.save()
    if not obj.url_exists(url):
        obj.incr(url)


def read_intersphinx(project, file, urlpattern):
    """
    Reads file as intersphinx format. Prepends the url pattern on the front of
    URLs. URL Pattern should have a %s in it for string formatting.

    Only supports intersphinx v2. It parses down into an effective set of data
    that is:

    {'<id>': [
        "<project>", # From conf.py
        "<version>", # From conf.py
        "<url>", # With anchor
        <title>" # Usually blank
        ]
    }

    We then smartly parse the anchor tag and add it into Redis.
    """
    f = open(file)
    f.readline()
    data = intersphinx.read_inventory_v2(f, urlpattern, operator.mod)
    for top_key in data.keys():
        print "KEY: %s" % top_key
        inner_keys = data[top_key].keys()
        for inner_key in inner_keys:
            print "INNER KEY: %s" % inner_key
            _project, version, url, title = data[top_key][inner_key]
            url_key = url.split('#')[1]
            if ":" in url_key:
                #This dumps junk data into the url namespace we don't need
                print "INNER: %s->%s" % (inner_key, url)
                safe_save(project, inner_key, url)
            else:
                last_key = url_key.split('.')[-1]
                if last_key != url_key:
                    #Only save last key if it differes
                    print "LAST: %s->%s" % (last_key, url)
                    safe_save(project, last_key, url)
                print "URL: %s->%s" % (url_key, url)
                safe_save(project, url_key, url)


def in_whitelist(project, url):
    parsed_url = urlparse(url)
    if parsed_url.scheme == '':
        return False, 'url must be absolute'
    project = RedisProject(project)
    results = [parsed_url.netloc.endswith('.%s' % domain)
               for domain in project.whitelist]
    results.append(parsed_url.netloc in project.whitelist)
    if not any(results):
        return False, '%s is not on a domain in the whitelist.' % url
    return True, ''
