import pandas as pd
from pandas import DataFrame
import math
import numpy as np
from .decorators import *

@iterate_jit(nopython=True)
def FilingStatus(MARS):
    if MARS == 3 or MARS == 6:
        _sep = 2
    else: _sep = 1

    return _sep 

@iterate_jit(nopython=True)
def Adj(   e35300_0, e35600_0, e35910_0, e03150, e03210, e03600, e03260,
                e03270, e03300, e03400, e03500, e03280, e03900, e04000,
                e03700, e03220, e03230, e03240, e03290 ):
    # Adjustments
    _feided = max(e35300_0, e35600_0 + e35910_0)  # Form 2555

    c02900 = (e03150 + e03210 + e03600 + e03260 + e03270 + e03300
              + e03400 + e03500 + e03280 + e03900 + e04000 + e03700
              + e03220 + e03230
              + e03240
              + e03290)

    return (_feided, c02900)


@iterate_jit(parameters=['feimax'], nopython=True)
def CapGains(  e23250, e22250, e23660, _sep, _feided, feimax,
                    f2555, e00200, e00300, e00600, e00700, e00800,
                    e00900, e01100, e01200, e01400, e01700, e02000, e02100,
                    e02300, e02600, e02610, e02800, e02540, e00400, e02400,
                    c02900, e03210, e03230, e03240, e02615):
    # Capital Gains

    c23650 = e23250 + e22250 + e23660
    c01000 = max(-3000 / _sep, c23650)
    c02700 = min(_feided, feimax * f2555)
    _ymod1 = (e00200 + e00300 + e00600
            + e00700 + e00800 + e00900
            + c01000 + e01100 + e01200
            + e01400 + e01700 + e02000
            + e02100 + e02300 + e02600
            + e02610 + e02800 - e02540)
    _ymod2 = e00400 + (0.50 * e02400) - c02900
    _ymod3 = e03210 + e03230 + e03240 + e02615
    _ymod = _ymod1 + _ymod2 + _ymod3

    return (c23650, c01000, c02700, _ymod1, _ymod2, _ymod3, _ymod)


@iterate_jit(parameters=["_ssb50", "_ssb85"], nopython=True)
def SSBenefits(SSIND, MARS, e02500, _ymod, e02400, _ssb50, _ssb85):

    if SSIND !=0 or MARS == 3 or MARS == 6:
        c02500 = e02500
    elif _ymod < _ssb50[MARS-1]:
        c02500 = 0.
    elif _ymod >= _ssb50[MARS-1] and _ymod < _ssb85[MARS-1]:
        c02500 = 0.5 * min(_ymod - _ssb50[MARS-1], e02400)
    else:
        c02500 = min(0.85 * (_ymod - _ssb85[MARS-1]) +
                    0.50 * min(e02400, _ssb85[MARS-1] -
                    _ssb50[MARS-1]), 0.85 * e02400)
    c02500 = float(c02500)

    return (c02500, e02500)


@iterate_jit(parameters=["amex", "exmpb"], nopython=True)
def AGI(   _ymod1, c02500, c02700, e02615, c02900, e00100, e02500, XTOT, 
                amex, exmpb, MARS, _sep, _fixup):

    # Adjusted Gross Income

    c02650 = _ymod1 + c02500 - c02700 + e02615  # Gross Income

    c00100 = c02650 - c02900
    _agierr = e00100 - c00100  # Adjusted Gross Income
    
    if _fixup >= 1:
        c00100 = c00100 + _agierr

    _posagi = max(c00100, 0)
    _ywossbe = e00100 - e02500
    _ywossbc = c00100 - c02500

    _prexmp = XTOT * amex
    # Personal Exemptions (_phaseout smoothed)

    _dispc_numer = 0.02 * (_posagi - exmpb[MARS - 1])
    _dispc_denom = (2500 / _sep)
    _dispc = min(1, max(0, _dispc_numer / _dispc_denom ))

    c04600 = _prexmp * (1 - _dispc)
    
    return (c02650, c00100, _agierr, _posagi, _ywossbe, _ywossbc, _prexmp, c04600)

@iterate_jit(parameters=["puf", "phase2"], nopython=True, puf=True)
def ItemDed(_posagi, e17500, e18400, e18425, e18450, e18500, e18800, e18900,
                 e20500, e20400, e19200, e20550, e20600, e20950, e19500, e19570,
                 e19400, e19550, e19800, e20100, e20200, e20900, e21000, e21010,
                 MARS, _sep, c00100, phase2, puf):
    """
    WARNING: Any additional keyword args, such as 'puf=True' here, must be passed
    to the function at the END of the argument list. If you stick the argument
    somewhere in the middle of the signature, you will get errors.
    """
    # Medical #
    c17750 = 0.075 * _posagi
    c17000 = max(0, e17500 - c17750)

    # State and Local Income Tax, or Sales Tax #
    _sit1 = max(e18400, e18425)
    _sit = max(_sit1, 0)
    _statax =  max(_sit, e18450)

    # Other Taxes #
    c18300 = _statax + e18500 + e18800 + e18900

    # Casulty #
    if e20500 > 0:
        c37703 = e20500 + 0.1 * _posagi
        c20500 = c37703 + 0.1 * _posagi
    else:
        c37703 = 0.
        c20500 = 0.

    # Miscellaneous #
    c20750 = 0.02 * _posagi
    if puf == True:
        c20400 = e20400
        c19200 = e19200
    else:
        c20400 = e20550 + e20600 + e20950
        c19200 = e19500 + e19570 + e19400 + e19550
    c20800 = max(0, c20400 - c20750)

    # Charity (assumes carryover is non-cash)
    base_charity = e19800 + e20100 + e20200
    if base_charity <= 0.2 * _posagi:
        c19700 = base_charity
    else:
        lim50 = min(0.50 * _posagi, e19800)
        lim30 = min(0.30 * _posagi, e20100 + e20200)
        c19700 = min(0.5 * _posagi, lim30 + lim50)
    # temporary fix!??

    # Gross Itemized Deductions #
    c21060 = (e20900 + c17000 + c18300 + c19200 + c19700
              + c20500 + c20800 + e21000 + e21010)

    _phase2_i = phase2[MARS-1]

    _nonlimited = c17000 + c20500 + e19570 + e21010 + e20900
    _limitratio = _phase2_i/_sep

    if c21060 > _nonlimited and c00100 > _limitratio:
        dedmin = 0.8 * (c21060 - _nonlimited)
        dedpho = 0.03 * max(0, _posagi - _limitratio)
        c21040 = min(dedmin, dedpho)
    else:
        c21040 = 0.0


    if c21060 > _nonlimited and c00100 > _limitratio:
        c04470 = c21060 - c21040
    else:
        c04470 = c21060

    c20400 = float(c20400)

    # the variables that are casted as floats below can be either floats or ints depending
    # on which if/else branches they follow in the above code. they need to always be the same type

    c20400 = float(c20400)
    c19200 = float(c19200)
    c37703 = float(c37703)
    c20500 = float(c20500)

    return (c17750, c17000, _sit1, _sit, _statax, c18300, c37703, c20500,
            c20750, c20400, c19200, c20800, c19700, c21060, _phase2_i,
            _nonlimited, _limitratio, c04470, c21040)


