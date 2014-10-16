# -*- coding: utf-8 -*-
##
## KS wrapper to test BibCheck rules
##
"""
testbed for bibcheck check_record with comparison of records
Usage: debug_check_record search_pattern [collection]
"""
def diffrec(oldrec, newrec):
    """ try to find difference between 2 records and print it """
    recid = oldrec['001'][0][3]
    oldkeys = oldrec.keys()
    oldkeys.sort()
    for tag in oldkeys:
        if newrec.has_key(tag):
            for (fpos, field_obj) in enumerate(oldrec[tag]):
                tagii = tag + field_obj[1] + field_obj[2]
                tagii = tagii.replace(' ','_')
                oldfields = field_obj[0]
                try:
                    newfields = newrec[tag][fpos][0]
                except IndexError:
                    print "%s | %s %s deleted" % (recid, tagii, oldfields)
                    continue
                for (vpos, oldvalue) in enumerate(oldfields):
                    try:
                        newvalue = newfields[vpos]
                    except IndexError:
                        newvalue = 'deleted'
                    if not newvalue == oldvalue:
                        print "%s | %s %s -> %s" % \
                        (recid, tagii, oldvalue, newvalue)
                if len(newfields) > len(oldfields):
                    for newvalue in newfields[len(oldfields):]: 
                        print "%s | %s %s added" % (recid, tagii, newvalue)
            if len(newrec[tag]) > len(oldrec[tag]):
                for new_object in newrec[tag][len(oldrec[tag]):]: 
                    print "%s | %s %s added" % (recid, tagii, new_object[0])
        else:
            print "%s: deleted tag %s" % (recid, tag)
    for tag in newrec.iterkeys():
        if not oldrec.has_key(tag):
            print "%s: new tag %s" % (recid, tag)

def debug_check_record(pattern, collection):
    """ test environment for bibcheck check_record """
    import copy
    from mvtexkey_z2a import check_record
    from invenio.bibcheck_task import AmendableRecord
    from invenio.search_engine import get_record
    from invenio.search_engine import search_pattern
    from invenio.search_engine import get_collection_reclist
#    from invenio.bibrecord import record_add_field

    records = search_pattern(p=pattern)
    if collection:
        records = records.intersection(get_collection_reclist(collection))

    print "Checking %i records" % (len(records))

    for rec in records:
        marcrec = get_record(rec)
#        record_add_field(marcrec, "035", subfields=[("a","wegdamit"),("9","SPIRESTeX")])
        oldrec = copy.deepcopy(marcrec)
        message = check_record(AmendableRecord(marcrec))
        
        print message
        diffrec(oldrec, marcrec)
def main(): 
    """main function"""
    import sys
    if (len(sys.argv) < 2):
        print "Usage: debug_check_record search_pattern [collection] "
        sys.exit(0)
    pattern = sys.argv[1]
    if (len(sys.argv) > 2):
        collection = sys.argv[2]
    else:
        collection = ""
    debug_check_record(pattern, collection)

if __name__ == "__main__":
    main()  

