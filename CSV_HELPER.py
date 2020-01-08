import sys
class CSV_Object:
    def __init__(self, columnNames, values):
        self.columnNames = columnNames
        self.values = values

    def appendSelfToCSVFile(self, file):
        file = open(file,'a')
        file.write(self.convertValuesToCSV())
    def convertValuesToCSV(self):
        ret = ""
        for item in self.values:
            ret += str(item) + ","
        ret = ret[:-1]
        ret += "\n"
        return ret

def createCSVFromString(name, columnName, s):
    extension = "csv"
    try:
        name = name + "." + extension
        file = open(name, 'a')
        file.write(columnName +"\n"+ s[:-1])
        file.close()
    except:
        print("error occurred")
        sys.exit(0)


def createCSV(_name, csv_objects,i=0):
    columnNames = csv_objects[0].columnNames
    lines = columnNames + "\n"
    for s in csv_objects:
        lines += s.convertValuesToCSV()
    try:
        int(i)
        name = _name + "_"+ str(i+1)
    except:
        name = _name + i
    extension= "csv"
    try:
        name=name+"."+extension
        file=open(name,'a')
        file.write(lines)
        file.close()
    except:
            print("error occurred")
            sys.exit(0)


