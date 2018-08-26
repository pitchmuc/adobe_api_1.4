# -*- coding: utf-8 -*-
"""
This library is the Adobe Analytics API for the 1.4 API version.
It works on Python and is mostly built on Classes. 

@author: julienpiccini

"""

import json as _json#For reading the statement
import requests as _requests #for call to the API
import pandas as _pd
import time as _time
import os as _os
from pathlib import Path as _Path
_c_path = _Path.cwd() #get the current folder
_new_path = _c_path.joinpath('aanalytics') #create new folder
_new_path.mkdir(exist_ok=True) #create a new folder to store the data

"""
Configuration 
You need to place your API key below for the Oauth 2.0 autentification
"""
"""Configuration for the token & different admin request"""
_apliId=''
_secretApli=''
_reportsuite=''


"""
basic filename function
"""
def __newfilename():
    fmonth = _time.strftime("%m")
    fday = _time.strftime("%d")
    fhour = _time.strftime("%H")
    fminute = _time.strftime("%M")
    filename='report_'+fmonth+'_'+fday+'_'+fhour+'_'+fminute
    return filename
"""
Configure 
"""

"""
Statement class that enable to manipulate the statement easily with pre-made method. 

"""

class Statement:
    """
    Class to generate and / or create a statement for the Adobe Analytics API.
    This class initiate an object based on 1 argument, this argument can take several possible values :
        - an object that contains the dictionnary 
        - a file name as string, such as "filename.txt" that contains your JSON 
        - "new" that will create an empty statement
    """

    __empty_statement = {"reportDescription":{
    	"reportSuiteID":"",
    	"dateFrom":"2018-01-01",
    	"dateTo":"2018-01-31",
    	"metrics":[{"id":"visits"}],
    	"sortBy":"visits",
    	"elements":[],
    	"segments":[]}
    }
    def _initiate_elements(self,statement):#initiate the different elements
        self.statement = statement # return the dict
        self.start_dates = self.statement['reportDescription']['dateFrom']
        self.end_dates = self.statement['reportDescription']['dateTo']
        self.metrics = [x['id'] for x in statement['reportDescription']['metrics']]
        self.segments = [x['id'] for x in statement['reportDescription']['segments']]
        self.dimensions = statement['reportDescription']['elements']
        if 'source' in statement['reportDescription'].keys() :
            if statement['reportDescription']['source'] == 'warehouse':#Check if warehouse asked
                self.export = "csv"
            else:
                self.export = "json"
        else:
            self.export = "json"
        if 'dateGranularity' in statement['reportDescription'].keys():#Check if granularity
            self.date_granularity = statement['reportDescription']['dateGranularity']
        else:
            self.date_granularity = None
        return self.statement
    
    def __init__(self,*elements):
        if len(elements) == 0:
            print('an argument is required')
        for element in elements:
            if '.txt' in element : 
                with open(element,'r') as f:
                    read_statement = f.read()
                    try:
                        stat_json = _json.loads(read_statement)
                        self._initiate_elements(stat_json)# initiate the different objects
                    except :
                        print('Error reading your statement.\nPlease verify.')
            elif type(element) is dict:
                self._initiate_elements(element)# initiate the different objects
                
            elif element == 'new':
                obj=self.__empty_statement
                self._initiate_elements(obj)
        
    def __str__(self):
        return 'Return an Adobe Analytics statement as object to work with underlying method'
        
    def __repr__(self):
        return str(self.statement)
    
    def add_metrics(self,*metrics):
        """ Add metrics to your statement, this method can take several elements"""
        for metrics in metrics:
            self.statement['reportDescription']['metrics'].append({'id':metrics})
        self.metrics = [x['id'] for x in self.statement['reportDescription']['metrics']]##update the variables
        
    def remove_metrics(self,*metrics):
        """ Remove metrics to your statement, this method can take several elements"""
        for metrics in metrics:
            self.statement['reportDescription']['metrics'].remove({'id':metrics})
        self.metrics = [x['id'] for x in self.statement['reportDescription']['metrics']]##update the variables
        
    def add_segments(self,*segments):
        """ Add segments to your statement, this method can take several elements"""
        for segment in segments:
            self.statement['reportDescription']['segments'].append({'id':segment})
        self.segments = [x['id'] for x in self.statement['reportDescription']['segments']]##update the variables

    def remove_segments(self, *segments):
        """ Remove segments to your statement, this method can take several elements """
        for segment in segments:
            self.statement['reportDescription']['segments'].remove({'id':segment})
        self.segments = [x['id'] for x in self.statement['reportDescription']['segments']]##update the variables

    def add_dimensions(self,*dimensions):
        """ Add a dimension to your statement, this method can take several elements"""
        for dim in dimensions:
            self.dimensions.append(dim)
    
    def remove_dimensions(self, *dimensions):
        """ Remove dimensions """
        for dim in dimensions:
            self.dimensions.remove(dim)
            
    def add_granularity(self,granularity):
        """ Add granularity to your statement (month, day, etc...)"""
        self.statement['reportDescription']['dateGranularity'] = granularity
        
    def remove_granularity(self):
        """ Remove the granularity from your statement """
        del self.statement['reportDescription']['dateGranularity']
    
    def add_top(self,dim=None,top=10):
        """ Change the number of element to retrieve for a specific dimension
        
        By default, your statement return the top 10 for normal reporting. 
        Return everything for Data Warehouse. 
        """
        for dimension in self.statement['reportDescription']['elements']:
            if dim == dimension['id']:
                dimension['top']=top
        self.dimensions = self.statement['reportDescription']['elements']##update the variable
    def change_dates(self,start=None,end=None):
        """ Change the start dates or end dates of your statement depending on the argument you pass
        """
        if start is not None : 
            self.statement['reportDescription']['dateFrom'] = start
            self.start_dates = self.statement['reportDescription']['dateFrom']
        if end is not None : 
            self.statement['reportDescription']['dateTo'] = end
            self.end_dates = self.statement['reportDescription']['dateTo']
    def add_source(self):
        """ Add Datawarehouse as source. Be careful as calculated metric, 
        some segments and events are not supported by data wareouse request
        """
        self.statement['reportDescription']['source'] = 'warehouse'
        self._initiate_elements(self.statement)
    
    def remove_source(self):
        """ remove Datawarehouse as source.
        """
        del self.statement['reportDescription']['source']
        self._initiate_elements(self.statement)
    

