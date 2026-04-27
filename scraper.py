import re
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urljoin, urldefrag
#import urllib

seen = set()
# took stopwords from the link provided by prof
# need to ignore these
stop_words = {
    "a","about","above","after","again","against","all","am","an","and","any",
    "are","aren't","as","at","be","because","been","before","being","below",
    "between","both","but","by","can't","cannot","could","couldn't","did",
    "didn't","do","does","doesn't","doing","don't","down","during","each",
    "few","for","from","further","had","hadn't","has","hasn't","have",
    "haven't","having","he","he'd","he'll","he's","her","here","here's",
    "hers","herself","him","himself","his","how","how's","i","i'd","i'll",
    "i'm","i've","if","in","into","is","isn't","it","it's","its","itself",
    "let's","me","more","most","mustn't","my","myself","no","nor","not",
    "of","off","on","once","only","or","other","ought","our","ours",
}
words = {} # 50 most common words; maps every word to how many times it appeared across all pages crawled
pages = {} #  maps every URL to the number of words on that page
subdomains = {} 


def scraper(url, resp):
    result = []
    links = extract_next_links(url, resp)
    for link in links:
        if is_valid(link) and link not in seen:
            seen.add(link)
            result.append(link)
    return result
    # defragged link??
    # return [urllib.parse.urldefrag(link) for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if resp is None:
        return []
    

    if resp.status == 200 and resp.raw_response and resp.raw_response.content:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        links = []
        for tag in soup.find_all('a', href=True):
            absolute = urljoin(url, tag['href'])
            defragged, _ = urldefrag(absolute)
            links.append(defragged)
        return links
    return []

def is_valid(url):
   
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    parsed = urlsplit(url)
    try:    
        # do not download zip files!! the href says .zip
        # for calendars, there is no ending, there is an infinite trap, we must consider that
        #print("TYPE ", type(parsed.netloc))
        if url is None:
            return False

        if ".zip" in url or ".pdf" in url:
            return False
            
        if parsed.scheme not in {"http", "https"}:
            return False
        
        if not parsed.netloc.endswith((".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu",".stat.uci.edu")):
            return False
        
        """ Calender Trap Detection """
        if "date=" in url:
            return False

        if re.search(r"/calendar", parsed.path.lower()):
            return False
        
        # print("HELLOOOO ", parsed.netloc)
        #correctUrl = False
        #if "ics.uci.edu" in parsed.netloc or "cs.uci.edu" in parsed.netloc or "informatics.uci.edu" in parsed.netloc or "stat.uci.edu" in parsed.netloc:
            #correctUrl = True
            
        # defragging url? urllib.parse.urldefrag(url)
        #if parsed.scheme not in set(["http", "https"]):
            #return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise