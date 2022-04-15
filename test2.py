class Foo():
     
     def del_self(self):
          del self

a = Foo()
print(a)
a.del_self()
print(a)