def _getToken(_apliId,_secretApli):
    """
    Internal function to retrieve token for the API. Oauth usage. 
    """
    urladobetoken ='https://api.omniture.com/token'
    params = {'grant_type':'client_credentials','client_id':_apliId,'client_secret':_secretApli}
    query =  _requests.post(urladobetoken, data=params)
    data = _json.loads(query.text)
    token = str(data['access_token'])
    return token
         
"""
General API variables to be set
"""         
     
_dict_api = {
        'endpoint':'https://api.omniture.com/admin/1.4/rest/', #1.4 endpoint
        'reportSuite' : {
                'geteVars':'ReportSuite.GetEvars',
                'getprops':'ReportSuite.GetProps',
                'getevents':'ReportSuite.GetEvents'},
        'calcmetrics':{
                'getcalcmetrics':'CalculatedMetrics.Get'
                },
        'segments':{
                'getsegments':'Segments.Get'
                },
        'Report':{
                'create':'Report.Queue',
                'check':'Report.GetQueue',
                'retrieve':'Report.Get'
                }
        }

#_apliId,_secretApli,_reportsuite = self.__application_id()
#Function
def _retrieveDataElements(_data_admin,_prog):
    elements = []
    if _prog == 'evars': ##_prog = prog[1]
        data=_data_admin[0]['evars']
        elements = list(zip([x['id'] for x in data],[x['name'] for x in data]))#Comprehensive list to turn into df later
    elif _prog == 'props':
        data=_data_admin[0]['props']
        elements = list(zip([x['id'] for x in data],[x['name'] for x in data]))
    elif _prog == 'events':
        data=_data_admin[0]['events']
        elements = list(zip([x['id'] for x in data],[x['name'] for x in data]))
    elif _prog == 'calcmetrics':
        data = _data_admin
        elements = list(zip([x['id'] for x in data],[x['name'] for x in data]))
    elif _prog == 'segments':
        data = _data_admin
        elements = list(zip([x['id'] for x in data],[x['name'] for x in data]))
    return elements

