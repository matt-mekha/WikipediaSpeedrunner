from bs4 import BeautifulSoup
from requests import get
from sys import argv
from queue import Queue
from threading import Thread

base = "https://en.wikipedia.org"
prefixes = ["Talk", "User", "User talk", "Wikipedia", "Wikipedia talk", "File", "File talk", "MediaWiki", "MediaWiki talk", "Template", "Template talk", "Help", "Help talk", "Category", "Category talk", "Portal", "Portal talk", "Draft", "Draft talk", "TimedText", "TimedText talk", "Module", "Module talk", "Book", "Book talk", "Education Program", "Education Program talk", "Gadget", "Gadget talk", "Gadget definition", "Gadget definition talk", "Special", "Media"]

finished, result = False, None

def bfs(start, end):
    checked = set()
    q = Queue()
    q.put([start])

    def done(urls):
        global finished, result
        finished = True
        result = urls

    def fetch(url):
        response = get(url, allow_redirects=True)
        print(response.url)
        if response.url.split("/wiki/")[1] == end:
            return done(urls)
        html = response.text
        dom = BeautifulSoup(html, features="html.parser")
        div = dom.find("div", {"class": "mw-parser-output"})
        if not div: return
        links = div.find_all("a")

        for l in links:
            href = l.get("href")
            if href and len(href) > 6 and href[:6] == "/wiki/":
                if ":" in href:
                    prefix = href.split("/wiki/")[1].split(":")[0]
                    if prefix in prefixes:
                        continue
                total = urls + [base + href]
                if href.split("/wiki/")[1] == end:
                    return done(total)
                if finished:
                    break
                else:
                    q.put(total)

    while not finished:
        urls = q.get(timeout=5)
        url = urls[-1]

        if url in checked: continue
        checked.add(url)

        thr = Thread(target=fetch, daemon=True, args=(url,))
        thr.start()
    
    return result

start, end = argv[1], argv[2].split("/wiki/")[1]
bfs(start, end)

with open("result.txt", "w+") as file:
    file.write('\n'.join(result))