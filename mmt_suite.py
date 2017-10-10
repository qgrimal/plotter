#!/usr/bin/python

#Need to figure out if a single import will work for all modules

import scipy as sp
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import wx
import sys
import matplotlib
matplotlib.use('WXAgg')
#matplotlib.rcParams.update(matplotlib.rcParamsDefault)
import matplotlib.pyplot as pp
from collections import defaultdict
import random

#These are the classes needed for the GUI to function
from import_class import Import
from plotter import Plotter


#Define some global parameters here that should not change 
curDir = './'
dataFile_ext = '.txt'

menu_titles = ["Rename","Plot Label","Remove item (del)","Save array to file","Average arrays"]
menu_title_by_id = {}
for title in menu_titles:
    menu_title_by_id[ wx.NewId() ] = title

class TheGUI(wx.Frame):
    """ This is the GUI frontend for the program """

    def __init__(self,*args,**kwargs):
        super(TheGUI,self).__init__(size=(500,500),*args,**kwargs)
        self.currentDirectory = curDir
        self.SetTitle('Measurement Analysis and Plotting')

        #All the variables from a file are appended to the lists
        self.objects = defaultdict(list)
        self.currentList = []               #This list goes along with the listbox (needed for the listbox)
        self.xlabel = ''
        self.ylabel = ''
        self.xlims = []
        self.ylims = []
        self.title = ''
        self.xArray_expr = ''
        self.yArray_expr = ''

        #Some flags
        self.plotLegend_bool = True       #Display legend or not
        self.arrays_defined = False       #The x,y arrays are not initially defined. Define when first time file opened
        self.xylabelFlag = False

        #Shortcut key bindings
        bindings = [ (wx.ACCEL_CTRL,'o')]       #Add more if needed

    #Add the listbox
        self.panel = wx.Panel(self)
        self.box0 = wx.BoxSizer(wx.HORIZONTAL)
        self.box1 = wx.BoxSizer(wx.VERTICAL)
        self.box1a = wx.BoxSizer(wx.HORIZONTAL)
        self.box2 = wx.BoxSizer(wx.VERTICAL)
        self.listBox = wx.ListBox(self.panel,size=(300,-1),choices=self.currentList,style=wx.LB_MULTIPLE)
        self.normalize_button = wx.Button(self.panel,id=wx.ID_ANY,label='Normalize')
        self.unnormalize_button = wx.Button(self.panel,id=wx.ID_ANY,label='Un-Normalize')
        self.legendToggle_button = wx.Button(self.panel,id=wx.ID_ANY,label='Legend On/Off')
        self.plotWindow_button = wx.Button(self.panel,id=wx.ID_ANY,label='Plot Window Settings')
        self.rePlot_button = wx.Button(self.panel,id=wx.ID_ANY,label='Update Plot')
        self.exit_button = wx.Button(self.panel,id=wx.ID_ANY,label='Exit')
        self.box0.Add(self.listBox,0,wx.EXPAND)
        self.box0.Add(self.box1,1)
        self.box1.Add(self.box1a,2)
        self.box1a.Add(self.normalize_button,0)
        self.box1a.Add(self.unnormalize_button,1)
        self.box1.Add(self.legendToggle_button,1)
        self.box1.Add(self.plotWindow_button,2)
        self.box1.Add(self.rePlot_button,3)
        self.box1.Add(self.exit_button,9)
        self.panel.SetSizer(self.box0)
        self.panel.Fit()
        self.Centre()
        self.Show(True)

        #Display right click menu when right-clicked
        wx.EVT_LIST_ITEM_RIGHT_CLICK(self.listBox,-1,self.RightClick)
        self.list_item_clicked = None

        # Bindings for the window elements
        self.listBox.Bind(wx.EVT_LISTBOX_DCLICK,self.listBox_dblclk)
        self.listBox.Bind(wx.EVT_RIGHT_DOWN,self.RightClick)
        self.normalize_button.Bind(wx.EVT_BUTTON,self.normalize_click)
        self.unnormalize_button.Bind(wx.EVT_BUTTON,self.unnormalize_click)
        self.legendToggle_button.Bind(wx.EVT_BUTTON,self.legend_toggle)
        self.plotWindow_button.Bind(wx.EVT_BUTTON,self.plotWindow_settings)
        self.rePlot_button.Bind(wx.EVT_BUTTON,self.update_plot)
        self.exit_button.Bind(wx.EVT_BUTTON,self.onQuit)
        
    # The menubar
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        fileMenu = wx.Menu()
        menubar.Append(fileMenu,'&File')
        file_new = fileMenu.Append(wx.NewId(),'New Session (Ctrl+N)','Start new session')
        self.Bind(wx.EVT_MENU,self.NewSession,file_new)
        #open_session = wx.FileDialog(self,"Import",'','',"data files | *.txt",wx.FD_OPEN)
        file_import = fileMenu.Append(wx.FD_OPEN,'Import(Ctrl+O)','Import Datafiles')
        self.Bind(wx.EVT_MENU,self.OpenFile,file_import)
        file_close = fileMenu.Append(wx.ID_EXIT,'Quit','Quit Program')
        self.Bind(wx.EVT_MENU,self.onQuit,file_close)

        editMenu = wx.Menu()
        menubar.Append(editMenu,'&Operations')
        redefine_array = editMenu.Append(wx.ID_ANY,'Redefine Arrays','Redefine Arrays')
        self.Bind(wx.EVT_MENU,self.redefArrays,redefine_array)

        helpMenu = wx.Menu()
        menubar.Append(helpMenu,'&Help')
        help_help = helpMenu.Append(wx.ID_ANY,'Help','Help')  ##Add accordingly
        help_about = helpMenu.Append(wx.ID_ANY,'About','About the program')

        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,ord('o'),file_import.GetId())])
        self.SetAcceleratorTable(accel_tbl)
        self.Centre()
        self.Show(True)

    # plot window does not quit if window close (x) button pressed
    def onQuit(self,event):
        pp.ioff()
        pp.close()
        self.Close()

    def GetKeyPress(self,event):
        keycode = event.GetKeyCode()
        if key==wx.WXK_CONTROL:
            print 'pressed open'

    #Method for normalize button
    #Need a normalize flag so that any subsequent imports will auto import normalized arrays
    #Also need to add a method to check if array is already normalized (not important)
    def normalize_click(self,event):
        for item in self.objects:
            self.objects[item][0].normalize()
            self.objects[item][1] = self.objects[item][0].normalized
        pp.clf()
        self.plot_list()

    #This is to revert the normalized plot to non-normalized. Need to implement this after changing fileObjects to dictionary
    def unnormalize_click(self,event):
        for item in self.objects:
            self.objects[item][1] = self.objects[item][0].xyArray
        pp.clf()
        self.plot_list()


    def legend_toggle(self,event):
        self.plotLegend_bool = not self.plotLegend_bool
        if self.plotLegend_bool:
            pp.legend()
        else:
            pp.legend().remove()

    #Use this method to change plot window settings such as x,y labels, plotmarkers, tick params, etc
    def plotWindow_settings(self,event):
        dialog_window = PlotDialog(None,title='Change Plot Parameters')
        dialog_window.ShowModal()
        if dialog_window.xlabelFlag:
            self.xlabel = dialog_window.xlabel
            pp.xlabel(self.xlabel)
        if dialog_window.ylabelFlag:
            self.ylabel = dialog_window.ylabel
            pp.ylabel(self.ylabel)
        if dialog_window.titleFlag:
            self.title = dialog_window.title
            pp.title(self.title)
        if dialog_window.xlimFlag:
            self.xlims = dialog_window.xlims
            pp.xlim(self.xlims)
        if dialog_window.ylimFlag:
            self.ylims = dialog_window.ylims
            pp.ylim(self.ylims)
        self.xylabelFlag = True
        dialog_window.Destroy()

    def update_plot(self,event=None):
        #pp.close()
        pp.clf()
        self.plot_list()
        

    #Make separate instances for flags and add all in a single method. Call the method whenever pp.plot() is called
    #This will help ensure that the plots will remain the same 
    def plot_list(self):
        for each_file in self.objects:
            single_plot = Plotter(self.objects[each_file][1])
            single_plot.label = self.objects[each_file][2]
            single_plot.xlabel = self.xlabel
            single_plot.ylabel = self.ylabel

            #This will append the plot to the dictionary in case plot does not exist
            try:      
                self.objects[each_file][3] = single_plot
            except IndexError:
                self.objects[each_file].append(single_plot)  # Third item is for the plot

            single_plot.plot()
            
        if not self.plotLegend_bool:
            pp.legend().remove()


