# -*- coding: utf-8 -*-
#############################################################
#           _              _          _        _            #
#        __| | ___   ___  | |_ ___   | |___  _| |_          #
#       / _` |/ _ \ / __| | __/ _ \  | __\ \/ / __|         #
#      | (_| | (_) | (__  | || (_) | | |_ >  <| |_          #
#       \__,_|\___/ \___|  \__\___/   \__/_/\_\\__|         #
#                                                           #
#############################################################
# Written by William Kinsman. Please fork / modify / fix as needed.

import olefile
from doctotext import builders
from doctotext.utilities import find_value_by_key

def extract_text(path: str):
    """
    @param path: path to *.doc file
    returns: list of text spans in document
    """
    try:
        # fetch word_data
        ole = olefile.OleFileIO(path)
        word_stream = ole.openstream('WordDocument')
        word_data = word_stream.read()
        assert len(word_data) <= 0x7FFFFFFF
    
        # build the fib
        fib = builders.build_fib(word_data)
        
        # fetch table_data
        table_data = ole.openstream(fib['_table']).read()
        assert len(table_data) <= 0x7FFFFFFF
        
        # build the clx
        fcclx = find_value_by_key(fib, 'fcClx')
        lcbclx = find_value_by_key(fib, 'lcbClx')
        clx = builders.build_clx(table_data[fcclx:fcclx+lcbclx])
    except:
        assert False, "Error in parsing. Aborting."
    
    # build text ranges
    text = []
    for i in range(len(clx['Pcdt']['PlcPcd']['aCP'])-1):
        aCp_i     = clx['Pcdt']['PlcPcd']['aCP'][i]
        aCp_i_end = clx['Pcdt']['PlcPcd']['aCP'][i + 1]
        pcd       = clx['Pcdt']['PlcPcd']['aPcd'][i]
        
        # uncompressed text
        if pcd['fc']['fCompressed'] == 0:
            offset_s = pcd['fc']['fc']
            offset_e = offset_s + (2 * (aCp_i_end - aCp_i))
            text.append(word_data[offset_s:offset_e].decode("utf-16", errors='ignore'))
        
        # compressed text
        else:
            offset_s = (pcd['fc']['fc'] // 2)
            offset_e = offset_s + (aCp_i_end - aCp_i)
            text.append(word_data[offset_s:offset_e].decode('cp1252', errors='ignore'))
    ole.close()
    return text