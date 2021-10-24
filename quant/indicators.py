"""
Indicators as shown by Peter Bakker at:
https://www.quantopian.com/posts/technical-analysis-indicators-without-talib-code
"""

"""
25-Mar-2018: Fixed syntax to support the newest version of Pandas. Warnings should no longer appear.
             Fixed some bugs regarding min_periods and NaN.

			 If you find any bugs, please report to github.com/palmbook
"""

# Import Built-Ins
import logging
# Import Third-Party
import pandas as pd
import numpy as np
from pandas import DataFrame
from numpy import NaN as npNaN
import pandas_ta as ta

# Import Homebrew

# Init Logging Facilities
log = logging.getLogger(__name__)


def moving_average(df, n):
    """Calculate the moving average for the given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    MA = pd.Series(df['close'].rolling(n, min_periods=n).mean(), name='ma')
    df = df.join(MA)
    return df


def exponential_moving_average(df, n):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    EMA = pd.Series(df['close'].ewm(span=n, min_periods=n).mean(), name='ema')
    df = df.join(EMA)
    return df

def dma(df, n_fast=10, n_slow=50, m=10):
    MAfast = pd.Series(df['close'].rolling(n_fast, min_periods=1).mean(), name='MA_' + str(n_fast))
    MAslow = pd.Series(df['close'].rolling(n_slow, min_periods=1).mean(), name='MA_' + str(n_slow))
    DMA = pd.Series(MAfast - MAslow, name='dma')
    AMA = pd.Series(DMA.ewm(span=m, min_periods=3).mean(), name='ama')
    df = df.join(DMA)
    df = df.join(AMA)
    return df

def momentum(df, n):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    M = pd.Series(df['close'].diff(n), name='Momentum_' + str(n))
    df = df.join(M)
    return df

def rate_of_change(df, n=12):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    M = df['close'].diff(n - 1)
    N = df['close'].shift(n - 1)
    ROC = pd.Series((M *100 / N).ewm(span=3, min_periods=1).mean(), name='roc')
    #ROC = pd.Series(M / N, name = 'roc')
    ROCEMA = pd.Series(ROC.ewm(span=6, min_periods=3).mean(), name='roc_ema')
    ROCMA = pd.Series(ROC.rolling(6).mean(), name='roc_ma')
    ROCH = pd.Series(ROC - ROCEMA, name='roch')
    df = df.join(ROC)
    df = df.join(ROCEMA)
    df = df.join(ROCMA)
    df = df.join(ROCH)
    return df


def bollinger_bands(df, n=20):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    MA = pd.Series(df['close'].rolling(n, min_periods=10).mean())
    MSD = pd.Series(df['close'].rolling(n, min_periods=10).std())
    b1 = 4 * MSD / MA
    B1 = pd.Series(b1, name='BollingerB_' + str(n))
    df = df.join(B1)
    b2 = (df['close'] - MA + 2 * MSD) / (4 * MSD)
    B2 = pd.Series(b2, name='Bollinger%b_' + str(n))
    df = df.join(B2)
    return df


def ppsr(df):
    """Calculate Pivot Points, Supports and Resistances for given data

    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    PP = pd.Series((df['High'] + df['Low'] + df['Close']) / 3)
    R1 = pd.Series(2 * PP - df['Low'])
    S1 = pd.Series(2 * PP - df['High'])
    R2 = pd.Series(PP + df['High'] - df['Low'])
    S2 = pd.Series(PP - df['High'] + df['Low'])
    R3 = pd.Series(df['High'] + 2 * (PP - df['Low']))
    S3 = pd.Series(df['Low'] - 2 * (df['High'] - PP))
    psr = {'PP': PP, 'R1': R1, 'S1': S1, 'R2': R2, 'S2': S2, 'R3': R3, 'S3': S3}
    PSR = pd.DataFrame(psr)
    df = df.join(PSR)
    return df

