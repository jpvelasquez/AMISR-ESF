import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
#from datetime import datetime
from datetime import timezone
from dateutil.tz import *
import matplotlib.dates as mdates
from datetime import timedelta
import os
from model_utils import *
import matplotlib.dates as dates
import matplotlib as mpl
from scipy import stats


def GetTimeAndArray(directory,filename, PlotFlag):
    file_hf5 = directory + os.sep + filename
    hf = h5py.File(file_hf5, 'r')
    #arr = np.array(hf['Data/data_snr']['channel00'])#['day'])
    arr = np.array(hf['Data/data_pow']['channel00'])#['day'])

    timestamps = np.array(hf['Data/']['utctime']) # hora local
    time_zone = np.array(hf['Metadata/']['timeZone'])
    data_type = np.array(hf['Metadata/']['type'])
#    num_profiles = np.array(hf['Metadata/']['nProfiles'])
    height_list = np.array(hf['Metadata/']['heightList'])

    prev_stamps = []
    datetime_objects = []
    for ts in timestamps:
        if ts in prev_stamps:
            print('Same timestap')
        else:
            date_time_obj = datetime.datetime.fromtimestamp(ts)
            datetime_objects.append(date_time_obj)
    index = pd.DatetimeIndex(datetime_objects) #- timedelta(hours=5)
    datetime_objects = np.array(datetime_objects,dtype='datetime64[ns]')
    #print("data_spc array shape: ", arr.shape)
    arr_total = arr#np.nansum(arr, axis=1)
    #'''
    if PlotFlag==True:
        fig, ax = plt.subplots(figsize=(12, 6))
        clrs= ax.pcolormesh(mdates.date2num(datetime_objects),height_list, 10*np.log10(arr_total.T),cmap='jet')#'RdBu_r')#'jet')
        #print("Punto de control 2")
        ax.xaxis_date()
        date_format = mdates.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(date_format)
        ax.set_xlabel("Hora Local (h)", fontsize=16)
        ax.set_ylabel("Rango (km)", fontsize=17)
        #ax.set_xlim(-10,750)
        fig.autofmt_xdate()
        box=ax.get_position()
        cbarax=fig.add_axes([box.x0+box.width+0.01, box.y0, 0.025, box.height])
        cb=plt.colorbar(clrs,cax=cbarax)
        cb.set_label(r'$10 \times log_{10}SNR (dB)$', fontsize=17)
        plt.show()
#cb.mappable.set_clim(120,140)
    #'''
    return datetime_objects, height_list, arr_total

def GetRTI_AMISR(year, doy):
    channel = 0
    sub_dir1 = 'd%d%d' % (year, doy)
    sub_dir2 = 'd%d%d' % (year, doy+1)
    directory1 =  'Data/Agosto/ESF%d%d' % (year, doy) + os.sep + sub_dir1
    directory2 =  'Data/Agosto/ESF%d%d' % (year, doy) + os.sep + sub_dir2

#D2021218004
    filename1 = 'D%d%d0%02d.hdf5' % (year,doy,channel)#'D2021218000.hdf5'
    filename2 = 'D%d%d0%02d.hdf5' % (year,doy+1,channel)#'D2021218000.hdf5'
#filename1 = 'D%d%d%d.hdf5' % (year,doy,channel)#'D2021218000.hdf5'
#filename2 = 'D%d%d%d.hdf5' % (year,doy+1,channel)#'D2021218000.hdf5'
    #month=9
    d = datetime.datetime.strptime('{} {}'.format(doy, year),'%j %Y')
    month = d.month
    str_month = GetMonth(month)
    current_month = '%s-%d' % (str_month, year)
    directory = 'Data-%s/' % current_month
    plots_boletin = '/home/juanpablo/Desktop-JRO/Plots-Boletines/%02d/%s' % (year,str_month)
    str_format = 'png'

    #file_hf5_1 = directory1 + os.sep + filename1
    #hf1 = h5py.File(file_hf5_1, 'r')