@iterate_jit(parameters=["ssmax"], nopython=True)
def EI_FICA(   e00900, e02100, ssmax, e00200,
                    e11055, e00250, e30100):
    # Earned Income and FICA #

    _sey = e00900 + e02100
    _fica = max(0, .153 * min(ssmax, e00200 + max(0, _sey) * 0.9235))
    _setax = max(0, _fica - 0.153 * e00200)
    
    if _setax <= 14204:
        _seyoff = 0.5751 * _setax
    else: 
        _seyoff = 0.5 * _setax + 10067

    c11055 = e11055

    _earned = max(0, e00200 + e00250 + e11055 + e30100 + _sey - _seyoff)

    return (_sey, _fica, _setax, _seyoff, c11055, _earned)


@iterate_jit(parameters=["stded", "aged", "rt1", "rt2", "rt3", "rt4", 
             "rt5", "rt6", "rt7", "brk1", "brk2", "brk3", "brk4", "brk5", 
            "brk6"], nopython=True)
def StdDed( DSI, _earned, stded, e04470, 
            MARS, MIdR, e15360, AGEP, AGES, PBI, SBI, _exact, e04200, aged,
            c04470, c00100, c21060, c21040, e37717, c04600, e04805, t04470,
            f6251, _feided, c02700, FDED, rt1, rt2, rt3, rt4, rt5, rt6, rt7,
            brk1, brk2, brk3, brk4, brk5, brk6):
    # Standard Deduction with Aged, Sched L and Real Estate #

    if DSI == 1:
        c15100 = max(300 + _earned, stded[6])
    else:
        c15100 = 0.

    if e04470 > 0 and e04470 < stded[MARS-1]:
        _compitem = 1.
    else:
        _compitem = 0.

    if (DSI == 1):
        c04100 = min( stded[MARS-1], c15100)
    elif _compitem == 1 or (3 <= MARS and MARS <=6 and MIdR == 1):
        c04100 = 0.
    else:
        c04100 = stded[MARS - 1]

    c04100 = c04100 + e15360

    _numextra = AGEP + AGES + PBI + SBI

    if MARS == 2 or MARS == 3:
        _txpyers = 2.
    else:
        _txpyers = 1.

    if _exact == 1 and MARS == 3 or MARS == 5:
        c04200 = e04200
    else:
        c04200 = _numextra * aged[int(_txpyers - 1)]

    c15200 = c04200

    if (MARS == 3 or MARS == 6) and (c04470 > 0):
        _standard = 0.
    else:
        _standard = c04100 + c04200

    if FDED == 1:
        _othded = e04470 - c04470
        c04100 = 0.
        c04200 = 0.
        _standard = 0.
    else: 
        _othded = 0.

    c04500 = c00100 - max(c21060 - c21040,
                                 max(c04100, _standard + e37717))
    c04800 = max(0., c04500 - c04600 - e04805)

    #why is this here, c60000 is reset many times? 
    if _standard > 0:
        c60000 = c00100
    else:
        c60000 = c04500

    c60000 = c60000 - e04805

    #PAUSED HERE!!!
    # Some taxpayers iteimize only for AMT, not regular tax
    _amtstd = 0.

    if (e04470 == 0 and (t04470 > _amtstd) and f6251 == 1 and _exact == 1):
        c60000 = c00100 - t04470
   

    if (c04800 > 0 and _feided > 0):
        _taxinc = c04800 + c02700
    else:
        _taxinc = c04800

    if (c04800 > 0 and _feided > 0):
        _feitax = Taxer_i(_feided, MARS, rt1, rt2, rt3, rt4, rt5, rt6, rt7,
                          brk1, brk2, brk3, brk4, brk5, brk6)

        _oldfei = Taxer_i(c04800, MARS, rt1, rt2, rt3, rt4, rt5, rt6, rt7,
                          brk1, brk2, brk3, brk4, brk5, brk6)
    else:
        _feitax, _oldfei = 0., 0.

    return (c15100, _numextra, _txpyers, c15200,
                  _othded, c04100, c04200, _standard, c04500,
                 c04800, c60000, _amtstd, _taxinc, _feitax, _oldfei)


@iterate_jit(parameters=["rt1", "rt2", "rt3", "rt4", "rt5", "rt6", "rt7",
             "brk1", "brk2", "brk3", "brk4", "brk5", "brk6"],nopython=True)
def XYZD(_taxinc, c04800, MARS, rt1, rt2, rt3, rt4, rt5, rt6, rt7, brk1, 
              brk2, brk3, brk4, brk5, brk6):

    _xyztax = Taxer_i(_taxinc, MARS, rt1, rt2, rt3, rt4, rt5, rt6, rt7, brk1,
                      brk2, brk3, brk4, brk5, brk6) 
    c05200 = Taxer_i(c04800, MARS, rt1, rt2, rt3, rt4, rt5, rt6, rt7, brk1,
                     brk2, brk3, brk4, brk5, brk6)

    return (_xyztax, c05200)


@iterate_jit(nopython=True)
def NonGain(c23650, e23250, e01100):
    _cglong = min(c23650, e23250) + e01100
    _noncg = 0
    return (_cglong, _noncg)



@iterate_jit(parameters=[ "rt1", "rt2", "rt3", "rt4", "rt5", "rt6", "rt7", 
             "brk1", "brk2", "brk3", "brk4", "brk5", "brk6"], nopython=True)

