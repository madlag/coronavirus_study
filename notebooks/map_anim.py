import urllib
import pathlib
from bs4 import BeautifulSoup
import sh

filename = "temp_dir/wiki.html"

if not pathlib.Path(filename).exists():
    url = "https://commons.wikimedia.org/wiki/File:COVID-19_Outbreak_Cases_in_Italy_(Density).svg"
    data = urllib.request.urlopen(url).read()
    f = open(filename, "wb")
    f.write(data)
    f.close()

f=open(filename)
html_data = f.read()

soup = BeautifulSoup(html_data, 'html.parser')

tables = soup.find_all('table')
hrefs = []
for t in tables:
    if "filehistory" in t.get("class"):
        for a in t.find_all("a"):
            href = a.get("href")
            if href.startswith("http") and href.endswith(".svg"):
                if href not in hrefs:
                    hrefs.append(href)

hrefs.reverse()

for i, href in enumerate(hrefs):
    data = urllib.request.urlopen(href).read()
    filename = "temp_dir2/wiki%03d.svg" % i
    png_filename = "temp_dir2/wiki%03d.png" % i
    f = open(filename, "wb")
    f.write(data)
    f.close()
    sh.convert(filename, png_filename)



