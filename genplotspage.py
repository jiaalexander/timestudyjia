import os, sys, pymysql, re, operator
import matplotlib.pyplot as plt
import matplotlib.dates as mdt
from datetime import datetime, timedelta

def mysql_connect(passwd):
    mc = {"host":"db1.antd.nist.gov",
          "user":"anj1",
          "passwd":passwd,
          "port":0,
          "db":"time",
          "mysqldump":"mysqldump"}
    conn = pymysql.connect(host=mc["host"], port=int(mc["port"]), user=mc["user"], passwd=mc["passwd"], db=mc["db"])
    conn.cursor().execute("set innodb_lock_wait_timeout=20")
    conn.cursor().execute("set tx_isolation='READ-COMMITTED'")
    conn.cursor().execute("set time_zone = '+00:00'")
    return conn

def create_timeseries(conn, img_dir):
    c = conn.cursor()
    cmd = "select host from hosts where usg=1"
    c.execute(cmd)
    hosts = [row[0] for row in c.fetchall()]
    rev_hosts = sorted([".".join(addr.split(".")[::-1]) for addr in hosts])
    sorted_hosts = [".".join(addr.split(".")[::-1]) for addr in rev_hosts]
    cmd = "select qdatetime,ipaddr,offset from times "
    epoch = datetime.utcfromtimestamp(0)
    num_hosts, num_empty_hosts = 0, 0
    htmlfile = open("/var/www/html/time-data/index.html", 'w')
    htmlfile.write("<!DOCTYPE html>\n\n<html>\n")
    htmlfile.write("<head>\n\t<link rel='stylesheet' href='style.css'>\n</head>\n")
    tablesize, timessize, datedsize = get_sizes(conn)
    num_images = len(os.listdir(img_dir))
    htmlfile.write("<p style='font-size:35px'>Rows in 'times': %s</p>" % timessize)
    htmlfile.write("<p style='font-size:35px'>Rows in 'dated': %s</p>" % datedsize)
    htmlfile.write("<p style='font-size:35px'>Database size: %s MB</p>" % tablesize)
    
    for host in sorted_hosts:
        points = []
        c.execute("%swhere host='%s'" % (cmd, host))
        for row in c.fetchall():
            time, ipaddr, offset = row
            offset = int(offset)
            if offset < 3:
                offset = 0
#            time = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
            epochseconds = int((time-epoch).total_seconds())
            points.append((epochseconds, time, int(offset)))
        abs_sum = 0
        for es, t, oset in points:
            abs_sum += abs(oset)
        if abs_sum == 0:
            num_empty_hosts += 1
        else:
            num_hosts += 1
            epochtimes, times, offsets = zip(*sorted(points, key=operator.itemgetter(0)))
            img_name = host.replace(".", "-")+".png"
            plt.clf()
            plt.gca().xaxis.set_major_formatter(mdt.DateFormatter('%m/%d/%Y'))
            plt.gca().xaxis.set_major_locator(mdt.DayLocator())
            plt.plot(times, offsets, "k-x")
            plt.gcf().autofmt_xdate()
            plt.savefig(img_dir+img_name)
            htmlfile.write("<div class='floated_img'>\n\t<img src='%s' alt=\%s\>\n\t<p style='font-size:20px'>%s</p>\n</div>\n" % (img_dir.split("/")[-2:][0]+'/'+img_name, "timeseries plot " + str(num_hosts), img_name[:-4]))
    
    htmlfile.write("</html>")
    htmlfile.close()
    print ("Hosts with no offset: " + str(num_empty_hosts))
    print ("Images created: " + str(num_hosts))
    
def get_sizes(conn):
    c = conn.cursor()
    c.execute("select table_schema 'DB Name', SUM(data_length+index_length)/1024/1024 'Database Size' FROM information_schema.TABLES where table_schema='time'")
    tablesize = c.fetchall()[0][1]
    tables = ["times", "dated"]
    sizes = []
    for t in tables:
        c.execute("select count(*) from "+t)
        sizes.append(c.fetchall()[0][0])
    return (tablesize, sizes[0], sizes[1])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("Password Required")
    else:
        conn = mysql_connect(sys.argv[1])
        dr = ("/var/www/html/time-data/plots")
        create_timeseries(conn, "/var/www/html/time-data/plots/")