def TaxGains(e00650, c04800, e01000, c23650, e23250, e01100, e58990, 
                  e58980, e24515, e24518, MARS, _taxinc, _xyztax, _feided, 
                  _feitax, _cmp, e59410, e59420, e59440, e59470, e59400, 
                  e83200_0, e10105, e74400, rt1, rt2, rt3, rt4, rt5, rt6, rt7, 
                  brk1, brk2, brk3, brk4, brk5, brk6):

    c00650 = e00650
    _addtax = 0.

    if e01000 > 0 or c23650 > 0. or e23250 > 0. or e01100 > 0. or e00650 > 0.:
        _hasgain = 1.
    else:
        _hasgain = 0.

    if _taxinc > 0. and _hasgain == 1.:
        #if/else 1
        _dwks5 = max(0., e58990 - e58980)
        c24505 = max(0., c00650 - _dwks5)

        # gain for tax computation
        if e01100 > 0.:
            c24510 = float(e01100)
        else:
            c24510 = max(0., min(c23650, e23250)) + e01100

        _dwks9 = max(0, c24510 - min(e58990, e58980))
        c24516 = c24505 + _dwks9

        #if/else 2
        _dwks12 = min(_dwks9, e24515 + e24518)
        c24517 = c24516 - _dwks12
        c24520 = max(0., _taxinc - c24517)
        # tentative TI less schD gain
        c24530 = min(brk2[MARS - 1], _taxinc)

        #if/else 3
        _dwks16 = min(c24520, c24530)
        _dwks17 = max(0., _taxinc - c24516)
        c24540 = max(_dwks16, _dwks17)
        c24534 = c24530 - _dwks16
        _dwks21 = min(_taxinc, c24517)
        c24597 = max(0., _dwks21 - c24534)

        #if/else 4
        # income subject to 15% tax
        c24598 = 0.15 * c24597  # actual 15% tax
        _dwks25 = min(_dwks9, e24515)
        _dwks26 = c24516 + c24540
        _dwks28 = max(0., _dwks26 - _taxinc)
        c24610 = max(0., _dwks25 - _dwks28)
        c24615 = 0.25 * c24610
        _dwks31 = c24540 + c24534 + c24597 + c24610
        c24550 = max(0., _taxinc - _dwks31)
        c24570 = 0.28 * c24550

        if c24540 > brk6[MARS - 1]:
            _addtax = 0.05 * c24517

        elif c24540<= brk6[MARS - 1] and _taxinc > brk6[MARS - 1]:
            _addtax = 0.05 * min(c24517, c04800 - brk6[MARS - 1])

        c24560 = Taxer_i(c24540, MARS, rt1, rt2, rt3, rt4, rt5, rt6, rt7, 
                         brk1, brk2, brk3, brk4, brk5, brk6)

        _taxspecial = c24598 + c24615 + c24570 + c24560 + _addtax
        c24580 = min(_taxspecial, _xyztax)

    else:
        ## these variables only be used to check accuracy? unused in calcs. (except c24580)
        _dwks5 = 0.
        _dwks9 = 0.
        c24505 = 0.
        c24510 = 0.
        c24516 = max(0., min(e23250, c23650)) + e01100

        _dwks12 = 0.
        c24517 = 0.
        c24520 = 0.
        c24530 = 0.

        _dwks16 = 0.
        _dwks17 = 0.
        c24540 = 0.
        c24534 = 0.
        _dwks21 = 0.
        c24597 = 0.

        c24598 = 0.
        _dwks25 = 0.
        _dwks26 = 0.
        _dwks28 = 0.
        c24610 = 0.
        c24615 = 0.
        _dwks31 = 0.
        c24550 = 0.
        c24570 = 0.
        _addtax = 0.
        c24560 = 0.
        _taxspecial = 0.
        c24580 = _xyztax


    if c04800 > 0. and _feided > 0.:
        c05100 = max(0., c24580 - _feitax)
    else:
        c05100 = c24580


    # Form 4972 - Lump Sum Distributions
    if _cmp == 1.:
        c59430 = max(0., e59410 - e59420)
        c59450 = c59430 + e59440 # income plus lump sum
        c59460 = max(0., min(0.5 * c59450, 10000.)) - 0.2 * max(0., 59450. - 20000.)
        _line17 = c59450 - c59460
        _line19 = c59450 - c59460 - e59470

        if c59450 > 0.:
            _line22 = max(0., e59440 - e59440*c59460/c59450)
        else:
            _line22 = 0.

        _line30 = 0.1 * max(0., c59450 - c59460 - e59470)

        _line31 = 0.11 * min(_line30, 1190.)\
                + 0.12 * min(2270. - 1190., max(0, _line30 - 1190.))\
                + 0.14 * min(4530. - 2270., max(0., _line30 - 2270.))\
                + 0.15 * min(6690. - 4530., max(0., _line30 - 4530.))\
                + 0.16 * min(9170. - 6690., max(0., _line30 - 6690.))\
                + 0.18 * min(11440. - 9170., max(0., _line30 - 9170.))\
                + 0.20 * min(13710. - 11440., max(0., _line30 - 11440.))\
                + 0.23 * min(17160. - 13710., max(0., _line30 - 13710.))\
                + 0.26 * min(22880. - 17160., max(0., _line30 - 17160.))\
                + 0.30 * min(28600. - 22880., max(0., _line30 - 22880.))\
                + 0.34 * min(34320. - 28600., max(0., _line30 - 28600.))\
                + 0.38 * min(42300. - 34320., max(0., _line30 - 34320.))\
                + 0.42 * min(57190. - 42300., max(0., _line30 - 42300.))\
                + 0.48 * min(85790. - 57190., max(0., _line30 - 57190.))

        _line32 = 10. * _line31

        if e59440 == 0.:
            _line36 = _line32
            ## below are unused in calcs
            _line33 = 0.
            _line34 = 0.
            _line35 = 0.

        elif e59440 > 0.:
            _line33 = 0.1 * _line22

            _line34 = 0.11 * min(_line30, 1190.)\
                    + 0.12 * min(2270. - 1190., max(0., _line30 - 1190.))\
                    + 0.14 * min(4530. - 2270., max(0., _line30 - 2270.))\
                    + 0.15 * min(6690. - 4530., max(0., _line30 - 4530.))\
                    + 0.16 * min(9170. - 6690., max(0., _line30 - 6690.))\
                    + 0.18 * min(11440. - 9170., max(0., _line30 - 9170.))\
                    + 0.20 * min(13710. - 11440., max(0., _line30 - 11440.))\
                    + 0.23 * min(17160. - 13710., max(0., _line30 - 13710.))\
                    + 0.26 * min(22880. - 17160., max(0., _line30 - 17160.))\
                    + 0.30 * min(28600. - 22880., max(0., _line30 - 22880.))\
                    + 0.34 * min(34320. - 28600., max(0., _line30 - 28600.))\
                    + 0.38 * min(42300. - 34320., max(0., _line30 - 34320.))\
                    + 0.42 * min(57190. - 42300., max(0., _line30 - 42300.))\
                    + 0.48 * min(85790. - 57190., max(0., _line30 - 57190.))

            _line35 = 10. * _line34
            _line36 = max(0., _line32 - _line35)

        else:
            _line33 = 0.
            _line34 = 0.
            _line35 = 0.
            _line36 = 0.

        # tax saving from 10 yr option
        c59485 = _line36

        c59490 = c59485 + 0.2 * max(0., e59400)
        # pension gains tax plus
        c05700 = c59490

    else:
        # all but one unused in calcs
        c59430 = 0.
        c59450 = 0.
        c59460 = 0.
        _line17 = 0.
        _line19 = 0.
        _line22 = 0.
        _line30 = 0.
        _line31 = 0.
        _line32 = 0.
        _line33 = 0.
        _line34 = 0.
        _line35 = 0.
        _line36 = 0.
        c59485 = 0.
        c59490 = 0.
        c05700 = 0.


    _parents = e83200_0
    _s1291 = e10105
    c05750 = max(c05100 + _parents + c05700, e74400)
    _taxbc = c05750

    return (e00650, _hasgain, _dwks5, c24505, c24510, _dwks9, c24516,
            c24580, _dwks12, c24517, c24520, c24530, _dwks16,
            _dwks17, c24540, c24534, _dwks21, c24597, c24598, _dwks25,
            _dwks26, _dwks28, c24610, c24615, _dwks31, c24550, c24570,
            _addtax, c24560, _taxspecial, c05100, c05700, c59430,
            c59450, c59460, _line17, _line19, _line22, _line30, _line31,
            _line32, _line36, _line33, _line34, _line35, c59485, c59490,
            _s1291, _parents, _taxbc, c05750)