def StochRSI(df, m=30,  p=100):
    close = df['close']
    close = pd.Series(df['close'])
    #RSI = talib.RSI(np.array(close), timeperiod=m)
    RSI = talib.RSI(close, timeperiod=m)
    LLV= RSI .rolling(window=m).min()
    HHV= RSI .rolling(window=m).max()
    stochRSI = (RSI  - LLV) / (HHV - LLV) * 100
    fastk = talib.MA(np.array(stochRSI), p)
    fastd = talib.MA(np.array(fastk), p)

    df = df.join(pd.Series(fastk, name='fastk').fillna(0))
    df = df.join(pd.Series(fastd, name='fastd').fillna(0))
    return df

def stochastic_oscillator_k(df):
    """Calculate stochastic oscillator %K for given data.

    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    SOk = pd.Series((df['Close'] - df['Low']) / (df['High'] - df['Low']), name='SO%k')
    df = df.join(SOk)
    return df


def stochastic_oscillator_d(df, n):
    """Calculate stochastic oscillator %D for given data.
    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    SOk = pd.Series((df['Close'] - df['Low']) / (df['High'] - df['Low']), name='SO%k')
    SOd = pd.Series(SOk.ewm(span=n, min_periods=n).mean(), name='SO%d_' + str(n))
    df = df.join(SOd)
    return df


def trix(df, n=12):
    """Calculate TRIX for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    tr = df['close'].ewm(span=n, min_periods=n/2).mean()
    #Matrix = trix.ewm(span=n, min_periods=n/2).mean()
    Trix = pd.Series((tr - tr.diff())/tr.diff()*100, name='trix')
    Trixs = pd.Series(Trix.rolling(9).mean(), name='trixs')
    df = df.join(Trix)
    df = df.join(Trixs)
    return df


def average_directional_movement_index(df, n, n_ADX):
    """Calculate the Average Directional Movement Index for given data.

    :param df: pandas.DataFrame
    :param n:
    :param n_ADX:
    :return: pandas.DataFrame
    """
    i = 0
    UpI = []
    DoI = []
    while i + 1 <= df.index[-1]:
        UpMove = df.loc[i + 1, 'High'] - df.loc[i, 'High']
        DoMove = df.loc[i, 'Low'] - df.loc[i + 1, 'Low']
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i = i + 1
    i = 0
    TR_l = [0]
    while i < df.index[-1]:
        TR = max(df.loc[i + 1, 'High'], df.loc[i, 'Close']) - min(df.loc[i + 1, 'Low'], df.loc[i, 'Close'])
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l)
    ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean())
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean() / ATR)
    NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean() / ATR)
    ADX = pd.Series((abs(PosDI - NegDI) / (PosDI + NegDI)).ewm(span=n_ADX, min_periods=n_ADX).mean(),
                    name='ADX_' + str(n) + '_' + str(n_ADX))
    df = df.join(ADX)
    return df


def mass_index(df):
    """Calculate the Mass Index for given data.

    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    Range = df['High'] - df['Low']
    EX1 = Range.ewm(span=9, min_periods=9).mean()
    EX2 = EX1.ewm(span=9, min_periods=9).mean()
    Mass = EX1 / EX2
    MassI = pd.Series(Mass.rolling(25).sum(), name='Mass Index')
    df = df.join(MassI)
    return df


