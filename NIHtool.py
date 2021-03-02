#!/usr/bin/python

import re
import os
import pickle
#import g2NIH

MIN_RESPONSE = 25  # min # of characters for a valid response (except 'N/A' etc)
class review:
  def __init__(self,proj_name):  # init review from template text file
    self.project = proj_name
    self.ID = ""
    self.PI = ""
    self.Institution = ""
    self.Title = ""
    self.criteria = []
    self.total = 0
    self.nscores = 0
    self.overall_score = 0
    self.completed_fields = 0  # number of completed fields ('Approach/strengths' e.g.)
    self.nfields = 0       # total number of fields to be done
    self.most_complete = ''
    self.least_complete = ''
    self.char_count = 0   # total character count
        
    ##########
    #
    #    Check to see if there are any .pdfs breaks if none!)
    #
    #
    f1 = os.popen('ls -1 ' + self.project+'/*.pdf').read()
    if(len(str(f1)) == 0):
           print '\n\n\n'
           print 'There are no proposals (.pdf) in this project yet'
           print 'please add them, update apps.csv, and try again.'
           print '\n\n\n'
           quit()
    
    whitespace = r'^\s*\Z'
    thing_inside_brackets = r'<[^>]+>'
    cmd = re.compile(thing_inside_brackets)       # a thing inside <> brackets
    cmd2 = re.compile(r'[^><]+')       # stuff thats not <> 
    trailingtext = re.compile('>.*$') # stuff after <> 
    
    ############
    #  initialize from template file
    template_file_name = self.project + "/rev_template.txt"
    template = open(template_file_name,"r")
    print '-------'
    print 'Opened: ',template_file_name
    print '-------'


    mode = "basic"

    lno = 0
    for line in template:
      if (re.match(whitespace,line)):  # skip whitespace
          continue
      lno += 1
      # analyze the line and parse it
      #print "[" + line + "]"
      hascommand = cmd.search(line)   # does line have an initial <command>?
      if(hascommand):
        #print "[" + line + "]"
        command = hascommand.group()         # get the command
        keys = cmd2.findall(command)   # find 1 or more commands   
        if (mode == "basic" and hascommand):
          #print keys[0]
          if (keys[0] == "CRITERION"):
            mode = "crit"
            #rev_template.criteria.append(
            items = cmd.findall(line)
            #print "        *******************  Criterion name: ", items[1]
            t = criterion()
            t.name = items[1][1:-1] # omit <> chars
        if(mode == "crit"):   #  accumulate <strengths> <weaknesses> <instructions> <score> etc.
            foundsomething = False
            #if (keys[0] == "CRITERION"):
                #print ' \n\n\nCheck format of rev_template.txt'
                #print '         line ', lno
                #print line
                #quit()
            DEB = 0
            if(keys[0] == "score"):
              foundsomething = True
              if(DEB):
                  print "        *******************  this criteria requires a score"
              t.scored = 1
              t.score  = 4  # default score
            if(keys[0] == "general comments"):
              foundsomething = True
              if(DEB):
                  print "        *******************  this criteria requires general comments"
              t.fields["general comments"]  = ""
            if(keys[0] == "comments"):
              foundsomething = True
              if(DEB):
                  print "        *******************  this criteria requires (just plain) comments"
              t.fields["general comments"]  = ""  # combine two types of comments
            if(keys[0] == "strengths"):
              foundsomething = True
              if(DEB):
                  print "        *******************  this criteria requires strengths"
              t.fields["strengths"]  = ""
            if(keys[0] == "weaknesses"):
              foundsomething = True
              if(DEB):
                  print "        *******************  this criteria requires weaknesses"
              t.fields["weaknesses"]= ""
            if(keys[0] == "instructions"):  # instructions can be multi-line until next comand
              foundsomething = True
              if(DEB):
                  print "        *******************  this criteria has instructions"
              hascommand = 0
              mode = "instr"
              tmpstr = trailingtext.search(line).group()[1:]  
              #print "first part of instructions: ", tmpstr
            if(keys[0] == "end"):              
              foundsomething = True
              self.criteria.append(t)
              mode = "basic"
            #if(not foundsomething):
                #print '  Not finding tokens in rev_template.txt'
                #print '        line ', lno
                #quit()
      if(mode == "instr"):   # accumulate instruction lines
          #print "Instruction Mode:", line
          if(hascommand):
              t.instructions = tmpstr # we're done with instructions
              mode = "crit"
              #
              #  TODO: Note it seems this code has a bug where a criterion right after 
              #        instructions is dropped. 
          else:
              tmpstr += line  # accumulate instructions
     
    template.close()
    
  # check completed_fields of this review
  def check_comp(self):
    self.completed_fields = 0  #  re-initialize these
    self.nfields = 0
    self.char_count = 0   # total character count
    min_comp = {}
    min_comp['val'] = 9.9
    min_comp['crit'] = 'undefined'
    
    for c in self.criteria:
        c.comp_check()
        #print '---- checking ',c.name
        self.nfields += c.n_fields
        # review thoroughness = min_comp(criteria completeness)
        if(c.thoroughness < min_comp['val']):
            min_comp['val'] = c.thoroughness 
            min_comp['crit'] = c.name
        self.char_count += c.char_count
        self.completed_fields += c.n_fields-c.n_empty  # num of completed fields
    self.least_complete = min_comp
        
  def get_score(self):
      if (self.nscores > 0):
          self.score = self.total / self.nscores
      else:
          self.score = 0
          
  def save(self):
       if (self.ID == ""):
           print "Cannot save review since no name is defined - quitting"
           quit()
       fname = self.project + '/' + self.ID + ".pickle"
       #print 'Saving: ', fname
       #x = raw_input('CR to cont')
       try:
           pf = open(fname, 'wd')
       except IOError as e:
           print 'review.save(), Could not open pickle file: ,',fname
           quit()
       pickle.dump(self, pf)
       pf.close()
       
  # generate a human readable / editable review     
  def human_output(self, instmode):
    # instmode: bool   Include the instructions, criterion and score or not
    str = self.ID + "\n"
    str += "PI:     " + self.PI  + "\n"
    str += "Title:  " + self.Title + "\n\n"
    for c in self.criteria:
        str += '\n'+c.name.upper()+'\n'
        if(instmode):
            if c.scored:
                tmp = "\n{:20}     {}\n".format(c.name, c.score)
                self.total += int(c.score)
                self.nscores += 1
            else:
                tmp = "\n{:20}       \n".format(c.name)
            str +=  tmp 
        if(instmode):
            str += c.instructions + "\n"
        for f in c.fields:
            str += f + ":\n" + c.fields[f] +"\n\n"
    fname = self.project + "/" + self.ID + "_review.txt"
    print "Saving review to ", fname
    with open(fname,'w') as f:
        stUC = str.encode('utf-8')
        f.write(stUC)
        f.close()
        
  def score_csv_string(self):
      st = self.ID + ", "
      st += self.PI  + ", "
      
      for c in self.criteria:
          if (c.scored):
              st += str(c.score) + ', '

      return st
         