# TODO should we be returning c00650 instead of e00650??? Would need to change tests




@iterate_jit(parameters=["_thresx"], nopython=True)
def MUI(c00100, _thresx, MARS, c05750, e00300, e00600, c01000, e02000):
    # Additional Medicare tax on unearned Income
    if c00100 > _thresx[MARS - 1]:
        c05750  = (c05750 + 0.038 * min(e00300 + e00600 + max(0, c01000)
                + max(0, e02000), c00100 - _thresx[MARS - 1]))
    return c05750



@iterate_jit(parameters=["almsp", "brk6", "brk2", "almdep", "cgrate1", 
                         "cgrate2", "amtys", "amtsep", "amtage", "almsep", 
                         "amtex", "puf"], nopython=True, puf=True)
def AMTI(  c60000, _exact, e60290, _posagi, e07300, x60260, c24517,
                e60300, e60860, e60100, e60840, e60630, e60550,
                e60720, e60430, e60500, e60340, e60680, e60600, e60405,
                e60440, e60420, e60410, e61400, e60660, e60480,
                e62000,  e60250, _cmp, _standard,  e04470, e17500, 
                f6251,  e62100, e21040, _sit, e20800, c00100, 
                c04470, c17000, e18500, c20800, c21040,   
                DOBYR, FLPDYR, DOBMD, SDOBYR, SDOBMD,  c02700, 
                e00100,  e24515, x62730, x60130, 
                x60220, x60240, c18300, _taxbc, almsp, 
                brk6, MARS, _sep, brk2, almdep, cgrate1,
                cgrate2, amtys, amtsep, x62720, e00700, c24516, 
                c24520, c04800, e10105, c05700, e05800, e05100, e09600, 
                amtage, x62740, e62900, almsep, _earned, e62600, amtex, puf):

    c62720 = c24517 + x62720
    c60260 = e00700 + x60260
    ## QUESTION: c63100 variable is reassigned below before use, is this a BUG?
    c63100 = max(0., _taxbc - e07300)
    c60200 = min(c17000, 0.025 * _posagi)
    c60240 = c18300 + x60240
    c60220 = c20800 + x60220
    c60130 = c21040 + x60130
    c62730 = e24515 + x62730 

    _amtded = c60200 + c60220 + c60240
    if c60000 <= 0:

        _amtded = max(0., _amtded + c60000)
   
    if _exact == 0 or (_exact == 1 and ((_amtded + e60290) > 0)):
        _addamt = _amtded + e60290 - c60130


    if _cmp == 1:
        c62100 = (_addamt + e60300 + e60860 + e60100 + e60840 + e60630 + e60550
               + e60720 + e60430 + e60500 + e60340 + e60680 + e60600 + e60405
               + e60440 + e60420 + e60410 + e61400 + e60660 - c60260 - e60480
               - e62000 + c60000 - e60250)


    if (puf and (_standard == 0 or (_exact == 1 and e04470 > 0))):

        _edical = max(0., e17500 - max(0., e00100) * 0.075)
    else: _edical = 0.

    if (puf and ((_standard == 0 or (_exact == 1 and e04470 > 0))
        and f6251 == 1)):
        _cmbtp = (-1 * min(_edical, 0.025 * max(0., e00100)) + e62100 + c60260
               + e04470 + e21040 - _sit - e00100 - e18500 - e20800)
    else: _cmbtp = 0.

    if (puf == True and ((_standard == 0 or (_exact == 1 and e04470 > 0)))):
        c62100 = (c00100 - c04470 + min(c17000, 0.025 * max(0., c00100)) + _sit
               + e18500 - c60260 + c20800 - c21040 + _cmbtp)


    if (puf == True and ((_standard > 0 and f6251 == 1))):
        _cmbtp = e62100 - e00100 + c60260


    if (puf == True and _standard > 0):
        c62100 = (c00100 - c60260 + _cmbtp)
 


    if (c62100 > amtsep) and (MARS == 3 or MARS == 6):
        _amtsepadd = max(0., min(almsep, 0.25 * (c62100 - amtsep)))
    else: _amtsepadd = 0.
    c62100 = c62100 + _amtsepadd

    c62600 = max(0., amtex[MARS - 1] - 0.25 * max(0., c62100 - amtys[MARS - 1]))

    if DOBYR > 0:
        _agep = float(math.ceil((12 * (FLPDYR - DOBYR) - DOBMD / 100) / 12))
    else:
        _agep = 0.

    if SDOBYR > 0:
        _ages = np.ceil((12 * (FLPDYR - SDOBYR) - SDOBMD / 100) / 12)

    else: _ages = 0.

    if (_cmp == 1 and f6251 == 1 and _exact == 1):
        c62600 = e62600

    if _cmp == 1 and _exact == 0 and _agep < amtage and _agep != 0:
        c62600 = min(c62600, _earned + almdep)
  
    c62700 = max(0., c62100 - c62600)


    _alminc = c62700

    if (c02700 > 0):
        _alminc = max(0., c62100 - c62600 + c02700)

        _amtfei = 0.26 * c02700 + 0.02 * max(0., c02700 - almsp / _sep)
    else:
        _alminc = c62700

        _amtfei = 0.


    c62780 = 0.26 * _alminc + 0.02 * \
        max(0., _alminc - almsp / _sep) - _amtfei

    if f6251 != 0:
        c62900 = float(e62900)
    else: 
        c62900 = float(e07300)
    
    c63000 = c62780 - c62900

    if c24516 == 0:
        c62740 = c62720 + c62730
    else: 
        c62740 = min(max(0., c24516 + x62740), c62720 + c62730)
    
    
    _ngamty = max(0., _alminc - c62740)

    c62745 = 0.26 * _ngamty + 0.02 * \
        max(0., _ngamty - almsp / _sep)

    y62745 = almsp / _sep

    _tamt2 = 0.

    _amt5pc = 0.0

  
    _amt15pc = min(_alminc, c62720) - _amt5pc - min(max(
        0., brk2[MARS - 1] - c24520), min(_alminc, c62720))
    if c04800 == 0:
        _amt15pc = max(0., min(_alminc, c62720) - brk2[MARS - 1])
    
   
    _amt25pc = min(_alminc, c62740) - min(_alminc, c62720)
    
    if c62730 == 0:
        _amt25pc = 0.
    else: 
        _amt25pc = min(_alminc, c62740) - min(_alminc, c62720)
  
    c62747 = cgrate1 * _amt5pc

    
    c62755 = cgrate2* _amt15pc
    
    c62770 = 0.25 * _amt25pc
    
    _tamt2 = c62747 + c62755 + c62770
 

    _amt = 0.
  
    if _ngamty > brk6[MARS - 1]:
        _amt = 0.05 * min(_alminc, c62740)
    else: 
        _amt = 0.
    
    if _ngamty <= brk6[MARS - 1] and _alminc > brk6[MARS - 1]:
        _amt = 0.05 * min(_alminc - brk6[MARS - 1], c62740)


    _tamt2 = _tamt2 + _amt


    c62800 = min(c62780, c62745 + _tamt2 - _amtfei)
    c63000 = c62800 - c62900
    c63100 = _taxbc - e07300 - c05700
    c63100 = c63100 + e10105
    c63100 = max(0., c63100)

    c63200 = max(0., c63000 - c63100)
    c09600 = c63200
    _othtax = e05800 - (e05100 + e09600)

    c05800 = _taxbc + c63200

    return   (c62720, c60260, c63100, c60200, c60240, c60220,
              c60130, c62730, _addamt, c62100, _cmbtp, _edical,
              _amtsepadd, c62600, _agep, _ages,  c62700,
              _alminc, _amtfei, c62780, c62900, c63000, c62740,
              _ngamty, c62745, y62745, _tamt2, _amt5pc, _amt15pc,
              _amt25pc, c62747, c62755, c62770, _amt, c62800,
              c09600, _othtax, c05800)    


