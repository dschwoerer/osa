#!/usr/bin/env python
# test_xmltypes_complex.py - test serialization of compound classes, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under GPLv3 or later, see the COPYING file.

import sys
for x in sys.path:
    if x.find("osa") != -1:
        sys.path.remove(x)
sys.path.append("../")

import unittest

import xml.etree.cElementTree as etree

from osa.xmltypes import *
from osa.xmlnamespace import *

ns_test = 'test_namespace'

Address = ComplexTypeMeta('Address', (), {
                "_children":[
                        {'name':"street", "type":XMLString, "min":1, "max": 1},
                        {'name':"city", "type":XMLString, "min":1, "max": 1},
                        {'name':"zip", "type":XMLInteger, "min":1, "max": 1},
                        {'name':"since", "type":XMLDateTime, "min":0, "max": 1},
                        {'name':"lattitude", "type":XMLDouble, "min":1, "max": 1},
                        {'name':"longitude", "type":XMLDouble, "min":1, "max": 1},
                        ], "__doc__": "an address info"})
Person = ComplexTypeMeta('Person', (), {
                "_children":[
                        {'name':"name", "type":XMLString, "min":0, "max": 1},
                        {'name':"birthdate", "type":XMLDateTime, "min":0, "max": 1},
                        {'name':"age", "type":XMLInteger, "min":0, "max": 1},
                        {'name':"addresses", "type":Address, "min":0, "max": 'unbounded'},
                        {'name':"titles", "type":XMLString, "min":0, "max": 'unbounded'},
                        ], "__doc__": "a person info"})

Employee = ComplexTypeMeta('Employee', (Person,), {
                "_children":[
                        {'name':"id", "type":XMLInteger, "min":1, "max": 1},
                        {'name':"salary", "type":XMLDouble, "min":1, "max": 1},
                        ], "__doc__": "an employee info"})

Level2 = ComplexTypeMeta('Level2', (), {
                "_children":[
                        {'name':"arg1", "type":XMLString, "min":1, "max": 1},
                        {'name':"arg2", "type":XMLDouble, "min":1, "max": 1},
                        ], "__doc__": "don't know"})

Level3 = ComplexTypeMeta('Level3', (), {
                "_children":[
                        {'name':"arg1", "type":XMLInteger, "min":1, "max": 1},
                        ], "__doc__": "don't know"})
Level4 = ComplexTypeMeta('Level4', (), {
                "_children":[
                        {'name':"arg1", "type":XMLString, "min":1, "max": 1},
                        ], "__doc__": "don't know"})

Level1 = ComplexTypeMeta('Level1', (), {
                "_children":[
                        {'name':"level2", "type":Level2, "min":1, "max": 1},
                        {'name':"level3", "type":Level3, "min":0, "max": 'unbouneded'},
                        {'name':"level4", "type":Level4, "min":0, "max": 'unbouneded'},
                        ], "__doc__": "don't know"})

class TestClassSerializer(unittest.TestCase):
    def test_simple_class(self):
        a = Address()
        a.street = '123 happy way'
        a.city = 'badtown'
        a.zip = 32
        a.lattitude = 4.3
        a.longitude = 88.0

        element = etree.Element('test')
        a.to_xml( element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        self.assertEquals(5, len(element.getchildren()))

        r = Address().from_xml(element)

        self.assertEquals(a.street, r.street)
        self.assertEquals(a.city, r.city)
        self.assertEquals(a.zip, r.zip)
        self.assertEquals(a.lattitude, r.lattitude)
        self.assertEquals(a.longitude, r.longitude)
        self.assertEquals(a.since, r.since)

    def test_nested_class(self):
        p = Person()
        element = etree.Element('test')
        p.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEquals(None, p.name)
        self.assertEquals(None, p.birthdate)
        self.assertEquals(None, p.age)
        self.assertEquals(None, p.addresses)

    def test_complex_class(self):
        l = Level1()
        l.level2 = Level2()
        l.level2.arg1 = 'abcd'
        l.level2.arg2 = 1.0/3.0
        l.level3 = []
        l.level4 = []

        for i in range(0, 100):
            a = Level3()
            a.arg1 = i
            l.level3.append(a)

        for i in range(0, 4):
            a = Level4()
            a.arg1 = str(i)
            l.level4.append(a)

        element = etree.Element('test')
        l.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        l1 = Level1().from_xml(element)

        self.assertEquals(l1.level2.arg1, l.level2.arg1)
        self.assertEquals(l1.level2.arg2, l.level2.arg2)
        self.assertEquals(len(l1.level4), len(l.level4))
        self.assertEquals(len(l1.level3), len(l.level3))
        for i in range(100):
            self.assertEquals(l1.level3[i].arg1, l.level3[i].arg1)
        for i in range(4):
            self.assertEquals(l1.level4[i].arg1, l.level4[i].arg1)


    def test_any(self):
        a = Address()
        a.street = '123 happy way'
        a.city = 'badtown'
        a.zip = 32
        a.lattitude = 4.3
        a.longitude = 88.0

        element = etree.Element('test')
        a.to_xml( element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        element.set("{%s}type" %NS_XSI, 'Address')

        XMLAny._types = {'Person':Person, 'Address':Address, 'Level4':Level4,
                        'Level3':Level3, 'Level2': Level2, 'Level1':Level1}

        r = XMLAny().from_xml(element)
        self.assertTrue(isinstance(r, Address))

        self.assertEquals(a.street, r.street)
        self.assertEquals(a.city, r.city)
        self.assertEquals(a.zip, r.zip)
        self.assertEquals(a.lattitude, r.lattitude)
        self.assertEquals(a.longitude, r.longitude)
        self.assertEquals(a.since, r.since)
    def test_tofrom_file(self):
        fname = "out.xml"
        a = Address()
        a.street = '123 happy way'
        a.city = 'badtown'
        a.zip = 32
        a.lattitude = 4.3
        a.longitude = 88.0
        try:
            os.remove(fname)
        except:
            pass
        a.to_file(fname)
        b = Address.from_file(fname)
        self.assertEquals(b, a)
        self.assertTrue(b is not a)

if __name__ == '__main__':
    unittest.main()