import os
import shelve

from threading import Thread, RLock
from queue import Queue, Empty

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid
from urllib.parse import urlsplit
import time

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = {}
        self.count = 0
        self.r_lock = RLock()
        
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        with self.r_lock:
            total_count = len(self.save)
            tbd_count = 0
            for url, completed in self.save.values():
                if not completed and is_valid(url):
                    parsed = urlsplit(url)
                    # FIRST print("THIS IS THE URL ", parsed.netloc)
                    if parsed.netloc.endswith(".ics.uci.edu"):
                        if ".ics.uci.edu" not in self.to_be_downloaded:
                            self.to_be_downloaded[".ics.uci.edu"] = [[],[]]
                        self.to_be_downloaded[".ics.uci.edu"][0].append(url)
                        self.to_be_downloaded[".ics.uci.edu"][1] = time.time()
                    elif parsed.netloc.endswith(".cs.uci.edu"):
                        if ".cs.uci.edu" not in self.to_be_downloaded:
                            self.to_be_downloaded[".cs.uci.edu"] = [[],[]]
                        self.to_be_downloaded[".cs.uci.edu"][0].append(url)
                        self.to_be_downloaded[".cs.uci.edu"][1] = time.time()
                    elif parsed.netloc.endswith(".informatics.uci.edu"):
                        if ".informatics.uci.edu" not in self.to_be_downloaded:
                            self.to_be_downloaded[".informatics.uci.edu"] = [[],[]]
                        self.to_be_downloaded[".informatics.uci.edu"][0].append(url)
                        self.to_be_downloaded[".informatics.uci.edu"][1] = time.time()
                    elif parsed.netloc.endswith(".stat.uci.edu"):
                        if ".stat.uci.edu" not in self.to_be_downloaded:
                            self.to_be_downloaded[".stat.uci.edu"] = [[],[]]
                        self.to_be_downloaded[".stat.uci.edu"][0].append(url)
                        self.to_be_downloaded[".stat.uci.edu"][1] = time.time()
                    # self.to_be_downloaded.append(url)
                    tbd_count += 1
            self.logger.info(
                f"Found {tbd_count} urls to be downloaded from {total_count} "
                f"total urls discovered.")

    def get_tbd_url(self):
        try:
            with self.r_lock:
                # were going to use domain of link later!
                domain_of_link = ""
                
                # checking each domain's time value in the dictionary to make sure it fits within the 500ms politeness policy
                # if there is another domain available, it will return a link from that domain
                # if there is no other domain
                for domain in self.to_be_downloaded:
                    present_time = time.time()
                    if self.to_be_downloaded[domain]:
                        prev_time = self.to_be_downloaded[domain][1]
                        domain_of_link = domain
                        if present_time - prev_time >= 0.5:
                            self.to_be_downloaded[domain][1] = present_time
                            return self.to_be_downloaded[domain][0].pop()
                        # else:
                        #     print("GOING TO SLEEP!! ", present_time - prev_time)
                        
                time.sleep(0.5)
                
                if domain_of_link:
                    self.to_be_downloaded[domain_of_link][1] = present_time
                    return self.to_be_downloaded[domain_of_link][0].pop()
                
                return None

        except IndexError:
            return None

    def add_url(self, url):
        # need to do self.r_lock in order for only thread to go in add_url at a time!
        with self.r_lock:
            url = normalize(url)
            urlhash = get_urlhash(url)
            if urlhash not in self.save:
                self.save[urlhash] = (url, False)
                self.save.sync()
                # splitting url 
                parsed = urlsplit(url)
                # print("PARSED NETLOC ", parsed.netloc)
                # making a dictionary where the keys are the domains, the values are two lists inside a list
                # the first list is all the urls of the domain, the second list is the timestamp which the url was added!
                if parsed.netloc.endswith(".ics.uci.edu"):
                    if ".ics.uci.edu" not in self.to_be_downloaded:
                        self.to_be_downloaded[".ics.uci.edu"] = [[],[]]
                    self.to_be_downloaded[".ics.uci.edu"][0].append(url)
                    self.to_be_downloaded[".ics.uci.edu"][1] = time.time()
                elif parsed.netloc.endswith(".cs.uci.edu"):
                    if ".cs.uci.edu" not in self.to_be_downloaded:
                        self.to_be_downloaded[".cs.uci.edu"] = [[],[]]
                    self.to_be_downloaded[".cs.uci.edu"][0].append(url)
                    self.to_be_downloaded[".cs.uci.edu"][1] = time.time()
                elif parsed.netloc.endswith(".informatics.uci.edu"):
                    if ".informatics.uci.edu" not in self.to_be_downloaded:
                        self.to_be_downloaded[".informatics.uci.edu"] = [[],[]]
                    self.to_be_downloaded[".informatics.uci.edu"][0].append(url)
                    self.to_be_downloaded[".informatics.uci.edu"][1] = time.time()
                elif parsed.netloc.endswith(".stat.uci.edu"):
                    if ".stat.uci.edu" not in self.to_be_downloaded:
                        self.to_be_downloaded[".stat.uci.edu"] = [[],[]]
                    self.to_be_downloaded[".stat.uci.edu"][0].append(url)
                    self.to_be_downloaded[".stat.uci.edu"][1] = time.time()
    
    def mark_url_complete(self, url):
        with self.r_lock:
            urlhash = get_urlhash(url)
            if urlhash not in self.save:
                # This should not happen.
                self.logger.error(
                    f"Completed url {url}, but have not seen it before.")

            self.save[urlhash] = (url, True)
            self.save.sync()
