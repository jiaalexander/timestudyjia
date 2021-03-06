import pymysql, re, sys, operator
import matplotlib.pyplot as plt
import matplotlib.dates as mdt
from datetime import datetime, timedelta

def mysql_connect():
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

def create_timeseries(conn, savefolder):
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
        points = []
        num_hosts = 0
        num_empty_hosts = 0
        for line in infile:
            line = line.strip()
            if re.search('[a-zA-Z]', line) != None:
                if len(points) > 0:
                    num_hosts += 1
                    epochtimes, times, offsets = zip(*sorted(points, key=operator.itemgetter(0)))
                    plt.clf()
                    plt.gca().xaxis.set_major_formatter(mdt.DateFormatter('%m/%d/%Y'))
                    plt.gca().xaxis.set_major_locator(mdt.DayLocator())
                    plt.plot(times, offsets)
                    plt.gcf().autofmt_xdate()
                    plt.savefig(savefolder+hostname.replace(".","-")+".png")
                else:
                    num_empty_hosts += 1
                hostname = line
                points = []
            else:
                row = line.split(',')
                time = datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S")
                epochseconds = int((time-epoch).total_seconds())
                points.append((epochseconds, time, int(row[2])))
        print ("hosts with no times entry: " + str(num_empty_hosts))
        print ("Images created: " + str(num_hosts))

if __name__ == "__main__":
    conn = mysql_connect()
    if len(sys.argv) < 2:
        create_timeseries(conn, "/var/www/html/time-data/plots/")
    else:
        create_timeseries(conn, sys.argv[1])
