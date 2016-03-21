# -*- coding: utf-8 -*-
import sys, locale, wb_engine.read, datetime, os
from wb_engine.utility import DateUtility
from wb_engine.io import IO
from wb_engine.preprocessing import PreProcessing
from wb_engine.engine import WbEngine
from wb_engine.pca import PcaCalculator
from wb_engine.pca import test
from wb_engine.io_template import IoTemplate

reload(sys)
sys.setdefaultencoding('utf-8')

#test = raw_input(u"입력:")

module = IoTemplate()
module.test()

#module = PcaCalculator()
#wb_engine.pca.test()