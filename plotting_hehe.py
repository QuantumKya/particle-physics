import matplotlib.pyplot as plt
import numpy as np

from hexadecimal_decimalwise import DataLooker



dl = DataLooker("EQUIP_12FEB2026_161338.txt")
dl.process_all_data()

_n = 2

detectorpts: list[list[tuple[int, int, str]]] = [[] for i in range(_n)]

for i in range(round(len(dl.datalist)/3)):
    ddata1 = dl.get_detector_data(i, 0)
    ddata2 = dl.get_detector_data(i, 1)
    
    def forthat(detector_data, index):
        if detector_data["rising"]["happened"]:
            pointmode = ("x" if detector_data["rising"]["new_trigger"] else "_") + " b"
            detectorpts[index].append((i, 2, pointmode))
        if detector_data["falling"]["happened"]:
            pointmode = ("x" if detector_data["falling"]["new_trigger"] else "_") + " r"
            detectorpts[index].append((i, 1, pointmode))
    
    forthat(ddata1, 0)
    forthat(ddata2, 1)






for i in range(_n):
    plt.subplot(_n, 1, i+1)
    plt.title("Detector #" + str(i+1))


    check = [False for r in range(4)]
    
    for pt in detectorpts[i]:
        typ = "Rising" if bool(pt[1]-1) else "Falling"
        nova = "(New)" if pt[2].find('x') != -1 else "(Repeat)"
        label = typ + " " + nova
        
        i = ["Rising (New)", "Rising (Repeat)", "Falling (New)", "Falling (Repeat)"].index(label)
        if i != -1 and not check[i]:
            check[i] = True
            plt.plot(*pt, label=label)
            continue
        
        plt.plot(*pt)
    
    plt.ylim(0, 3)
    plt.legend()


plt.tight_layout()
plt.show()