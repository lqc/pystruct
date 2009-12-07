pyStruct
========

This module lets you describe binary structures by declaring 
python classes which syntanticly resamble C structures.

For example:

class Simple(CStruct):
   field = IntField()

Then packing and unpacking is very simple:

>>> obj = Simple(b'\x00\x00\x00\x05')
>>> print(obj.field)
5
>>> obj.bytes()
b'\x00\x00\x00\x05'