def vortex_indicator(df, n):
    """Calculate the Vortex Indicator for given data.

    Vortex Indicator described here:
        http://www.vortexindicator.com/VFX_VORTEX.PDF
    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    TR = [0]
    while i < df.index[-1]:
        Range = max(df.loc[i + 1, 'High'], df.loc[i, 'Close']) - min(df.loc[i + 1, 'Low'], df.loc[i, 'Close'])
        TR.append(Range)
        i = i + 1
    i = 0
    VM = [0]
    while i < df.index[-1]:
        Range = abs(df.loc[i + 1, 'High'] - df.loc[i, 'Low']) - abs(df.loc[i + 1, 'Low'] - df.loc[i, 'High'])
        VM.append(Range)
        i = i + 1
    VI = pd.Series(pd.Series(VM).rolling(n).sum() / pd.Series(TR).rolling(n).sum(), name='Vortex_' + str(n))
    df = df.join(VI)
    return df


def kst_oscillator(df, r1, r2, r3, r4, n1, n2, n3, n4):
    """Calculate KST Oscillator for given data.

    :param df: pandas.DataFrame
    :param r1:
    :param r2:
    :param r3:
    :param r4:
    :param n1:
    :param n2:
    :param n3:
    :param n4:
    :return: pandas.DataFrame
    """
    M = df['Close'].diff(r1 - 1)
    N = df['Close'].shift(r1 - 1)
    ROC1 = M / N
    M = df['Close'].diff(r2 - 1)
    N = df['Close'].shift(r2 - 1)
    ROC2 = M / N
    M = df['Close'].diff(r3 - 1)
    N = df['Close'].shift(r3 - 1)
    ROC3 = M / N
    M = df['Close'].diff(r4 - 1)
    N = df['Close'].shift(r4 - 1)
    ROC4 = M / N
    KST = pd.Series(
        ROC1.rolling(n1).sum() + ROC2.rolling(n2).sum() * 2 + ROC3.rolling(n3).sum() * 3 + ROC4.rolling(n4).sum() * 4,
        name='KST_' + str(r1) + '_' + str(r2) + '_' + str(r3) + '_' + str(r4) + '_' + str(n1) + '_' + str(
            n2) + '_' + str(n3) + '_' + str(n4))
    df = df.join(KST)
    return df


def relative_strength_index(df, n=6):
    """Calculate Relative Strength Index(RSI) for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    UpI = [0]
    DoI = [0]
    High = [70]
    Low = [30]
    df = df.reset_index()
    while i + 1 <= df.index[-1]:
        UpMove = df.loc[i + 1, 'high'] - df.loc[i, 'high']
        DoMove = df.loc[i, 'low'] - df.loc[i + 1, 'low']
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        High.append(70)
        Low.append(30)
        i = i + 1
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI6 = pd.Series(UpI.ewm(span=6, min_periods=6).mean())
    NegDI6 = pd.Series(DoI.ewm(span=6, min_periods=6).mean())
    RSI6 = pd.Series(PosDI6 * 100 / (PosDI6 + NegDI6), name='rsi_' + str(6))
    PosDI12 = pd.Series(UpI.ewm(span=n, min_periods=n).mean())
    NegDI12 = pd.Series(DoI.ewm(span=n, min_periods=n).mean())
    RSI12 = pd.Series(PosDI12 * 100 / (PosDI12 + NegDI12), name='rsi')
    df = df.join(RSI6)
    df = df.join(RSI12)
    df = df.join(pd.Series(High, name='rsi_h'))
    df = df.join(pd.Series(Low, name='rsi_l'))
    return df


def true_strength_index(df, r, s):
    """Calculate True Strength Index (TSI) for given data.

    :param df: pandas.DataFrame
    :param r:
    :param s:
    :return: pandas.DataFrame
    """
    M = pd.Series(df['Close'].diff(1))
    aM = abs(M)
    EMA1 = pd.Series(M.ewm(span=r, min_periods=r).mean())
    aEMA1 = pd.Series(aM.ewm(span=r, min_periods=r).mean())
    EMA2 = pd.Series(EMA1.ewm(span=s, min_periods=s).mean())
    aEMA2 = pd.Series(aEMA1.ewm(span=s, min_periods=s).mean())
    TSI = pd.Series(EMA2 / aEMA2, name='TSI_' + str(r) + '_' + str(s))
    df = df.join(TSI)
    return df


def accumulation_distribution(df, n):
    """Calculate Accumulation/Distribution for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    ad = (2 * df['Close'] - df['High'] - df['Low']) / (df['High'] - df['Low']) * df['Volume']
    M = ad.diff(n - 1)
    N = ad.shift(n - 1)
    ROC = M / N
    AD = pd.Series(ROC, name='Acc/Dist_ROC_' + str(n))
    df = df.join(AD)
    return df


def chaikin_oscillator(df):
    """Calculate Chaikin Oscillator for given data.

    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    ad = (2 * df['Close'] - df['High'] - df['Low']) / (df['High'] - df['Low']) * df['Volume']
    Chaikin = pd.Series(ad.ewm(span=3, min_periods=3).mean() - ad.ewm(span=10, min_periods=10).mean(), name='Chaikin')
    df = df.join(Chaikin)
    return df

