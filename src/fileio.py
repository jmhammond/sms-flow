#!/usr/bin/env python

"""
    File IO module
"""

def read_html(file_name):
    my_html = ""
    fh = open(file_name)
    for line in fh:
        my_html = my_html + line
    
    return my_html
        
