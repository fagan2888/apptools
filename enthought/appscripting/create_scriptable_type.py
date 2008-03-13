#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought application scripting package component>
#------------------------------------------------------------------------------


# Standard library imports.
import inspect
import types

# Enthought library imports.
from enthought.traits.api import HasTraits

# Local imports.
from package_globals import get_script_manager
from scriptable import scriptable, Scriptable


def create_scriptable_type(scripted_type, api=None, includes=None, excludes=None):
    """Create and return a new type based on the given scripted_type that will
    (by default) have its public methods and traits (ie. those not beginning
    with an underscore) made scriptable.  If api is given then it is a class,
    or a list of classes, that define the attributes that will be made
    scriptable.  Otherwise if includes is given it is a list of names of
    attributes that will be made scriptable.  Otherwise all the public
    attributes of scripted_type will be made scriptable except those in the
    excludes list."""

    def __init__(self, *args, **kwargs):
        """Initialise the dynamic sub-class instance."""

        get_script_manager().new_object(self, scripted_type, args, kwargs)
        scripted_type.__init__(self, *args, **kwargs)

    # See if we need to pull all attribute names from a type.
    if api is not None:
        if isinstance(api, list):
            src = api
        else:
            src = [api]
    elif includes is None:
        src = [scripted_type]
    else:
        names = includes
        src = None

    if src:
        ndict = {}

        for cls in src:
            if issubclass(cls, HasTraits):
                for n in cls.class_traits().keys():
                    if not n.startswith('_') and not n.startswith('trait'):
                        ndict[n] = None

            for c in inspect.getmro(cls):
                if c is HasTraits:
                    break

                for n in c.__dict__.keys():
                    if not n.startswith('_'):
                        ndict[n] = None

        # Respect the excludes so long as there was no explicit API.
        if api is None and excludes is not None:
            for n in excludes:
                try:
                    del ndict[n]
                except KeyError:
                    pass

        names = ndict.keys()

    # Create the type dictionary containing replacements for everything that
    # needs to be scriptable.
    type_dict = {'__init__': __init__}

    if issubclass(scripted_type, HasTraits):
        traits = scripted_type.class_traits()

        for n in names:
            trait = traits.get(n)

            if trait is not None:
                type_dict[n] = Scriptable(trait)

    for n in names:
        try:
            attr = getattr(scripted_type, n)
        except AttributeError:
            continue

        if type(attr) is types.MethodType:
            type_dict[n] = scriptable(attr)

    type_name = 'Scriptable(%s)' % scripted_type.__name__

    return type(type_name, (scripted_type, ), type_dict)
