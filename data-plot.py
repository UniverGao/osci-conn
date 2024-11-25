import matplotlib.pyplot as plt
import numpy as np
import csv

with open("file.csv", 'r') as file:
    line_reader = csv.reader(file)
    list_reader = list(line_reader)
    list_reader = np.array(list_reader[1:])
    list_reader = list_reader.T
    
    plt.plot(list_reader[0])
    plt.show()