def money_flow_index(df, n):
    """Calculate Money Flow Index and Ratio for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    PP = (df['high'] + df['low'] + df['close']) / 3
    TotMF = PP * df['volume']
    i = 0
    PMF = [0]
    NMF = [0]
    while i < df.index[-1]:
        if TotMF[i + 1] > TotMF[i]:
            PMF.append(TotMF[i + 1])
            NMF.append(0)
        else:
            NMF.append(TotMF[i + 1])
            PMF.append(0)
        i = i + 1


    PMF = pd.Series(PMF)
    NMF = pd.Series(NMF)

    MFR = pd.Series(PMF.rolling(n, min_periods=n).sum() / NMF.rolling(n, min_periods=n).sum())

    MFI = pd.Series(100 - (100/(1+MFR)), name='mfi')
    #MFI = pd.Series(MFR.rolling(n, min_periods=n).mean(), name='mfi')
    df = df.join(MFI)
    return df


def money_flow_index1(df, n):
    """Calculate Money Flow Index and Ratio for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    PP = (df['high'] + df['low'] + df['close']) / 3
    i = 0
    PMF = [0]
    NMF = [0]
    while i < df.index[-1]:
        if PP[i + 1] > PP[i]:
            PMF.append(PP[i + 1] * df.loc[i + 1, 'volume'])
            NMF.append(0)
        else:
            NMF.append(PP[i + 1] * df.loc[i + 1, 'volume'])
            PMF.append(0)
        i = i + 1
    PosMF = pd.Series(PosMF)
    TotMF = PP * df['volume']
    MFR = pd.Series(PosMF.rolling(n, min_periods=n).sum() / TotMF.rolling(n, min_periods=n).sum())
    #MFI = 100 - 100/(1+MFR)
    MFI = pd.Series(MFR, name='mfi')
    #MFI = pd.Series(MFR.rolling(n, min_periods=n).mean(), name='mfi')
    df = df.join(MFI)
    return df


def on_balance_volume(df, n):
    """Calculate On-Balance Volume for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    OBV = [0]
    while i < df.index[-1]:
        if df.loc[i + 1, 'Close'] - df.loc[i, 'Close'] > 0:
            OBV.append(df.loc[i + 1, 'Volume'])
        if df.loc[i + 1, 'Close'] - df.loc[i, 'Close'] == 0:
            OBV.append(0)
        if df.loc[i + 1, 'Close'] - df.loc[i, 'Close'] < 0:
            OBV.append(-df.loc[i + 1, 'Volume'])
        i = i + 1
    OBV = pd.Series(OBV)
    OBV_ma = pd.Series(OBV.rolling(n, min_periods=n).mean(), name='OBV_' + str(n))
    df = df.join(OBV_ma)
    return df


def force_index(df, n):
    """Calculate Force Index for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    F = pd.Series(df['Close'].diff(n) * df['Volume'].diff(n), name='Force_' + str(n))
    df = df.join(F)
    return df


def ease_of_movement(df, n):
    """Calculate Ease of Movement for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    EoM = (df['High'].diff(1) + df['Low'].diff(1)) * (df['High'] - df['Low']) / (2 * df['Volume'])
    Eom_ma = pd.Series(EoM.rolling(n, min_periods=n).mean(), name='EoM_' + str(n))
    df = df.join(Eom_ma)
    return df


def commodity_channel_index(df, m=14):
    """Calculate Commodity Channel Index for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    PP = (df['high'] + df['low'] + df['close']) / 3
    CCI = pd.Series((PP - PP.rolling(m, min_periods=m).mean()) / (PP.rolling(m, min_periods=m).std() * 0.015), name='cci_' + str(m))
    df = df.join(CCI)
    return df


