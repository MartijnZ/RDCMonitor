import numpy as np
from scipy.signal import welch, csd, get_window

def frf_h1(x: np.ndarray, y: np.ndarray, fs:int, nperseg:int, window:str, noverlap:int):
    win = get_window(window, nperseg, fftbins=True)
    f, Gxx = welch(x, fs=fs, window=win, nperseg=nperseg, noverlap=noverlap, detrend="constant", return_onesided=True)
    _, Gyy = welch(y, fs=fs, window=win, nperseg=nperseg, noverlap=noverlap, detrend="constant", return_onesided=True)
    _, Gxy = csd(x, y, fs=fs, window=win, nperseg=nperseg, noverlap=noverlap, detrend="constant", return_onesided=True)
    H1 = Gxy / Gxx
    coh = (np.abs(Gxy)**2) / (Gxx * Gyy + 1e-20)
    return f, H1, coh
