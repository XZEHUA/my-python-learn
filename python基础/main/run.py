#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/3/8 12:48
# @Desc:

import os
import sys
print(sys.path)

# import OOP.demo01
# from python基础.OOP import demo01 as op
# from python基础.OOP.demo02 import hello_python, HouYi
from python基础.OOP import *

op.func()

wk = op.WuKong('悟空', 3000,100,0.2)
print(wk)
