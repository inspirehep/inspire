#!/usr/bin/env python
"""
NOTE: in order for this script to work, you have to put in
CFG_ETCDIR/twitter-credentials.txt a four-lines text file containing in order:

* consumer_key
* consumer_secret
* access_token_key
* access_token_secret
"""

import time
import sys

try:
    import twitter
except:
    import warnings
    warnings.warn("Install twitter package. Otherwise the twitter box in the main page will not work.")
    sys.exit(0)

import os
import cgi
import re

from invenio.dbquery import run_sql
from invenio.config import CFG_ETCDIR, CFG_SITE_URL, CFG_SITE_SECURE_URL
from invenio.errorlib import register_exception

CFG_TWITTER_CREDENTIALS_PATH = os.path.join(CFG_ETCDIR, 'twitter-credentials.txt')
CFG_TWITTER_INSPIRE_USER = 78852440
CFG_PBX_ID = 2

RE_TWITTER_PLACEMARK = re.compile("\n*%s(.*?)%s\n*" % (re.escape("<!-- TWITTER_START -->"), re.escape("<!-- TWITTER_END -->")), re.M + re.S)

CFG_TWITTER_BOX_TPL = """
<!-- TWITTER_START -->
<table class="sidebar_bugboxtable">
  <tbody><tr>
   <td class="bugboxtd">
    <h3>INSPIRE News</h3>
    <ul class="hanging">
%s
    </ul>
   </td>
  </tr>
  <tr>
   <td>
    <p align="right">
     <a href="http://www.twitter.com/inspirehep">
      <img src="http://twitter-badges.s3.amazonaws.com/t_small-a.png" alt="Follow inspirehep on Twitter" />
     </a>
    </p>
   </td>
  </tr>
 </tbody>
</table>
<!-- TWITTER_END -->
"""

def get_twitter_api(path=CFG_TWITTER_CREDENTIALS_PATH):
    lines = open(path).readlines()
    consumer_key = lines[0].strip()
    consumer_secret = lines[1].strip()
    access_token_key = lines[2].strip()
    access_token_secret = lines[3].strip()
    return twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret)

def get_twitter_timeline(api=None, user=CFG_TWITTER_INSPIRE_USER, n=3):
    if api is None:
        api = get_twitter_api()
    return api.GetUserTimeline(user, include_rts=False, exclude_replies=True)[:3]

def adapt_urls(text, urls):
    for url_from, url_to in urls.items():
        url_from = url_from.encode('utf8')
        url_to = url_to.encode('utf8')
        if url_to.startswith(CFG_SITE_URL) or url_to.startswith(CFG_SITE_SECURE_URL):
            ## Internal link, no need fot target="_blank"
            text = text.replace(url_from, '<a href="%s">%s</a>' % (cgi.escape(url_to, True), cgi.escape(url_from)))
        else:
            text = text.replace(url_from, '<a href="%s" target="_blank">%s</a>' % (cgi.escape(url_to, True), cgi.escape(url_from)))
    return text

def tweet2html(tweet):
    tweet_time = tweet.GetCreatedAtInSeconds()
    tweet = tweet.AsDict()
    text = tweet['text'].encode('utf8')
    urls = tweet.get('urls')
    if urls:
        text = adapt_urls(text, urls)
    return '<li class="hanging">%s %s</li>' % (time.strftime("%Y-%m-%d", time.gmtime(tweet_time)), text)


def get_twitter_box(api=None, timeline=None):
    if timeline is None:
        timeline = get_twitter_timeline(api=api)
    return CFG_TWITTER_BOX_TPL % '\n'.join([tweet2html(tweet) for tweet in timeline])

def update_portalbox(twitter_box=None):
    if twitter_box is None:
        twitter_box = get_twitter_box()
    portalbox = run_sql("SELECT body FROM portalbox WHERE id=%s", (CFG_PBX_ID,))[0][0]
    portalbox = RE_TWITTER_PLACEMARK.sub(twitter_box, portalbox)
    run_sql("UPDATE portalbox SET body=%s WHERE id=%s", (portalbox, CFG_PBX_ID))

if __name__ == "__main__":
    try:
        update_portalbox()
    except Exception, err:
        register_exception(alert_admin=True)
        print >> sys.stderr, "ERROR: issue in updating twitter box: %s" % err
