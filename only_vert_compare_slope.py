
import os
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from datetime import datetime
from statsmodels.tsa.stattools import acf



directory = './'

def cal_95CI(years, columns, labels, y_lim):
   fig, axes = plt.subplots(figsize=(10, 6))
   colors = ['black', 'purple']  # Add more colors if needed
   shift=0
   my_year = []
   saved_ang = 0 
   for i_col, (year, ts, label) in enumerate(zip(years, columns, labels)):

    N=len(ts)             # Total points
    T=year[N-1]-year[0]   # Total year range
    


   
# -----------------------------------------------------------------------------
# Step 1: Linear regresion on the whole time series
#         Eq.1: Li=a+b*ti+Ri, using OLS--Ordinary Least Squares
# -----------------------------------------------------------------------------
    x = sm.add_constant(year)
    model = sm.OLS(ts,x)
    results = model.fit()
    b_L = results.params[1]
   
    # stand error. SEs, Eq. 7
    s=np.sqrt(np.sum(results.resid**2)/results.df_resid)    # Eq.6
    SEs= s/np.sqrt(N)                                       # Eq.7
    SEb=SEs*2*np.sqrt(3.0)/T                                # Eq.8

    Li = results.params[0]+results.params[1]*year
# -----------------------------------------------------------------------------
# Step 2: Calculate the slope (b_NL) of the non-linear component (NLi)
#         The non-linear trend is obtained from LOWESS filter
#         yi=Li+NLi+Si+ri, Eq.9 
# -----------------------------------------------------------------------------
    Ri = ts - Li
    # cal RMS of Ri, for printing on final figure, sub-Fig.2
    RMS_rm_L= math.sqrt(np.square(Ri).mean())
    
    # smooth Ri with LOWESS
    x_tmp = np.array(year)
    y_tmp = np.array(Ri)
    Ri_smooth = sm.nonparametric.lowess(y_tmp, x_tmp, frac= 1.0/2.5, it=2)
    NLi=Ri_smooth[:,1]

    # cal Linear trend of NL(i)
    x = sm.add_constant(x_tmp)
    model = sm.OLS(NLi,x)
    results = model.fit()
    NLi_line=results.params[0]+results.params[1]*year
    b_NL = results.params[1]
