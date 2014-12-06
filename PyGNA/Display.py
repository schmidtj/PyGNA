"""
Display class

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['addInputValues','addExperimentalValues','addInputXValueList','addInputYValueList',
           'addInputZValueList','addExperimentalXValueList','addExperimentalYValueList','addExperimentalZValueList',
           'addInputValue','addExperimentalValue','loglogPlot','histogramCompare','lineGraphCompare','show']

#    Copyright (C) 2012 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Benjamin Bush <benjaminjamesbush@gmail.com>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import matplotlib.pyplot as plt
import numpy
import Utility
import copy
from itertools import groupby

class display(object):
    
    def __init__(self, compare=False):
        
        self.xInputValues= []
        self.xInputValuesList = []
        self.yInputValues= []
        self.yInputValuesList = []
        self.zInputValues = []
        self.zInputValuesList = []
        self.xExperimentalValues = []
        self.xExperimentalValuesList = []
        self.yExperimentalValues = []
        self.yExperimentalValuesList = []
        self.zExperimentalValues = []
        self.zExperimentalValuesList = []
        self.compare = compare
        self.BhattacharyyaDist = 0.
        self.BDGenerated = False
        self.utility = Utility.utility()
        self.histDataGenerated = False
        self.histMapping = {}
        self.histInputData = []
        self.histSimulatedData = []
     
    def addInputValues(self, xValues, yValues, zValues=None):
        self.xInputValues = xValues
        self.yInputValues = yValues
        if zValues !=None:
            self.zInputValues = zValues
      
    def addExperimentalValues(self, xValues, yValues, zValues=None):
        self.xExperimentalValues = xValues
        self.yExperimentalValues = yValues
        if zValues != None:
            self.zExperimentalValues=zValues
            
    def addToExperimentalValuesList(self, xValues, yValues, zValues=None):
        self.xExperimentalValuesList.append(xValues)
        self.yExperimentalValuesList.append(yValues)
        if zValue != None:
            self.zExperimentalValuesList.append(zValues)
            
    def addInputXValueList(self, xList):
        self.xInputValues = xList
        
    def addExperimentalXValueList(self, xList):
        self.xExperimentalValues = xList
        
    def addInputYValueList(self, yList):
        self.yInputValues = yList
        
    def addExperimentalYValueList(self, yList):
        self.yExperimentalValues = yList
        
    def addInputZValueList(self, yList):
        self.zInputValues = yList
            
    def addExperimentalZValueList(self, yList):
        self.zExperimentalValues = yList    
    
    def addInputValue(self, yValue, zValue=None):
        self.xInputValues.append(len(self.yInputValues))
        self.yInputValues.append(yValue)
        if zValue != None:
            self.zInputValues.append(zValue)
        
    def addExperimentalValue(self, yValue, zValue=None):
        self.xExperimentalValues.append(len(self.yExperimentalValues))
        self.yExperimentalValues.append(yValue)
        if zValue != None:
            self.zExperimentalValues.append(zValue)
            
    def clearExperimentalValues(self):
        self.xExperimentalValues = []
        self.yExperimentalValues = []
        
    def clearInputValues(self):
        self.xInputValues = []
        self.yInputValues = []
        
    def appendInputValuesToList(self):
        self.xInputValuesList.extend(copy.deepcopy(self.xInputValues))
        self.yInputValuesList.extend(copy.deepcopy(self.yInputValues))
        
    def appendExperimentalValuesToList(self):
        self.xExperimentalValuesList.extend(copy.deepcopy(self.xExperimentalValues))
        self.yExperimentalValuesList.extend(copy.deepcopy(self.yExperimentalValues))
        
    
    def generateBhattacharyyaFromInputs(self):
        if not self.histDataGenerated:
            self.setupHistogramData()
        
        bins = numpy.linspace(0, len(set(self.yInputValues)), len(self.histMapping)+1)
        
        if __debug__:
            print set(self.yInputValues)
            
        inputProbDist = [float(x)/sum(self.histInputData) for x in self.histInputData]
        simulatedProbDist = [float(x)/sum(self.histSimulatedData) for x in self.histSimulatedData]
        self.BhattacharyyaDist = self.utility.BhattacharyyaDistance(inputProbDist, simulatedProbDist)
        self.BDGenerated = True
        
    def getBhattacharyyaDistance(self):
        if not self.BDGenerated:
            self.generateBhattacharyyaFromInputs()
            
        return self.BhattacharyyaDist
        
    def loglogPlot(self, title, xAxisName, yAxisName, zAxisName="None", legloc='best', multiLine=False):
        if self.compare:
            titleOne = title + " - Observed"
            titleTwo = title + " - Experimental"
            #plt.subplot(221)
            plt.xlabel(xAxisName)
            plt.ylabel(yAxisName)
            plt.title(title)
            #n, bins, patches = plt.hist(self.yObservedValues, max(self.xObservedValues),  facecolor='b')
            plt.loglog(self.xInputValues, self.yInputValues, 'b', label='Input', lw = 2)
            if not multiLine:
                plt.loglog(self.xExperimentalValues, self.yExperimentalValues, 'g', label='Simulated')
            else:
                count = 0
                first = True
                while count < len(self.xExperimentalValuesList):
                    if first:
                        plt.loglog(self.xExperimentalValuesList[count], self.yExperimentalValuesList[count], 'g', label='Simulated')
                    else:
                        plt.loglog(self.xExperimentalValuesList[count], self.yExperimentalValuesList[count], 'g')
                    first = False
                    count += 1
            plt.legend(loc=legloc)
            path = title + ".pdf"
            plt.savefig(path, format='pdf')
            plt.close()
            #plt.show()
            
        else:
            plt.xlabel(xAxisName)
            plt.ylabel(yAxisName)
            plt.title(title)
            plt.loglog(self.xInputValues, self.yInputValues)
            path = title + ".pdf"
            plt.savefig(path, format='pdf')    
            plt.close()
            #plt.show()
    
    def setupHistogramData(self):
        self.histMapping = {}
        count = 0
        for x in set(self.yInputValues):
            self.histMapping[x] = count
            count += 1    
            
        inputMap  = [self.histMapping[x] for x in self.yInputValues]
        simulatedMap = [self.histMapping[x] for x in self.yExperimentalValues]
        self.histInputData = [inputMap.count(x) for x in set(inputMap)]
        self.histSimulatedData = [simulatedMap.count(x) for x in set(inputMap)]
        self.histDataGenerated = True
        
    def improvedHistDataSetup(self):
        deg_seq_one = sorted(self.yInputValues)
        deg_seq_two = sorted(self.yExperimentalValues)
        
        freq_seq_one = dict((key, float(len(list(group)))) for key, group in groupby(deg_seq_one))
        freq_seq_two = dict((key, float(len(list(group)))) for key, group in groupby(deg_seq_two))
        
        # Make sure items in the input network exist in the generated network
        for key in freq_seq_one.iterkeys():
            if key not in freq_seq_two:
                freq_seq_two[key] = 0.
                
        for key in freq_seq_two.iterkeys():
            if key not in freq_seq_one:
                freq_seq_one[key] = 0.
                
        orderedKeys = list(set(freq_seq_one.keys() + freq_seq_two.keys()))
        self.xInputValues = [str(x) for x in orderedKeys]
        self.histInputData = [freq_seq_one[x] for x in orderedKeys]
        self.histSimulatedData = [freq_seq_two[x] for x in orderedKeys]
        self.histDataGenerated = True
        
    def getHistInputData(self):
        if not self.histDataGenerated:
            self.setupHistogramData()
        return self.histInputData
    
    def getHistSimulatedData(self):
        if not self.histDataGenerated:
            self.setupHistogramData()
        return self.histSimulatedData
    
    def histogramCompare(self, title, xAxisName, yAxisName, zAxisName="None"):
        if self.compare:
            titleOne = title + " - Input"
            titleTwo = title + " - Simulated"
            plt.xlabel(xAxisName)
            plt.ylabel(yAxisName)
            plt.title(title)
            
            if not self.histDataGenerated:
                self.setupHistogramData()
                
            bins = numpy.linspace(0, len(set(self.yInputValues)), len(self.histMapping)+1)
            highestCount = max(max(self.histInputData),max(self.histSimulatedData))
            plt.text(len(self.histMapping), highestCount, "DB: " + str(self.BhattacharyyaDist), va='top', ha='right')
            
            plt.hist([self.histInputData, self.histSimulatedData], bins, 
                     color = ['blue', 'green'],
                     label = ['Input','Simulated'])
            
            plt.legend(loc='center right')
            path = title + ".pdf"
            plt.savefig(path, format='pdf')
            #plt.show()
        else:
            plt.xlabel(xAxisName)
            plt.ylabel(yAxisName)
            plt.title(title)
            n, bins, patches = plt.hist(self.yInputValues, len(set(self.yInputValues)), facecolor='b')  
            path = title + ".pdf"
            plt.savefig(path, format='pdf')
            #plt.show()        
    
    def UESBarPlot(self, title, xlabel, ylabel, means, std, BDMean):
        self.histInputData = self.yInputValues
        self.histSimulatedData = self.yExperimentalValues
        self.histDataGenerated = True
        self.generateBhattacharyyaFromInputs()
        
        ind = numpy.arange(len(self.yInputValues))
        n_means = numpy.array(means)
        n_std = numpy.array(std)
        width = 0.45
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        rects1 = ax.bar(ind, self.yInputValues, width, color='b')
        
        rects2 = ax.bar(ind+width, means, width, color='g')#, yerr=std, error_kw=dict(ecolor='red'))
        
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        ax.set_title(title)
        ax.axes.get_xaxis().set_ticks([])
        
        ax.legend((rects1[0], rects2[0]), ('Input', 'Simulated Mean'),loc='upper right')
        #plt.text(max(ind)*1.0, .90*max(max(means),max(self.yInputValues)),"DB  = " + str(self.BhattacharyyaDist), va='center', ha='center')
        plt.text(0.7, 0.8,"DB  = " + str(self.BhattacharyyaDist), va='center', ha='center', transform=ax.transAxes)
        plt.xlim(0, ind[-1]+width*2)
        low = n_std
        lowTest = n_means-n_std
        i = 0
        while i < len(low):
            if lowTest[i] < 0:
                low[i] = n_means[i]
            i += 1
        
        plt.errorbar(ind+width*1.5, means, fmt=None, ecolor='red',yerr=[low,n_std]) 
        path = title + ".pdf"
        plt.savefig(path, format='pdf')
        #plt.show()
    
    def barCompare(self, title, xlabel, ylabel, xdata, ydata):
        ind = numpy.arange(len(xdata))
        width = 0.45
        
        fig , ax = plt.subplots()
        rects1 = ax.bar(ind, xdata, width, color='b')
        
        rects2 = ax.bar(ind+width, ydata, width, color='g')#, yerr=std, error_kw=dict(ecolor='red'))
        
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        ax.set_title(title)
        ax.set_xticks(ind+width)
        ax.set_xticklabels(ind)
        
        ax.legend((rects1[0], rects2[0]), ('Input', 'Simulated'),loc='upper right')
        #plt.text(max(ind)*1.0, .90*max(max(means),max(self.yInputValues)),"DB  = " + str(self.BhattacharyyaDist), va='center', ha='center')
        #plt.text(0.7, 0.8,"DB  = " + str(self.BhattacharyyaDist), va='center', ha='center', transform=ax.transAxes)
        #plt.xlim(0, ind[-1]+width*2)
        path = title + ".pdf"
        plt.savefig(path, format='pdf')
        #plt.show()
                
    def lineGraph(self, title, xAxisName, yAxisName, zAxisName="None", legloc='best', multiLine=False):
        if self.compare:
            titleOne = title + " - Observed"
            titleTwo = title + " - Experimental"
            #plt.subplot(221)
            plt.xlabel(xAxisName)
            plt.ylabel(yAxisName)
            plt.title(title)
            #n, bins, patches = plt.hist(self.yObservedValues, max(self.xObservedValues),  facecolor='b')
            plt.plot(self.xInputValues, self.yInputValues, 'b', label='Input', lw = 2)
            if not multiLine:
                plt.plot(self.xExperimentalValues, self.yExperimentalValues, 'g', label='Simulated')
            else:
                x_vals = [x for x in range(len(self.xExperimentalValuesList))]
                plt.plot(x_vals, self.yExperimentalValuesList, 'g', label='Simulated')
            
            '''
            plt.subplot(224)
            plt.xlabel(xAxisName)
            plt.ylabel(yAxisName)
            plt.title(titleTwo)
            #n, bins, patches = plt.hist(self.yExperimentalValues, max(self.xExperimentalValues), facecolor='b')
            plt.plot(self.xExperimentalValues, self.yExperimentalValues, 'b')'''
            plt.legend(loc=legloc)
            path = title + ".pdf"
            plt.savefig(path, format='pdf')
            plt.close()
            #plt.show()
        else:
            plt.xlabel(xAxisName)
            plt.ylabel(yAxisName)
            plt.title(title)
            if not multiLine:
                plt.plot(self.xInputValues, self.yInputValues, 'b')
            else:
                x_vals = [x for x in range(len(self.xInputValuesList))]
                plt.plot(x_vals, self.yInputValuesList, 'b')
            path = title + ".pdf"
            plt.savefig(path, format='pdf')
            plt.close()
            #plt.show()
       
    def scatter(self, x, y):
        plt.scatter(x, y)
        plt.show()
     
    def pieChart(self, title, data, labels):
        plt.figure(1, figsize=(8,8))
        ax = plt.axes([0.1, 0.1, 0.8, 0.8])
        plt.pie(data, labels=labels, shadow=True)
        plt.title(title)
        path = title + ".pdf"
        plt.savefig(path, format='pdf')
        plt.close()
        #plt.show()
         
    def show(self, title, xAxisName, yAxisName):
        if self.compare:
            titleOne = title + " - Observed"
            titleTwo = title + " - Experimental"
            plt.subplot(221)
            plt.xlabel(xAxisName)
            plt.ylabel(yAxisName)
            plt.title(titleOne)
            plt.plot(self.xInputValues, self.yInputValues,'o')
            
            plt.subplot(222)
            plt.xlabel(xAxisName)
            plt.ylabel(yAxisName)
            plt.title(titleTwo)
            plt.plot(self.xExperimentalValues, self.yExperimentalValues,'o')
            
            path = title + ".pdf"
            plt.savefig(path, format='pdf')            
            #plt.show()
                    
        else:                
            plt.xlabel(xAxisName)
            plt.ylabel(yAxisName)
            plt.title(title)
            plt.plot(self.xInputValues,self.yInputValues, 'o')
            path = title + ".pdf"
            plt.savefig(path, format='pdf')            
            #plt.show()