@iterate_jit(parameters=["dcmax", "puf"], nopython=True, puf=True)
def F2441(_earned, _fixeic, e59560, MARS, f2441, dcmax,
               e32800, e32750 , e32775, CDOB1, CDOB2, e32890, e32880, puf):

    if _fixeic == 1: 
        _earned = e59560

    if MARS == 2 and puf == True:
        c32880 = 0.5 * _earned
        c32890 = 0.5 * _earned
    else: c32880, c32890 = 0., 0.

    if MARS == 2 and puf == False:
        c32880 = max(0., e32880)
        c32890 = max(0., e32890)

    if MARS != 2:
        c32880 = _earned
        c32890 = _earned

    _ncu13 = 0.
    if puf == True:
        _ncu13 = f2441


    if puf == False and CDOB1 > 0:
        _ncu13 += 1

    if puf == False and CDOB2 > 0:
        _ncu13 += 1

    _dclim = min(_ncu13, 2.) * dcmax
    
    c32800 = min(max(e32800, e32750 + e32775), _dclim)

    #TODO deal with these types
    _earned = float(_earned)
    c32880 = float(c32880)
    c32890 = float(c32890)
    _ncu13 = float(_ncu13)

    return _earned, c32880, c32890, _ncu13, _dclim, c32800



@iterate_jit(nopython=True)
def DepCareBen(c32800, _cmp, MARS, c32880, c32890, e33420, e33430, e33450, 
                    e33460, e33465, e33470, _sep, _dclim, e32750, e32775, 
                    _earned):

    # Part III ofdependent care benefits
    if _cmp == 1  and MARS == 2:
        _seywage = min(c32880, c32890, e33420 + e33430 - e33450, e33460)
    else: 

        _seywage = 0.

    if _cmp == 1 and MARS != 2:  #this is same as above, why?
        _seywage = min(c32880, c32890, e33420 + e33430 - e33450, e33460)
   
    if _cmp == 1:
        c33465 = e33465
        c33470 = e33470
        c33475 = max(0., min(_seywage, 5000 / _sep) - c33470)
        c33480 = max(0., e33420 + e33430 - e33450 - c33465 - c33475)
        c32840 = c33470 + c33475

        c32800 = min(max(0., _dclim - c32840), max(0., e32750 + e32775 - c32840))

    else: 
        c33465, c33470, c33475, c33480, c32840 = 0.,0.,0.,0.,0.
        c32800 = c32800

    if MARS == 2:
        c33000 = max(0, min(c32800, min(c32880, c32890)))
    else: 
        c33000 = max(0, min(c32800, _earned))

    return _seywage, c33465, c33470, c33475, c33480, c32840, c32800, c33000




