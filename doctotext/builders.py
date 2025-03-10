# -*- coding: utf-8 -*-

from doctotext.utilities import formatted_hex

def build_fib(bytecode):
    
    output = {}
    offset = 0

    # 32 bytes
    output['base'] = bytecode[offset:offset + 32]
    output['base'] = build_base(output['base'])
    offset += 32
    
    # 2 bytes
    output['csw'] = int.from_bytes(bytecode[offset:offset + 2],'little', signed=False)
    output['csw_hex'] = formatted_hex(output['csw'])
    assert output['csw'] == 0x000E
    offset += 2
    
    # x*16 bites (16/8  = 2)
    output['fibRgW'] = bytecode[offset:offset + (output['csw']*2)]
    output['fibRgW'] = build_fibrgw97(output['fibRgW'])
    offset += output['csw']*2

    # 2 byte integer
    output['cslw'] = int.from_bytes(bytecode[offset:offset + 2],'little', signed=False)
    output['cslw_hex'] = formatted_hex(output['cslw'])
    assert output['cslw'] == 0x0016
    offset += 2

    # cslw*32 bites (32/8  = 4)
    output['fibRgLw'] = bytecode[offset:offset + (output['cslw']*4)]
    output['fibRgLw'] = build_fibrglw97(output['fibRgLw'])
    offset += output['cslw']*4

    # 2 bytes
    output['cbRgFcLcb'] = int.from_bytes(bytecode[offset:offset + 2],'little', signed=False)
    output['cbRgFcLcb_hex'] = formatted_hex(output['cbRgFcLcb'])
    offset += 2

    # cslw*64 bites (64/8  = 8)    
    output['fibRgFcLcb'] = bytecode[offset:offset + (output['cbRgFcLcb']*8)]
    offset += (output['cbRgFcLcb']*8)

    # 2 bytes
    output['cswNew'] = int.from_bytes(bytecode[offset:offset + 2],'little', signed=False)
    output['cswNew_hex'] = formatted_hex(output['cswNew'])
    assert output['cswNew'] in {0, 0x0002, 0x0005}
    offset += 2
    
    # x*16 (16/8=2)
    if output['cswNew'] != 0:
        output['fibRgCswNew'] = bytecode[offset:offset + (output['cswNew']*2)]
        output['fibRgCswNew'] = build_fibrgcswnew(output['fibRgCswNew'])
        offset += output['cswNew']*2
    else:
        output['fibRgCswNew'] = {}

    # variables
    if output['cswNew']==0:
        output['nFib'] = formatted_hex(output['base']['nFib'])
    else:
        output['nFib'] = formatted_hex(output['fibRgCswNew']['nFibNew'])
    if output['base']['fWhichTblStm'] == 1:
        output['_table'] = '1Table'
    else:
        output['_table'] = '0Table'
    
    # build the complex object
    if output['nFib'] == '0x00C1':
        output['fibRgFcLcb'] = build_fibrgfclcb97(output['fibRgFcLcb'])
    elif output['nFib'] == '0x00D9':
        output['fibRgFcLcb'] = build_fibrgfclcb2000(output['fibRgFcLcb'])
    elif output['nFib'] == '0x0101':
        output['fibRgFcLcb'] = build_fibrgfclcb2002(output['fibRgFcLcb'])
    elif output['nFib'] == '0x010C':
        output['fibRgFcLcb'] = build_fibrgfclcb2003(output['fibRgFcLcb'])
    elif output['nFib'] == '0x0112':
        output['fibRgFcLcb'] = build_fibrgfclcb2007(output['fibRgFcLcb'])
    else:
        assert False, "Invalid value detected for nFib. Aborting."
    
    output['_lenfib'] = offset
    return output


