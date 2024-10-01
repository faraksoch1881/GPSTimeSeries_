
import os
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from datetime import datetime
from statsmodels.tsa.stattools import acf



directory = './'



def cal_95CI(year, ts, Dir,ax,df_name):
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

    # cal the predicted 95%CI (mm/year) based on the Formulas Eq.17 and Eq.18
    if Dir == 'UD(cm)':
      b95CI_mod = 5.2/math.pow(T,1.25)

    else:
     b95CI_mod = 1.8/T 


    ax.plot(year, ts, 'k.')
    ax.plot(year,Li, 'r.')
    


    # fig1.plot(year, ts, 'k.')
    # fig1.plot(year,Li, 'r.')

    # fig2.plot(year, Ri,'.',c='0.5')
    # fig2.plot(year, NLi, 'r.')

    

    ax.spines['top'].set_visible(False)    # Remove top border
    ax.spines['right'].set_visible(False)  # Remove right border
    ax.spines['bottom'].set_visible(False)
    # if mynum != len(columns) - 1:  # For all subplots except the last one
    #  ax.tick_params(axis='x', which='both', bottom=False, labelbottom=False)  # Remove x-axis and labels

    ax.set_ylim(bottom=min(ts)*1.2, top=max(ts)*1.2)
    str_bL=str(round(b_L*10,2))
    str_bNL=str(round(b_NL*10,2))
    str_bS=str(round(b_S*10,2))
    str_b95CI=str(round(b95CI*10,2))
    str_b95CI_mod=str(round(b95CI_mod,2))   # mm/year
    str_c0=str(round(c0,2))
    str_SEb=str(round(SEb*10,2))
    str_SEbc=str(round(SEbc*10,2))
    
    str_RMS_rm_L=str(round(RMS_rm_L*10,1))
    str_RMS_rm_LNL=str(round(RMS_rm_LNL*10,1))
    str_RMS_ri=str(round(RMS_ri*10,1))
    
    str_P1=str(round(P1*10,1))
    str_P2=str(round(P2*10,1))
    str_P2T=str(round(P2T*10,1))

    if c1 >= 0:
     str_c1='+'+str(round(c1,2))
    else:
     str_c1=str(round(c1,2))
    if d1 >= 0:
     str_d1='+'+str(round(d1,2))
    else:
     str_d1=str(round(d1,2))
    if c2 >= 0:
     str_c2='+'+str(round(c2,2))
    else:
     str_c2=str(round(c2,2))
    if d2 >= 0:
     str_d2='+'+str(round(d2,2))
    else:
     str_d2=str(round(d2,2))

    ax.text(0.2,0.2, str_bL + '$\pm$' + str_b95CI+' mm/year', ha='center', va='center', transform=ax.transAxes,alpha=1,fontsize=8,backgroundcolor='1')
    ax.set_ylim(bottom=min(ts)*1.2, top=max(ts)*1.2)
  

df = []
df_name=[]
for fin in os.listdir(directory):
    if fin.endswith(".col"):
       ts_enu = []
       ts_enu = pd.read_csv (fin, header=0, delim_whitespace=True)
       df.append(ts_enu)
       df_name.append(fin)
    else:
       pass


def plot_combined_dataframes(dfs, col_name,df_name):
    fig, axes = plt.subplots(3, 1, figsize=(10, 6))
    for i, ax in enumerate(axes):
        if i < len(dfs):
            print('sagar')
            if col_name == 'NS(cm)':
             cal_95CI(dfs[i].iloc[:, 0], dfs[i].iloc[:, 1], col_name, ax, df_name[i])
            elif col_name == 'EW(cm)':
             cal_95CI(dfs[i].iloc[:, 0], dfs[i].iloc[:, 2], col_name, ax, df_name[i])
            elif col_name == 'UD(cm)':
             cal_95CI(dfs[i].iloc[:, 0], dfs[i].iloc[:, 3], col_name, ax, df_name[i])

            ax.set_title(df_name[i])
            ax.set_xlabel('Year')
            ax.set_ylabel(col_name)
        else:
            fig.delaxes(ax)  # Remove extra subplots if there are fewer than 3 dataframes

    plt.tight_layout()
    plt.show()
 

user_input = int(input("Enter Displacement Direction \n 1. NS(cm) \n 2. EW(cm) \n 3. UD(cm) \n "))

if user_input == 1:
    col_name = 'NS(cm)'
elif user_input == 2:
    col_name = 'EW(cm)'
elif user_input == 3:
    col_name = 'UD(cm)'
else:
    print("Invalid input. Please enter 1, 2, or 3.")

plot_combined_dataframes(df, col_name,df_name)

