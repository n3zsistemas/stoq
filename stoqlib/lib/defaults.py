# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2008 Async Open Source
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
##
## Author(s):       Evandro Vale Miquelito      <evandro@async.com.br>
##                  Henrique Romano             <henrique@async.com.br>
##                  Johan Dahlin                <jdahlin@async.com.br>
##
"""Default values for applications"""

import ctypes
from ctypes.util import find_library
import re

from decimal import Decimal

from dateutil import relativedelta

from stoqlib.lib.translation import stoqlib_gettext

_ = stoqlib_gettext

MINIMUM_PASSWORD_CHAR_LEN = 6

#
# Unicode related
#

# "Used to replace an incoming character whose value is unknown or
#  undefined in Unicode"
UNKNOWN_CHARACTER = u"\N{REPLACEMENT CHARACTER}"

#
# Dates and time
#

(INTERVALTYPE_DAY,
 INTERVALTYPE_WEEK,
 INTERVALTYPE_MONTH,
 INTERVALTYPE_YEAR) = range(4)

interval_types = {INTERVALTYPE_DAY:      _('Days'),
                  INTERVALTYPE_WEEK:     _('Weeks'),
                  INTERVALTYPE_MONTH:    _('Months'),
                  INTERVALTYPE_YEAR:     _('Years')}

interval_values = {INTERVALTYPE_DAY:        1,
                   INTERVALTYPE_WEEK:       7,
                   INTERVALTYPE_MONTH:      30,
                   INTERVALTYPE_YEAR:       365}

# weekday constants

NL_TIME_WEEK_1STDAY = 131174
NL_TIME_FIRST_WEEKDAY = 131176

# C library

_libc = None

def get_libc():
    """Returns an accessor to C library.

    @returns: a ctypes.CDLL instance
    """
    global _libc
    if _libc is None:
        _libc = ctypes.CDLL(find_library("c"))
    return _libc


def calculate_interval(interval_type, intervals):
    """Get the interval type value for a certain INTERVALTYPE_* constant.
    Intervals are useful modes to calculate payment duedates.

    @param interval_type:
    @param intervals:
    @returns:

    >>> calculate_interval(INTERVALTYPE_DAY, 5)
    5

    >>> calculate_interval(INTERVALTYPE_MONTH, 3)
    90

    >>> calculate_interval(INTERVALTYPE_YEAR, 10)
    3650

    """
    if not interval_values.has_key(interval_type):
        raise KeyError('Invalid interval_type %r argument for '
                       'calculate_interval function.' % (interval_type,))
    if not type(intervals) == int:
        raise TypeError('Invalid type for intervals argument. It must be '
                        'integer, got %s' % type(intervals))
    return interval_values[interval_type] * intervals


def get_weekday_start():
    """Returns the dateutil.relativedelta.weekday based on the current locale.

    @returns: a dateutil.realtivedelta.weekday instance
    """
    libc = get_libc()

    week_origin = libc.nl_langinfo(NL_TIME_WEEK_1STDAY)
    # we will set week_1sday based on the dateutil.relativedelta.weekday mapping
    if week_origin == 19971130: # Sunday
        week_1stday = 6
    elif week_origin == 19971201: # Monday
        week_1stday = 0
    else:
        raise TypeError('Unknown NL_TIME_WEEK_1STDAY constant')

    v = libc.nl_langinfo(NL_TIME_FIRST_WEEKDAY)
    first_weekday = ord(ctypes.cast(v, ctypes.c_char_p).value[0])
    week_start = (week_1stday + first_weekday - 1) % 7

    return relativedelta.weekday(week_start)


#
# Payments
#

def payment_value_colorize(column_data):
    """A helper method for payment value columns used to set different
    colors for negative values
    """
    return column_data < 0


#
# Kiwi combobox
#

ALL_ITEMS_INDEX = -1

ALL_BRANCHES = _('All branches'), ALL_ITEMS_INDEX

#
# Common methods
#

def get_country_states():
    # This is Brazil-specific information.
    return [ 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
             'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
             'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO' ]


def _split_parts(a):
    parts = re.findall('(\d+|\D+)', a)
    for i in xrange(len(parts)):
        try: parts[i] = int(parts[i])
        except: pass
    return parts

def sort_sellable_code(a, b):
    return cmp(_split_parts(a), _split_parts(b))


#
# Decimal precision
#

DECIMAL_PRECISION = 2
QUANTITY_PRECISION = 3
_format = Decimal('10e-%d' % DECIMAL_PRECISION)

def quantize(dec):
    """Quantities a decimal according to the current settings.
    if DECIMAL_PRECISION is set to two then everything but
    the last two decimals will be removed

    >>> quantize(Decimal("10.123"))
    Decimal('10.12')

    >>> quantize(Decimal("10.678"))
    Decimal('10.68')
    """
    return dec.quantize(_format)
