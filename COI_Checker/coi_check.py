#!/usr/bin/python3
#
#      Scan proposal list for COI matches
#
#   1) Agency sends a PDF with all investigators and their affiliations
#   2) 
##
import unicodedata
import nltk
from nltk.util import ngrams
import csv
import os, subprocess
import Levenshtein as sed

import regex as re

# Customize these for yourself
MYUNIV = 'University of Washington'
# super similar but not a COI(!)
EXUNIVS = ['Washington University', 'Washington State University']

NIHpropno = re.compile('[0-9]R[0-9][0-9][A-Z]*[0-9]{6}[0][0-9](A1)?')
NIHpropstub = re.compile('[0-9]R[0-9][0-9][A-Z]*')
NIHname = re.compile('^[/s]*[A-Z,. ]+$')  # all caps plus ,.
lcf_name = re.compile('[\s]*[A-Z][a-z]+[,][\s]*[A-Z][a-z]+[\s]*')   
fl_name = re.compile('[\s]*[A-Z][a-z]+[\s]*[A-Z][a-z]+[\s]*')   

UCNAME = {'Lu','Pc'}
ac = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz,.#()- '
ALLOWEDCHARS = []
for c in ac:
    ALLOWEDCHARS.append(c)
alchar = re.compile('[a-zA-Z,. ]')

def filter_non_printable(str):
  #return ''.join(c for c in str if unicodedata.category(c) in UCNAME)
  return ''.join(c for c in str if c in ALLOWEDCHARS)

def match_unis(a,b):
    a = a.lower()
    a = a.replace('university','')
    a = a.replace('of','')
    a = a.replace(' ','')
    b = b.lower()
    b = b.replace('university','')
    b = b.replace('of','')
    b = b.replace(' ','')
    if sed.distance(a,b) < 3:
        return True
    else:
        return False
    
def is_PI_name(s):
    exwds = 'LLC INC PROFESSOR ASSISTANT ASSOCIATE UNIVERSITY ASSOCIATES INNOVATION MEDICAL SURGICAL  INCORPORATED PARTNERS RHL RHLA RCA PT NOI'.split()
    val = True
    s1 = filter_non_printable(s)
    #print('n> checking: [{}]'.format(s1), s)
    if s1.isspace() or not NIHname.match(s1):
        val = False 
    else:
        ns = s1.split()
        for name in ns:
            for w in exwds:
                if w == name:  # detect e.g. LLC
                    val = False  
    #if val:
        #print('I found PIName: ',s1)
    return val,s1

def name_dist(a,b):  # compare names which might be last, first
    # convert to first last if nesc.
    if ',' in a:  
        n1 = a.split(',')
        a = n1[1]+' '+n1[0]
    if ',' in b:
        n1 = b.split(',')
        b = n1[1]+' '+n1[0]
    a = a.lower()
    b = b.lower()
    return sed.distance(a,b)

#COIs = ['Zumbrunnen', 'Oliver Consulting', 'Stanford'] 

# read in COIs.  This CSV contains all your mentees, co-i's, co-authors etc. 
#This file comes from the required NSF spreadsheet which needs to have junk edited out. 
#  Also added a new relationship "O:" so that you can declare ownership stake in companies 
coifile = open('coa_Hannaford_Jul2020.csv')

data = csv.reader(coifile)
 

COIs = []
Relationships = {}
Affiliations = {}
for d in data:
    #print('Storing ',d)
    COIs.append(d[1].strip()) # first middle last name
    Relationships[d[1]] = d[0].strip()  # Type code
    Affiliations[d[1]] = d[2].strip()   # coi's affil.
    
print('Found ', len(COIs), ' persons with COI')

# print COIs    
#for n in COIs:
    #r = Relationships[n]
    #a = Affiliations[n]
    #print('{:30} {:4} {}'.format(n,r,a))

print('\n\n                COI Scanner Tool ')
#
#  Now user enters the PDF file sent from agency
#
#filename = input('enter pdf filename: ')
#password = input('enter pdf password: ')
filename = 'tmp.pdf'
password = 'SBIBY12*'
print ('scanning...')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
args = ["/usr/bin/pdftotext",
        '-opw', password,
        #'-enc UTF-8',
        #'-layout',
        '-enc',
        'UTF-8',
        '{}/{}'.format(SCRIPT_DIR,filename),
        '-']
res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

errorinfo = res.stderr.decode('utf-8')
doctext = res.stdout.decode('utf-8')


#print (doctext)
#for i in range(50):
    #print(doctext[i])
print('********************************Done') 

docstrings = ''.join(doctext).split()
doclines  =  doctext.splitlines()

#for i in range(50):
    #print (doclines[i])
#quit()


if len(docstrings) == 0:
    print('Pdf Scanner found no words found to check.  Is your password correct? is the pdf empty? wrong filename?')
    quit()

print('len: ', len(docstrings))     
    