##Output with Pandas
def _writeFile(_data,_prog):
    df=_pd.DataFrame(_data)
    columns = ["id","name"]
    df.columns = columns
    df.to_csv(_new_path.as_posix()+'/'+_prog+'.csv',index=False)
    return df

#Current function display to the user
def getElements(*elements,export=True,return_data=True):
    """
    This function can take multiple predefined arguments, as well as some optional key value pairs. 
    the possibles arguments are :  
        - evars : list of evars on your reportsuite
        - props : list of props on your reportsuite
        - events : list of events on your reportsuite
        - calcmetrics : list of calculated metrics on your reportsuite
        - segments : list of segments on your reportsuite
    
    the optional key values pairs are : 
     - export = determine if a csv file will be created with the data (default : True)
     - return_data = determine if a dictionnary of dataframe will be return (default : True)
    """
    token = _getToken(_apliId,_secretApli)#retrieve the token and reportSuite
    r_statement = {"rsid_list":[_reportsuite]}##statement for reportSuite method
    a_statement = {"accessLevel":"all"}
    df_all  = {}
    for element in elements:
        if element == 'evars':
            reqReport = _requests.post(url=_dict_api['endpoint'], params={"method": _dict_api['reportSuite']['geteVars'], "access_token": token},json=r_statement)
            responseReport = reqReport.json()
            raw_data = _retrieveDataElements(responseReport,element)
            if export:
                evars = _writeFile(raw_data,element)
            df_all['evars'] = evars
        elif element == 'props':
            reqReport = _requests.post(url=_dict_api['endpoint'], params={"method": _dict_api['reportSuite']['getprops'], "access_token": token},json=r_statement)
            responseReport = reqReport.json()
            raw_data = _retrieveDataElements(responseReport,element)
            if export :
                props = _writeFile(raw_data,element)
            df_all['props'] = props
        elif element == 'events':
            reqReport = _requests.post(url=_dict_api['endpoint'], params={"method": _dict_api['reportSuite']['getevents'], "access_token": token},json=r_statement)
            responseReport = reqReport.json()
            raw_data = _retrieveDataElements(responseReport,element)
            if export : 
                events = _writeFile(raw_data,element)
            df_all['events']= events
        elif element == 'calcmetrics':
            reqReport = _requests.post(url=_dict_api['endpoint'], params={"method": _dict_api['calcmetrics']['getcalcmetrics'], "access_token": token},json=a_statement)
            responseReport = reqReport.json()
            raw_data = _retrieveDataElements(responseReport,element)
            if export : 
                calcmetrics = _writeFile(raw_data,element)
            df_all['calcmetrics'] = calcmetrics
        elif element == 'segments':
            reqReport = _requests.post(url=_dict_api['endpoint'], params={"method": _dict_api['segments']['getsegments'], "access_token": token},json=a_statement)
            responseReport = reqReport.json()
            raw_data = _retrieveDataElements(responseReport,element)
            if export : 
                segments = _writeFile(raw_data,element)
            df_all['segments'] = segments
            #something
    if export:##if the option has been selected
        print('Please find the data on this folder : '+_new_path.as_posix())
    if return_data : #if the option has been selected
        return df_all
    

#function to check if the statement is correct.
#Work with a file and a dict
def _checkStatement(statement):
    if '.txt' in statement : #if the statement is a txt file
        try : 
            with open(statement, 'r') as f:
                read_statement = f.read()
                stat_json = _json.loads(read_statement)
                try:
                    if stat_json['reportDescription']['source'] == 'warehouse':
                        export = 'csv'
                except:
                    export = 'json'
        except:
            print('error with your statement. Please verify your file.')
            exit()
    elif type(statement) == dict:
        stat_json = statement
        try:
            if stat_json['reportDescription']['source'] == 'warehouse':
                export = 'csv'
        except:
            export = 'json'
    else : 
        print('error with your statement. Please verify')
        exit
    return stat_json, export

