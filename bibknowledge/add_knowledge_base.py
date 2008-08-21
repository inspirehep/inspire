#usage: add_knowledge_base.py filename 
#adds a knowledge base file into invenio database
#knowledge base file format: xxx---yyy
#the name of the file will become the name of the knowledge base
#you can get CERN knowledge bases by:
#wget -r -l1 -H -t1 -nd -N -np -A.kb -erobots=off http://doc.cern.ch/uploader/KB
#you should create this index to speed things up:
#create index mappingskey on fmtKNOWLEDGEBASEMAPPINGS(m_key)
from invenio.bibformat_dblayer import add_kb, add_kb_mapping, kb_mapping_exists
import sys

ok_files = []
#open the files given as parameters
for arg in sys.argv:
    try:
        f=open(arg)
        ok_files.append(arg)
        f.close()
    except:
        pass

for file in ok_files:
    #create a corresponding kb
    add_kb(file, file)
    for line in open(file):
        line=line.rstrip('\n')
        #see if it contains ---
        if (line.count("---") == 1):
            leftright = line.split("---")
            #if the mapping does not exist in the kb, add it
            if not kb_mapping_exists(file,leftright[0]):
                add_kb_mapping(file, leftright[0], leftright[1])
    f.close()