#This method redefines the array from previous definition and then replots the new one
#Need to use Try::except in case of index error
    def redefArrays(self,event):
        array_definition = ArrayDefineDialog(None,title='Define Arrays')
        array_definition.ShowModal()
        self.arrays_defined = True
        self.xArray_expr = array_definition.xArray_expr
        self.yArray_expr = array_definition.yArray_expr
        self.arrayObjects = []
        self.xyArrays = []
        self.xyArrays_orig = []
        self.listbox = []
        for item in self.objects:
            plot_label = self.objects[item][2] 
            #plot_label = item.split('/')[-1]

            self.objects.pop(item)      #first remove the key
            self.objects[item] = []   #Then add it again
            individual_file = Import(item)
            individual_file.xArray_expr = self.xArray_expr
            individual_file.yArray_expr = self.yArray_expr
            full_array = individual_file.import_arrays()
            xy_array = individual_file.import_xyArray()

            self.objects[item].append(individual_file)   #zeroth item of list is the xy array
            self.objects[item].append(xy_array)   #first item of list is the xy array
            self.objects[item].append(plot_label)       #second item of list is the label to be used
        self.update_plot()

        array_definition.Destroy()

    #This method opens files and plots them directly. 
    #All plotting parameters are defined in the Plotter() class as lists
    # and the position of file in the import determines these parameters
    def OpenFile(self,event):
        wildcard = "Data files (*.txt)|*.txt|" "CSV files (*.csv)|*.csv|" "All Files (*.*)|*.*"
        if not self.arrays_defined:
            array_definition = ArrayDefineDialog(None,title='Define Arrays')
            array_definition.ShowModal()
            self.arrays_defined = True
            self.xArray_expr = array_definition.xArray_expr
            self.yArray_expr = array_definition.yArray_expr
            array_definition.Destroy()
            if array_definition.canceled:
                self.arrays_defined = False

        if self.arrays_defined:
            dialog = wx.FileDialog(self,message='Import data files',defaultDir=self.currentDirectory,\
                wildcard=wildcard, style=wx.OPEN|wx.MULTIPLE|wx.CHANGE_DIR)

