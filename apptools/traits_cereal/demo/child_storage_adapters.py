#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apptools.traits_cereal.aits.api import Instance, provides
from apptools.traits_cereal.aits.adaptation.adaptation_manager import (
    adaptation_manager as GLOBAL_ADAPTATION_MANAGER)

from storables import Child
from apptools.traits_cereal.storage_manager import IDeflatable, IInflatable, Blob
from apptools.traits_cereal.default_storage_adapters import (
    DefaultDeflator, DefaultInflator)


@provides(IDeflatable)
class ChildToIDeflatable(DefaultDeflator):
    # class_name = 'Child'
    version = 2
    adaptee = Instance(Child)

    def deflate(self):
        blob = super(ChildToIDeflatable, self).deflate()
        # Could change blob.class_name here
        return blob


@provides(IInflatable)
class ChildToIInflatable1(DefaultInflator):
    adaptee = Instance(Blob)

    def inflate(self, get_obj_by_uuid, reify=True):
        print("Loading Child v1")
        self.adaptee = super(ChildToIInflatable1, self).inflate(
            get_obj_by_uuid, reify=False)
        return Child(**self.adaptee.attrs)


@provides(IInflatable)
class ChildToIInflatable2(DefaultInflator):
    adaptee = Instance(Blob)

    def inflate(self, get_obj_by_uuid, reify=True):
        print("Loading Child v2")
        self.adaptee = super(ChildToIInflatable2, self).inflate(
            get_obj_by_uuid, reify=False)
        return Child(**self.adaptee.attrs)


CHILD_DESERIALIZERS = {
    1: ChildToIInflatable1,
    2: ChildToIInflatable2
}


def child_to_IInflatable(adaptee):
    # class_name is potentially fully qualified.
    # We should discuss if this will make any sense or not long term.
    if adaptee.class_name.endswith('Child'):
        factory = CHILD_DESERIALIZERS[adaptee.version]
        return factory(adaptee=adaptee)


def register_adapters(adaptation_manager=GLOBAL_ADAPTATION_MANAGER):
    adaptation_manager.register_factory(
        ChildToIDeflatable, Child, IDeflatable)
    adaptation_manager.register_factory(
        child_to_IInflatable, Blob, IInflatable)
