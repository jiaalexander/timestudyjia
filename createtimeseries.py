import pymysql
import re
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def mysqlConnect():
    mc = {"host":"db1.antd.nist.gov",
          "user":"anj1",
          "passwd":"dbwr1te!",
          "port":0,
          "db":"time",
          "mysqldump":"mysqldump"}
    conn = pymysql.connect(host=mc["host"], port=int(mc["port"]), user=mc["user"], passwd=mc["passwd"], db=mc["db"])
    conn.cursor().execute("set innodb_lock_wait_timeout=20")
    conn.cursor().execute("set tx_isolation='READ-COMMITTED'")
    conn.cursor().execute("set time_zone = '+00:00'")
    return conn

def createTimeseries(conn):
    c = conn.cursor()
    cmd = "select host from hosts where usg=1"
    c.execute(cmd)
    hosts = [row[0] for row in c.fetchall()]
    cmd = "select qdatetime,ipaddr,offset from times "
    outfile = open("timeseries.txt", 'w')
    print ("Number of hosts: " + str(len(hosts)))
    for host in hosts:
        c.execute("%swhere host='%s'" % (cmd,host))
        outfile.write(host+'\n')
        for row in c.fetchall():
            outfile.write("%s,\t%s,\t%s\n" % (row[0],row[1],row[2]))
        
    outfile.write("END")
    outfile.close()

    with open("timeseries.txt", 'r') as infile:
        epoch = datetime.utcfromtimestamp(0)
        hostname = ""
        times = []
        offsets = []
        num_hosts = 0
        num_empty_hosts = 0
        for line in infile:
            line = line.strip()
            if re.search('[a-zA-Z]', line) != None:
                if len(times) > 0:
                    num_hosts += 1
                    plt.plot(times, offsets)
                    plt.savefig("/home/anj1/timestudy/plots/"+hostname.replace(".","-")+".png")
                else:
                    num_empty_hosts += 1
                hostname = line
                times = []
                offsets = []
            else:
                row = line.split(',')
                time = datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S")
                epochseconds = int((time-epoch).total_seconds())
                times.append(epochseconds)
                offsets.append(int(row[2]))
        print ("hosts with no times entry: " + str(num_empty_hosts))
        print ("Images created: " + str(num_hosts))

if __name__ == "__main__":
    conn = mysqlConnect()
    createTimeseries(conn)
