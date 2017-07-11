# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 09:28:14 2017

@author: anj1
"""

import random
import matplotlib.pyplot as plt
import time
import jenks2
import numpy as np
from sklearn.cluster import DBSCAN

def genOffset(offset, dur):
    return [offset for i in range(dur)]

def genDrift(rate, dur):
    return [i*rate for i in range(1, dur+1)]

def genDriftWSync(frequency, rate, dur):
    ts = []
    curr = -rate
    for i in range(dur):
        if random.random() < frequency:
            curr = 0
        else:
            curr += rate
        ts.append(curr)
    return ts

# frequency is chance that the clock will jump
# jumpmin and jumpmax are the two values it jumps between
def genJumpy(frequency, jumpmin, jumpmax, dur):
    ts = []
    curr = random.choice([jumpmin, jumpmax])
    for i in range(dur):
        if random.random() < frequency:
            if curr == jumpmin:
                curr = jumpmax
            else:
                curr = jumpmin
        ts.append(curr)
    return ts
        
def genSpike(frequency, rate, jumpto, jumpdur, dur):
    ts = []
    curr = -rate
    jump = 0
    for i in range(dur):
        if jump == 0:
            curr = -rate
        if random.random() < frequency:
            jump = jumpdur
            curr = jumpto
        curr += rate
        ts.append(curr)
        jump -= 1
    return ts

def genRandJumps(frequency, minval, maxval, dur):
    ts = []
    curr = random.uniform(minval, maxval)
    nochange = int(random.choice([(frequency*dur*0.5), (frequency*dur*1.5)]))
    for i in range(dur):
        if nochange == 0:
            curr = random.uniform(minval, maxval)
            nochange = int(random.choice([(frequency*dur*0.5), (frequency*dur*1.5)]))
        ts.append(curr)
        nochange -= 1
    return ts

def genShared(ts1, ts2):
    ts = []
    for i in range(len(ts1)):
        if random.random() < 0.5:
            ts.append(ts1[i])
        else:
            ts.append(ts2[i])
    return ts  

def madOutliers(ts, threshold):
    med = ts[len(ts)//2]
    absdiff = [abs(t-med) for t in ts]
    meddiff = absdiff[len(absdiff)//2]
    if meddiff == 0:
        return [abs(t) > abs(med) for t in absdiff]
    else:
        return [(t*0.6745)/meddiff > threshold for t in absdiff]
 
def get_breaks(dataset, threshold):
    breaks = []
    cumul_mean, count, total = dataset[0], 1, 0
    for datapoint in dataset:
        total += 1
        if cumul_mean != 0 and abs(datapoint/cumul_mean) - 1 >= threshold:
            #print((datapoint/cumul_mean) - 1)
            breaks.append(count-1)
            cumul_mean = datapoint
            total = 0
        else:
            cumul_mean += (datapoint-cumul_mean)/(total)
        count += 1
        
    return breaks
    
def offsetClasses(ts_sorted, trend):
    classes = []
    threshold= 0.1
    class_total, prev_os, class_min = 0, ts_sorted[0], ts_sorted[0]
    if trend < 0:    
        for offset in ts_sorted:
            class_total += 1
            if 0 > (offset-prev_os) > (1+threshold)*trend:
                class_total += 1
                prev_os = offset
            else:
                classes.append((class_min, prev_os))
                class_min = offset
                class_total = 0
    else:
        for offset in ts_sorted:
            class_total += 1
            if 0 < (offset-prev_os) < (1+threshold)*trend:
                class_total += 1
                prev_os = offset
            else:
                classes.append((class_min, prev_os))
                class_min = offset
                class_total = 0
                
    return classes
        
def genChars(ts):
    zeroes = ts.count(0)
    ts_sorted = sorted(ts)
    slopes = [ts_sorted[i+1] - ts_sorted[i] for i in range(len(ts_sorted)-1)]
    prev_slope = slopes[0]
    slope_changes = 0
    for s in slopes:
        if prev_slope != 0 and not s/prev_slope > 0:
            slope_changes += 1
        prev_slope = s
        
    trendpoints, trendsum = 0, 0
    is_outlier = madOutliers(slopes, 3)
    for i in range(len(is_outlier)):
        if not is_outlier[i]:
            trendpoints += 1
            trendsum += slopes[i]
            
    print (len(is_outlier))
    print (trendpoints)
    avg_trend_len = len(ts)//(len(is_outlier)-trendpoints)
    trend_direction = 0 if trendsum == 0 else trendsum/abs(trendsum)
    avg_trend = trendsum/trendpoints
    offsets = offsetClasses(ts_sorted, avg_trend)
    print (avg_trend)
    return (zeroes, len(offsets), avg_trend_len, trend_direction)
    
def genChars_original(ts):
    # FIGURE OUT WHERE TO REPLACE SORTED TS
    ts_sorted = sorted(ts)
    tsmin = ts_sorted[0]
    tsmax = ts_sorted[-1]
    tsrange = tsmax-tsmin
    zeroes = ts.count(0)
    total = len(ts)
    if tsrange != 0:
        ts_scaled = [(p - tsmin)/tsrange for p in ts_sorted]
    else:
        ts_scaled = ts_sorted
    pointrates = []
    pointdiff = 0
    
    # FIGURE OUT WHAT THE DEAL WITH THIS IS
    # median offset
    med = ts_sorted[total//2]
    # absolute offset diff from median
    absdiff = [abs(t-med) for t in ts_sorted]
    # median offset diff
    meddiff = absdiff[len(absdiff)//2]
    
    for i in range(total-1):
        diff_scaled = ts_scaled[i+1]-ts_scaled[i]
        diff = abs(ts[i+1]-ts[i])
        # record all point differentials to search for anomalies
        pointrates.append(diff_scaled)
        # IS THIS EVEN NECESSARY
        # sum up total point differentials
        pointdiff += abs(diff)
    pointrates.sort()
    # determine potential behavior classes; rategroups is a list that contains
    # indices (in the sorted array) of determined breaks 
    isoutlier = madOutliers(pointrates, 3)
    trendpoints, trendsum = 0, 0
    for i in range(len(isoutlier)):
        if not isoutlier[i]:
            trendpoints += 1
            trendsum += pointrates[i]
    if trendsum > 0:
        trendrate = 1
    elif trendsum == 0:
        trendrate = 0
    else:
        trendrate = -1
    jumpfreq = (len(isoutlier) - trendpoints)
    print(jumpfreq)

    avgdiff = pointdiff/(total-1)
    jumpclasses = jenks2.classify_timeseries(ts)
    #return (jumpfreq, (len(jumpclasses)+1), trendrate, zeroes/total)
    return (trendrate, zeroes/total)

if __name__ == "__main__":
    rate = random.uniform(-1, 1)
    ts = genDriftWSync(0.05, rate, 1000)
    # CHECK IF IT'S PROPERLY DETERMINING OUTLIERS
    print (genChars(ts))
    plt.plot(ts)
    plt.show()
    
    """
    HOW THE CODE DEALS WITH RTT 
    qduration = t1-t0
    qdatetime = datetime.datetime.fromtimestamp(t0+qduration/2,pytz.utc)
    """

#    tslist = []
#    num_samples = 200
#    for i in range(num_samples):
#        tslist.append(genOffset(random.choice([random.randrange(1, 15), random.randrange(-15, -1)]), 1000))
#        tslist.append(genRandJumps(0.1, random.randrange(-15, 0), random.randrange(0, 15), 1000))
#        tslist.append(genSpike(0.001, 0, random.choice([random.randrange(1, 15), random.randrange(-15, -1)]), 1, 1000))
#        tslist.append(genJumpy(0.5, random.randrange(-15, -1), random.randrange(1, 15), 1000))
#        tslist.append(genDrift(random.uniform(1, 1), 1000))
#        tslist.append(genDriftWSync(0.01, random.uniform(-1, 1), 1000))
#    chars = []
#    starttime = time.time()
#    for ts in tslist:
#        chars.append(list(genCharacteristics(ts)))
#    endtime = time.time() - starttime
#    print ('Time to extract characteristics: ' + str(endtime))
#    starttime = time.time()
#    db = DBSCAN(eps=0.5, min_samples=10).fit(chars)
#    endtime = time.time() - starttime
#    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
#    core_samples_mask[db.core_sample_indices_] = True
#    labels = db.labels_
#    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
#    print ('Clustering time: ' + str(endtime))
#    print ('Estimated number of clusters: %d' % n_clusters_)
#
#    num_types = 6
#    typenames = ["Offset", "Rand Jumps", "Spike", "Jumpy", "Drift", "Drift w/ Sync"]
#    types = {}
#    avgs = []
#    for i in range(num_types):
#        types[i] = []
#        avgs.append(chars[num_types])
#        
#    i = 0
#    for label in labels:
#        types[i % num_types].append(label)
#        i += 1
#    i = 0
#        
#    for char in chars:
#        avgs[i % num_types] = list(map(sum, zip(avgs[i % num_types], char)))
#        i += 1
#    for i in range(num_types):
#        avgs[i] = [c/num_samples for c in avgs[i]]
#        
#    for i in range(num_types):
#        print (typenames[i])
#        print (types[i])
#        
#    for i in range(num_types):
#        print (avgs[i])
