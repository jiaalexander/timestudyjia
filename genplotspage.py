import os
import sys

def gen_html(img_dir):
    htmlfile = open("/var/www/html/time-data/index.html", 'w')
    htmlfile.write("<!DOCTYPE html>\n\n<html>\n")
    htmlfile.write("<head>\n\t<link rel=\"stylesheet\" href=\"style.css\">\n</head>\n")
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
    if len(sys.argv) < 2:
        dr = ("/var/www/html/time-data/plots")
    else:
        dr = sys.argv[1]
    gen_html(dr)
