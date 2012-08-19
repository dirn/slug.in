#!/usr/bin/python
"""
Basic API client

To populate some data::

    python client.py create

To query that data::

    python client.py list

To search that data::

    python client.py list <slug__startswith>

To delete all the data::

    python client.py delete

"""

import os
import json
import sys

import slumber

if os.environ.get("BUILDPACK_URL", None):
    print "HITTING PROD!"
    api = slumber.API("http://zzz.herokuapp.com/_api/v1/")
else:
    print "HITTING LOCAL"
    api = slumber.API("http://localhost:8000/_api/v1/")

LIMIT = 500
test_data = [
    ["rtd", "http://readthedocs.org", "django"],
    ["google", "http://google.com", "django"],
    ["google", "http://google.com/2/", "readthedocs"],
    ["dash", "http://djangodash.com", "django"],
]

project_data = [
    {
        "name": "django",
        "whitelist":
            [
                "djangoproject.com",
                "readthedocs.org",
            ]
    },
    {
        "name": "readthedocs",
        "whitelist":
            [
                "djangoproject.com",
                "readthedocs.org",
            ]
    },
    {
        "name": "fabric",
        "whitelist":
            [
                "djangoproject.com",
                "readthedocs.org",
            ]
    }
]


if len(sys.argv) > 1:
    if sys.argv[1] == 'create':
        for data in test_data:
            key, url, project = data
            try:
                resp = api.redirect.post({"slug": key,
                                          "urls": [url],
                                           "project": project})
                print "WOOT"
                print resp
            except Exception, e:
                print "Exception: %s" % e
                try:
                    ret = json.loads(e.content)
                    print ret['traceback']
                except:
                    pass
    if sys.argv[1] == 'list':
        if len(sys.argv) == 3:
            ret = api.redirect.get(slug=sys.argv[2], limit=LIMIT)
        else:
            ret = api.redirect.get(limit=LIMIT)
        for ret in ret['objects']:
            print ret['slug']

    if sys.argv[1] == 'delete':
        ret = api.redirect.get(limit=LIMIT)
        for ret in ret['objects']:
            slug = ret['slug']
            print slug,
            print " - Deleted: %s" % api.redirect(slug).delete()

    if sys.argv[1] == "project":
        if sys.argv[2] == 'create':
            for obj in project_data:
                print api.project.post(obj)