def restore_review(project, ID):
    #print 'Restoring: ', project, ID
    fname = project+"/"+ID + ".pickle"
    
    try: 
        with open(fname, 'rd') as pf:
            rev = pickle.load(pf)
            # below is for updating from an old pickle
            for c in rev.criteria: # these are dynamic so can zero
                c.n_fields = 0         # number of fields
                c.n_empty = 0          # number of empty fields
            pf.close()
    except:
        #print "no pickle file - opening template, ", project, fname
        #print '      Creating: [', project, ID, ']'
        rev = review(project)
        rev.ID = ID
    #print 'Restoring ', rev.project
    rev.project = project  # reset project name if it is moved
    return rev
        
class criterion:
  def __init__(self):
    self.name = "-unnamed-"
    self.score = 0
    self.scored = 0 
    self.fields = {}   # name:value pairs: strengths, weakensses, etc
    self.instructions = "-no instructions-"
    self.bp = []        # biolerplate - list of freq used strings
    self.thoroughness = 0.0   # thoroughness score
    self.char_count = 0       # total character count for all fields of this crit.
    self.n_fields = 0         # number of fields
    self.n_empty = 0          # number of empty fields
    
  # compute the "completeness" of entries for this criterion
  def comp_check(self):
    self.char_count = 0
    min_len = 99999
    n = 0
    n_flds = len(self.fields.keys())
    n_empty = n_flds
    if n_flds > 0:
        for f in self.fields.keys():
            #print '++++ checking: ', f
            l = len(self.fields[f])
            EMPTY = True
            if l >= MIN_RESPONSE:
                EMPTY = False
            elif l > 0 and 'N/A' in self.fields[f] or 'None' in self.fields[f]:
                EMPTY = False
            if not EMPTY:
                n_empty -= 1
            if(l < min_len):
                min_len = l
            self.char_count += len(self.fields[f])
        self.n_fields = n_flds
        self.n_empty = n_empty
        self.thoroughness = (n_flds-n_empty)/n_flds
    else:
        print 'no fields for criterion: ',self.name # hack to fix the TODO after the fact
        print 'fixing: adding "general comments"'
        self.fields['general comments'] = ''
        self.n_fields = 1
        self.n_empty = 1
        self.thoroughness = 0.0


##################################################################################
#
#                  Main

if __name__ == '__main__':
  #main test: 
  print "\n\n    ------ \n\n"
  proj_name = "fill in this string"
  # open the list of applications
  apps = file(proj_name+"/apps.csv","r")
  reviews = []

  for line in apps:
    keys = line.split(',')
    r = review()
    r.ID = keys[0].strip()
    r.PI = keys[2].strip()
    r.Title = keys[1].strip()
    reviews.append(r)
                    
  for r in reviews:
    print "Review of:"
    print "Title:        ", r.Title
    print "ID:           ", r.ID
    print "Principal inv:", r.PI

##### 

##########################  Main loop
    
  while 1:
            
    input_text = raw_input("Select a proposal, enter the first few letters of PI name\n 'h' for text output files, 'q' to quit: 's' to save: ")
        
    if(input_text == 'q'):
        quit()
    
    if(input_text == 'h'):
        for r in reviews:
            r.human_output(False)  # don't include instructions
            
    if(input_text == 's'):
        for r in reviews:
            print "Saving: "+r.ID
            r.save()
        break
    
    i = 0
    for r in reviews:
        #print "Looking for ", input_text, " in ["+r.PI+"] giving", r.PI.find(input_text)
        if(r.PI.find(input_text) >= 0):
            selection = i
            break
        else:
            i += 1

    if(i == len(reviews)):
        print "PI name not found"
        break

    r = reviews[i]
    
    print "Selection:"
    print "Title:        ", r.Title
    print "ID:           ", r.ID
    print "Principal inv:", r.PI
        
    cri = raw_input("Enter first few letters of the Criterion: ")
    i = 0
    for c in r.criteria:
        if(c.name.find(cri) == 0):
            crit = i
            break
        else:
            i += 1
    
    if (i < len(r.criteria)):
        c = r.criteria[i]
        print c.name + ":"
        for f in c.fields:
            cri = raw_input("Enter your text for {}:".format(f))
            r.criteria[i].fields[f] = cri
        
    else:
        print "Criterion not found.  Select from:"
        for c in r.criteria: 
            print c.name,"|",
        print "\n\n"
    
  
  
