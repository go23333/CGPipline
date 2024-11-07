#coding=utf-8

import cv2
import numpy as np

import UnrealPipeline.core.watermark as script


def psnr(im1,im2):
    if im1.shape != im2.shape or  len(im2.shape)<2:
        return 0
    
    di = im2.shape[0] * im2.shape[1]
    if len(im2.shape)==3:
        di = im2.shape[0] * im2.shape[1] *  im2.shape[2]
    
    diff = np.abs(im1 - im2)
    rmse = np.sum(diff*diff) /di
    print(rmse)
    psnr = 20*np.log10(255/rmse)
    return psnr

def addWatermark(alg:str,imgName:str,outName:str,wmName:str):
    handle = script.dctwm

    if alg == 'DCT':
        handle = script.dctwm
    if alg == 'DWT':
        handle = script.dwtwm
    img = cv2.imread(imgName)
    try:
        if(img.all() == None):
            return
    except:
        return
    wm  = cv2.imread(wmName,cv2.IMREAD_GRAYSCALE)
    wmd = handle.embed(img,wm)
    cv2.imwrite(outName,wmd)
def extractWatermark(alg:str,wmdName:str,wmName:str):
    handle = script.dctwm

    if alg == 'DCT':
        handle = script.dctwm
    if alg == 'DWT':
        handle = script.dwtwm

    wmd = cv2.imread(wmdName)
    try:
        if(wmd.all() == None):
            return
    except:
        return
    wm = cv2.imread(wmName,cv2.IMREAD_GRAYSCALE)
    sim = handle.extract(wmd,wm)
    return(sim)


if __name__ == "__main__":
    addWatermark('DCT','test.png','test_wm.png','Data/wm_ZYNN.png')
    print(extractWatermark('DCT','test_wm.png','Data/wm_ZYNN.png'))