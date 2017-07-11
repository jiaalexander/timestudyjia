import os

def gen_html(img_dir):
    htmlfile = open("plots.html", 'w')
    htmlfile.write("<!DOCTYPE html>\n\n<html>\n")
    htmlfile.write("<head>\n\t<link rel=\"stylesheet\" href=\"style.css\">\n</head>\n")
    count = 1
    for file in os.listdir(img_dir):
        if "png" in file:
            htmlfile.write("<div class=\"floated_img\">\n\t<img src=\"%s\" alt=\"%s\">\n\t<p>%s</p>\n</div>\n" %
                           (img_dir+'/'+file, "timeseries plot "+str(count), file[:-4]))
        count += 1
    htmlfile.write("</html>")
    htmlfile.close()

if __name__ == "__main__":
    dr = ""
    gen_html(dr)
