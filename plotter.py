import scipy as sp
import random
import matplotlib
matplotlib.use('WXAgg')
#matplotlib.rcParams.update(matplotlib.rcParamsDefault)
import matplotlib.pyplot as pp

#The plots are currently implemented through pyplot. 
#Need to create an individual figure instance for each plot and append each to a single plot


class Plotter():
    '''All the plotting needs are satisfied by this class '''
    '''Usage : Plotter(array_object) ;     where, array object is from Import() class'''

    #Need to find a way to choose a different marker color, type, linetype, etc. for each this class is invoked
    # An idea is to continually update a list depending on the length of the listbox from GUI
    # Plotting is very slow. Find a way to minimize the time
    def __init__(self,xyArray):
        self.xarray = xyArray[0]
        self.yarray = xyArray[1]

        self.title = ''
        self.xlabel = 'x'
        self.ylabel = 'y'
        self.xlim = sp.array([min(self.xarray),max(self.xarray)])
        self.ylim = sp.array([min(self.yarray),max(self.yarray)])

        self.markersize = 5
        self.mew = 0.01
        self.markerstyles = ['>','o','D','^','8','s','<','h','d','*','v','+','H',',']*5
        self.fillstyles = ['full','left','right','left','bottom','top','none']
        self.colors = ['b','g','r','c','m','y','k']
        for i in range(50):
            self.colors.append(self.random_color())

        self.set_marker = random.choice(self.markerstyles)
        self.color = self.random_color()
        self.linewidth = 1
        self.set_fill = random.choice(self.fillstyles)     # Change this
        self.label =  ''     #Need to change this to something else


        #Need to add more

    def random_color(self):
        return ''.join([random.choice('0123456789ABCDEF') for i in range(6)])

    def plot(self):
        pp.ion()
        pp.xlabel(self.xlabel)
        pp.ylabel(self.ylabel)
        pp.plot(self.xarray,self.yarray,label=self.label,markersize=self.markersize,\
                marker=self.set_marker,fillstyle=self.set_fill,mew=self.mew)
        pp.legend()
        pp.show()


