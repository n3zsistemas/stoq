# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2012 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##

import mock

from kiwi.currency import currency

from stoqlib.exceptions import TillError
from stoqlib.domain.events import (TillOpenEvent, TillAddCashEvent,
                                   TillRemoveCashEvent)
from stoqlib.domain.payment.payment import Payment
from stoqlib.gui.uitestutils import GUITest
from stoqlib.gui.editors.tilleditor import (TillClosingEditor,
                                            TillOpeningEditor,
                                            CashAdvanceEditor,
                                            CashInEditor, CashOutEditor)


def _till_event(*args, **kwargs):
    raise TillError("ERROR")


class _BaseTestTillEditor(GUITest):
    need_open_till = False

    def setUp(self):
        super(_BaseTestTillEditor, self).setUp()
        if self.need_open_till:
            self.till = self.create_till()
            self.till.open_till()


class TestTillOpeningEditor(_BaseTestTillEditor):
    need_open_till = False

    def testCreate(self):
        editor = TillOpeningEditor(self.trans)
        self.check_editor(editor, 'editor-tillopening-create')

    @mock.patch('stoqlib.gui.editors.tilleditor.warning')
    def testConfirm(self, warning):
        editor = TillOpeningEditor(self.trans)

        TillOpenEvent.connect(_till_event)
        editor.confirm()
        warning.assert_called_once_with("ERROR")
        self.assertEqual(editor.retval, False)

        TillOpenEvent.disconnect(_till_event)
        editor.confirm()
        self.assertEqual(editor.retval, editor.model)


class TestTillClosingEditor(_BaseTestTillEditor):
    need_open_till = True

    def testCreate(self):
        editor = TillClosingEditor(self.trans)
        self.check_editor(editor, 'editor-tillclosing-create')

    @mock.patch('stoqlib.gui.editors.tilleditor.warning')
    def testConfirm(self, warning):
        editor = TillClosingEditor(self.trans)

        editor.model.value = editor.model.till.get_balance() + 1
        self.assertFalse(editor.confirm())
        warning.assert_called_once_with(
            "The amount that you want to remove is "
            "greater than the current balance.")
        editor.model.value = editor.model.till.get_balance()
        self.assertTrue(editor.confirm())


class TestCashInEditor(_BaseTestTillEditor):
    need_open_till = True

    def testCreate(self):
        editor = CashInEditor(self.trans)
        self.check_editor(editor, 'editor-cashin-create')

    @mock.patch('stoqlib.gui.editors.tilleditor.warning')
    def testConfirm(self, warning):
        editor = CashInEditor(self.trans)
        self.assertNotSensitive(editor.main_dialog, ['ok_button'])
        editor.cash_slave.proxy.update('value', currency(10))
        self.assertSensitive(editor.main_dialog, ['ok_button'])

        TillAddCashEvent.connect(_till_event)
        editor.confirm()
        self.assertEqual(editor.retval, False)
        warning.assert_called_once_with("ERROR")

        TillAddCashEvent.disconnect(_till_event)
        editor.confirm()
        self.assertEqual(editor.retval, editor.model)


class TestCashOutEditor(_BaseTestTillEditor):
    need_open_till = True

    def testCreate(self):
        editor = CashOutEditor(self.trans)
        self.check_editor(editor, 'editor-cashout-create')

    @mock.patch('stoqlib.gui.editors.tilleditor.warning')
    def testConfirm(self, warning):
        # Add some amount to till so it can be removed above
        p = self.create_payment(payment_type=Payment.TYPE_IN,
                                value=currency(50))
        self.till.add_entry(p)

        editor = CashOutEditor(self.trans)
        self.assertNotSensitive(editor.main_dialog, ['ok_button'])
        editor.cash_slave.proxy.update('value', currency(10))
        self.assertSensitive(editor.main_dialog, ['ok_button'])

        TillRemoveCashEvent.connect(_till_event)
        editor.confirm()
        self.assertEqual(editor.retval, False)
        warning.assert_called_once_with("ERROR")

        TillRemoveCashEvent.disconnect(_till_event)
        editor.confirm()
        self.assertEqual(editor.retval, editor.model)


class TestCashAdvanceEditor(_BaseTestTillEditor):
    need_open_till = True

    def testCreate(self):
        editor = CashAdvanceEditor(self.trans)
        self.check_editor(editor, 'editor-cashadvance-create')