@iterate_jit(parameters=["pcmax", "agcmax"], nopython=True)
def ExpEarnedInc(  _exact, c00100, agcmax, pcmax,
                        c33000, c05800, e07300, e07180):
    # Expenses limited to earned income

    if _exact == 1: 

        _tratio = float(math.ceil(max((c00100 - agcmax)
                / 2000, 0.)))

        c33200 = c33000 * 0.01 * max(20., pcmax - min(15., _tratio))

    
    else: 
        _tratio = 0.

        c33200 = c33000 * 0.01 * max(20., pcmax
                - max((c00100 - agcmax) / 2000, 0.))

    c33400 = min(max(0., c05800 - e07300), c33200)

    # amount of the credit

    if e07180 == 0:

        c07180 = 0.
    else: 
        c07180 = c33400

    return _tratio, c33200, c33400, c07180



@iterate_jit(nopython=True)
def RateRed(c05800, _fixup, _othtax, _exact, x59560, _earned):

    # rate reduction credit for 2001 only, is this needed?
    c05800 = c05800
    c07970 = 0.


    if _fixup >= 3:
        c05800 = c05800 + _othtax

    if _exact == 1:
        c59560 = x59560
    else:
        c59560 = _earned 

    return c07970, c05800, c59560


@iterate_jit(parameters=["joint", "rtbase", "crmax", "rtless", "dylim", 
                         "ymax", "puf"], nopython=True, puf=True)
def NumDep(EICYB1, EICYB2, EICYB3,
                EIC, c00100, e00400, MARS, 
                ymax, joint, rtbase, c59560, crmax,
                rtless, e83080, e00300, e00600, e01000, e40223, 
                e25360, e25430, e25470, e25400, e25500, e26210,
                e26340, e27200, e26205, e26320, dylim, _cmp, SOIYR, 
                DOBYR, SDOBYR, _agep, _ages, c59660, puf):

    EICYB1 = max(0.0, EICYB1)
    EICYB2 = max(0.0, EICYB2)
    EICYB3 = max(0.0, EICYB3)

    if puf == True:
        _ieic = EIC
    else: 
        _ieic = int(EICYB1 + EICYB2 + EICYB3)

    # Modified AGI only through 2002

    _modagi = c00100 + e00400


    if MARS == 2 and _modagi > 0:
        _val_ymax = float((ymax[_ieic]
                    + joint[_ieic]))

    else: _val_ymax = 0.

    if (MARS == 1 or MARS == 4 or MARS == 5 or MARS == 7) and _modagi > 0:
        _val_ymax = float(ymax[_ieic])


    if (MARS == 1 or MARS == 4 or MARS == 5 or 
            MARS == 2 or MARS == 7) and _modagi > 0:

        c59660 = min(rtbase[_ieic] * c59560,
                crmax[_ieic])

        _preeitc = c59660 
    else: 

        c59660, _preeitc = 0., 0.

    if (MARS != 3 and MARS != 6 and _modagi > 0 and
            (_modagi > _val_ymax or c59560 > _val_ymax)):
        c59660 = max(0, c59660 - rtless[_ieic]
                * (max(_modagi, c59560) - _val_ymax))

    if MARS != 3 and MARS != 6 and _modagi > 0:
        _val_rtbase = rtbase[_ieic] * 100
        _val_rtless = rtless[_ieic] * 100
        _dy = (e00400 + e83080 + e00300 + e00600

                   + max(0., max(0., e01000) - max(0., e40223))
                   + max(0., max(0., e25360) - e25430 - e25470 - e25400 - e25500)
                   + max(0., e26210 + e26340 + e27200
                        - math.fabs(e26205) - math.fabs(e26320)))
    else:
        _val_rtbase = 0.
        _val_rtless = 0.
        _dy = 0.

    if (MARS != 3 and MARS != 6 and _modagi > 0 
            and _dy > dylim):
        c59660 = 0.

    if (_cmp == 1 and _ieic == 0 and SOIYR - DOBYR >= 25 and SOIYR - DOBYR < 65
        and SOIYR - SDOBYR >= 25 and SOIYR - SDOBYR < 65):
        c59660 = 0.
    
    if _ieic == 0 and (_agep < 25 or _agep >=65 or _ages <25 or _ages >= 65):
        c59660 = 0.


    return (_ieic, EICYB1, EICYB2, EICYB3, _modagi, c59660,
               _val_ymax, _preeitc, _val_rtbase, _val_rtless, _dy)


@iterate_jit(parameters=["_cphase", "chmax"], nopython=True)
def ChildTaxCredit(n24, MARS, chmax, c00100, _feided, _cphase, _exact, 
                        c11070, c07220, c07230, _num, _precrd, _nctcr):

    # Child Tax Credit
    if MARS == 2:
        _num = 2.

    _nctcr = n24

    _precrd = chmax * _nctcr

    _ctcagi = c00100 + _feided

    if _ctcagi > _cphase[MARS - 1] and _exact == 1:
        _precrd = max(0., _precrd - 50 * 
                    math.ceil(_ctcagi - _cphase[MARS - 1]) / 1000)

    if _ctcagi > _cphase[MARS - 1] and _exact != 1:
        _precrd = max(0., _precrd - 50 * 
                    (max(0., _ctcagi - _cphase[MARS - 1]) + 500) / 1000)

    #TODO get rid of this type declaration
    _precrd = float(_precrd)

    return (c11070, c07220, c07230, _num, _nctcr, _precrd, _ctcagi)

# def HopeCredit():
    # W/o congressional action, Hope Credit will replace 
    # American opportunities credit in 2018. NEED TO ADD LOGIC!!!


@iterate_jit(nopython=True)
def AmOppCr(_cmp, e87482, e87487, e87492, e87497):
    # American Opportunity Credit 2009+

    if _cmp == 1:

        c87482 = max(0., min(e87482, 4000.))
        c87487 = max(0., min(e87487, 4000.))
        c87492 = max(0., min(e87492, 4000.))
        c87497 = max(0., min(e87497, 4000.))
    else: 
        c87482, c87487, c87492, c87497 = 0.,0.,0.,0.

    if max(0, c87482 - 2000) == 0:
        c87483 = c87482
    else: 
        c87483 = 2000 + 0.25 * max(0, c87482 - 2000)

    if max(0, c87487 - 2000) == 0:
        c87488 = c87487
    else: 
        c87488 = 2000 + 0.25 * max(0, c87487 - 2000)

    if max(0, c87492 - 2000) == 0:
        c87493 = c87492
    else: 
        c87493 = 2000 + 0.25 * max(0, c87492 - 2000)

    if max(0, c87497 - 2000) == 0:
        c87498 = c87497
    else: 
        c87498 = 2000 + 0.25 * max(0, c87497 - 2000)


    c87521 = c87483 + c87488 + c87493 + c87498

    return (c87482, c87487, c87492, c87497,
               c87483, c87488, c87493, c87498, c87521)



