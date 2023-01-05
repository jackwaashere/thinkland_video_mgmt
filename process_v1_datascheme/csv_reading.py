import csv
import os

"""
define flag, e.g. cmd(string)
define flag, working_dir = "xx/"

in main() {
    if (cmd == "parse_class_csv"):
        parse_class_csv(flag_class_csv_filepath)
    elif (cmd == "load_class_json")
        load_class_json()
}
"""

if __name__ == '__main__':
    print(os.getcwd())
    with open('test.csv', mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        firstRow = True
        for row in reader:
            if firstRow:
                firstRow = False
            else:
                print(f'Zoom ID: {row["Zoom ID"]}, Class Name: {row["Class Name"]}, Class Date: {row["Class Date"]}, Class Time: {row["Class Time (ET)"]}, Teacher Name: {row["Teacher Name"]}, Day of Week: {row["Day of Week"]}')