def build_base(bytecode):
    fields = {
        'wIdent': 2, 'nFib': 2, 'unused': 2, 'lid': 2, 'pnNext': 2,
        'bit_flags': 2,  # 16 bits covering multiple fields
        'nFibBack': 2, 'lKey': 4, 'envr': 1, 'extra_flags': 1,
        'reserved3': 2, 'reserved4': 2, 'reserved5': 4, 'reserved6': 4
    }
    
    output = {}
    offset = 0
    for key, size in fields.items():
        output[key] = int.from_bytes(bytecode[offset:offset + size], 'little')
        output[key + '_hex'] = formatted_hex(int.from_bytes(bytecode[offset:offset + size], 'little'))
        offset += size
    
    # Extract individual bit fields from 'bit_flags'
    bit_flags = output.pop('bit_flags')
    bit_fields = [
        'fDot', 'fGlsy', 'fComplex', 'fHasPic',
        'cQuickSaves', 'fEncrypted', 'fWhichTblStm', 'fReadOnlyRecommended',
        'fWriteReservation', 'fExtChar', 'fLoadOverride', 'fFarEast', 'fObfuscated']
    
    for i, name in enumerate(bit_fields):
        if name == 'cQuickSaves':
            output[name] = (bit_flags >> i) & 0b1111  # 4 bits
        else:
            output[name] = (bit_flags >> i) & 1  # 1 bit
    
    # Extract individual bit fields from 'extra_flags'
    extra_flags = output.pop('extra_flags')
    extra_bit_fields = ['fMac', 'fEmptySpecial', 'fLoadOverridePage', 'reserved1', 'reserved2', 'fSpare0']
    for i, name in enumerate(extra_bit_fields):
        output[name] = (extra_flags >> i) & 1
        
    # assertions
    assert output['fExtChar'] == 1
    assert output['nFibBack'] in {0x00BF, 0x00C1}
    assert output['envr'] == 0
    assert output['fMac'] == 0
    assert output['reserved3'] == 0
    assert output['reserved4'] == 0
    return output


def build_fibrgw97(bytecode):
    fields = {
        'reserved1': 2, 'reserved2': 2, 'reserved3': 2, 'reserved4': 2,
        'reserved5': 2, 'reserved6': 2, 'reserved7': 2, 'reserved8': 2,
        'reserved9': 2, 'reserved10': 2, 'reserved11': 2, 'reserved12': 2,
        'reserved13': 2, 'lidFE': 2
    }
    output = {}
    offset = 0
    for key, size in fields.items():
        output[key] = int.from_bytes(bytecode[offset:offset + size], 'little')
        offset += size
    return output


def build_fibrglw97(bytecode):
    fields = {
        'cbMac': 4, 'reserved1': 4, 'reserved2': 4, 'ccpText': 4,
        'ccpFtn': 4, 'ccpHdd': 4, 'reserved3': 4, 'ccpAtn': 4,
        'ccpEdn': 4, 'ccpTxbx': 4, 'ccpHdrTxbx': 4, 'reserved4': 4,
        'reserved5': 4, 'reserved6': 4, 'reserved7': 4, 'reserved8': 4,
        'reserved9': 4, 'reserved10': 4, 'reserved11': 4, 'reserved12': 4,
        'reserved13': 4, 'reserved14': 4}
    output = {}
    offset = 0
    for key, size in fields.items():
        output[key] = int.from_bytes(bytecode[offset:offset + size], 'little', signed=True)
        offset += size
    assert output['reserved13'] == output['reserved14'] == 0
    return output