@iterate_jit(parameters=['learn', 'puf'], nopython=True, puf=True)
def LLC(e87530, learn, e87526, e87522, e87524, e87528, c87540, c87550, puf):

    # Lifetime Learning Credit


    if puf == True:
        c87540 = float(min(e87530, learn))
        c87530 = 0.
    else:
        c87530 = e87526 + e87522 + e87524 + e87528
        c87540 = float(min(c87530, learn))


    c87550 = 0.2 * c87540

    return (c87540, c87550, c87530)



@iterate_jit(nopython=True)
def RefAmOpp(_cmp, c87521, _num, c00100, EDCRAGE, c87668):
    # Refundable American Opportunity Credit 2009+

    if _cmp == 1 and c87521 > 0: 
        c87654 = 90000 * _num 
        c87656 = c00100
        c87658 = np.maximum(0., c87654 - c87656)
        c87660 = 10000 * _num
        c87662 = 1000 * np.minimum(1., c87658 / c87660)
        c87664 = c87662 * c87521 / 1000.0
    else: 
        c87654, c87656, c87658, c87660, c87662, c87664 = 0., 0., 0., 0., 0., 0.

    if _cmp == 1 and c87521 > 0 and EDCRAGE == 1: 
        c87666 = 0.
    else: 
        c87666 = 0.4 * c87664

    if c87521 > 0 and _cmp == 1:
        c10960 = c87666
        c87668 = c87664 - c87666
        c87681 = c87666

    else: c10960, c87668, c87681 = 0., 0., 0.

    return (c87654, c87656, c87658, c87660, c87662,
               c87664, c87666, c10960, c87668, c87681)



@iterate_jit(parameters=["edphhm", "edphhs"], nopython=True)
def NonEdCr(c87550, MARS, edphhm, c00100, _num,
    c07180, e07200, c07230, e07240, e07960, e07260, e07300,
    e07700, e07250, t07950, c05800, _precrd, edphhs):

    # Nonrefundable Education Credits
    # Form 8863 Tentative Education Credits
    c87560 = c87550

    # Phase Out
    if MARS == 2:
        c87570 = float(edphhm * 1000)
    else:
        c87570 = float(edphhs * 1000)

    c87580 = float(c00100)


    c87590 = max(0., c87570 - c87580)

    c87600 = 10000.0 * _num

    c87610 = min(1., float(c87590 / c87600))

    c87620 = c87560 * c87610

    _ctc1 = c07180 + e07200 + c07230

    _ctc2 = e07240 + e07960 + e07260 + e07300

    _regcrd = _ctc1 + _ctc2

    _exocrd = e07700 + e07250

    _exocrd = _exocrd + t07950

    _ctctax = c05800 - _regcrd - _exocrd

    c07220 = min(_precrd, max(0., _ctctax))
    # lt tax owed
    
    return (c87560, c87570, c87580, c87590, c87600, c87610,
               c87620, _ctc1, _ctc2, _regcrd, _exocrd, _ctctax, c07220)



@iterate_jit(parameters=['adctcrt', 'ssmax', 'ealim', 'puf'],
                        nopython=True, puf=True)
def AddCTC(_nctcr, _precrd, c07220, e00200, e82882, e30100, _sey, _setax, 
                _exact, e82880, ealim, adctcrt, ssmax,
                e03260, e09800, c59660, e11200, e59680, e59700, e59720,
                _fixup, e11070, puf):

    # Additional Child Tax Credit


    c82940 = 0.

    # Part I of 2005 form 8812
    if _nctcr > 0:
        c82925 = _precrd

        c82930 = c07220

        c82935 = c82925 - c82930

        # CTC not applied to tax


        c82880 = max(0., e00200 + e82882 + e30100
                        + max(0., _sey) - 0.5 * _setax)
        if _exact == 1:
            c82880 = e82880

        h82880 = c82880


        c82885 = max(0., c82880 - ealim)

        c82890 = adctcrt * c82885

    else:
        c82925, c82930, c82935, c82880, h82880, c82885, c82890 = (0.,0., 0.,
            0., 0., 0., 0.)

    # Part II of 2005 form 8812

    if _nctcr > 2 and c82890 < c82935:
        c82900 = 0.0765 * min(ssmax, c82880)


        c82905 = float(e03260 + e09800)

        c82910 = c82900 + c82905
        
        c82915 = c59660 + e11200


        c82920 = max(0., c82910 - c82915)
        c82937 = max(c82890, c82920)


    else:

        c82900, c82905, c82910, c82915, c82920, c82937 = 0., 0., 0., 0., 0., 0.

    # Part II of 2005 form 8812
    if _nctcr > 2 and c82890 >= c82935:
        c82940 = c82935

    if _nctcr > 2 and c82890 < c82935:
        c82940 = min(c82935, c82937)

    if _nctcr > 0:
        c11070 = c82940
    else: 

        c11070 = 0.

                #WHY ARE WE SETTING AN 'E' VALUE HERE?     
    if puf == True and _nctcr > 0:
        e59660 = float(e59680 + e59700 + e59720)
    else:
        e59660 = 0.

    if _nctcr > 0:
        _othadd = e11070 - c11070
    else:
        _othadd = 0.

    if _nctcr  > 0 and _fixup >= 4:
        c11070 = c11070 + _othadd


    return ( c82925, c82930, c82935, c82880, h82880, c82885, c82890,
            c82900, c82905, c82910, c82915, c82920, c82937, c82940, c11070,
            e59660, _othadd)


def F5405(pm, rc):
    # Form 5405 First-Time Homebuyer Credit
    #not needed

    c64450 = np.zeros((rc.dim,))
    return DataFrame(data=np.column_stack((c64450,)), columns=['c64450'])