# -----------------------------------------------------------------------------
# Step 3: Setup the seasonal model (Si), calculate b_S
#         The data gap needs to be filled 
# -----------------------------------------------------------------------------
    res_L_NL = Ri-NLi
    # cal RMS of res_L_NL, for printing on final figure, sub-Fig.3
    RMS_rm_LNL= math.sqrt(np.square(res_L_NL).mean())
    
    def decimalYear2Date(dyear):
        year = int(dyear)
        yearFraction = float(dyear) - year
        doy = int(round(yearFraction * 365.25-0.5)) + 1
        ydoy = str(year) + "-" + str(doy)
        r = datetime.strptime(ydoy, "%Y-%j").strftime("%Y-%m-%d")
        return r  

    # Preparing for filling gaps
    # use a loop converting original decimal year to date, e.g., 2021-05-25
    ymdR = []
    for line  in year:
        ymdi = decimalYear2Date(line)
        ymdR.append(ymdi)
    
    # convert row to column
    ymd = pd.DataFrame (ymdR)

    # combine column ymd and res_L_NL
    ymd_and_res = pd.concat([ymd, res_L_NL], axis=1)

    # add column name to the DataFrame
    ymd_and_res.columns = ['Date', 'RES']
    df = ymd_and_res

    # Convert column "Date" to DateTime format
    df.Date = pd.to_datetime(df.Date, format='%Y-%m-%d')
    df = df.set_index('Date')

    # Firstly, fill the gap in YMD seris and give NaN for RES series
    df_con_nan = df.resample('1D').mean()      # 1D---1day
    y_con_nan=df_con_nan['RES']    # used for output
    y_con_nan=y_con_nan.reset_index()

    # Secondly, fill the NaN in RES column as a number, use assign, or random, prefer random
    # df_con = df_con_nan['RES'].interpolate(method='linear')  # This works
    # df_con = df_con_nan.assign(InterpolateTime=df_con_nan.RES.interpolate(method='time'))   # This also works

    def fill_with_random(df2, column):
        '''Fill df2's column  with random data based on non-NaN data from the same column'''
        df = df2.copy()
        df[column] = df[column].apply(lambda x: np.random.choice(df[column].dropna().values) if np.isnan(x) else x)
        return df
    
    df = fill_with_random(df_con_nan,'RES')

    # Calculate Seasonal coefficients, see Eq.10
    # df include "2012-12-14   -0.087698". The first col is index. 
    df = df.reset_index()
    df = pd.DataFrame(df)
    x_con = df.iloc[:,0]
    y_con = df.iloc[:,1]

    # Build continuous decimal year time series, xt
    x0 = year[0]
    npts = len(y_con) 
    xt=np.zeros(npts)
    for i in range(npts):
        xt[i] = x0 + i*1/365.25
      
    # The function for calculating Seasonal Model coeffients
    def seasonal_model(x,y):
        twopi = 2.0 * np.pi
        x0=x[0]
        x=x-x0+1.0/365.25
       
        # For this method, just use integer Years of data, e.g., 10 years not 10.3
        npoint_in=len(y)
        ny = int(np.floor(npoint_in/365.25))
        npts = int(ny*365.25)   # used points of ny years
        dy = 1.0/365.25
        rn = 1.0/npts
    
        # mp--maximum ip should be 3 times ny or larger
        mp = int(3*ny)
        c=np.zeros(mp)
        d=np.zeros(mp)
    
        for ip in range(mp):
            c[ip]=0
            d[ip]=0
            for i in range(npts):
                c[ip]=c[ip]+2.0*rn*y[i]*np.cos(twopi*(ip-1)*i*rn)
                d[ip]=d[ip]+2.0*rn*y[i]*np.sin(twopi*(ip-1)*i*rn)
           
        c0=c[1]
        c1=c[ny+1]
        d1=d[ny+1]
        c2=c[2*ny+1]
        d2=d[2*ny+1]
        Si=c0+c1*np.cos(1.0*twopi*x)+d1*np.sin(1.0*twopi*x)+c2*np.cos(2.0*twopi*x)+d2*np.sin(2.0*twopi*x) 

        return Si, c0, c1, d1, c2, d2

    result_seasonM= seasonal_model(xt,y_con)
    Si=result_seasonM[0]

    # output c0,c1,d1,c2,d2 for plotting on the final figure
    c0=result_seasonM[1]
    c1=result_seasonM[2]
    d1=result_seasonM[3]
    c2=result_seasonM[4]
    d2=result_seasonM[5]

    # calculate the linear trend of Si
    x = sm.add_constant(xt)
    model = sm.OLS(Si,x)
    results = model.fit()
    Si_Line=results.params[0]+results.params[1]*xt
    b_S = results.params[1]
    
    # cal annual and hal-annual amplitudes,P2T--Peak to trough amplitude 
    P1=math.sqrt(np.square(c1)+np.square(d1))
    P2=math.sqrt(np.square(c2)+np.square(d2))
    P2T=math.sqrt(np.square(P1)+np.square(P2))*2.0

    ri = y_con - Si
    
    # cal RMS of ri
    RMS_ri= math.sqrt(np.square(ri).mean())

    # get ACF and PACF, cal PACF is very slow. Doesnot need PACF!
    # Plot ACF
    if len(ri) < 1095:
     maxlag = len(ri)-1
    else:
     maxlag=1095 


    data = np.array(ri)
    lag_acf = acf(data, nlags=maxlag,fft=True)


    sum = 0
    i=0
    for acfi in lag_acf:
     if acfi >= 0:
      i=i+1
      sum = sum + acfi
     else:
      # print("Found lag-M at", i)
      break

    tao = 1 + 2*sum            # Eq.14
    Neff = int(N/tao)          # Eq.13
    SEbc=np.sqrt(tao)*SEb      # Eq.15, same as SEbc=np.sqrt(N/Neff)*SEb
    

    b95CI = 1.96 * SEbc + abs(b_NL) + abs(b_S)     #Eq.16

    sizes = np.random.rand(N) * 50  # Bubble sizes
    #plt.scatter(year, ts, color=colors[i_col], label=label, s=sizes, alpha=1, edgecolors='w')
    axes.plot(year, ts,'.', color=colors[i_col], label=label)

    #axes.plot(year,Li, 'r.',markersize=1)

    axes.spines['top'].set_visible(False)    # Remove top border
    axes.spines['right'].set_visible(False)  # Remove right border
    
    str_bL=str(round(b_L*10,2))

    str_b95CI=str(round(b95CI*10,2))


    dy=Li.iloc[-1]-Li.iloc[452]
    dx=year.iloc[-1]-year.iloc[452]


    ang_sag = np.rad2deg(np.arctan2(dy, dx))
 
        # Find the middle row
    middle_idx = len(year) // 2  # Integer division to get middle index
        # Get the middle row values for positioning
    x_middle = year.iloc[middle_idx]  # Middle value of 'year' column
    y_middle = Li.iloc[middle_idx]    # Middle value of 'Li' column
    y_median = Li.median()


    if saved_ang == 0:  # Use the correct comparison
        y_offset = y_middle + y_median*0.80 
        print("is zero") 

    else:
        y_offset = y_middle - y_median*0.80  
        print("not zero")

    
    print(y_middle)
    print(y_median)
    print(y_offset)
    
    saved_ang=5
 
    axes.text(x_middle, y_offset, 'Vel = '+ str_bL + '$\pm$' + str_b95CI+' mm/year',alpha=1,transform_rotates_text=True,rotation=ang_sag,rotation_mode='anchor', color=colors[i_col])





    # axes.text(0.1, 0.07, '$SE_b$= '+ str_SEb + ' mm/year', ha='center', va='center', transform=axes.transAxes)
    # axes.text(0.3, 0.07, '$SE_{bc}$= '+ str_SEbc + ' mm/year', ha='center', va='center', transform=axes.transAxes)
    # axes.text(0.7, 0.07, 'Calculated vs. Projected 95%CI: '+ str_b95CI + ' vs. '+ str_b95CI_mod + ' mm/year', ha='center', va='center', transform=axes.transAxes)

   axes.set_ylim(y_lim[0]-5, y_lim[1]+5)
   axes.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

   axes.legend()
   plt.show()



all_years = []
all_columns = []
labels = []

for fin in os.listdir(directory):
    if fin.endswith(".col"):
        ts_enu = pd.read_csv(fin, header=0, delim_whitespace=True)
        
        year = ts_enu.iloc[:, 0]  # decimal year
        column = ts_enu.iloc[:, 3]  # Fourth column
        
        all_years.append(year)
        all_columns.append(column)
        first_four = fin[:4]
        labels.append(first_four)  # Use filename as label
    
all_years_combined = pd.concat(all_years)
all_columns_combined = pd.concat(all_columns)

y_lim = [all_columns_combined.min(), all_columns_combined.max()]

cal_95CI(all_years, all_columns, labels, y_lim)