def _save_reportID(_report_id,_export):
    """ This function will save the report id for further usage """
    data = {'report_id':[_report_id],'request_type':[_export]}
    save = _pd.DataFrame(data)
    if 'save_report_id.txt' in _os.listdir(_new_path.as_posix()):
        try:
            df=_pd.read_csv('save_report_id.txt')
            df = df.append(save)
            df.to_csv('save_report_id.txt',index=False)
        except:
            save.to_csv('save_report_id.txt',index=False)
    else:
         save.to_csv('save_report_id.txt',index=False)
         
#Call to create report and save the reportID
def _CreateReport(statement,_token,_export):
    """ This function send the request to Adobe and return the reportID"""
    reqReport = _requests.post(url=_dict_api['endpoint'], params={"method": _dict_api['Report']['create'], "access_token": _token, },json=statement)
    j_response = reqReport.json()
    report_id = j_response['reportID']
    return report_id

def _getQueue(_token,_reportID):
    """ This function check the queue and if the report ID is in the queue """
    reqQueue = _requests.post(url=_dict_api['endpoint'], params={"method": _dict_api['Report']['check'], "access_token": _token })
    responseQueue = reqQueue.json()
    if(len(responseQueue)==0):#if there is no queue
        return True
    else :#if there is a queue
        for report_nb in range(len(responseQueue)):
            if responseQueue[report_nb]['reportID'] != int(_reportID):
                status_queue = True
            elif responseQueue[report_nb]['reportID'] == int(_reportID):
                return False
            else:
                return True
        return status_queue

def _reportGet(_token,_reportid,_export):
    """ API request to retrieve the data  """
    reqGet = _requests.post(url=_dict_api['endpoint'], params={"method":_dict_api['Report']['retrieve'], "access_token": _token, },json={"reportID":int(_reportid),"format":_export})
    responseGet = reqGet ##cannot return a json because of DW
    return responseGet


## Wait for the DW 
def _waitingDataWarehouse():
    _time.sleep(10*60)

## Check the status for the report ID
def _returnStatusDW(_reportID,_apliID,_secretApli):
    """ Function to check the datawarehouse status
    
    It returns True as value when the function succeed to retrieve data.
    1 additional value returned : response from the report requested. 
        
    """
    _waitingDataWarehouse()##Waiting 10 mn
    _token = _getToken(_apliID,_secretApli)##Creating new token
    try : 
        raw_data = _reportGet(_token,_reportID,'csv').json()
        if 'error' in raw_data.keys():
            if raw_data['error'] == 'report_not_ready':
                return False, 'report_not_ready'
    except:
        try: 
            raw_data = _reportGet(_token,_reportID,'csv') ##if the response is the data
            return True, raw_data
        except :
            return False, []
    

def _data_preparation(_raw_data,_export): 
    """data preparation for further steps.
    This function return directly the dataframe for DW
    It returns a json report for normal report"""
    if _export == 'csv':
        data_warehouse = _raw_data.content.decode("utf-8").replace('"','').splitlines()
        dw_splitComma = [x.split(',') for x in data_warehouse]
        df = _pd.DataFrame(dw_splitComma)
        df.columns = [df.iat[0,x].replace('\ufeff','') for x in range(len(df.columns))] ## assign column name & clean names
        df.drop(0,inplace=True)
        df.dropna(inplace=True)
        return df
    else: ### if the report is normal report
        dict_overview = _raw_data['report']
        return dict_overview


def _csdmpr(j_report): 
    """ retrieve the column,segments, Length, Dimension, Metrics, Period, Report Type from the data"""
    metrics = list() #retrieve the metrics as list
    dict_overview = j_report
    period = dict_overview['period']
    if 'segments' in dict_overview.keys():
        segments = [x['name'] for x in dict_overview['segments']]
    metrics = [x['name'] for x in dict_overview['metrics']]
    dim = [x['name'] for x in dict_overview['elements']]
    ###Check what kind of report it is
    report_type = dict_overview['type']
