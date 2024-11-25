import pyvisa
rm = pyvisa.ResourceManager()
t = rm.list_resources()
print(t)