def coppock_curve(df, n):
    """Calculate Coppock Curve for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    M = df['Close'].diff(int(n * 11 / 10) - 1)
    N = df['Close'].shift(int(n * 11 / 10) - 1)
    ROC1 = M / N
    M = df['Close'].diff(int(n * 14 / 10) - 1)
    N = df['Close'].shift(int(n * 14 / 10) - 1)
    ROC2 = M / N
    Copp = pd.Series((ROC1 + ROC2).ewm(span=n, min_periods=n).mean(), name='Copp_' + str(n))
    df = df.join(Copp)
    return df


def keltner_channel(df, n):
    """Calculate Keltner Channel for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    KelChM = pd.Series(((df['High'] + df['Low'] + df['Close']) / 3).rolling(n, min_periods=n).mean(),
                       name='KelChM_' + str(n))
    KelChU = pd.Series(((4 * df['High'] - 2 * df['Low'] + df['Close']) / 3).rolling(n, min_periods=n).mean(),
                       name='KelChU_' + str(n))
    KelChD = pd.Series(((-2 * df['High'] + 4 * df['Low'] + df['Close']) / 3).rolling(n, min_periods=n).mean(),
                       name='KelChD_' + str(n))
    df = df.join(KelChM)
    df = df.join(KelChU)
    df = df.join(KelChD)
    return df


def ultimate_oscillator(df):
    """Calculate Ultimate Oscillator for given data.

    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    i = 0
    TR_l = [0]
    BP_l = [0]
    while i < df.index[-1]:
        TR = max(df.loc[i + 1, 'High'], df.loc[i, 'Close']) - min(df.loc[i + 1, 'Low'], df.loc[i, 'Close'])
        TR_l.append(TR)
        BP = df.loc[i + 1, 'Close'] - min(df.loc[i + 1, 'Low'], df.loc[i, 'Close'])
        BP_l.append(BP)
        i = i + 1
    UltO = pd.Series((4 * pd.Series(BP_l).rolling(7).sum() / pd.Series(TR_l).rolling(7).sum()) + (
            2 * pd.Series(BP_l).rolling(14).sum() / pd.Series(TR_l).rolling(14).sum()) + (
                             pd.Series(BP_l).rolling(28).sum() / pd.Series(TR_l).rolling(28).sum()),
                     name='Ultimate_Osc')
    df = df.join(UltO)
    return df


def donchian_channel(df, n):
    """Calculate donchian channel of given pandas data frame.
    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    dc_l = []
    while i < n - 1:
        dc_l.append(0)
        i += 1

    i = 0
    while i + n - 1 < df.index[-1]:
        dc = max(df['High'].ix[i:i + n - 1]) - min(df['Low'].ix[i:i + n - 1])
        dc_l.append(dc)
        i += 1

    donchian_chan = pd.Series(dc_l, name='Donchian_' + str(n))
    donchian_chan = donchian_chan.shift(n - 1)
    return df.join(donchian_chan)


