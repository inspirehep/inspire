#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################################################################
"""Get N most recent public items from a set of feeds; format and dump them."""

try:
    import feedparser
except ImportError:
    print "Please install the Python feedparser library."
import re
import sys
import codecs
import optparse

from invenio.dbquery import run_sql


FEEDS = [
         #("http://invenio-software.org/query?status=assigned&status=in_work&status=infoneeded&status=infoneeded_new&status=new&changetime=30daysago..&keywords=~INSPIRE+NEWS&format=rss&col=id&col=summary&col=status&col=type&col=priority&col=milestone&col=component&order=priority", "Current Work"),
         #("http://invenio-software.org/query?status=closed&status=in_merge&changetime=30daysago..&keywords=~NEWS&format=rss&col=id&col=summary&col=status&col=type&col=priority&col=milestone&col=component&order=priority", "Recently Finished Work"),
         ("http://twitter.com/statuses/user_timeline/78852440.rss", "INSPIRE News", False, 2),
        ]

FEED_PRE = { 2: """
<div id="sidebar" class="portalboxbody">
 <table class="sidebar_linktable">
  <tr>
   <td>
    <h3>HEP</h3>
     <ul>
      <li><a href="/help/search-tips">Search Tips</a></li>
      <li><a href="/help/">INSPIRE Help</a></li>
      <li><a href="/help/corrections">Corrections</a></li>
      <li><a href="/help/additions">Additions</a></li>
      <li><a href="mailto:feedback@inspirehep.net">Email Us</a></li>
     </ul>

    <h3>INSPIRE</h3>
     <ul>
      <li><a href="http://www.projecthepinspire.net">About INSPIRE</a></li>
      <li><a href="/search?ln=en&amp;p=cited%3A50-%3E30000+year%3A2009&amp;f=&amp;action_search=Search&amp;sf=&amp;so=d&amp;rm=citation&amp;rg=10&amp;sc=0&amp;of=hb">Recent topcites</a></li>
      <li><a href="search?ln=en&p=find+tc+review&f=&action_search=Search&sf=&so=d&rm=citation&rg=10&sc=0&of=hb">HEP Reviews</a></li>
      <li><a href="http://www.symmetrymagazine.org/breaking"><i>symmetry breaking</i></a></li>
     </ul>

    <h3>Resources</h3>
     <ul>
      <li><a href="http://www.arXiv.org">arXiv</a></li>
      <li><a href="http://hepdata.cedar.ac.uk/">HEPDATA</a></li>
      <li><a href="http://pdg.lbl.gov">PDG</a></li>
     </ul>
   </td>
  </tr>
 </table>

 <table class="sidebar_bugboxtable">
  <tr>
""",
}

FEED_POST = { 2: """
  </tr>
  <tr>
   <td>
    <p align=right>
     <a href="http://www.twitter.com/inspirehep">
      <img src="http://twitter-badges.s3.amazonaws.com/t_small-a.png" alt="Follow inspirehep on Twitter"/>
     </a>
    </p>
   </td>
  </tr>
 </table>
</div>
""",
}

def configOptParse():
    parser = optparse.OptionParser(usage = "%prog [options] [-o outfile]")
    parser.add_option('-n', '--number', dest="number", action="store", type="int", metavar="N",
                      default=3, help="Get N most recent public LJ posts.  Defaults to 3")
    parser.add_option('-u', '--uname', dest="uname", action="store", metavar="UNAME", default='anonymous',
                      help="Substituted for UNAME into the resource URL.  Defaults to anonymous")
    parser.add_option('-r', '--resource', dest="url", action="store", metavar="URL",
                      default='http://cdswaredev.cern.ch/invenio/report/1?format=rss&USER=UNAME',
                      help="Updates from URL (Token UNAME substituted for value of -u). Defaults to http://cdswaredev.cern.ch/invenio/report/1?format=rss&USER=UNAME")
    parser.add_option('-o', '--outfile', dest="outfile", action="store", metavar="FILE", default=None,
                      help="Output to FILE.  - writes to stdout.  Defaults to no output")
    parser.add_option('-d', '--dbwrite', dest="dbwrite", action="store_true", default=False,
                      help="Write feed data into the MySQL instance. Defaults to off.")
    options, args = parser.parse_args()
    return parser, options, args

def postGenerator(url, max, filter = lambda x: x, transform = lambda x: x):
    count = 0
    date = ''
    for post in feedparser.parse(url).entries:
        if count == max: break
        if filter(post.title):
            count += 1
            try:
                date = post.published[:19]
            except AttributeError:
                date = "%d-%02d-%02d" % post.updated_parsed[0:3]
            try:
                title = post.title.decode('utf-8')
            except UnicodeEncodeError:
                title = post.title
            yield date, transform(title), post.link

def filters(msg):
    """Enable filtering of the entries displayed.

    Multiple kinds of filtering can be done by making this a logical and of
    several additional filter functions.
    """

    # Remove @ replies from twitter feed
    if re.search('@[a-zA-Z]+', msg, re.IGNORECASE):
        return False
    return True

def transforms(msg):
    """Enable various content transformations in one place"""

    # Remove 'inspirehep: ' from the front of tweets
    if msg.startswith('inspirehep: '):
        msg = msg[12:]

    # Autoheat URLs
    toks = msg.split()
    ret_toks = []
    for tok in toks:
        if tok.startswith("http://") or tok.startswith("https://"):
            ret_toks.append('<a href="'+tok+'">'+tok+'</a>')
        else:
            ret_toks.append(tok)
    msg = ' '.join(ret_toks)

    return msg

def outputGenerator(header, input, tolink):
    yield u"   <td class=\"bugboxtd\">\n    <h3>"+header+"</h3>\n    <ul class=\"hanging\">"
    for date, title, link in input:
        if tolink:
            yield u"\n     <li class=\"hanging\">%s <a href=\"%s\">%s</a></li>" % (date, link, title)
        else:
            yield u"\n     <li class=\"hanging\">%s %s</li>" % (date, title)
    yield u'\n    </ul>\n   </td>'


if __name__ == "__main__":

    parser, options, args = configOptParse()
    out = sys.stdout

    if (len(sys.argv) == 0) or ((options.outfile == None) and (options.dbwrite == False)):
        parser.print_help()
        sys.exit()
    if options.outfile:
        if options.outfile != '-':
            out = codecs.open(options.outfile, 'w', 'utf-8')

    for url, title, tolink, db_num in FEEDS:
        portalbox_content = u'' + FEED_PRE[db_num]
        for line in outputGenerator(title,
                                    sorted(postGenerator(url.replace('UNAME', options.uname),
                                                         options.number,
                                                         filter=filters,
                                                         transform=transforms),
                                           reverse=True),
                                    tolink
                                    ):
            portalbox_content += line
        portalbox_content += FEED_POST[db_num]
        if options.dbwrite:
            run_sql("UPDATE portalbox SET body=%s WHERE id=%s", (portalbox_content, str(db_num)))
        if options.outfile:
            out.write(portalbox_content)

    # close any working files
    outname = out.name
    if outname != '<stdout>':
        out.close()
