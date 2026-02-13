# do something cool in Python please
def to_decimal(hex):
    num = 0
    for i, c in enumerate(hex):
        num += pow(16, len(hex)-i-1) * ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'].index(c)
    return num

class DataLooker:
    def __init__(self, filename):
        self.datalist = []
        self.datalines = []
        with open(filename, 'r') as file:
            in_data = False
            for line in file:
                linedata = line.strip()
                if linedata == 'CE':
                    in_data = True
                elif linedata == 'CD':
                    in_data = False
                
                if not in_data:
                    continue
                self.datalines.append(line.strip())

    def process_data(self, i):
        data = {}

        words = self.datalines[i].split()
        
        def get_word_val(i):
            return to_decimal(words[i])
        
        def get_data_block(i):
            return {
                "rising": get_word_val(i),
                "falling": get_word_val(i+1)
            }
        data["detector_data"] = map(get_data_block, [1, 3, 5, 7])

        data["date"] = get_word_val(11)
        data["internal_time"] = get_word_val(0)
        data["clock_check_time"] = {
            "internal": get_word_val(9),
            "utc": float(words[10]),
        }
        data["ppi_gps_time_difference"] = int(words[15])

        data["valid_gps"] = ({ "A": True, "V": False })[words[12]]
        data["sattelite_count"] = int(words[13])
        data["errors"] = int(words[14])

        self.datalist.append(data)

    def get_data(self, datum_index):
        return self.datalist[datum_index]

    def get_detector_data(self, datum_index, detector_id):
        return self.get_data(datum_index)["detector_data"][detector_id]

    def was_error(self, datum_index):
        return self.get_data(datum_index)["errors"] > 0

    def was_valid_gps(self, datum_index):
        return self.get_data(datum_index)["valid_gps"]

    def get_time_data(self, datum_index):
        datum = self.get_data(datum_index)
        
        out = {}
        for key in ["date", "internal_time", "ppi_gps_time_difference"]:
            out[key] = datum[key]
        out["gps_clock_check"] = datum["clock_check_time"]
        
        return out


decoder = DataLooker("EQUIP_12FEB2026_161338.txt")
decoder.process_data()