def build_fibrgfclcb97(bytecode):

    output = {}
    fields = [
        "fcStshfOrig", "lcbStshfOrig", "fcStshf", "lcbStshf", "fcPlcffndRef", "lcbPlcffndRef",
        "fcPlcffndTxt", "lcbPlcffndTxt", "fcPlcfandRef", "lcbPlcfandRef", "fcPlcfandTxt", "lcbPlcfandTxt",
        "fcPlcfSed", "lcbPlcfSed", "fcPlcPad", "lcbPlcPad", "fcPlcfPhe", "lcbPlcfPhe", "fcSttbfGlsy", "lcbSttbfGlsy",
        "fcPlcfGlsy", "lcbPlcfGlsy", "fcPlcfHdd", "lcbPlcfHdd", "fcPlcfBteChpx", "lcbPlcfBteChpx", "fcPlcfBtePapx",
        "lcbPlcfBtePapx", "fcPlcfSea", "lcbPlcfSea", "fcSttbfFfn", "lcbSttbfFfn", "fcPlcfFldMom", "lcbPlcfFldMom",
        "fcPlcfFldHdr", "lcbPlcfFldHdr", "fcPlcfFldFtn", "lcbPlcfFldFtn", "fcPlcfFldAtn", "lcbPlcfFldAtn", 
        "fcPlcfFldMcr", "lcbPlcfFldMcr", "fcSttbfBkmk", "lcbSttbfBkmk", "fcPlcfBkf", "lcbPlcfBkf", "fcPlcfBkl",
        "lcbPlcfBkl", "fcCmds", "lcbCmds", "fcUnused1", "lcbUnused1", "fcSttbfMcr", "lcbSttbfMcr", "fcPrDrvr", 
        "lcbPrDrvr", "fcPrEnvPort", "lcbPrEnvPort", "fcPrEnvLand", "lcbPrEnvLand", "fcWss", "lcbWss", "fcDop", 
        "lcbDop", "fcSttbfAssoc", "lcbSttbfAssoc", "fcClx", "lcbClx", "fcPlcfPgdFtn", "lcbPlcfPgdFtn", 
        "fcAutosaveSource", "lcbAutosaveSource", "fcGrpXstAtnOwners", "lcbGrpXstAtnOwners", "fcSttbfAtnBkmk", 
        "lcbSttbfAtnBkmk", "fcUnused2", "lcbUnused2", "fcUnused3", "lcbUnused3", "fcPlcSpaMom", "lcbPlcSpaMom", 
        "fcPlcSpaHdr", "lcbPlcSpaHdr", "fcPlcfAtnBkf", "lcbPlcfAtnBkf", "fcPlcfAtnBkl", "lcbPlcfAtnBkl", "fcPms", 
        "lcbPms", "fcFormFldSttbs", "lcbFormFldSttbs", "fcPlcfendRef", "lcbPlcfendRef", "fcPlcfendTxt", 
        "lcbPlcfendTxt", "fcPlcfFldEdn", "lcbPlcfFldEdn", "fcUnused4", "lcbUnused4", "fcDggInfo", "lcbDggInfo", 
        "fcSttbfRMark", "lcbSttbfRMark", "fcSttbfCaption", "lcbSttbfCaption", "fcSttbfAutoCaption", 
        "lcbSttbfAutoCaption", "fcPlcfWkb", "lcbPlcfWkb", "fcPlcfSpl", "lcbPlcfSpl", "fcPlcftxbxTxt", 
        "lcbPlcftxbxTxt", "fcPlcfFldTxbx", "lcbPlcfFldTxbx", "fcPlcfHdrtxbxTxt", "lcbPlcfHdrtxbxTxt", 
        "fcPlcffldHdrTxbx", "lcbPlcffldHdrTxbx", "fcStwUser", "lcbStwUser", "fcSttbTtmbd", "lcbSttbTtmbd", 
        "fcCookieData", "lcbCookieData", "fcPgdMotherOldOld", "lcbPgdMotherOldOld", "fcBkdMotherOldOld", 
        "lcbBkdMotherOldOld", "fcPgdFtnOldOld", "lcbPgdFtnOldOld", "fcBkdFtnOldOld", "lcbBkdFtnOldOld", 
        "fcPgdEdnOldOld", "lcbPgdEdnOldOld", "fcBkdEdnOldOld", "lcbBkdEdnOldOld", "fcSttbfIntlFld", "lcbSttbfIntlFld",
        "fcRouteSlip", "lcbRouteSlip", "fcSttbSavedBy", "lcbSttbSavedBy", "fcSttbFnm", "lcbSttbFnm", "fcPlfLst", 
        "lcbPlfLst", "fcPlfLfo", "lcbPlfLfo", "fcPlcfTxbxBkd", "lcbPlcfTxbxBkd", "fcPlcfTxbxHdrBkd", 
        "lcbPlcfTxbxHdrBkd", "fcDocUndoWord9", "lcbDocUndoWord9", "fcRgbUse", "lcbRgbUse", "fcUsp", "lcbUsp", 
        "fcUskf", "lcbUskf", "fcPlcupcRgbUse", "lcbPlcupcRgbUse", "fcPlcupcUsp", "lcbPlcupcUsp", "fcSttbGlsyStyle", 
        "lcbSttbGlsyStyle", "fcPlgosl", "lcbPlgosl", "fcPlcocx", "lcbPlcocx", "fcPlcfBteLvc", "lcbPlcfBteLvc", 
        "dwLowDateTime", "dwHighDateTime", "fcPlcfLvcPre10", "lcbPlcfLvcPre10", "fcPlcfAsumy", "lcbPlcfAsumy", 
        "fcPlcfGram", "lcbPlcfGram", "fcSttbListNames", "lcbSttbListNames", "fcSttbfUssr", "lcbSttbfUssr"
    ]
    offset = 0
    for key in fields:
        output[key] = int.from_bytes(bytecode[offset:offset + 4], 'little')
        offset += 4
    assert all([output[i]==0 for i in [
        'lcbPlcfSea','lcbPlcfFldMcr','lcbUnused1','lcbSttbfMcr',
        'lcbPlcfPgdFtn','lcbAutosaveSource','lcbUnused2','lcbUnused3',
        'lcbFormFldSttbs','lcbUnused4','lcbSttbfIntlFld']])
    return output



