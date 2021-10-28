#!/usr/bin/env python3
"""
Processor for SRT subtitles files.
https://docs.fileformat.com/video/srt/

Reformats text lines into 2 line blocks of 42 chars each

"""
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
import re
import datetime
import tkinter as tk
import tkinter.ttk as ttk
import argparse

# Setup root_logger:
from os.path import splitext, split
import logging as root_logger
LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################

TIME_PAIR = re.compile("^.+?-->")
COUNTER   = re.compile("^[0-9]+$")

MAIN_SIZE = 300

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog = "\n".join(["SRT Processor"]))
parser.add_argument('-t', "--target", action="append")

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        master.minsize(width=MAIN_SIZE,height=MAIN_SIZE)
        args = parser.parse_args()
        if args.target is None:
            logging.warning("No Targets Specified")
            exit(1)
        self.files = [abspath(expanduser(x)) for x in args.target]

    def process(self, text: str) -> List[str]:
        words = text.split(" ")
        result = []
        summed = ""
        for word in words[0:]:
            if len(summed) < 42:
                summed += " "
                summed += word
            else:
                result.append(summed)
                summed = word[:]

        result.append(summed)
        return result

    def process_files(self):
        lines : List[str] = []

        for target in self.files:
            with open(target, 'r') as f:
                lines = f.readlines()

            with open("{}.backup".format(target), 'w') as bkup:
                bkup.write("\n".join(lines))

            # Loop over lines, reformatting as necessary
            cleaned : List[str] = []
            joined : str = ""
            for line in lines:
                if not bool(line.strip()):
                    cleaned += process(joined)
                    cleaned.append(line)
                    joined = ""
                elif COUNTER.match(line):
                    cleaned.append(line)
                elif TIME_PAIR.match(line):
                    cleaned.append(line)
                else:
                    joined += line
                    continue

            with open(target, 'w') as f:
                f.write("\n".join(cleaned))


    def destroy(self):
        """ Customised destroy method  """
        logging.info("Closing program")
        tk.Frame.destroy(self)

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
