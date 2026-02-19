# do something cool in Python please
def to_decimal(hex: str) -> int:
    num = 0
    for i, c in enumerate(hex):
        num += pow(16, len(hex)-i-1) * ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'].index(c)
    return num

def bit_from_byte(num: int, bid: int) -> bool:
    if bid >= 8:
        return False
    return not bool((num >> bid) % 2)

class DataLooker:
    def __init__(self, filename):
        self.datalist: list[dict] = []
        self.datalines: list[str] = []
        with open(filename, 'r') as file:
            in_data = False
            for line in file:
                linedata = line.strip()
                if linedata == 'Data Saved':
                    in_data = True
                    continue
                elif linedata == 'CE':
                    continue
                elif linedata == 'CD':
                    if in_data:
                        in_data = False
                    continue
                elif linedata == '':
                    continue
                
                if not in_data:
                    continue
                self.datalines.append(line.strip())
                self.datalist.append({})

    def process_data(self, i):
        data: dict = {}
        words: list[str] = self.datalines[i].split(' ')
        
        def get_word_val(i: int) -> int:
            return to_decimal(words[i])
        
        def get_data_block(i: int) -> dict:
            rising_edge_data = get_word_val(i)
            falling_edge_data = get_word_val(i+1)
            
            def data_from_byte(byt: int) -> dict:
                return {
                    "happened": bit_from_byte(byt, 5),
                    "new_trigger": bit_from_byte(byt, 7),
                    "tmc": byt % 32,
                }
            
            return {
                "rising": data_from_byte(rising_edge_data),
                "falling": data_from_byte(falling_edge_data)
            }
        
        
        # detector data
        data["detector_data"] = [
            get_data_block(1),
            get_data_block(3),
            get_data_block(5),
            get_data_block(7),
        ]
        
        
        # time and date information
        dateinfo = words[11]
        day = str(to_decimal(dateinfo[:2]))
        month = str(to_decimal(dateinfo[2:4]))
        year = str(to_decimal(dateinfo[4:6]))
        data["date"] = f"{day}/{month}/{year}"
        
        timedata = words[10]
        hour = str(to_decimal(timedata[:2]))
        minute = str(to_decimal(timedata[2:4]))
        second = str(to_decimal(timedata[4:6]))
        millisecond = str(to_decimal(timedata[7:10]))
        
        data["clock_check_time"] = {
            "internal": get_word_val(9),
            "utc": hour + ':' + minute + ':' + second + '.' + millisecond
        }
        
        data["internal_time"] = get_word_val(0)
        data["ppi_gps_time_difference"] = int(words[15])


        # gps and error data
        data["valid_gps"] = ({ "A": True, "V": False })[words[12]]
        data["sattelite_count"] = int(words[13])
        data["errors"] = int(words[14])

        self.datalist[i] = data

    def process_all_data(self):
        for i in range(len(self.datalines)):
            self.process_data(i)

    def get_data(self, datum_index):
        return self.datalist[datum_index]

    def get_detector_data(self, datum_index, detector_id):
        return self.get_data(datum_index)["detector_data"][detector_id]

    def print_detector_data(self, datum_index, detector_id):
        datum = self.get_detector_data(datum_index, detector_id)
        datestr = self.get_time_data(datum_index)["date"]
        print(f"Data from detector #{detector_id+1} on {datestr}:")
        
        def print_from_datum(section_name: str) -> bool:
            dat = datum[section_name]
            if dat["happened"]:
                print("\tThere was a " + section_name + " particle in this datum.")
                print("\tIt was " + ("" if dat["new_trigger"] else "not ") + "a new trigger.")
                print(f"\tThe TMC was {dat["tmc"]} ms.")
                print('')
                return True
            print("\tThere was no " + section_name + " particle in this datum.")
            return False
        
        print_from_datum("rising")
        print_from_datum("falling")
        return
        

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

decoder.process_data(0)
decoder.print_detector_data(0, 0)
decoder.print_detector_data(0, 1)
decoder.print_detector_data(0, 2)
decoder.print_detector_data(0, 3)