#Need to use Try::except in case of index error
            if dialog.ShowModal() == wx.ID_OK:
                sel_files = dialog.GetPaths()
                for anItem in sel_files:
                    item = anItem.split('/')[-1]
                    print "Appending "+item
                    if item not in self.currentList:
                        self.objects[anItem] = []
                        self.listBox.Append(item)
                        individual_file = Import(anItem)
                        individual_file.import_arrays()
                        individual_file.xArray_expr = self.xArray_expr
                        individual_file.yArray_expr = self.yArray_expr
                        xy_array = individual_file.import_xyArray()

                        self.objects[anItem].append(individual_file)   #zeroth item of list is the xy array
                        self.objects[anItem].append(xy_array)   #first item of list is the xy array
                        self.objects[anItem].append(item)       #second item of list is the label to be used
                    else:
                        print "File already appended to list. Skipping"
                self.plot_list()

                lastDir = '/'
                for i in anItem.split('/')[:-1]:
                    lastDir += i+'/'
                self.currentDirectory = lastDir

            dialog.Destroy()


    #If this is invoked, start a new session in a new window
    def NewSession(self,event):
        execfile('mmt_suite.py')


    # Double-click action on an item in listbox
    def listBox_dblclk(self,event):
        #Need to work on multiple selections for filenames so that multiple files can be plotted at the same time
        selected_item = self.listBox.GetString(self.listBox.GetSelection())
        print selected_item


    def RightClick(self,event):
        rtClk_menu = wx.Menu()
        for (id,title) in menu_title_by_id.items():
            rtClk_menu.Append(id,title)
            wx.EVT_MENU(rtClk_menu,id,self.MenuSelectionCb)

        self.panel.PopupMenu(rtClk_menu,event.GetPosition())  #Replace GetPoint with something else
        rtClk_menu.Destroy()

    def MenuSelectionCb(self,event):
        operation = menu_title_by_id[event.GetId()]
        if operation=='Remove item (del)':
            self.removeItems()
        elif operation=='Rename':
            self.labelItem()
        elif operation=='Save array to file':
            self.saveArrays()
        elif operation=='Average arrays':
            self.average_arrays()

    # Invoke after "remove object" in right click menu clicked or "DEL" button pressed
    # Remove the object and arrays related to the imported file
    def removeItems(self):
        new_currentList = []
        new_arrayObjects = []
        new_xyArrays = []
        selection_indices = self.listBox.GetSelections()[::-1]  #descending order so that index will not be out of range
        counter = 0     #Keeping track of list that is decreasing with revoal of items
        for i in selection_indices:
            print self.currentList[i], 'removed'
            self.currentList.pop(i)
            self.arrayObjects.pop(i)
            self.xyArrays.pop(i)
            self.listBox.Delete(i)
            counter -= 1

        self.plots = []
        pp.close()      #This causes the plot to close and reappear (flashing effect). Any way around this?
        self.plot_list()

    def clearListBox(self):
        for i in range(self.listBox.GetCount()):
            self.listBox.Delete(0)

    # re-Label the selected listbox item
    #Must have selected only a single item
    def labelItem(self):
        selected_index = self.listBox.GetSelections()[0]
        label_dialog = LabelDialog(None,title='Rename')
        label_dialog.ShowModal()
        current_label = label_dialog.label
        current_marker = label_dialog.marker
        current_color = label_dialog.color
        current_linewidth = label_dialog.linewidth
        self.currentList[selected_index] = current_label
        self.listBox.SetString(selected_index,current_label)
        #self.plot_list()
        label_dialog.Destroy()

    #Save the xy arrays for the selected object as a datafile
    def saveArrays(self,event):
        pass

    
    def average_arrays(self):
        selected_objects = self.listBox.GetSelections()
        new_array = ArrayAverageDialog(None,title='Insert new array')
        new_array.ShowModal()
        new_array.Destroy()



