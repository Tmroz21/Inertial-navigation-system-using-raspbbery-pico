import serial
import pandas as pd


ser = serial.Serial('/dev/tty.usbmodem143201')
results = []
data = ''
it = 0
while 1:
# for i in range(0, 500000):
    s = ser.read()
    r = s.decode('utf-8')
    if it == 1000:
        break
    if r == ' ':
        data = data + ','

    if r == '|':
        data = data[2:len(data)]
        results.append(data)
        data = ''
        it = it + 1
    else:
        data = data + r

f = open('pomiar4.txt', 'w')  # otwieramy/tworzymy plik pomiar1.txt w trybie do odczytu
for line in results:  # iterujamy listę results
    f.write(line + '\n')  # i w każdej iteracji zapisujemy kolejny element listy do pliku
f.close()