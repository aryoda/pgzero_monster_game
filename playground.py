
class Test(object):

    __slots__ = ["inst_attr1", "inst_attr2", "_inst_attr3"]

    static_attr = 100

    def __init__(self, a = 1, b = 2):
        self.inst_attr1 = a
        self.inst_attr2 = b
        self._inst_attr3 = -3

    def __str__(self):
        return str(self.static_attr) + " / " + str(self.inst_attr1) + " / " + str(self.inst_attr2)

    @staticmethod
    def static_m1():
        return Test.static_attr

    @classmethod
    def class_m1(cls):
        return cls.static_attr

    @classmethod
    def class_m2(cls, some_value):
        pass

    # Starting with the Python version later than 2.6 you can use a Python decorator. The decorator method is used as getter method.
    # Declare getter method (@x.deleter would be a deleter method)
    # The deleter would be invoked when you delete the property using keyword del
    @property
    def inst_attr3(self):
        """This is the documentation for inst_attr3..."""
        return self._inst_attr3

    # Declare setter method (function name must be like this)
    @inst_attr3.setter
    def inst_attr3(self, value):
        self._inst_attr3 = value

    # property(fget, fset, fdel, doc)
    # or use:
    # inst_attr3 = property(__get_inst_attr3, __set_inst_attr3, doc = "your property doc")


    # For me make use of the @property decoration, you'll need to inherit from object

    # Abstract function (and classes):
    # https://stackoverflow.com/questions/372042/difference-between-abstract-class-and-interface-in-python
    def aMethod(self):

        NotImplementedError("Class %s doesn't implement aMethod()" % self.__class__.__name__)


t1 = Test()
t2 = Test(5, 6)
print(t1)
print(t2)
Test.static_attr = 200
print(t1)
print(t2)
print(Test.static_m1())
print(t1.static_m1())
print(t1.class_m1())
print(Test.class_m1())

t1._inst_attr3 = 3
t1.inst_attr3 = 3

# t1.inst_attr4 = 4  # AttributeError: 'Test' object has no attribute 'inst_attr4'
print(t1.inst_attr3)
print(t1._inst_attr3) # access to a protected member!

Test.static_attr2 = 2
print(Test.static_attr2)

# print(t1.__dict__)


# eine_globale_variable = "globale Variable"
#
# def test():
#
#     print("test() aufgerufen")
#
#     global eine_globale_variable
#
#     print(eine_globale_variable)
#
#     eine_lokale_variable = "locale Variable"
#
#     print(eine_lokale_variable)
#
#     eine_globale_variable = "immer noch eine global Variable"   # local variable 'eine_globale_variable' referenced before assignment
#
#     print("test() beendet")
#
#
# print(eine_globale_variable)
# test()
# print(eine_globale_variable)
# # print(eine_lokale_variable)



liste = ["eins", "zwei", "drei"]
for eintrag in liste:
    print(eintrag)
    if eintrag == "zwei":
        print("lösche")
        liste.remove(eintrag)

print(liste)


import sys
for dir in sys.path:
    print(dir)

import pgzero
pgzero.__file__
import numpy
# numpy.__file__
# dir(numpy)


print(__name__)

if __name__ == "__main__":
    print("wurde als main aufgerufen")


# Unit tests
# See: https://www.python-kurs.eu/python3_tests.php
import unittest

class AUnitTest(unittest.TestCase):

    def test1(self):

        t = Test(10, 20)

        self.assertEqual(t.static_attr, 200, "200 erwartet")
        self.assertGreater(t.inst_attr1, 9, "muss größer als 9 sein")

unittest.main()

