#!/bin/env python
# -*- coding: utf-8 -*-
''' requires mod_wsgi'''
import os, sys
os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(__file__))
from dasist import app as application
