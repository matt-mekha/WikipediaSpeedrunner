from bs4 import BeautifulSoup
from requests import get
from sys import argv
from queue import Queue
from threading import Thread
from time import time

base = "https://en.wikipedia.org"
prefixes = ["Talk", "User", "User talk", "Wikipedia", "Wikipedia talk", "File", "File talk", "MediaWiki", "MediaWiki talk", "Template", "Template talk", "Help", "Help talk", "Category", "Category talk", "Portal", "Portal talk", "Draft", "Draft talk", "TimedText", "TimedText talk", "Module", "Module talk", "Book", "Book talk", "Education Program", "Education Program talk", "Gadget", "Gadget talk", "Gadget definition", "Gadget definition talk", "Special", "Media"]
max_links = 50

finished, result = False, None

def search(start, end):
    start_time = time()
    end_words = set(end.lower().split("_"))

    checked = set()

    unsearched = [[start]]
    nodes = {}
    threads = []

    def done(urls):
        global finished, result
        finished = True
        result = urls
    
    def score_page(text, html, links):
        return len(text)
    
    def score_link(urls):
        url = urls[-1]
        title = url.split("/wiki/")[1].lower()

        scores = [
            (1.0, 100 - (0.01 * (len(title) ** 2))),
            (1.0, 100 if len(title) > 8 and title[:8] == "list_of_" else 0),
            (5.0, 100 if len(set(title.split("_")) & end_words) > 0 else 0),
        ]

        weighted_scores = [weight * score for weight, score in scores]
        return sum(weighted_scores)

    def fetch(urls, url):
        response = get(url, allow_redirects=True)
        print(f"SEARCHING {response.url}")
        if response.url.split("/wiki/")[1] == end:
            return done(urls)
        html = response.text
        dom = BeautifulSoup(html, features="html.parser")
        div = dom.find("div", {"class": "mw-parser-output"})
        if not div: return
        links = div.find_all("a")
        parsed_links = []

        for l in links:
            href = l.get("href")
            if href and len(href) > 6 and href[:6] == "/wiki/":
                href = href.split("#")[0]
                if ":" in href:
                    prefix = href.split("/wiki/")[1].split(":")[0]
                    if prefix in prefixes:
                        continue
                total = urls + [base + href]
                if href.split("/wiki/")[1] == end:
                    return done(total)
                if finished:
                    break
                if total[-1] not in checked:
                    parsed_links.append(total)
        
        parsed_links.sort(key=score_link, reverse=True)
        if len(parsed_links) > max_links:
            parsed_links = parsed_links[:max_links]

        nodes[url] = (score_page(response.text, html, parsed_links), parsed_links)

    while not finished:
        if len(unsearched) == 0:
            for thr in threads:
                if thr.is_alive():
                    thr.join()

            best_node = max(nodes, key=lambda k: nodes[k][0])
            print(f"\nSELECTED NEXT BEST NODE: {best_node}\n")
            unsearched = nodes[best_node][1]
            nodes = {}
        
        urls = unsearched.pop(0)
        url = urls[-1]

        if url in checked: continue
        checked.add(url)

        try:
            thr = Thread(target=fetch, daemon=True, args=(urls, url))
            thr.start()
            threads.append(thr)
        except RuntimeError:
            pass
    
    for thr in threads:
        if thr.is_alive():
            thr.join()
    
    end_time = time()
    elapsed_time = round((end_time - start_time) * 100.0) / 100.0

    with open("result.txt", "w+") as file:
        file.write('\n'.join(result))
    
    print(f"\nRESULT in {elapsed_time}s:")
    print(*result, sep="\n")
    print("\nSAVED TO \"result.txt\"")
    return result

###########################################

if len(argv) > 2:
    start, end = argv[1], argv[2].split("/wiki/")[1]
else:
    start, end = input("Paste the start URL: "), input("Paste the end URL: ")

search(start, end)