#The plot settings dialog window
class PlotDialog(wx.Dialog):
    '''This is the dialog that appears for plot window options '''

    def __init__(self,*args,**kwargs):
        super(PlotDialog,self).__init__(*args,**kwargs)

        self.xlabel = ''
        self.xlabelFlag = False
        self.ylabel = ''
        self.ylabelFlag = False
        self.xlims = []    
        self.xlimFlag = False
        self.ylims = []
        self.ylimFlag = False
        self.title = ''
        self.titleFlag = False

        self.InitUI()

    #The user interface window
    def InitUI(self):
        self.panel = wx.Panel(self)
        self.box0 = wx.BoxSizer(wx.VERTICAL)    #The container
        self.box1 = wx.BoxSizer(wx.HORIZONTAL)
        self.box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.box3 = wx.BoxSizer(wx.HORIZONTAL)
        self.box4 = wx.BoxSizer(wx.HORIZONTAL)
        self.box5 = wx.BoxSizer(wx.HORIZONTAL)
        self.box10 = wx.BoxSizer(wx.HORIZONTAL)

        self.xlabel_text = wx.StaticText(self.panel,label='xLabel')
        self.xlabelObj = wx.TextCtrl(self.panel)
        self.ylabel_text = wx.StaticText(self.panel,label='yLabel')
        self.ylabelObj = wx.TextCtrl(self.panel)
        self.xlim_text = wx.StaticText(self.panel,label='xLimits')
        self.xlimObj = wx.TextCtrl(self.panel)
        self.ylim_text = wx.StaticText(self.panel,label='yLimits')
        self.ylimObj = wx.TextCtrl(self.panel)
        self.title_text = wx.StaticText(self.panel,label='plotTitle')
        self.titleObj = wx.TextCtrl(self.panel)
        self.updateButton = wx.Button(self.panel,id=wx.ID_ANY,label='Update Plot')
        self.closeButton = wx.Button(self.panel,id=wx.ID_ANY,label='Close')

        self.box0.Add(self.box1,0)
        self.box0.Add(self.box2,1)
        self.box0.Add(self.box3,2)
        self.box0.Add(self.box4,3)
        self.box0.Add(self.box5,4)
        self.box0.Add(self.box10,5)
        self.box1.Add(self.xlabel_text,0)
        self.box1.Add(self.xlabelObj,1)
        self.box2.Add(self.ylabel_text,0)
        self.box2.Add(self.ylabelObj,1)
        self.box3.Add(self.xlim_text,0)
        self.box3.Add(self.xlimObj,1)
        self.box4.Add(self.ylim_text,0)
        self.box4.Add(self.ylimObj,1)
        self.box5.Add(self.title_text,0)
        self.box5.Add(self.titleObj,1)
        self.box10.Add(self.updateButton,0)
        self.box10.Add(self.closeButton,1)
        self.panel.SetSizer(self.box0)
        self.panel.Fit()
        self.Centre()

        self.updateButton.Bind(wx.EVT_BUTTON,self.update_plot)
        self.closeButton.Bind(wx.EVT_BUTTON,self.onClose)


    def onClose(self,event):
        self.Destroy()

    #This is not fully implemented yet. Need to change so that leaving one or more empty does not create error. 
    # Check the plotWindow_settings() function in the main window class and modify accordingly
    def update_plot(self,event):
        lim_separators = [':',',','&']
        if self.xlabelObj.GetValue()!='':
            self.xlabelFlag = True
            self.xlabel = str(self.xlabelObj.GetValue())
        if self.ylabelObj.GetValue()!='':
            self.ylabelFlag = True
            self.ylabel = str(self.ylabelObj.GetValue())
        if self.titleObj.GetValue()!='':
            self.titleFlag = True
            self.title = str(self.titleObj.GetValue())
        if self.xlimObj.GetValue()!='':
            self.xlimFlag = True
            for separator in lim_separators:
                if separator in self.xlimObj.GetValue():
                    self.xlims = [float(i) for i in self.xlimObj.GetValue().split(separator)]
        if self.ylimObj.GetValue()!='':
            self.ylimFlag = True
            for separator in lim_separators:
                if separator in self.ylimObj.GetValue():
                    self.ylims = [float(i) for i in self.ylimObj.GetValue().split(separator)]
        self.Destroy()


