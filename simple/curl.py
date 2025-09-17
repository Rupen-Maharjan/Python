import argparse
import requests

parse=argparse.ArgumentParser()

parse.add_argument('url', help='Add url here')
parse.add_argument('-o','--o', help='Output filename', default=None)

def save(url,filename):
    if filename ==None:
        filename=url.split('/')[-1]
    with requests.get(url,stream=True) as r:
        r.raise_for_status()
        with open (filename,'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return filename


arg = parse.parse_args()

print(arg.url)
print(arg.o)
save (arg.url, arg.o)
