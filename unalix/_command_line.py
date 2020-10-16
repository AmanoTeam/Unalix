from argparse import ArgumentParser
from subprocess import call, DEVNULL, getoutput
import webbrowser

from . import clear_url, unshort_url
from ._config import description
from ._files import arguments

parser = ArgumentParser(description=description)

for argument in arguments:
    args, kwargs = argument["args"], argument["options"]
    parser.add_argument(*args, **kwargs)

options = parser.parse_args()
options_dict = options.__dict__

input_urls = options_dict["url"]
ouput_urls = []

launch_in_browser = options_dict["launch_in_browser"]
unshort = options_dict["unshort"]
parse_documents = options_dict["parse_documents"]

bad_keys = [
    "url",
    "launch_in_browser",
    "unshort",
    "parse_documents"
]

for bad_key in bad_keys:
    del options_dict[bad_key]

kwargs = options.__dict__

def main():
    
    global ouput_urls
    
    if not unshort:
        for url in input_urls:
            ouput_urls += [clear_url(url, **kwargs)]
    else:
        for url in input_urls:
            ouput_urls += [unshort_url(url, parse_documents=parse_documents, **kwargs)]
    
    if launch_in_browser:
        platform = getoutput("uname -o")
        if platform == "GNU/Linux":
            for url in ouput_urls:
                call(["xdg-open", url], stdout=DEVNULL)
        elif platform == "Android":
            for url in ouput_urls:
                call(["am", "start", url], stdout=DEVNULL)
        else:
            for url in ouput_urls:
                webbrowser.open(url)
    else:
        for url in ouput_urls:
            print(url)
