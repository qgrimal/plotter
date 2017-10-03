import scipy as sp
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import re
import os

class Import():
    """This creates an object with a particular filename that imports the full arrays associated with the file"""
    """ Usage : file_object = Import(filename) """

    def __init__(self,filename):
        self.filename = filename.split('/')[-1]
        self.label = ''     #Need to split label according to MR or RT
        self.arrays = None
        self.xyArray = None
        self.interp_pts = 100   #Number of pts for interpolation

        self.xArray_expr = ''
        self.yArray_expr = ''
        self.object_prop = {filename:[]}     #This is the dictionary that keeps all values of the object
        self.normalized = None

    #Still need to implement data delimiter choosing
    def import_arrays(self):
        self.arrays = sp.genfromtxt(self.filename)
        return self.arrays   #in case values need to be retrieved

    #The columns are defined in gnuplot style i.e. $0,$1,...
    #The replaced open_file is defined per import_xyarray method below
    def define_array(self,expr):
        all_columns = re.findall('\$[0-9]*',expr)
        sub_expr = expr
        for item in all_columns:
            sub_expr = sub_expr.replace(item,'open_file[:,%s]'%item[1:])
        return sub_expr

    # Always keep the xarray in ascending order
    def import_xyArray(self):
        if self.arrays is None:
            self.import_arrays()

        open_file = self.arrays
        self.xArray_expr = self.define_array(self.xArray_expr)
        self.yArray_expr = self.define_array(self.yArray_expr)
        xArray = eval(self.xArray_expr)
        yArray = eval(self.yArray_expr)
        self.xyArray = sp.array([xArray,yArray])
        return self.xyArray         # To retrieve the xy arrays

    def normalize(self):
        #Only normalization to max value. Need to implement local max normalization. Only yArray is normalized
        self.normalized = sp.array([self.xyArray[0],(self.xyArray[1]-min(self.xyArray[1]))/max(self.xyArray[1])])
        return self.normalized

    def array_reversal(self):
        return sp.array([self.xyArray[0,::-1],self.xyArray[1,::-1]])

    # Interpolation. Ensure that the datapoints are within the xarray limits - not to exceed boundary
    # This only accounts for linear points between min and max of the array. Need to implement different scalings 
    def interpolate(self,xyarray,numpts):
        min_xarray = min(xyarray[0])
        max_xarray = max(xyarray[1])
        stepVal = (max_xarray-min_xarray)/len(xarray)
        interp_func = interp1d(xarray,yarray)
        x_interp = sp.linspace(min_xarray+stepVal,max_xarray-stepVal,numpts)
        y_interp = interp_func(x_interp)
        return sp.array([x_interp,y_interp])

    #Averages two or more arrays. Each arg is a (x,y) array. Returns (xAvg,yAvg)
    def average(self,*arg):
        to_average_arrays = []
        print len(arg), 'arrays selected for averaging'
        for item in range(len(arg)):
            interp_arrays = self.interpolate(item,self.interp_pts)
            to_average_arrays.append(interp_arrays)
        self.toAverage = sp.array(to_average_arrays)
        averageArray = sp.average(to_average_arrays,axis=0)
        return averageArray
        