#    if report_type =='ranked' or report_type =='overtime':
#          length_dim = len(dim)
#    elif report_type=='trended':##Add the date as one of the dimension
#          length_dim = len(dim)+1
    ###column of the future DataFrame
    if report_type =='ranked' or report_type =='overtime':
          columns = dim+metrics
    elif report_type=='trended':
          columns = ["date"]+dim+metrics
    return columns,segments, dim, metrics,period, report_type


def _data_retrieve(data,row=[],rows=[],start=False):#takes dict_overview['data'] as input
    if start:##Sure to clean the rows at the beginning
        rows=[]
    if type(data) == list :
        if len(row) == 0:
            for x in range(len(data)):
                _data_retrieve(data[x],rows=rows)
        elif len(row) >0:
            for x in range(len(data)):
                _data_retrieve(data[x],row=row,rows=rows)
    elif type(data) == dict:
        if 'breakdownTotal' in data.keys(): #not the last element
            name = [data['name']]
            row = row + name
            _data_retrieve(data['breakdown'],row=row,rows=rows)
        elif 'counts' in data.keys():
            name = [data['name']]
            counts = data['counts']
            row = row + name + counts
            rows.append(row)
    return _pd.DataFrame(rows)

def getReport(statement,export=True,return_data=True,recursive=False,verbose=False,safe_mode=False):
    """ 
    This function takes 1 required arguments and 5 optionnals.
    It returns a file and / or a dataframe with the data requested. 
    arguments : 
        statement : REQUIRED : statement for the data ask to Adobe
        export : OPTIONNAL : boolean to determine if a csv file is going to be created (default : True)
        return_data : OPTIONNAL : boolean to determine if a dataframe is returned (default : True)
        recursive : OPTIONNAL : for non DW reports, automatically retrieve 50K rows for the first element until there is no more rows to fetch. (default : False)
        verbose : OPTIONNAL : print comments if you want to follow the status of the request (default : False)
        safe_mode : OPTIONNAL : save the report ID created into a file (default : False)
    """
    _statement, _export = _checkStatement(statement)
    if verbose:
        print('your statement : \n'+str(_statement))
    _token = _getToken(_apliId,_secretApli)#retrieve the token and reportSuite
    if verbose: 
        print('Token is retrieved')
    if _export == 'csv': ##if a datawarehouse request
        _reportId = _CreateReport(_statement,_token,_export)
        if safe_mode : 
            _save_reportID(_reportId,_export)
            if verbose: 
                print('report ID retrieved & saved.\report ID : '+str(_reportId))
        if verbose: 
                print('report ID retrieved : '+str(_reportId))
        status_DW, _raw_data = _returnStatusDW(_reportId,_apliId,_secretApli)
        while not status_DW:
            if verbose:
                print('Adobe processing...')
            status_DW, _raw_data = _returnStatusDW(_reportId,_apliId,_secretApli)
        df = _data_preparation(_raw_data,_export)
        _filename = __newfilename()
        if export:
            df.to_csv(_new_path.as_posix()+'/'+_filename+'.csv',index=False)
            if verbose:
                print('File has been created in this folder: '+_new_path.as_posix())
        if return_data:
            return df
    if _export == 'json':##if a normal request
        if not recursive:## normal request with limited number of rows
            _reportId = _CreateReport(_statement,_token,_export)
            if safe_mode:
                _save_reportID(_reportId,_export)
                if verbose:
                    print('report ID retrieved & saved.\report ID : '+str(_reportId))
            if verbose:
                print('report ID retrieved : '+str(_reportId))
            status = _getQueue(_token,_reportId)
            if not status and verbose:
                print('data are processed by Adobe')
            while not status:
                _time.sleep(60)
                status = _getQueue(_token,_reportId)
            _raw_data = _reportGet(_token,_reportId,_export).json()
            if verbose:
                print('Data retrieved')
            j_report = _data_preparation(_raw_data,_export)
            j_data = j_report['data']
            columns, segments, dimensions, metrics, period, report_type = _csdmpr(j_report)
            df = _data_retrieve(j_data,start=True) ##Start clean previous call data
            df.columns = columns#rename the columns
            _filename = __newfilename()
            if export:
                df.to_csv(_new_path.as_posix()+'/'+_filename+'.csv',index=False)
                if verbose:
                    print('File has been created in this folder: '+_new_path.as_posix())
            if return_data:
                return df
        else : ## normal request with unlimited number of rows
            rows = 50000
            start_with = 1
            df_all = _pd.DataFrame() ##to regroup all the dataframe
            statement['reportDescription']['elements'][0]['top'] = rows
            while rows == 50000:
                if verbose:
                    iter = round(start_with/50000)+1
                    print(str(iter) + ' iteration')
                    print('start with : '+str(start_with))
                statement['reportDescription']['elements'][0]['startingWith'] = start_with
                _reportId = _CreateReport(_statement,_token,_export)
                status = _getQueue(_token,_reportId)
                while not status:
                    if verbose:
                        print('data are processed by Adobe')
                    _time.sleep(60)
                    status = _getQueue(_token,_reportId)
                _raw_data = _reportGet(_token,_reportId,_export).json()
                if verbose:
                    print('iteration of data retrieved')
                j_report = _data_preparation(_raw_data,_export)
                j_data = j_report['data']
                columns, segments, dimensions, metrics, period, report_type = _csdmpr(j_report)
                element2check = dimensions[0]
                if verbose:
                    print('element to check for unlimited data : '+str(element2check))
                df = _data_retrieve(j_data,start=True)
                df.columns = columns#rename the columns
                rows = len(df[element2check].unique())
                df_all = df_all.append(df)
                if verbose:
                    print('number of rows : '+str(rows))
                start_with += 50000
            _filename = __newfilename()
            del statement['reportDescription']['elements'][0]['startingWith']##remove the element that has been created during loop
            del statement['reportDescription']['elements'][0]['top'] ##remove the element that has been created during loop
            if export:
                df_all.to_csv(_new_path.as_posix()+'/'+_filename+'.csv',index=False)
                if verbose:
                    print('File has been created in this folder: '+_new_path.as_posix())
            if return_data:
                return df_all

