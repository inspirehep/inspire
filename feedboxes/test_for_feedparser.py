#!/usr/bin/env python
# A simple script to test whether the feedparser library is installed, and 
# set our exit value according to the unix standard.
import sys
try:
    import feedparser
except ImportError:
    print """********************************************
* WARNING: 'feedparser' library not installed
********************************************
* The 'feedparser' library is required for feedboxes to actually get feeds.
*
* You may want to consider running:
*                $ sudo yum install python-feedparser
*                                                ...or local equivalent
*
********************************************"""
    sys.exit(1)
sys.exit(0)