@iterate_jit(parameters=['puf'], nopython=True, puf=True)
def C1040( e07400, e07180, e07200, c07220, c07230, e07250,
                e07600, e07260, c07970, e07300, x07400, e09720,
                e07500, e07700, e08000, e07240, e08001, e07960, e07970,
                SOIYR, e07980, c05800, e08800, e09900, e09400, e09800, 
                e10000, e10100, e09700, e10050, e10075, e09805, e09710, 
                c59660, puf ):

    # Credits 1040 line 48

    x07400 = e07400
    c07100 = (e07180 + e07200 + c07220 + c07230 + e07250
              + e07600 + e07260 + c07970 + e07300 + x07400
              + e07500 + e07700 + e08000)

    y07100 = c07100

    c07100 = c07100 + e07240
    c07100 = c07100 + e08001
    c07100 = c07100 + e07960 + e07970

    if SOIYR >= 2009:
        c07100 = c07100 + e07980
 
    x07100 = c07100
    c07100 = min(c07100, c05800)

    # Tax After credits 1040 line 52

    _eitc = c59660

    c08795 = max(0., c05800 - c07100)

    c08800 = c08795

    if puf == True:

        e08795 = float(e08800)
    else:
        e08795 = 0.

    # Tax before refundable credits

    c09200 = c08795 + e09900 + e09400 + e09800 + e10000 + e10100
    c09200 = c09200 + e09700
    c09200 = c09200 + e10050
    c09200 = c09200 + e10075
    c09200 = c09200 + e09805
    c09200 = c09200 + e09710 + e09720

    return (c07100, y07100, x07100, c08795, c08800, e08795, c09200, _eitc)



@iterate_jit(nopython=True)
def DEITC(c08795, c59660, c09200, c07100):


    # Decomposition of EITC

    if c08795 > 0 and c59660 > 0 and c08795 <= c59660:
       c59680 = c08795

       _comb = c59660 - c59680

    else:   

        c59680 = 0.
        _comb = 0.

    if c08795 > 0 and c59660 > 0 and c08795 > c59660: 
        c59680 = c59660


    if (c08795 > 0 and c59660 > 0 and _comb > 0 and c09200 - c08795 > 0 and c09200 - c08795 > _comb): 
        c59700 = _comb
    else:
        c59700 = 0.

    if (c08795 > 0 and c59660 > 0 and _comb > 0 and c09200 - c08795 > 0 and c09200 - c08795 <= _comb):  
        c59700 = c59700 = c09200 - c08795
        c59720 = c59660 - c59680 - c59700

    else: c59720 = 0.

    if c08795 == 0 and c59660 > 0:
        c59680 = 0.

    if c08795 == 0 and c59660 > 0 and c09200 > 0 and c09200 > c59660:
        c59700 = c59660

    if c08795 == 0 and c59660 > 0 and c09200 > 0 and c09200 < c59660:
        c59700 = c09200
        c59720 = c59660 - c59700

    if c08795 == 0 and c59660 > 0 and c09200 <= 0:
        c59720 = c59660 - c59700

    # Ask dan about this section of code! e.g., Compb goes to zero


    if c08795 < 0 or c59660 <= 0:
        _compb = 0.
        c59680 = 0.
        c59700 = 0.
        c59720 = 0.

    else:
        _compb = 0.

    c07150 = c07100 + c59680
    c07150 = c07150
    c10950 = 0.

    return (c59680, c59700, c59720, _comb, c07150, c10950)



@iterate_jit(nopython=True)
def SOIT(   c09200, e10000, e59680, c59700,e11070, e11550, e11580,e09710, 
            e09720, e11581, e11582, e87900, e87905, e87681, e87682, c10950, 
            e11451, e11452, e11601, e11602, _eitc ):

    # SOI Tax (Tax after non-refunded credits plus tip penalty)
    # QUESTION, why not consolidate into one line??
    c10300 = c09200 - e10000 - e59680 - c59700
    c10300 = c10300 - e11070
    c10300 = c10300 - e11550
    c10300 = c10300 - e11580
    c10300 = c10300 - e09710 - e09720 - e11581 - e11582
    c10300 = c10300 - e87900 - e87905 - e87681 - e87682
    # QUESTION 'c10300 - c10300'a typo?
    c10300 = c10300 - c10300 - c10950 - e11451 - e11452
    c10300 = c09200 - e09710 - e09720 - e10000 - e11601 - e11602

    c10300 = max(c10300, 0.)

    # Ignore refundable partof _eitc to obtain SOI income tax

    if c09200 <= _eitc:
        _eitc = c09200

        c10300 = 0.

    return (c10300, _eitc)




@jit(nopython=True)
def Taxer_i(inc_in, MARS, rt1, rt2, rt3, rt4, rt5, rt6, rt7, brk1, brk2, brk3,
        brk4, brk5, brk6):
    ## note still should pass in all globals being used, including _rt1-_rt7 and _brk1-_brk6

    # low = 0 
    # med = 0

    # if inc_in < 3000:
    #     low = 1 

    # elif inc_in >=3000 and inc_in < 100000:
    #     med = 1 

    # _a1 = inc_in * 0.01

    # # if _a1 < 0:
    # #     _a2 = math.floor(_a1) - 1 
    # # else: _a2 = math.floor(_a1)
    # _a2 = math.floor(_a1)

    # _a3 = _a2 * 100

    # _a4 = (_a1 - _a2) * 100

    # _a5 = 0

    # if low == 1 and _a4 < 25:
    #     _a5 = 13
    # elif low == 1 and (25 <= _a4 < 50):
    #     _a5 = 38
    # elif low == 1 and (50 <= _a4 < 75):
    #     _a5 = 63
    # elif low == 1 and _a4 >= 75:
    #     _a5 = 88
    # elif med == 1 and _a4 < 50:
    #     _a5 = 25
    # elif med == 1 and _a4 >= 50: 
    #     _a5 = 75
    # if inc_in == 0:
    #     _a5 = 0

    # if low == 1 or med == 1:
    #     _a6 = _a3 + _a5 
    # else: _a6 = inc_in

    _a6 = inc_in

    inc_out = (rt1 * min(_a6, brk1[MARS - 1])
               + rt2
               * min(brk2[MARS - 1] - brk1[MARS - 1],
                            max(0., _a6 - brk1[MARS - 1]))
               + rt3
               * min(brk3[MARS - 1] - brk2[MARS - 1],
                            max(0., _a6 - brk2[MARS - 1]))
               + rt4
               * min(brk4[MARS - 1] - brk3[MARS - 1],
                            max(0., _a6 - brk3[MARS - 1]))
               + rt5
               * min(brk5[MARS - 1] - brk4[MARS - 1],
                            max(0., _a6 - brk4[MARS - 1]))
               + rt6
               * min(brk6[MARS - 1] - brk5[MARS - 1],
                            max(0., _a6 - brk5[MARS - 1]))
               + rt7 * max(0., _a6 - brk6[MARS - 1]))

    return inc_out
