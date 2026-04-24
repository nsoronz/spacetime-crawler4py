import re
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import urllib


def scraper(url, resp):
    links = extract_next_links(url, resp)
    # defragged link??
    return [link for link in links if is_valid(link)]
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
    validHyperLinks = []
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    # do we need to put the current url for this function?
    if resp.status == 200:
        for link in soup.find_all('a'):
            validHyperLinks.append(link.get('href')) 

    return validHyperLinks

# is this desirable, want to keep the url or not. both of these functions already have url to work on. 
# do you want it or do you not, decide the code for it.
# 
def is_valid(url):
   
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    parsed = urlsplit(url)
    try:    
        # do not download zip files!! the href says .zip
        # for calendars, there is no ending, there is an infinite trap, we must consider that
        print("TYPE ", type(parsed.netloc))

        # print("HELLOOOO ", parsed.netloc)
        correctUrl = False
        if "ics.uci.edu" in parsed.netloc or "cs.uci.edu" in parsed.netloc or "informatics.uci.edu" in parsed.netloc or "stat.uci.edu" in parsed.netloc:
            correctUrl = True
            
        # defragging url? urllib.parse.urldefrag(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) and correctUrl

    except TypeError:
        print ("TypeError for ", parsed)
        raise