def standard_deviation(df, n):
    """Calculate Standard Deviation for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    df = df.join(pd.Series(df['Close'].rolling(n, min_periods=n).std(), name='STD_' + str(n)))
    return df

def average_true_range(df, n):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    TR_l = [0]
    while i < df.index[-1]:
        #TR = max(df.loc[i + 1, 'high'], df.loc[i, 'close']) - min(df.loc[i + 1, 'low'], df.loc[i, 'close'])
        TR = max(abs(df.loc[i+1, 'high'] - df.loc[i+1, 'low']), abs(df.loc[i+1, 'high'] - df.loc[i, 'close']), abs(df.loc[i, 'close'] - df.loc[i+1, 'low']))
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l, name='tr_s')
    df = df.join(TR_s)
    df['atr'] = df.ta.rma(close='tr_s', length=n)
    #ATR = pd.Series(TR_s.rma(span=n, min_periods=n).mean(), name='atr')
    #ATR = pd.Series(TR_s.rolling(7, min_periods=1).mean(), name='atr')
    #ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean(), name='atr')
    #ATREMA5 = pd.Series(ATR.ewm(span=5, min_periods=5).mean(), name='atr_ema5')
    #ATREMA10 = pd.Series(ATR.ewm(span=10, min_periods=5).mean(), name='atr_ema10')
    #df = df.join(ATR)
    #df = df.join(ATREMA5)
    #df = df.join(ATREMA10)
    return df

def supertrend(df, length=14, multiplier=4):
    """Indicator: Supertrend"""
    # Validate Arguments
    high = df['high']
    low = df['low']
    close = df['close']
    length = int(length) if length and length > 0 else 14
    multiplier = float(multiplier) if multiplier and multiplier > 0 else 4.

    # Calculate Results
    m = close.size
    dir_, trend = [1] * m, [0] * m
    long, short = [npNaN] * m, [npNaN] * m

    hl2_ = df.ta.hl2()
    atr = df.ta.atr(length=length)
    #tr = df.ta.true_range(df['high'], df['low'], df['close'])
    #atr = df.sma(mamode, tr, length=length)['atr']
    matr = multiplier * atr
    upperband = hl2_ + matr
    lowerband = hl2_ - matr

    for i in range(1, m):
        if close.iloc[i] > upperband.iloc[i - 1]:
            dir_[i] = 1
        elif close.iloc[i] < lowerband.iloc[i - 1]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lowerband.iloc[i] < lowerband.iloc[i - 1]:
                lowerband.iloc[i] = lowerband.iloc[i - 1]
            if dir_[i] < 0 and upperband.iloc[i] > upperband.iloc[i - 1]:
                upperband.iloc[i] = upperband.iloc[i - 1]

        if dir_[i] > 0:
            trend[i] = long[i] = lowerband.iloc[i]
        else:
            trend[i] = short[i] = upperband.iloc[i]


    _props = f"_{length}_{multiplier}"
    new_df = DataFrame({
        "trend": dir_,
        "long": long,
        "short": short,
        "upperband": upperband,
        "lowerband": lowerband,
        "atr": atr,
        "hl2": hl2_
    }, index=close.index)
    return pd.concat([df, new_df], axis=1)


def rsi2(df):
    df['up'] = df['close'].rolling(window=2).apply(lambda x: 0 if (x[-1] - x[0]) < 0 else (x[-1] - x[0]), raw=True)
    df['down'] = df['close'].rolling(window=2).apply(lambda x: -(x[-1] - x[0]) if (x[-1] - x[0]) < 0 else 0, raw=True)
    df['rma_up'] = df.ta.rma(close='up', length=2)
    df['rma_down'] = df.ta.rma(close='down', length=2)
    df.loc[(df['rma_down'] == 0), 'rsi2'] = 100
    df.loc[(df['rma_up'] == 0), 'rsi2'] = 0
    df.loc[(df['rma_up'] != 0)|(df['rma_down'] != 0), 'rsi2'] = 100 - (100/(1+(df['rma_up']/df['rma_down'])))
    return df

def rsi_rma(df, length=None, close=None):
    """Indicator: Relative Strength Index (RSI)"""

    # Calculate Result
    negative = df[close].diff(1)
    positive = negative.copy()

    positive[positive < 0] = 0  # Make negatives 0 for the postive series
    negative[negative > 0] = 0  # Make postives 0 for the negative series

    df['positive'] = positive
    df['negative'] = negative

    alpha = (1.0 / length)
    df['positive_avg'] = df.ta.rma(length=length, close='positive')
    df['negative_avg'] = df.ta.rma(length=length, close='negative').abs()

    rs = df['positive_avg'] / df['negative_avg']

    rsi = 100 - 100 / (1+rs)
    #positive_avg = positive.ewm(alpha=alpha, min_periods=length).mean()
    #negative_avg = negative.ewm(alpha=alpha, min_periods=length).mean().abs()

    #rsi = 100 * df['positive_avg'] / (df['positive_avg'] + df['negative_avg'])

    # Name and Categorize it
    rsi.name = f"RSI_{length}"
    rsi.category = 'momentum'

    return rsi

def cci(df, length=14):
    mean_typical_price = df.ta.sma(length=length)
    mad_typical_price = df.ta.mad(length=length)

    cci = df['close'] - mean_typical_price
    cci /= 0.015 * mad_typical_price
    return cci

def stoch(df, m=14,  n=5):
    lowest_low   =  df['low'].rolling(m).min()
    highest_high = df['high'].rolling(m).max()
    fastk = 100 * (df['close'] - lowest_low) / (highest_high - lowest_low)
    fastd = fastk.rolling(n).mean()
    df = df.join(pd.Series(fastk, name='fastk'))
    df = df.join(pd.Series(fastd, name='fastd'))
    return df
