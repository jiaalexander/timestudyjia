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

def create_timeseries(conn, savefolder):
    c = conn.cursor()
    cmd = "select host from hosts where usg=1"
    c.execute(cmd)
    hosts = [row[0] for row in c.fetchall()]
    cmd = "select qdatetime,ipaddr,offset from times "
    outfile = open("timeseries.txt", 'w')
    print("Number of hosts: "+str(len(hosts)))
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
        num_hosts, num_empty_hosts = 0, 0
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
                time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                epochseconds = int((time-epoch).total_seconds())
                points.append((epochseconds, time, int(row[2])))
        print("Hosts with no 'times' entry: " + str(num_empty_hosts))
        print("Images created: " + str(num_hosts))


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

def gen_html(conn, img_dir):
    htmlfile = open("/var/www/html/time-data/index.html", 'w')
    htmlfile.write("<!DOCTYPE html>\n\n<html>\n")
    htmlfile.write("<head>\n\t<link rel=\"stylesheet\" href=\"style.css\">\n</head>\n")
    tablesize, timessize, datedsize = get_sizes(conn)
    num_images = len(os.listdir(img_dir))
    htmlfile.write("<p style='font-size:35px'>Num plots: %s</p>" % str(num_images))
    htmlfile.write("<p style='font-size:35px'>Rows in 'times': %s</p>" % timessize) 
    htmlfile.write("<p style='font-size:35px'>Rows in 'dated': %s</p>" % datedsize)
    htmlfile.write("<p style='font-size:35px'>Database size: %s MB</p>" % tablesize)
    count = 1
    folder = "plots"
    for file in os.listdir(img_dir):
        if "png" in file:
            htmlfile.write("<div class=\"floated_img\">\n\t<img src=\"%s\" alt=\"%s\">\n\t<p>%s</p>\n</div>\n" %
                           (folder+'/'+file, "timeseries plot "+str(count), file[:-4]))
        count += 1
    htmlfile.write("</html>")
    htmlfile.close()

if __name__ == "__main__":
    conn = mysql_connect()
    if len(sys.argv) < 2:
        print "Password Required"
    else:
        conn = mysql_connect(sys.argv[1])
        dr = ("/var/www/html/time-data/plots")
        create_timeseries(conn, "/var/www/html/time-data/plots/")
        gen_html(conn, dr)
