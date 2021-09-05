import sys
import re
import os
import math


# ======== split_n ========
# input : split_n("abcdefghijkl",3)
# output: ["abc","def","ghi","jkl"]
def split_n(text, n):
    return [text[i * n:i * n + n] for i in range(len(text) // n)]


def display(target_map):
    for k, v in target_map.items():
        print(k, v)


def main():
    os.makedirs('out', exist_ok=True)
    filepath = sys.argv[-1]
    filename = os.path.splitext(os.path.basename(filepath))[0]
    with open(filepath, encoding='utf8') as f:
        tap_notes_map = {}
        arrow_notes_map = {}
        long_notes_map = {}

        is_long_begin = {
            "1": False,
            "2": False,
            "3": False,
            "4": False,
        }

        lines = f.readlines()

        for line in lines:
            line = r'{}'.format(line)
            # tap
            pattern = '#(\d){3}1[1-4].*'
            match = re.match(pattern, line)
            if match:
                header = match.group().split(':')[0]
                data = match.group().split(':')[1]
                split = split_n(data, 2)
                for index, s in enumerate(split):
                    if s == "02":
                        split[index] = "1"
                    else:
                        split[index] = "."

                tap_notes_map.update({header: split})
                continue

            # arrow
            pattern = '#(\d){3}1[5-6].*'
            match = re.match(pattern, line)
            if match:
                header = match.group().split(':')[0]
                tmp_list = list(header)
                if tmp_list[5] == "5":
                    tmp_list[5] = "R"
                elif tmp_list[5] == "6":
                    tmp_list[5] = "L"

                header = "".join(tmp_list)

                data = match.group().split(':')[1]
                split = split_n(data, 2)
                for index, s in enumerate(split):
                    if s == "0A":
                        split[index] = "8"
                    elif s == "0B":
                        split[index] = "2"
                    elif s == "0C":
                        split[index] = "6"
                    elif s == "0D":
                        split[index] = "4"
                    else:
                        split[index] = "."

                arrow_notes_map.update({header: split})
                continue

            # long
            pattern = '#(\d){3}5[1-4].*'
            match = re.match(pattern, line)
            if match:
                header = match.group().split(':')[0]
                tmp_list = list(header)
                tmp_list[4] = '1'
                header = "".join(tmp_list)
                data = match.group().split(':')[1]
                split = split_n(data, 2)
                for index, s in enumerate(split):
                    if s == "02" and not is_long_begin[tmp_list[5]]:
                        split[index] = "2"
                        is_long_begin[tmp_list[5]] = True
                    elif s == "02" and is_long_begin[tmp_list[5]]:
                        split[index] = "3"
                        is_long_begin[tmp_list[5]] = False
                    else:
                        split[index] = "."

                long_notes_map.update({header: split})
                continue

        print("=====tap=====")
        display(tap_notes_map)
        print("=====arrow=====")
        display(arrow_notes_map)
        print("=====long=====")
        display(long_notes_map)

        notes_map = long_notes_map

        # merge tap notes and long notes
        for key, value in tap_notes_map.items():
            if key in long_notes_map:
                tap_size = len(value)
                long_size = len(long_notes_map[key])
                lcm = math.lcm(tap_size, long_size)
                tap_step = lcm // tap_size
                long_step = lcm // long_size
                tmp_list = ["." for _ in range(lcm)]
                print(tmp_list)
                for index, note in enumerate(value):
                    print(index * tap_step)
                    print(note)
                    tmp_list[index * tap_step] = note
                for index, note in enumerate(long_notes_map[key]):
                    if tmp_list[index * long_step] == '.':
                        tmp_list[index * long_step] = note
                print(value)
                print(long_notes_map[key])
                print(tmp_list)
                notes_map[key] = tmp_list
            else:
                notes_map[key] = value

        print("=====tap and long=====")
        display(notes_map)

        metadata = [
            "METADATA\n",
            "\tTITLE\tタイトル\n",
            "\tCOMPOSER\t作曲者名\n",
            "\tILLUSTRATOR\tジャケット作者名\n",
            "\tAUDIOFILEPATH\taudio.wav\n",
            "\tJACKETFILEPATH\tjacket.png\n",
            "\tTHEME\tOlynus\n",
            "\tOFFSET\t2\n",
            "\tDIFFICULTYID\t2\n",
            "\tDIFFICULTYNAME\tHard\n",
            "\tLEVEL\t8\n"
        ]

        metadata_str = "".join(metadata)

        measure = [
            "MEASURE\n",
            "\t1\t4/4\n"
        ]

        measure_str = "".join(measure)

        tempo = [
            "TEMPO\n",
            "\t1\t0+0/16\t120\n"
        ]

        tempo_str = "".join(tempo)

        layer = [
            "LAYER\n",
            "\tSPEED\n",
            "\t\t1\t0+0/16\t1\n"
            "\tNOTES\n"
        ]

        for key, value in notes_map.items():
            beat = int(key[1:4])
            lane = int(key[5])
            layer_str_line = "\t\t{0}\t{1}\t{2}\n".format(beat, lane, "".join(value))
            layer.append(layer_str_line)

        for key, value in arrow_notes_map.items():
            beat = int(key[1:4])
            lane = key[5]
            layer_str_line = "\t\t{0}\t{1}\t{2}\n".format(beat, lane, "".join(value))
            layer.append(layer_str_line)

        layer_str = "".join(layer)

        ctrg = "\n".join([metadata_str, measure_str, tempo_str, layer_str])

        with open("./out/{0}.ctrg".format(filename), encoding='utf8', mode='w') as f_w:
            f_w.write(ctrg)
            f_w.close()

        print("saved: ./out/{0}.ctrg".format(filename))
        print("--------end---------")


if __name__ == "__main__":
    main()