#clean out punctuation
ds2 = []
punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~='''
for i,ds in enumerate(docstrings):
    x = ds
    for p in punc:
        x = x.replace(p,'')
    if x == '':
        pass   # no need for empty kws
    else:
        ds2.append(x)
docstrings = ds2     


class grant():
    def __init__(self, gnum, pi):
        self.grantNo = gnum
        self.PIName = pi
        self.linerange = [0,0]
        self.lines = []
        self.coiHits = []
        
    def checkcoi(self):
        retval = False
        gn = self.grantNo
        c1 = ''
        c2 = ''
        #print ('c> Checking: {} {}'.format(self.grantNo,self.PIName))
        for name in COIs:
            #print('chcking coi: [{}]'.format(name))
            if fl_name.match(name):
                # is the PI name close to one of your coi's names?
                d = name_dist(name, self.PIName)
                #if d < 0:
                    #print('p> ',name, '<-> ',self.PIName, d)
                if d <= 5:
                    c1 = name
                    c2 = self.PIName
                    self.coiHits.append(c1)
                    retval=True
                    
                #print (name, 'is a name')
                ###   is a random name close to one of your coi's?
                for line in self.lines:
                    #print('l>checking ',line)
                    # is the line a person name???
                    if lcf_name.match(line) or NIHname.match(line):
                        d = name_dist(name, line) 
                        #print ('     ',line, 'is a name',name.lower(),'<->',line.lower(),d)
                        #if d < 7:
                            #
                        if d < 5:
                            c1 = name
                            c2 = line
                            self.coiHits.append(c1)
                            retval = True
        # check for own school
        for line in self.lines:
            for u in EXUNIVS:
                if line.strip() == u:
                    return False
            if match_unis(MYUNIV, line):
                c1 = MYUNIV
                c2 = line
                self.coiHits.append(c1)
                retval = True
                
        if retval:
            print('Potential COI: ', gn)
            print('     ', c1,' <-> ', c2 )
            print(self.coiHits)
        return retval
    
    def clean_lines(self):
        exwords = 'Institution/Organization Page__of_ Key_Personnel_(SF424) Key_Personnel_(SF) Role Department Institution Project_Title Other_(Specify) Application_# Position'.split()
        for i,e in enumerate(exwords):
            exwords[i] = e.replace('_',' ')
        #print(exwords) 
        for i,l in enumerate(self.lines):
            # get rid of non-printing characters:
            
            tmp = ''
            for c in l:
                if c in ALLOWEDCHARS:
                    tmp += c
            l = tmp.strip()
            self.lines[i] = l
            #print('[{}]'.format(l))
            #if l.strip() in exwords:
            for w in exwords:
                #if l.startswith('P'):
                    #print('************************************************  Role',w)
                    #print('                comparing [{}] <> [{}]'.format(l,w))
                if l == w:
                    #print ('Im removing, ',l)
                    self.lines.remove(l)
        
    def print(self):
        print('------------------------------------')
        print('{:30}  PI: {}'.format(self.grantNo, self.PIName))
        print('====================================')
        for l in self.lines:
            print('=[{}]'.format(l))
        print('====================================')
        if len(self.coiHits)>0:
            print('= Potential COIs: ',self.coiHits)
        print('====================================')
    def fprint(self,f):        
        print('------------------------------------',file=f)
        print('{:30}  PI: {}'.format(self.grantNo, self.PIName),file=f)
        print('====================================',file=f)
        for l in self.lines:
            print('=[{}]'.format(l),file=f)
        print('====================================',file=f)
        if len(self.coiHits)>0:
            print('= Potential COIs: ',self.coiHits,file=f)
        print('====================================',file=f)

##   let's look for grant numbers in lines
#      and also find PI names and log start and end lines of each grant

i=0
grants = []
first = True
for l in doclines:
    if NIHpropno.match(l) or NIHpropstub.match(l):
        if first:
            first = False
        else:
            g.linerange[1] = i-2  # mark last line of prev grant
        #print('line {} is a proposal number: {}'.format(i,l))
        pr_num = l.strip()
        pi_name = ''
        for j in range(5):
            lt = doclines[i-4+j]
            #print('    ',lt)
            val,s = is_PI_name(lt)
            if val:
                pi_name += s
        #look ahead
        g = grant(pr_num,pi_name)
        g.linerange[0] = i # store start linea
        for j in range(10):
            if i+j+10 < len(doclines):
                lt = doclines[i+j+10]
                #print('Check2:                      [{}] '.format(lt))
                #if regname.match(lt):
                    #print ('                     investigator: ', lt)
        grants.append(g)
    i+=1
grants[-1].linerange[1] = i

# now collect all lines for each grant:
gn = 0
grants[0].linerange[0] = 0
testgrant = 31
for i,l in enumerate(doclines):
    #print(gn, len(grants))
    g1 = grants[gn]
    
    lr0 = g1.linerange[0]
    lr1 = g1.linerange[1]
    if (i >= lr0) and (i <= lr1): 
        if not re.match('^[\s]*$',l):   # no empty lines
            grants[gn].lines.append(l)
    else:
        gn += 1
        if gn >= len(grants):
            break

print('Checking {} strings against {} COI names'.format(len(docstrings),len(COIs)))

######################    Now look for COI matches
nlines = 0
nCOIs = 0
potentialCOIs=[]

for g in grants:
    if g.checkcoi():
        potentialCOIs.append(g)
    
    
print('Found {} potential conflicts'.format(len(potentialCOIs)))

#
#   Let's review all the potential COIs

pc2 = []
for i,c in enumerate(potentialCOIs):
    c.print()
    x = input('Is this really a COI? (y|N):')
    if  x=='y' or x=='Y':
        pc2.append(c)
        
fc = open('coi_report.txt','w')
print("     ===     COI Report     ===",file=fc)
print('',file=fc)
i=0
for c in pc2:
    i+=1
    print('COI {}: {}    PI: {}'.format(i,c.grantNo, c.PIName),file=fc)
    print('   conflicts: ',c.coiHits,file=fc)
fc.close()

    
            
