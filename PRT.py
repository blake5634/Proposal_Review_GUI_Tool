#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Proposal Review Tool
 
Blake Hannaford May 2016

Variable Naming: 

    menu_selections:    selitm_xxxxxxxxxxx
    menu_index:         selind_xxxxxxxxxxx
    object_selections:  selobj_xxxxxxxxxxx


Updates:   October 2017:
    bug fixes.
    completeness score
"""

#from Tkinter import Tk, Text, TOP, BOTH, X, N, LEFT
#from ttk import Frame, Label, Entry

import Tkinter as Tk
import ttk as ttk
import tkFont
import datetime as dt


import os.path
import sys              # for command line args and running pdf viewer

from NIHtool import *
import subprocess

#PDF_VIEWER_APP = 'acroread'
PDF_VIEWER_APP = 'okular'

#proj_name = "Project01"
icon_dir = "icons/"

#define some colors
col_light = 'SteelBlue1'
col_dark  = 'SteelBlue2'
col_txtbg  = 'honeydew'

prog_definition_string = 'Progress: :'
prog_def_width = len(prog_definition_string) + 2


NIH_Prop_type_Codes = {'1R41' : 'STTR Ph 1',
            '1R43' : 'SBIR Ph 2',
            '2R42' : 'STTR Ph 2 or Ph 2 Comp. Renewal',
            '2R44' : 'SBIR Ph 2 or Ph 2 Comp. Renewal',
            '1R42' : 'STTR Fast Track Ph 1&2',
            '1R44' : 'SBIR Fast Track Ph 1&2'
            }

class ReviewTool(ttk.Frame):
    def __init__(self, parent, proj_name):
        #### read in the proposal info file
        try:
            apps = file(proj_name+"/apps.csv","r")
        except IOError as e:
            print 'Could not open apps.csv'
            quit()
        self.project = proj_name
        self.reviews=[]
        self.widgets_valid = False
        self.num_reviews=0
        self.prioritm_proposal = "--not yet defined--"
        self.prioritm_criterion = "--not yet defined--"
        self.prioritm_field = "--not yet defined--"
        self.priorobj_criterion = criterion()
        self.priorobj_criterion.fields['general comments'] = '--not yet entered--'
        self.priorobj_criterion.fields['weaknesses'] = '--not yet entered--'
        self.priorobj_criterion.fields['strengths'] = '--not yet entered--'
        due_date_str = apps.readline().split(':')[1].rstrip().strip()
        print(' Reviews Due Date: '+due_date_str)
        print('------')
        for line in apps:          # TODO: use csv module for ignoring , in quoted strings.
            keys = line.split(',')
            tmpIDstring = keys[0].strip()
            ##    look for a pickle file 
            #     and if its present load it into new review obect 
            r = restore_review(proj_name, tmpIDstring)  # check for pickle or start a new review
            self.num_reviews += 1   
            r.PI = keys[2].strip()
            r.Title = keys[1].strip()
            r.Institution = keys[3].strip()
            #print 'Opening: ', r.PI, r.Title, r.Institution
            self.reviews.append(r)
            self.rev_menu_items = []
            for r in self.reviews:
                #self.rev_ids.append(r.ID)
                #self.rev_menu_items.append(r.ID + ' | ' + r.Title)
                self.rev_menu_items.append(r.ID)
                # make the id prop_index
                #self.prop_index[r.ID] = r
        
        
        ttk.Frame.__init__(self, parent)         
        self.parent = parent 
        
        # create a ttk style
        s1 = ttk.Style()
        s1.configure('PRT.TFrame', background=col_dark)
        s2 = ttk.Style()
        s2.configure('PRT.TButton', background=col_light)
        s3 = ttk.Style()
        s3.configure('PRT.TLabel', background=col_txtbg) 
        s4 = ttk.Style()
        s4.configure('PRT.TText',  background=col_txtbg)
        s5 = ttk.Style()
        s5.configure('PRT.TMenubutton',  background=col_light, width=20)
        s6 = ttk.Style()
        s6.configure('NIH2.TMenubutton',  background=col_light, width=12)
        
        self.parent.title("Proposal Review Tool: " + proj_name+'    due: '+due_date_str)      #   PRT!
        self.pack(fill=Tk.BOTH,expand=True)

        # Build the frame hierarchy  
        #self.window_frame = ttk.Frame(self)
        self.top_frame = ttk.Frame(self,style='PRT.TFrame')
        self.top_frame.pack(fill=Tk.X)
        self.prop_info_frame = ttk.Frame(self,style='PRT.TFrame')
        self.prop_info_frame.pack(fill=Tk.X)
        self.criterion_frame = ttk.Frame(self,style='PRT.TFrame')
        self.criterion_frame.pack(fill=Tk.X)
        self.text_frame = ttk.Frame(self,style='PRT.TFrame')
        self.text_frame.pack(fill=Tk.X)        
        self.button_bar_frame = ttk.Frame(self,style='PRT.TFrame')
        self.button_bar_frame.pack(fill=Tk.X) 
 
        # start populating the frames       
        ###    top frame
        #                                                                                 Arrows
        self.updn_arrow_frame = ttk.Frame(self.top_frame,style='PRT.TFrame')
        self.updn_arrow_frame.pack(side=Tk.LEFT, padx=5, expand=False)       
        self.pic_up = Tk.PhotoImage(file=icon_dir+"up.png")
        self.but_up = ttk.Button(self.updn_arrow_frame,image=self.pic_up, command  = lambda x='up': self.click(x), style='PRT.TButton')
        self.but_up.pack(side=Tk.TOP)
        self.pic_dn = Tk.PhotoImage(file=icon_dir+"down.png")
        self.but_dn = ttk.Button(self.updn_arrow_frame,image=self.pic_dn,command  = lambda x='dn': self.click(x), style='PRT.TButton')
        self.but_dn.pack(side=Tk.BOTTOM)
        self.top_selector_frame = ttk.Frame(self.top_frame,style='PRT.TFrame')
        self.top_selector_frame.pack(fill=Tk.X, padx=5, expand=True)
        self.selitm_proposal = Tk.StringVar(self.top_selector_frame)           #           Select Proposal
        self.menu_proposal= ttk.OptionMenu(self.top_selector_frame, self.selitm_proposal, "", *self.rev_menu_items, command  = lambda x='WidgetName': self.click(x), style='PRT.TMenubutton')
        self.menu_proposal['menu'].invoke(0)
        self.selobj_proposal = self.reviews[0]
        self.menu_proposal.pack(side=Tk.LEFT)
        
        #self.id_string = Tk.StringVar(self.prop_info_frame)
        #self.prop_display = ttk.Label(self.prop_info_frame,text=self.id_string, width=35)
        #self.id_string.s  
        #self.id_string = Tk.StringVar(self.prop_info_frame)
        self.prop_display = ttk.Label(self.prop_info_frame,text="PI:           Institution: ", width=150, style='PRT.TLabel')
        #self.id_string.set("PI:           Institution: ")
        self.prop_display.pack(side=Tk.LEFT,expand=False)

        #   Save buttons
                 
        self.but_output_scores = ttk.Button(self.top_selector_frame, text="Make scores.csv", width=13, command=lambda x='csv_report': self.click(x), style='PRT.TButton')
        self.but_output_scores.pack(side=Tk.RIGHT)        
        
        self.but_output_file   = ttk.Button(self.top_selector_frame, text="Make rev.txt",    width=13, command=lambda x=False : self.selobj_proposal.human_output(x), style='PRT.TButton')
        self.but_output_file.pack(side=Tk.RIGHT)
        
        self.but_output_progress_data  = ttk.Button(self.top_selector_frame, text="Progress Graph",    width=13, command=lambda x=False : self.prog_data_graph(), style='PRT.TButton')
        self.but_output_progress_data.pack(side=Tk.RIGHT)
        
        self.but_open_pdf      = ttk.Button(self.top_selector_frame, text="View",            width=13, command=lambda x='view': self.click(x), style='PRT.TButton')
        self.but_open_pdf.pack(side=Tk.RIGHT,padx=10)
        
   
        ### prop_info_frame
        
        ### criterion_frame
        self.lr_arrow_frame = ttk.Frame(self.criterion_frame,style='PRT.TFrame')
        self.lr_arrow_frame.pack(side=Tk.LEFT,padx=5,pady=5)
        self.pic_left = Tk.PhotoImage(file=icon_dir+"left.png")
        self.but_left = ttk.Button(self.lr_arrow_frame,image=self.pic_left,command=lambda x='left': self.click(x), style='PRT.TButton')
        self.but_left.pack(side=Tk.LEFT,padx=5,pady=5)
        self.pic_right = Tk.PhotoImage(file=icon_dir+"right.png")
        self.but_right = ttk.Button(self.lr_arrow_frame,image=self.pic_right,command=lambda x='right': self.click(x), style='PRT.TButton')
        self.but_right.pack(side=Tk.LEFT,padx=5,pady=5)
        
        #                                                                                               Criteria Optionmenu
        self.selitm_criterion = Tk.StringVar(self.criterion_frame)
        self.crit_menu_items = []
        if(len(self.selobj_proposal.criteria) < 1):
            print 'This proposal has no criteria:'
            print self.selobj_proposal.name
            quit()
        for c in self.selobj_proposal.criteria:
            self.crit_menu_items.append(c.name)
            self.menu_criterion = ttk.OptionMenu(self.criterion_frame,self.selitm_criterion,'',*self.crit_menu_items,command  = lambda x='WidgetName': self.click(x), style='PRT.TMenubutton')
        self.menu_criterion.pack(side=Tk.LEFT,expand=False,padx=5,pady=5)
        self.menu_criterion['menu'].invoke(0)
        self.selobj_criterion = self.selobj_proposal.criteria[0]
        #  button for Criterion instructions (if any)
        self.but_crit_help = ttk.Button(self.criterion_frame, text='?', width=2,command=lambda : self.help_popup(),style='PRT.TButton')
        self.but_crit_help.pack(side=Tk.LEFT, padx = 5)
        #  canned text buttons
        
        # enter 'N/A' into the field
        self.but_NA = ttk.Button(self.criterion_frame, text="N/A", command=lambda x='N/A': self.click(x), style='PRT.TButton')
        self.but_NA.pack(side=Tk.RIGHT,padx=5,pady=5)        

        # enter 'None' into the field
        self.but_none  = ttk.Button(self.criterion_frame, text="None",  command=lambda x='None':self.click(x),  style='PRT.TButton')
        self.but_none.pack(side=Tk.RIGHT,padx=5,pady=5)
        
        # copy this text in window to same field in all proposals
        self.but_clone = ttk.Button(self.criterion_frame, text="Clone", command=lambda x='Clone':self.click(x), style='PRT.TButton')
        self.but_clone.pack(side=Tk.RIGHT,padx=5,pady=5)
        
        #                                                                                               Field Optionmenu
        self.selitm_field = Tk.StringVar(self.criterion_frame)
        self.field_menu_items = []
        for field, text in self.selobj_criterion.fields.iteritems():
            self.field_menu_items.append(field)
        self.menu_fields = ttk.OptionMenu(self.criterion_frame, self.selitm_field, '', *self.field_menu_items, command=lambda x='field_menu': self.click(x), style='NIH2.TMenubutton')
        self.menu_fields.pack(side=Tk.LEFT,expand=False,padx=5)
        self.menu_fields['menu'].invoke(0)
        #self.selobj_field = self.selobj_criterion.fields[self.selitm_field.get()]
                
        ########################################                     SCORE
        self.score_val = Tk.StringVar(self)
        self.score_val.set("0")
        self.score_widget = Tk.Spinbox(self.criterion_frame, from_=1, to=9,increment=1,state=Tk.DISABLED, width=5,textvariable = self.score_val, bg=col_txtbg)
        self.score_widget.pack(side=Tk.LEFT, padx=5,pady=5)
        
        ####                                                                                                  text_frame
        self.text_widget = Tk.Text(self.text_frame, background=col_txtbg)
        self.text_widget.pack(fill=Tk.BOTH,expand=True)
        
        ####                                                                                                button_bar_frame        
        but_save = ttk.Button(self.button_bar_frame, text="Save", width = 8, command = self.save_proposal, style='PRT.TButton')
        but_save.pack(side=Tk.LEFT, anchor=Tk.N, padx=5,pady=5)
        
        but_quit = ttk.Button(self.button_bar_frame, text="Quit", width = 8, command = self.quit_popup, style='PRT.TButton')
        but_quit.pack(side=Tk.RIGHT, anchor=Tk.N, padx=5,pady=5)
        
        # progress indicator labels
        self.prog_value = ttk.Label(self.button_bar_frame, text='0.0', width = 35,background=col_txtbg)
        self.prog_value.pack(side=Tk.RIGHT, anchor=Tk.N, padx=5,pady=5)
        self.widgets_valid = True   # enable the widgets post-setup
        self.prog_label = ttk.Label(self.button_bar_frame, text=prog_definition_string, width = prog_def_width, background=col_dark)
        self.prog_label.pack(side=Tk.RIGHT, anchor=Tk.N, padx=5,pady=5)

        
    def save_proposal(self):
      self.selobj_proposal.save()
        
    def help_popup(self):
        hpp = Tk.Tk()
        hpp.wm_title(self.selobj_criterion.name + ' Instructions')
        help = Tk.Text(hpp, bg=col_txtbg)
        help.insert(Tk.INSERT, self.selobj_criterion.instructions)
        help.pack(side=Tk.TOP,fill=Tk.X, pady=10)
        close = ttk.Button(hpp, text='Continue', command=hpp.destroy)
        close.pack()
        hpp.mainloop()
        
    def quit_popup(self):
        hpp = Tk.Tk()
        hpp.wm_title( 'Quit Proposal Review: Are you Sure?')
        help = Tk.Text(hpp, bg=col_txtbg)
        help.insert(Tk.INSERT, '''
                    
    Are you sure you want to quit without saving? 
    
    (doesn't work yet -- use the X in upper right corner to quit)
    ''')
        help.pack(side=Tk.TOP,fill=Tk.X, pady=10)
        close = ttk.Button(hpp, text='Cancel Quit', command=hpp.destroy)
        close.pack()
        quitb = ttk.Button(hpp, text='Save All & Quit', command = self.save_all_quit())
        quitb.pack()
        hpp.mainloop()
        
    def save_all_quit(self):
        for r in self.reviews:
            r.save()
        self.parent.destroy
        
    def click(self,*arg):
      #print "Click",
      if(self.widgets_valid):
          #print "!!!!!!"
          event = arg[0]
          #print "    click from ", arg[0]          
     
          if (event == 'view'):
              filename = self.project + '/' + self.selobj_proposal.ID + '.pdf'
              #print "= = = = = = =   Popen = = = = ="
              subprocess.Popen([PDF_VIEWER_APP, filename])
              #subprocess.Popen(['okular', filename])
              
          if (event == 'csv_report'):
              print 'got here'
              self.write_csv_score_file()
              
              
          if (event == 'up' or event == 'dn'):
              
            #print ''
            #print ''
            #print ' DOWN '
            #print ''
            n_proposals = len(self.rev_menu_items)
            s = self.selitm_proposal.get()
            s = s.strip()
            #s = s.split('|')[0].strip()
            index = 0
            i=0
            for p_name in self.rev_menu_items:
                #tmpID = p_name.split('|')[0].strip()
                tmpID = p_name.strip()
                if(str(s) == str(tmpID)):
                    index = i
                    break
                i += 1                    
            if(event == 'up'):
                #print " Uparrow: index:", index
                if (index == 0):
                    index = n_proposals - 1
                else:
                    index -= 1                    
            if(event == 'dn'):
                if (index == n_proposals-1):
                    index = 0
                else:
                    index += 1
            
            # change the proposal selection
            self.menu_proposal['menu'].invoke(index)
       
          if(event == 'left' or event == 'right'):
              n_criteria = len(self.crit_menu_items)
              s = self.selitm_criterion.get()
              index = 0
              i = 0
              for c_name in self.crit_menu_items:
                  if(s == c_name):
                      index = i
                      break
                  i += 1                  
              if(event == 'left'):
                  if (index == 0):
                      index = n_criteria-1
                  else:
                      index -= 1
              if(event == 'right'):
                 if (index == n_criteria-1):
                     index = 0 
                 else:
                     index += 1
              self.menu_criterion['menu'].invoke(index)
                 
          if(event == 'None' or event == 'N/A' or event == 'Excellent'):
               self.text_widget.insert(Tk.INSERT, event)
               
          if(event == 'Clone'): #################################################### clone text into all proposals
               cur_text = self.text_widget.get('1.0','end-1c')
               cp =  self.selitm_proposal.get()
               cc =  self.selitm_criterion.get()
               cf = self.selitm_field.get()
               
               print 'Cloning: [{}] into [{}], [{}]'.format(cur_text,cc,cf)
              
               for r in self.reviews:
                  for c in r.criteria:
                      print 'checking [{}] criterion'.format(c.name)
                      if c.name == cc:
                          print 'crit match'
                          for f in c.fields.keys():
                              if f == cf:
                                  print '             copying ', cur_text
                                  c.fields[f] = cur_text

                 
          if(False):  # good for debugging
                print "Selected "
                print "       Proposal: ", self.selitm_proposal.get()
                print "      Criterion: ", self.selitm_criterion.get()
                print "          Field: ", self.selitm_field.get()
                print "Prior Values "
                print "       Proposal: ", self.prioritm_proposal
                print "      Criterion: ", self.prioritm_criterion
                print "          Field: ", self.prioritm_field

          prop_change  = (self.selitm_proposal.get()  != self.prioritm_proposal)
          crit_change  = (self.selitm_criterion.get() != self.prioritm_criterion)
          field_change = (self.selitm_field.get()     != self.prioritm_field)
      
         # dependencies         
         #    (do things BEFORE channging to new prop/crit/field)
          if(prop_change):
              self.update_proposal()
              self.update_criterion()
              self.update_field_list()
              self.update_field()
          elif(crit_change):
              self.update_criterion()
              self.update_field_list()
              self.update_field()
          elif(field_change):
              self.update_field()
                
          #  Now register the change
          # store new values for prior selections

          self.prioritm_criterion = self.selitm_criterion.get()
          self.priorobj_criterion = self.selobj_criterion
          self.prioritm_proposal  = self.selitm_proposal.get()
          self.prioritm_field     = self.selitm_field.get()          
          
          #    (do things AFTER channging to new prop/crit/field)

          self.update_progress()  # display progress of current propsoal
          
          self.enable = 1
          
          
    def prog_data_graph(self):
        self.selobj_proposal.check_comp()  # update completeness on currently active propo.
        # find completion status of each review
        fieldcomps = []
        chars = []
        ids = []
        char_target = 2500   # goal for how many chars in a review
        for r in self.reviews:
            r.check_comp() # check completeness of each review
            fieldcomps.append(r.completed_fields)
            chars.append(r.char_count)
            ids.append(r.ID)
        total_todo = r.nfields  # all same so last one good.
        total_chars = sum(chars)
        total_fields = sum(fieldcomps)
        total_fields_needed = total_todo*len(self.reviews)
        pct_chars = total_chars/float(char_target*len(self.reviews))
        pct_fields = total_fields/float(total_fields_needed)
        # compute percentages
        for i,fc in enumerate(fieldcomps):
            fieldcomps[i] = float(fc)/float(total_todo)
        for i,cc in enumerate(chars):
            chars[i]  = float(cc)/float(char_target)
        for i, id in enumerate(ids):
            idcode = id.split('-')[0]
            idcode = idcode[-4:]
            ids[i] = idcode
        # write a csv for graphing
        fname = "rev_prog.csv"
        f = open(fname, 'w')
        for i,fc in enumerate(fieldcomps):
            print>>f, '{}, {:4.2f}, {:4.2f}'.format(ids[i],fc,chars[i])
        f.close
        # append to a csv for work-over-time graph
        fname = "rev_work.csv"
        dateTimeFormat = '%Y-%m-%d, %H:%M:%S'
        date = str(dt.datetime.now().strftime(dateTimeFormat))
        try:
            f = open(fname,'r') # if file is empty, due date becomes first line
            due_date_fmt = parse(due_date_str).strftime(dateTimeFormat)
            print>>f, due_date_fmt
            # print first row of data
            print>>f, '{}, {}, {}, {:4.2f}, {:4.2f}'.format(date,total_chars,total_fields,pct_chars,pct_fields)
            f.close
        except: 
            f = open(fname, 'a')
            # add today's row of data 
            print>>f, '{}, {}, {}, {:4.2f}, {:4.2f}'.format(date,total_chars,total_fields,pct_chars,pct_fields)
            f.close
        
            
        
        
    def update_progress(self):       ###  OOooops!!   This has to be referenced to the proposal itself and updated on current object.
        #print '\n\n UDPDATE PROGRESS '
        self.selobj_proposal.check_comp()  # update completeness
        #prog = self.selobj_proposal.completeness
        char_cnt = self.selobj_proposal.char_count
        #progvalstring =  '{:5.2f}'.format(float(char_cnt)) # sub character count - easier toveriry
        #print 'Progress: ', progvalstring, '\n'
        #self.prog_value.config(text=progvalstring)
        #self.prog_value['text'] = progvalstring
        total_comp = 0
        total_todo = 0
        # new June 2020 -  overall progress on the Package
        for r in self.reviews:
            r.check_comp() # check completeness of each review
            total_comp += r.completed_fields
            total_todo += r.nfields
        progvalstring = '[all: {:3}/{:3} fields], [this prop: {:5} chars]'.format(total_comp, total_todo, char_cnt)
        self.prog_value['text'] = progvalstring
        
    # decode prefix application type  (e.g. NIH: 1R01)
    def id_to_app_type(self,prop): 
        code = prop.ID[0:4]
        if code in NIH_Prop_type_Codes.keys():
            prtype = NIH_Prop_type_Codes[code]
        else:
            prtype = 'Type: '+code
        return prtype
    
        
    def update_proposal(self):
          ##print "Updating Proposal"
          for r in self.reviews:
              tmp = self.selitm_proposal.get()
              #tmp = tmp.split('|')[0]
              tmp = tmp.strip()
              if tmp == r.ID:
                self.selobj_proposal = r
                
          
          string = 'PI: {:20.20} Inst: {:20.20}  Title: {:50.50}'.format(self.selobj_proposal.PI, self.selobj_proposal.Institution, self.selobj_proposal.Title)
          string += '\n' + self.id_to_app_type(self.selobj_proposal)
          self.prop_display['text'] = string 
 
          
    def update_criterion(self):
          #print "Updating Criterion"
          # save the spinbox score
          if(self.selobj_criterion.scored):
               self.selobj_criterion.score = self.score_val.get()
          #  
          self.priorobj_criterion = self.selobj_criterion
          for c in self.selobj_proposal.criteria:
              if (c.name == self.selitm_criterion.get()):
                 self.selobj_criterion = c
          #update the score spinbox to current value for this crit
          if(self.selobj_criterion.scored):
              self.score_val.set(self.selobj_criterion.score)
              
          # Enable score spinbox if this crit is scored
          if(self.selobj_criterion.scored == 1):
               self.score_widget.configure(state=Tk.NORMAL)
          else:
               self.score_widget.configure(state=Tk.DISABLED)
          ##  clear field menu
          ##   add in new fields for current criterion
          
    def update_field_list(self):
          #print "Updating Field List"
          ## Update the items in the field OptionMenu acccording to current criterion
          field_list = []  # needs blank first item??
          self.menu_fields['menu'].delete(0,Tk.END)   # clear the menu
          fields = self.selobj_criterion.fields    # get new fields
          has_strengths = False
          for f,text in fields.iteritems():
              field_list.append(f)
              if (f == 'strengths'):
                  has_strengths=True
              self.menu_fields['menu'].add_command(label=f,command=lambda x=f:self.click_fields(x))
          if(has_strengths):
              self.selitm_field.set('strengths')
          else:
              if(len(field_list)>0):
                  self.selitm_field.set(field_list[0])
          
    def update_field(self):
          ####  update text in field text box according to current prop/crit_change
          #print 'Update Field -------'
          #print self.selobj_criterion.name, " / ", self.selitm_field.get()
          #print self.selobj_criterion.fields 
        
          if(self.text_widget.edit_modified()):
              text = self.text_widget.get('1.0',Tk.END)
              text = text.strip()
              if(self.prioritm_field != '--not yet defined--'):
                    ##print "***************************  saving: ", self.selitm_field.get(), ' <== ', text
                    #self.priorobj_criterion.fields[self.selitm_field.get()] = text
                    self.priorobj_criterion.fields[self.prioritm_field] = text
                    self.selobj_proposal.save()  # save this review to disk

          #print '  current proposal: ', self.selobj_proposal.ID, self.selobj_proposal.Title
          #print '  current criterion: ', self.selobj_criterion.name
          #print "  current criterion's fields:"
          #print self.selobj_criterion.fields
          #print '  current field: ', self.selitm_field.get()
          
          self.text_widget.delete('0.0',Tk.END)
          if(False):
              print "criterion: ", self.selobj_criterion.name
              print "field:     ", self.selitm_field.get()
              print "fields:    ", self.selobj_criterion.fields
          try:
              text = self.selobj_criterion.fields[self.selitm_field.get()]
          except:
              text =''
          #print "---> About to insert text: ", text, ' ==> text_widget window'
          self.text_widget.insert(0.0,text.strip())
          self.text_widget.edit_modified(False)        

          #print "New text: ", self.selobj_criterion.fields['general comments']
          self.prioritm_field = self.selitm_field.get() # store the "prior" field

    def click_fields(self,*arg):
        #print 'Click fields'
        #print self.priorobj_criterion.fields
        self.selitm_field.set(arg[0])  # don't know why menu_fields isn't doing this(!)        
        ## store away the current text field into the prior field
 
        self.click('fieldchange')
        
    def write_csv_score_file(self):    
        #filename = self.project + '/' + self.selobj_proposal.ID + '.pdf'
         fname = self.project + '/' + self.project + '_scores.csv'
         print 'Generating scores csv file: ', fname
         f = open(fname, 'w')
         string = 'Proposal, PI '
         for c in self.selobj_proposal.criteria:
             if (c.scored):
                string += ', ' + c.name
         string += ', Character Count'
         f.write(string+'\n')  # write the column headers
         for r in self.reviews:
             # write the scores for each review
             f.write(r.score_csv_string() + str(r.char_count) +'\n')
         f.close()
             
             
def main():
  
   
    #print 'Number of arguments:', len(sys.argv), 'arguments.'
    #print 'Argument List:', str(sys.argv)
    
    if(len(sys.argv) != 2):
        print "Usage:  NIHtool  <projectfoldername>"
        print "  please add a project folder name to the command line."
        quit()
    else:
        proj_name = str(sys.argv[1])
        # delete trailing '\' if present
        proj_name = re.sub(r'\/$','',  proj_name)
    print "opening Project: ",proj_name
    
    root = Tk.Tk()
    #root.geometry("900x625+300+300")    # 2015 era laptop
    root.geometry("1650x1050+300+300")   # 2020 era hi-res laptop
    app = ReviewTool(root, proj_name)
    
    root.mainloop()  


if __name__ == '__main__':
    main()
    
