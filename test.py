import re

if __name__ == "__main__":
    count = 0
    lines = 0
    outfile = open("test.txt", 'w')
    with open("timeseries.txt", 'r') as infile:
        for line in infile:
            lines += 1
            if re.search('[a-zA-Z]', line) != None:
                count += 1
            else:
                outfile.write(line)
    outfile.close()
    print (str(count))
    print (str(lines))