def build_fibrgfclcb2000(bytecode):
    
    output = {}
    offset = 0
    output['rgFcLcb97'] = build_fibrgfclcb97(bytecode[0:744])
    offset += 744

    # remaining sections
    fields = ['fcPlcfTch', 'lcbPlcfTch', 'fcRmdThreading', 'lcbRmdThreading',
              'fcMid', 'lcbMid', 'fcSttbRgtplc', 'lcbSttbRgtplc',
              'fcMsoEnvelope', 'lcbMsoEnvelope', 'fcPlcfLad', 'lcbPlcfLad',
              'fcRgDofr', 'lcbRgDofrfcPlcosl', 'lcbPlcosl', 'fcPlcfCookieOld',
              'lcbPlcfCookieOld', 'fcPgdMotherOld', 'lcbPgdMotherOld',
              'fcBkdMotherOld', 'lcbBkdMotherOld', 'fcPgdFtnOld',
              'lcbPgdFtnOld', 'fcBkdFtnOld', 'lcbBkdFtnOld', 'fcPgdEdnOld',
              'lcbPgdEdnOld', 'fcBkdEdnOld', 'lcbBkdEdnOld']
    for key in fields:
        output[key] = int.from_bytes(bytecode[offset:offset + 4], 'little')
        offset += 4
    return output


def build_fibrgfclcb2002(bytecode):
    
    
    output = {}
    offset = 0
    output['rgFcLcb2000'] = build_fibrgfclcb2000(bytecode[0:864])
    offset += 864
    fields = [
        'fcUnused1', 'lcbUnused1', 'fcPlcfPgp', 'lcbPlcfPgp','fcPlcfuim',
        'lcbPlcfuim', 'fcPlfguidUim', 'lcbPlfguidUim', 'fcAtrdExtra',
        'lcbAtrdExtra', 'fcPlrsid', 'lcbPlrsid', 'fcSttbfBkmkFactoid',
        'lcbSttbfBkmkFactoid', 'fcPlcfBkfFactoid', 'lcbPlcfBkfFactoid',
        'fcPlcfcookie', 'lcbPlcfcookie', 'fcPlcfBklFactoid',
        'lcbPlcfBklFactoid', 'fcFactoidData', 'lcbFactoidData', 'fcDocUndo',
        'lcbDocUndo', 'fcSttbfBkmkFcc', 'lcbSttbfBkmkFcc', 'fcPlcfBkfFcc',
        'lcbPlcfBkfFcc', 'fcPlcfBklFcc', 'lcbPlcfBklFcc',
        'fcSttbfbkmkBPRepairs', 'lcbSttbfbkmkBPRepairs', 'fcPlcfbkfBPRepairs',
        'lcbPlcfbkfBPRepairs', 'fcPlcfbklBPRepairs', 'lcbPlcfbklBPRepairs',
        'fcPmsNew', 'lcbPmsNew', 'fcODSO', 'lcbODSO', 'fcPlcfpmiOldXP',
        'lcbPlcfpmiOldXP', 'fcPlcfpmiNewXP', 'lcbPlcfpmiNewXP',
        'fcPlcfpmiMixedXP', 'lcbPlcfpmiMixedXP', 'fcUnused2', 'lcbUnused2',
        'fcPlcffactoid', 'lcbPlcffactoid', 'fcPlcflvcOldXP', 'lcbPlcflvcOldXP',
        'fcPlcflvcNewXP', 'lcbPlcflvcNewXP', 'fcPlcflvcMixedXP',
        'lcbPlcflvcMixedXP']
    for key in fields:
        output[key] = int.from_bytes(bytecode[offset:offset + 4], 'little')
        offset += 4
    return output


