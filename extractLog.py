""""
How to execute:
python extractlog <log-file.log> <out-directory> <no.-of-copies>
"""
import csv
import re
import sys
import numpy as np
import os
import errno
start = "CPU2006/"
end = "/run"
try:
    file1 = open(sys.argv[1], 'r')
    file2 = sys.argv[2]
    arg3 = int(sys.argv[3])
except:
    print ("Input 3 parameters: <in-file> <out-dir> <#-of-copies>")
    raise

arraylist = []
workload = []
total = []
count = 0
counters = []
for line in file1:
    if re.match("Specinvoke", line):
        result = re.search(re.escape(start) + "(.*)" + re.escape(end), line).group(1).strip(end)
        arraylist.append(result)
        counters.append(count)
        count = 0
    elif "Workload" in line:
        count = count + 1
        subsec = re.search('(\(\d*:\d*\))', line)
        s1 = subsec.group(1).strip("()")
        secs = re.search('([0-9]*\.[0-9]*)', line)
        s2 = secs.group(1)
        s3 = s1.split(":") + s2.split(" ")
        workload.append(s3)
    elif "Copy" in line:
        copy = re.search('(Copy [0-9]* )', line)
        elapsed = re.search('([0-9]+\.[0-9].*)', line)
        c1 = copy.group(1)
        c2 = elapsed.group(1)
        c3 = c1 + c2
        total.append(c3.split(" "))
counters = filter(lambda a1: a1 != 0, counters)
counters.insert(0, 0)
counter2 = []
cnt = 0
for ele in range(1, len(counters)):
    counter2.append(cnt + counters[ele])
    cnt = cnt + counters[ele]
counter2.insert(0, 0)
line = 1
start1 = 0
end1 = 1
start2 = 0
end2 = arg3
while end2 <= len(total):
    for item in total[start2:end2]:
        for list1 in workload[counter2[start1]:counter2[end1]]:
            if item[1] == list1[0]:
                total[line - 1].append(list1[2])
        line += 1
    start1 += 1
    end1 += 1
    start2 += arg3
    end2 += arg3
bench = []
for ele in arraylist:
    if ele not in bench:
        bench.append(ele)

tempd = []
for i in total:
    tempd.append(list(i))
cnt2 = 0
for i in total:
    i.pop(0)
    i.pop(0)
    i.insert(0, 'Copy' + str(cnt2))
    cnt2 += 1
    if cnt2 == arg3:
        cnt2 = 0

for data in tempd:
    data.pop(0)
    data.pop(0)

fin_data = []
cnt1 = 0
in2 = str()
header1 = [bench[cnt1], 'Total Elapsed Time']
try:
    os.makedirs(file2)
except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(file2):
        pass
    else:
        raise
for j in range(0, len(total), arg3):
    with open('./'+file2+'/' + bench[cnt1] + '.csv', 'wb') as csvfile:
        writer1 = csv.writer(csvfile, delimiter=',', quotechar='\n')
        for i in range(1, len(total[j]) - 1):
            in2 = 'Input' + str(i)
            header1.append(in2)
        writer1.writerow(header1)
        in2 = ''
        header1 = [bench[cnt1], 'Total Elapsed Time']
        for item in total[j:j + arg3]:
            writer1.writerow(item)
        fin_data.append(['Min', 'Max', 'Max_Min_delta', 'Mean', 'Median', 'Std Deviation'])
        for n in zip(*tempd[j:j + arg3]):
            temp_n = map(float, n)
            fin_data.append([min(n), max(n), str(float(max(n))/float(min(n))-1), np.mean(temp_n), np.median(temp_n), np.std(temp_n)])
        stat = [list(a) for a in zip(*fin_data)]
        for items in stat:
            writer1.writerow(items)
        fin_data[:] = []
        cnt1 += 1