#The popup dialog for label
class LabelDialog(wx.Dialog):
    '''This is the dialog that appears for ranaming the current label, and to change plot parameters (marker, color, linewidth) for the selected plot. Currently, only the label is implemented. Need to think about how to implement others. Think about using color picker for the color, dropdown/expand menu for markerstyle and linewidth '''

    def __init__(self,*args,**kwargs):
        super(LabelDialog,self).__init__(*args,**kwargs)

        self.label = ''
        self.marker = ''
        self.linewidth = 1
        self.color = ''
        self.InitUI()

    #The user interface window
    def InitUI(self):
        self.panel = wx.Panel(self)
        self.boxV = wx.BoxSizer(wx.VERTICAL)

        self.box0 = wx.BoxSizer(wx.HORIZONTAL)
        self.boxV.Add(self.box0,0)
        self.label_text0 = wx.StaticText(self.panel,label='Label')
        self.box0.Add(self.label_text0,0)
        self.labelObj0 = wx.TextCtrl(self.panel)
        self.box0.Add(self.labelObj0,1)

        self.box1 = wx.BoxSizer(wx.HORIZONTAL)
        self.boxV.Add(self.box1,1)
        self.label_text1 = wx.StaticText(self.panel,label='Marker')
        self.box1.Add(self.label_text1,0)
        self.labelObj1 = wx.TextCtrl(self.panel)    #This is the marker type. May be best to read in from the current value
        self.box1.Add(self.labelObj1,1)

        # Labels for marker/line color
        self.box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.boxV.Add(self.box2,2)
        self.label_text2 = wx.StaticText(self.panel,label='Color')
        self.box2.Add(self.label_text2,0)
        self.labelObj2 = wx.TextCtrl(self.panel)    #This is the marker type. May be best to read in from the current value
        self.box2.Add(self.labelObj2,1)

        # Labels for marker/line color
        self.box3 = wx.BoxSizer(wx.HORIZONTAL)
        self.boxV.Add(self.box3,3)
        self.label_text3 = wx.StaticText(self.panel,label='Linewidth')
        self.box3.Add(self.label_text3,0)
        self.labelObj3 = wx.TextCtrl(self.panel)    #This is the marker type. May be best to read in from the current value
        self.box3.Add(self.labelObj3,1)

        self.box10 = wx.BoxSizer(wx.HORIZONTAL)
        self.boxV.Add(self.box10,4)
        self.updateButton = wx.Button(self.panel,id=wx.ID_ANY,label='Apply')
        self.updateButton.Bind(wx.EVT_BUTTON,self.updateLabel)
        self.box10.Add(self.updateButton,0)
        self.closeButton = wx.Button(self.panel,id=wx.ID_ANY,label='Close')
        self.closeButton.Bind(wx.EVT_BUTTON,self.onClose)
        self.box10.Add(self.closeButton,1)
        
        self.panel.SetSizer(self.boxV)
        self.panel.Fit()
        self.Centre()

    def onClose(self,event):
        self.Destroy()

    def updateLabel(self,event):
        self.label = self.labelObj0.GetValue()
        self.marker = self.labelObj1.GetValue()
        self.color = self.labelObj2.GetValue()
        self.linewidth = self.labelObj3.GetValue()
        self.Destroy()


