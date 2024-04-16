#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.2
# Email  : 978654313@qq.com
# version: 3.10.13
##################################################################



import functools

class CTest():
    def __init__(self) -> None:
        pass
    def __double(self):
        print("double")
    def _single(self):
        print("single")





if __name__ == "__main__":
    ctest = CTest()
    ctest._single() 