def build_fibrgfclcb2003(bytecode):
    
    output = {}
    offset = 0
    output['rgFcLcb2002'] = build_fibrgfclcb2002(bytecode[0:1088])
    offset += 1088
    
    # remaining sections
    fields = ['fcHplxsdr', 'lcbHplxsdr', 'fcSttbfBkmkSdt', 'lcbSttbfBkmkSdt',
              'fcPlcfBkfSdt', 'lcbPlcfBkfSdt', 'fcPlcfBklSdt', 'lcbPlcfBklSdt',
              'fcCustomXForm', 'lcbCustomXForm', 'fcSttbfBkmkProt',
              'lcbSttbfBkmkProt', 'fcPlcfBkfProt', 'lcbPlcfBkfProt',
              'fcPlcfBklProt', 'lcbPlcfBklProt', 'fcSttbProtUser',
              'lcbSttbProtUser', 'fcUnused', 'lcbUnused', 'fcPlcfpmiOld',
              'lcbPlcfpmiOld', 'fcPlcfpmiOldInline', 'lcbPlcfpmiOldInline',
              'fcPlcfpmiNew', 'lcbPlcfpmiNew', 'fcPlcfpmiNewInline',
              'lcbPlcfpmiNewInline', 'fcPlcflvcOld', 'lcbPlcflvcOld',
              'fcPlcflvcOldInline', 'lcbPlcflvcOldInline', 'fcPlcflvcNew',
              'lcbPlcflvcNew', 'fcPlcflvcNewInline', 'lcbPlcflvcNewInline',
              'fcPgdMother', 'lcbPgdMother', 'fcBkdMother', 'lcbBkdMother',
              'fcAfdMother', 'lcbAfdMother', 'fcPgdFtn', 'lcbPgdFtn',
              'fcBkdFtn', 'lcbBkdFtn', 'fcAfdFtn', 'lcbAfdFtn', 'fcPgdEdn',
              'lcbPgdEdn', 'fcBkdEdn', 'lcbBkdEdn', 'fcAfdEdn', 'lcbAfdEdn',
              'fcAfd', 'lcbAfd']
    for key in fields:
        output[key] = int.from_bytes(bytecode[offset:offset + 4], 'little')
        offset += 4
    return output


def build_fibrgfclcb2007(bytecode):
    
    output = {}
    offset = 0
    output['rgFcLcb2003'] = build_fibrgfclcb2003(bytecode[0:1312])
    offset += 1312
    
    # remaining sections
    fields = ['fcPlcfmthd', 'lcbPlcfmthd', 'fcSttbfBkmkMoveFrom',
              'lcbSttbfBkmkMoveFrom', 'fcPlcfBkfMoveFrom',
              'lcbPlcfBkfMoveFrom', 'fcPlcfBklMoveFrom', 'lcbPlcfBklMoveFrom',
              'fcSttbfBkmkMoveTo', 'lcbSttbfBkmkMoveTo', 'fcPlcfBkfMoveTo',
              'lcbPlcfBkfMoveTo', 'fcPlcfBklMoveTo', 'lcbPlcfBklMoveTo',
              'fcUnused1', 'lcbUnused1', 'fcUnused2', 'lcbUnused2',
              'fcUnused3', 'lcbUnused3', 'fcSttbfBkmkArto', 'lcbSttbfBkmkArto',
              'fcPlcfBkfArto', 'lcbPlcfBkfArto', 'fcPlcfBklArto',
              'lcbPlcfBklArto', 'fcArtoData', 'lcbArtoData', 'fcUnused4',
              'lcbUnused4', 'fcUnused5', 'lcbUnused5', 'fcUnused6',
              'lcbUnused6', 'fcOssTheme', 'lcbOssTheme',
              'fcColorSchemeMapping', 'lcbColorSchemeMapping']
    for key in fields:
        output[key] = int.from_bytes(bytecode[offset:offset + 4], 'little')
        offset += 4
    return output


def build_clx(bytecode):

    # First byte of Clx determines whether there's a Prc array or not 
    clx = {}
    if bytecode[0] == 0x02:
        # This means the Prc array is empty, and the first byte of the Clx structure
        # is 0x02 to signal this. The Pcdt follows directly.
        clx['RgPrc'] = []
        clx['Pcdt'] = bytecode
    else:
        # If the first byte is not 0x02, it indicates there are Prc elements
        prcs = []
        idx = 0
        # Parse RgPrc (array of Prc)
        while bytecode[idx] != 0x02:  # We assume that 0x02 indicates the start of Pcdt
            prcs.append(bytecode[idx])  # This is simplified; actual parsing of Prc should be here
        # After Prcs, we parse the Pcdt
        clx['RgPrc'] = prcs
        clx['Pcdt'] = bytecode[idx:]  # Rest of the bytecode is the Pcdt
    clx['Pcdt'] = build_pcdt(clx['Pcdt'])
    return clx

