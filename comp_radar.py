# Libraries
import matplotlib.pyplot as plt
import matplotlib.dates as mpd
import numpy as np
from math import pi
import datetime as dt
from dateutil.parser import parse

# for use with PRT.py proposal review tool
#
#   to use, open PRT.py
#           click "Progress Graph" button
#           run this program.
#




#####################  "Radar" style radial status plot
# get data

f= open('rev_prog.csv','r')

fc = []
cc = []
id = []

for line in f:
    a,b,c = line.split(',')
    c = c.strip()
    b = b.strip()
    fc.append(float(b))
    cc.append(float(c))
    id.append(a)    

N = len(cc)
 
for i in range(N):
    print '{} {}'.format(fc[i],cc[i])
    
# We are going to plot the first line of the data frame.
# But we need to repeat the first value to close the circular graph:
#values=df.loc[0].drop('group').values.flatten().tolist()
#values += values[:1]
#values

fc.append(fc[0])
cc.append(cc[0])
 
# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]
 
# Initialize the spider plot
#fig = plt.figure(figsize=(8, 6)) 
fig,ax = plt.subplots(figsize=(15,15), subplot_kw=dict(polar=True))
#fig.figsize = (10,10)
ticks = []
for i in range(N):
    ticks.append('`{}'.format(id[i]))
                 
# Draw one axis per variable + add labels labels yet
plt.xticks(angles[:-1], ticks, color='blue', size=16)
 
## Draw ylabels
#ax.set_rlabel_position(0)
#plt.yticks([10,20,30], ["10","20","30"], color="grey", size=7)
plt.ylim(0,1.00)
 
# Plot data
ax.plot(angles, fc, linewidth=1, linestyle='solid')
ax.plot(angles, cc, linewidth=1, linestyle='solid')
 
# Fill area
ax.fill(angles, cc, 'b', alpha=0.1)
ax.fill(angles, fc, 'r', alpha=0.1)

plt.title( 'Completion: blue = characters, red = fields',size=24)


#####################  Plot progress over time

f= open('rev_work.csv','r')
dateTimeFormat = '%Y-%m-%d, %H:%M:%S'


day = []
time = []
chars = []
fields = []
char_pct = []
field_pct = []

a,b = f.readline().split(',')
duedate = parse(a+' '+b)

for line in f:
    a,b,c,d,e,f = line.split(',')
    day.append(parse(a+' '+b))
    chars.append(int(c))
    fields.append(int(d))
    char_pct.append(float(e))
    field_pct.append(float(f))
    
fig,ax = plt.subplots(figsize=(20,8))
#start_dt = day[0]
#end_dt = day[-1] 
end_dt = duedate
print('Plotting due date: ', end_dt.strftime(dateTimeFormat)) 
start_dt = duedate - dt.timedelta(days=30)
Nxticks = 5
time_inc = (end_dt-start_dt)/Nxticks
xticks = []
#for i in range(Nxticks)
    #xticks.append(str(time_inc*i))

#dts = mpd.drange(start_dt,end_dt,time_inc)
#dts = dts[:-1]
#np.append(dts, [end_dt+time_inc])
print('-----')
print day, chars
ax.xaxis.set_major_formatter(mpd.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mpd.DayLocator(interval=1))
ax.set_ylabel('Total Characters Entered',color='blue',fontsize=14)
ax.plot(day, chars)
ax.set_ylim(0,30000)

ax2=ax.twinx()
ax2.plot(day,field_pct,color='red')
ax2.set_ylabel('Fraction of Fields Entered',color='red',fontsize=14) 
ax2.set_ylim(0,1.00)

fig.autofmt_xdate()
#plt.ylim(0,30000)
plt.xlim(start_dt,end_dt)
plt.title('Character count vs time')


plt.show()