#The popup dialog for defining the x and y array columns. Only shows up once, first time that file open dialog shows up
#Currently allows simple arithmetic operations to define x and y arrays - (+,-,*,/)
class ArrayDefineDialog(wx.Dialog):
    '''This is the dialog that appears when importing files for the first time to define x and y arrays'''

    def __init__(self,*args,**kwargs):
        super(ArrayDefineDialog,self).__init__(*args,**kwargs)

        self.xArray_expr = ''
        self.yArray_expr = ''
        self.InitUI()
        self.canceled = False

    #The user interface window
    def InitUI(self):
        self.panel = wx.Panel(self)
        self.box0 = wx.BoxSizer(wx.VERTICAL)
        self.box1 = wx.BoxSizer(wx.HORIZONTAL)
        self.box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.box3 = wx.BoxSizer(wx.HORIZONTAL)
        self.box4 = wx.BoxSizer(wx.HORIZONTAL)

        self.xColumn_text = wx.StaticText(self.panel,label='X Column Number')
        self.yColumn_text = wx.StaticText(self.panel,label='Y Column Number')
        self.xColumnNum = wx.TextCtrl(self.panel)
        self.yColumnNum = wx.TextCtrl(self.panel)
        self.updateButton = wx.Button(self.panel,id=wx.ID_ANY,label='Set')
        self.updateButton.Bind(wx.EVT_BUTTON,self.updateLabel)
        self.cancelButton = wx.Button(self.panel,id=wx.ID_ANY,label='Cancel')
        self.cancelButton.Bind(wx.EVT_BUTTON,self.cancel_clicked)
        self.insert_helpText = wx.StaticText(self.panel,label='Insert column number preceeded by "$" (GNUPLOT STYLE).\n Eg : xColumn = $1/1000, yColumn=$7/$8')

        self.box0.Add(self.box1,0)
        self.box0.Add(self.box2,1)
        self.box0.Add(self.box3,2)
        self.box0.Add(self.box4,3)
        self.box1.Add(self.xColumn_text,0)
        self.box1.Add(self.xColumnNum,1)
        self.box2.Add(self.yColumn_text,0)
        self.box2.Add(self.yColumnNum,1)
        self.box3.Add(self.updateButton,0)
        self.box3.Add(self.cancelButton,1)
        self.box4.Add(self.insert_helpText,0)
        
        self.panel.SetSizer(self.box0)
        self.panel.Fit()
        self.Centre()

    def onClose(self,event):
        self.Destroy()

    def cancel_clicked(self,event):
        self.canceled = True
        self.Destroy()

    def updateLabel(self,event):
        self.xArray_expr = self.xColumnNum.GetValue()
        self.yArray_expr = self.yColumnNum.GetValue()
        self.Destroy()


class ArrayAverageDialog(wx.Dialog):
    '''This is the dialog that appears when averaging arrays '''

    def __init__(self,*args,**kwargs):
        super(ArrayAverageDialog,self).__init__(*args,**kwargs)

        self.newArray_label = ''
        self.interpolate_flag = True
        self.InitUI()

    #The user interface window
    def InitUI(self):
        self.panel = wx.Panel(self)
        self.box0 = wx.BoxSizer(wx.VERTICAL)
        self.box1 = wx.BoxSizer(wx.HORIZONTAL)
        self.box2 = wx.BoxSizer(wx.HORIZONTAL)

        self.newLabel_text = wx.StaticText(self.panel,label='New Array name')
        self.newLabel = wx.TextCtrl(self.panel)
        self.interpolateCheck = wx.CheckBox(self.panel,label='Interpolate')
        self.updateButton = wx.Button(self.panel,id=wx.ID_ANY,label='Set')
        self.updateButton.Bind(wx.EVT_BUTTON,self.getVals)

        self.box0.Add(self.box1,0)
        self.box0.Add(self.box2,1)
        self.box1.Add(self.newLabel_text,0)
        self.box1.Add(self.newLabel,1)
        self.box2.Add(self.interpolateCheck,0)
        self.box2.Add(self.updateButton,0)
        
        self.panel.SetSizer(self.box0)
        self.panel.Fit()
        self.Centre()

    def onClose(self,event):
        self.Destroy()

    def getVals(self,event):
        self.newArray_Label = self.newLabel.GetValue()
        self.interpolate_flag = self.interpolateCheck.GetValue()
        print self.newArray_Label, self.interpolate_flag
        self.Destroy()



def main():
    ex = wx.App()
    TheGUI(None)
    ex.MainLoop()
    pp.show()

if __name__ == '__main__':
    main()