#with h5py.File(file_hf5_1, 'r') as f:
    #g = f.visit(print)
    ###################################################################
    # Arreglo del primer día
    ###################################################################

    arr_dt_1 = np.array([],dtype='datetime64[ns]')
    arr_h_1 = np.array([])
    temp = np.array([])
    lista_arr_total_1 = []
    PlotFlag=False
    for filename1 in sorted(os.listdir(directory1)):
        if filename1.endswith(".hdf5"):
            #print('========================================================')
            #print(filename1)
            datetime_objects, height_list, arr_total = GetTimeAndArray(directory1,filename1, PlotFlag)
            #print("Datetime, height_list, arr_total shapes: ", datetime_objects.shape, height_list.shape, arr_total.shape)
            arr_dt_1 = np.concatenate([arr_dt_1, datetime_objects])
            arr_h_1 = np.concatenate([arr_h_1, height_list])
            #print(datetime_objects[0],datetime_objects[-1])
            #if (list(temp)==list(height_list)):
            #    print("Mismo perfil de alturas")
            temp = height_list
            lista_arr_total_1.append(arr_total)
    array_parte1 = np.vstack(lista_arr_total_1)
    #print(arr_dt_1.shape, arr_h_1.shape, array_parte1.shape)
    ###################################################################
    # Arreglo del segundo día
    ###################################################################
    arr_dt_2 = np.array([],dtype='datetime64[ns]')
    arr_h_2 = np.array([])
    lista_arr_total_2 = []
    temp = np.array([])
    PlotFlag=False
    for filename2 in sorted(os.listdir(directory2)):
        if filename2.endswith(".hdf5"):
            #print('========================================================')
            #print(filename2)
            datetime_objects, height_list, arr_total = GetTimeAndArray(directory2,filename2, PlotFlag)
            arr_dt_2 = np.concatenate([arr_dt_2, datetime_objects])
            arr_h_2 = np.concatenate([arr_h_2, height_list])
            #if (list(temp)==list(height_list)):
            #    print("Mismo perfil de alturas")
            temp = height_list
            lista_arr_total_2.append(arr_total)
    array_parte2 = np.vstack(lista_arr_total_2)
    #print(arr_dt_2.shape, arr_h_2.shape, array_parte2.shape)
    dt_final = np.array(np.r_[arr_dt_1, arr_dt_2],dtype='datetime64[ns]')
    array_final = np.vstack((array_parte1, array_parte2))

    return dt_final, height_list, 10*np.log10(array_final)

def GetRTI_JULIA(year,doy):
    directory = 'Data-JULIA'
    d = datetime.datetime.strptime('{} {}'.format(doy, year),'%j %Y')
    month = d.month
    day = d.day
    filename = 'jul%d%02d%02d_esf.001.hdf5' % (year,month,day)
    file_hf5 = directory + os.sep + filename
    hf = h5py.File(file_hf5, 'r')
    #with h5py.File(file_hf5, 'r') as f:
    #    g = f.visit(print)

    rango = hf['Data/Table Layout/']['gdalt']
    snl =  hf['Data/Table Layout/']['snl']
    snl2 = hf['Data/Array Layout/2D Parameters/snl']
    vipe1 = hf['Data/Array Layout/2D Parameters/vipe1']
    vipn1 = hf['Data/Array Layout/2D Parameters/vipn1']
    timestamps = hf['Data/Array Layout/']['timestamps']
    rango = getattr(rango, "tolist", lambda: rango)()
    ###########################################################
    ran_max = max(rango)
    ran_min = min(rango)
    max_index = rango.index(ran_max)
    min_index = rango.index(ran_min)
    range_diff = np.diff(rango)
    #delta_range = range_diff[-1] #valor constante para todo el arreglo
    mode = stats.mode(range_diff)
    print('delta_range', mode[0])
    delta_range = mode[0]
    MinRange, MaxRange = np.min(rango), ran_max#np.max(rango)
    DataMatrixRows = int((MaxRange-MinRange)/delta_range)
    range_array = np.linspace(MinRange, MaxRange, DataMatrixRows+1)
    DataMatrix = np.ones((DataMatrixRows+1, snl2.shape[0]))*np.nan
    RowInMatrix = np.array((rango-MinRange)/delta_range, dtype=int)
    range_array = np.linspace(MinRange, MaxRange, DataMatrixRows+1)
    RangeMatrix = np.ones((DataMatrixRows+1, snl2.shape[0]))*np.nan
    prev_stamps = []
#################################
    datetime_objects = []
    for ts in timestamps:
        if ts in prev_stamps:
            print('Same timestap')
        else:
            date_time_obj = datetime.datetime.fromtimestamp(ts)
            datetime_objects.append(date_time_obj)
    index = pd.DatetimeIndex(datetime_objects) # timedelta(hours=5)
#################################
    string_date = index[0].strftime('%B %d, %Y, %r')
    mes = GetMonth(month)
    col = 0 #counter for current columns
    PastRow = 0 #saving past row index
    #print("range(rango.size) ",range(rango.size))
    for k in range(len(rango)):
        row = RowInMatrix[k]
    # Putting snr in corresponding matrix element
        DataMatrix[row,col] = snl[k]
        if row<PastRow:
            col += 1
        PastRow = row
    data = DataMatrix#[::-1]

    return  np.array(datetime_objects,dtype='datetime64[ns]'), range_array, data
