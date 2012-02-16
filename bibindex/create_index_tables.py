#!/usr/bin/env python
# -*- coding: utf-8 -*-

from invenio.dbquery import run_sql
import getopt
import sys

def generate_tables(index_id):
    """
    This function will return SQL CREATE statements for
    creating BibIndex PAIR/PHRASE/WORD F/R tables for the given ID
    """
    return """CREATE TABLE IF NOT EXISTS idxPAIR%(id)sF (
  id mediumint(9) unsigned NOT NULL auto_increment,
  term varchar(100) default NULL,
  hitlist longblob,
  PRIMARY KEY  (id),
  UNIQUE KEY term (term)
) ENGINE=MyISAM;""" % {'id' : index_id}, """
CREATE TABLE IF NOT EXISTS idxPAIR%(id)sR (
  id_bibrec mediumint(9) unsigned NOT NULL,
  termlist longblob,
  type enum('CURRENT','FUTURE','TEMPORARY') NOT NULL default 'CURRENT',
  PRIMARY KEY (id_bibrec,type)
) ENGINE=MyISAM;""" % {'id' : index_id}, """
CREATE TABLE IF NOT EXISTS idxPHRASE%(id)sF (
  id mediumint(9) unsigned NOT NULL auto_increment,
  term text default NULL,
  hitlist longblob,
  PRIMARY KEY  (id),
  KEY term (term(50))
) ENGINE=MyISAM;""" % {'id' : index_id}, """
CREATE TABLE IF NOT EXISTS idxPHRASE%(id)sR (
  id_bibrec mediumint(9) unsigned NOT NULL,
  termlist longblob,
  type enum('CURRENT','FUTURE','TEMPORARY') NOT NULL default 'CURRENT',
  PRIMARY KEY (id_bibrec,type)
) ENGINE=MyISAM;""" % {'id' : index_id}, """
CREATE TABLE IF NOT EXISTS idxWORD%(id)sF (
  id mediumint(9) unsigned NOT NULL auto_increment,
  term varchar(50) default NULL,
  hitlist longblob,
  PRIMARY KEY  (id),
  UNIQUE KEY term (term)
) ENGINE=MyISAM;""" % {'id' : index_id}, """
CREATE TABLE IF NOT EXISTS idxWORD%(id)sR (
  id_bibrec mediumint(9) unsigned NOT NULL,
  termlist longblob,
  type enum('CURRENT','FUTURE','TEMPORARY') NOT NULL default 'CURRENT',
  PRIMARY KEY (id_bibrec,type)
) ENGINE=MyISAM;""" % {'id' : index_id}

def main():
    """
    Main function that executes on launch.
    """
    usage = """Usage: %s startindex [endindex]""" % (sys.argv[0],)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        print usage
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            print usage
            sys.exit()

    # Check parameters, we need at least startindex
    if len(args) == 1:
        args.append(args[0])
    elif len(args) != 2:
        print usage
        sys.exit(1)

    start = int(args[0])
    end = int(args[1])
    for i in range(start, end + 1):
        index = str(i)
        for query in generate_tables(index):
            run_sql(query)

if __name__ == "__main__":
    main()
