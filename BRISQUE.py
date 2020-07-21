# coding=utf-8
# source: https://github.com/bukalapak/pybrisque/
# Author: Akbar Gumbira

import os
from ctypes import c_double

import numpy as np
from IProcess import IProcess, EDataType
from brisquemodel import brisquemodel

class BRISQUE(IProcess):

    def __init__(self):
        IProcess.__init__(self)

    def toId(self):
        return str(__class__.__name__)

    def getType(self):
        return EDataType.BRISQUE

    def do(self, imageData):
        IProcess.do(self, imageData)

        inputImgData = np.array(self.data[-1])
        model = brisquemodel()
        self.brisque_score = model.get_score(inputImgData)

        return self