def build_pcdt(bytecode):

    offset = 0
    output = {}

    # 1 byte starting
    output['clxt'] = int.from_bytes(bytecode[offset:offset + 1], 'little')
    assert output['clxt'] == 0x02, "invalid starting byte. Aborting."
    offset += 1

    # 4 byte
    output['lcb'] = int.from_bytes(bytecode[offset:offset + 4], 'little')
    offset += 4

    # plcpcd is variable        
    size = output['lcb']
    output['PlcPcd'] = bytecode[offset:offset + size]
    output['PlcPcd'] = build_plcpcd(output['PlcPcd'])
    return output
    

def build_plcpcd(bytecode):
    """
    Parses the bytecode for PlcPcd structure and extracts CPs and Pcds.
    """
    
    # Extract CPs (starting points of text ranges)
    # note it alternates char position then PCD
    index = 0
    cp_list = []
    pcd_list = []
    
    num_pcds = int((len(bytecode) - 4) / 12)
    num_cps = int(num_pcds + 1)
    
    # cp is first
    for i in range(num_cps):
        cp = int.from_bytes(bytecode[index:index + 4], 'little')  # Read 4 bytes for CP (little-endian)
        cp_list.append(cp)
        index += 4  # Move by 4 bytes to the next CP

    for i in range(num_pcds):
        # then pcd
        pcd_list.append(bytecode[index:index + 8])
        index += 8

    output = {
        'aCP': cp_list,
        'aPcd': [build_pcd(i) for i in pcd_list]
        }
    return output


def build_pcd(bytecode):
    """
    Parses the full Pcd structure from the given bytecode.
    b'\x00\x00\x00\x00\x00\x88\x0b\x00'
    """
    assert len(bytecode) == 8, 'invalid bytecode length'
    output = {
        'fNoParaLast': (bytecode[0] +  (bytecode[1] << 8)) & 0x01,
        'fR1': (bytecode[0] + (bytecode[1] << 8) >> 1) & 0x01,
        'fDirty': (bytecode[0] + (bytecode[1] << 8) >> 2) & 0x01,
        'fR2': (bytecode[0] + (bytecode[1] << 8) >> 3) & 0x1FFF,
        'prm': bytecode[6:8]
    }

    # Extract fc (30 bits)
    fc = bytecode[2:6][::-1]
    combined_value = (fc[0] << 24) | (fc[1] << 16) | (fc[2] << 8) | fc[3]
    output['fc'] = {
        'fc': combined_value & 0x3FFFFFFF,  # Mask to get the lower 30 bits
        'fCompressed': (combined_value >> 30) & 0x01,  # Get the 31st bit (bit 30 in little-endian)
        'r1': (combined_value >> 31) & 0x01,  # Get the 32nd bit (bit 31 in little-endian)
        }

    # Extract the raw Prm (2 bytes)
    return output




# def build_prm(bytecode: bytes):
#     """
#     Parses a 16-bit (2-byte) Prm structure and determines whether it is Prm0 or Prm1.
#     """
#     if len(bytecode) < 2:
#         raise ValueError("Bytecode must be exactly 2 bytes long")

#     # Convert the 2-byte sequence to a 16-bit integer (little-endian)
#     prm_raw = int.from_bytes(bytecode, byteorder='little')
#     fComplex = (prm_raw >> 15) & 1  # Extract the highest bit (bit 15)
#     data = prm_raw & 0x7FFF  # Mask the lower 15 bits (0x7FFF = 0111 1111 1111 1111)

#     output = {
#         "fComplex": fComplex,
#         "data": data.to_bytes((data.bit_length() + 7) // 8, byteorder='little'),
#     }
    
#     structure_type = "Prm1" if fComplex else "Prm0"
#     if structure_type == "Prm1":
#         pass
#         # !!! 
#     elif structure_type == "Prm0":
#         pass
#         # !!! b'\x00\x10' is an example
#     else:
#         assert False
#     return output


def build_fibrgcswnew(bytecode):

    output = {}
    offset = 0
    output['nFibNew'] = int.from_bytes(bytecode[offset:offset + 2],'little', signed=False)
    output['nFibNew_hex'] = formatted_hex(output['nFibNew'])
    offset += 2

    # fibRgCswNewData2000 (2 bytes)
    if output['nFibNew_hex'] in {'0x00D9','0x0101','0x010C'}:
        output['rgCswNewData'] = bytecode[offset:offset + 2]
        
    # fibRgCswNewData2007 (8 bytes)
    elif output['nFibNew_hex'] in {'0x0112'}:
        output['rgCswNewData'] = bytecode[offset:offset + 8]
    return output
    