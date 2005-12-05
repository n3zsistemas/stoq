# -*- Mode: Python; coding: iso-8859-1 -*-
# vi:si:et:sw=4:sts=4:ts=4
#
# Copyright (C) 2005 Async Open Source
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

"""
gui/editors.py:

    Base classes for editors
"""

import gettext

from kiwi.ui.delegates import SlaveDelegate

from stoqlib.gui.dialogs import BasicWrappingDialog
from stoqlib.exceptions import EditorError

_ = gettext.gettext

class BaseEditorSlave(SlaveDelegate):
    """ Base class for editor slaves inheritance. It offers methods for
    setting up focus sequence, required attributes and validated attrs.
    """
    gladefile = None
    widgets = ()
    model_type = None

    def __init__(self, conn, model=None):
        # The model attribute represents the main object that has been
        # edited by an interface. It will be always the object the is sent
        # from a kiwi list to an editor.
        self.conn = conn
        self.edit_mode = model is not None
        if self.model_type:
            model = model or self.create_model(self.conn)
            if model and not isinstance(model, self.model_type):
                raise TypeError('%s editor requires a model of type %s, '
                                'got a %r' % (self.__class__.__name__,
                                              self.model_type,
                                              model))
        else:
            model = None
        self.model = model 
        SlaveDelegate.__init__(self, gladefile=self.gladefile,
                               widgets=self.widgets)
        self.setup_proxies()
        self.setup_slaves()


    def create_model(self, conn):
        """
        It is expected to return a new model, which will be used if a model
        wasn't sent to the object at instantiation time.
        The default behavior is to raise a TypeError, which can
        be overridden in a subclass.
        """
        raise TypeError("%r needs a model, got None. Perhaps you want to "
                        "implement create_model?" % self)
    
    def setup_proxies(self):
        """ This method should be defined in each child. """

    def setup_slaves(self):
        """ This method should be defined in each child. """



    #
    # Hook methods
    #



    def on_cancel(self):
        """ This is a hook method which must be redefined when some
        action needs to be executed when cancelling in the dialog. """
        return False

    def on_confirm(self):
        """ This is a hook method which must be redefined when some
        action needs to be executed when confirming in the dialog. """
        return self.model

    def validate_confirm(self):
        """ Must be redefined by childs and will perform some validations
        after the click of ok_button. It is interesting to use with some
        special validators that provide some tasks over more than one widget
        value """
        return True


class BaseEditor(BaseEditorSlave):
    """ Base class for editor dialogs. It offers methods of
    BaseEditorSlave, a windows title and OK/Cancel buttons. 

    model_name      =  the model type name of the model we are editing. 
                       This value will be showed in the title of
                       the editor and can not be merely the attribute 
                       __name__ of the object for usability reasons.
                       Callsites will decide what could be the best name
                       applicable in each situation.

    get_title_model_attribute = get a certain model attribute value to
                                allow creating customized editor titles.
                                Subclasses will choose the right attribute
                                acording to the editor features and
                                with usability in mind.
                                The editor title has this format: 
                                'Edit "title_model_attr" Details'
    """

    model_name = None
    header = ''
    size = ()

    def __init__(self, conn, model=None):
        BaseEditorSlave.__init__(self, conn, model)
        # We can not use self.model for get_title since we will create a new
        # one in BaseEditorSlave if model is None.
        self.main_dialog = BasicWrappingDialog(self,
                                               self.get_title(model),
                                               self.header, self.size)
        self.register_validate_function(self.refresh_ok)
        self.force_validation()

    def get_title(self, model):
        if model:
            model_attr = self.get_title_model_attribute(model)
            return _('Edit "%s" Details') % model_attr
        if not self.model_name:
            raise EditorError('A model_name attribute is required')
        return _('Add %s') % self.model_name

    def get_title_model_attribute(self, model):
        raise NotImplementedError

    def refresh_ok(self, validation_value):
        """ Refreshes ok button sensitivity according to widget validators
        status """
        self.main_dialog.ok_button.set_sensitive(validation_value)

class SimpleEntryEditor(BaseEditor):
    """Editor that offers a generic entry to input a string value."""
    gladefile = "SimpleEntryEditor"
    widgets = ('name_entry', 'name_entry_label')
    
    def __init__(self, conn, model, attr_name, name_entry_label='Name:',
                 title=''):
        self.title = title
        self.attr_name = attr_name
        BaseEditor.__init__(self, conn, model)
        self.name_entry_label.set_text(name_entry_label)

    def setup_proxies(self):
        assert self.model
        self.name_entry.set_property('model-attribute', self.attr_name)
        proxy = self.add_proxy(model=self.model, widgets=['name_entry'])

class NoteEditor(BaseEditor):
    """ Simple editor that offers a label and a textview. """
    gladefile = "NoteSlave"
    widgets = ('notes', )
    size = (500, 200)

    def __init__(self, conn, model, attr_name, title=''):
        assert model, ("You must supply a valid model to this editor "
                       "(%r)" % self)
        self.model_type = type(model)
        self.title = title
        self.attr_name = attr_name

        BaseEditor.__init__(self, conn, model)
        self.notes.set_accepts_tab(False)

    # 
    # BaseEditor hooks
    #

    def setup_proxies(self):
        self.notes.set_property('model-attribute', self.attr_name)
        proxy = self.add_proxy(model=self.model, widgets=self.widgets)


    def get_title(self, *args):
        return self.title