def retrieveReport(report_id, request_type='json',export=True,return_data=True,verbose=False):
    """
    This function takes 1 required arguments and 4 optionnals.
    It returns a file and / or a dataframe with the data requested. Cannot do recursive requests. 
        report_id : REQUIRED : The report id that you want to retrieve data from
        request_type : OPTIONNAL : The type of request you made to Adobe. It has been written in your save_report_id.txt file.
        export : OPTIONNAL : boolean to determine if a csv file has to be created (default : True)
        return_data : OPTIONNAL : boolean to determine if a dataframe is returned (default : True)
        verbose : OPTIONNAL : print comments if you want to follow the status of the request (default : False)
    """
    report_id = int(report_id)
    _token = _getToken(_apliId,_secretApli)#retrieve the token and reportSuite
    if verbose: 
        print('Token is retrieved')
    if request_type=='json':
        _raw_data = _reportGet(_token,report_id,request_type).json()
        if verbose:
            print('Data retrieved')
        j_report = _data_preparation(_raw_data,request_type)
        j_data = j_report['data']
        columns, segments, dimensions, metrics, period, report_type = _csdmpr(j_report)
        df = _data_retrieve(j_data,start=True) ##Start clean previous call data
        df.columns = columns#rename the columns
        _filename = __newfilename()
        if export:
            df.to_csv(_new_path.as_posix()+'/'+_filename+'.csv',index=False)
            if verbose:
                print('File has been created in this folder: '+_new_path.as_posix())
        if return_data:
            return df
    elif request_type=='csv':
        _raw_data = _reportGet(_token,report_id,request_type)
        df = _data_preparation(_raw_data,request_type)
        _filename = __newfilename()
        if export:
            df.to_csv(_new_path.as_posix()+'/'+_filename+'.csv',index=False)
            if verbose:
                print('File has been created in this folder: '+_new_path.as_posix())
        if return_data:
            return df