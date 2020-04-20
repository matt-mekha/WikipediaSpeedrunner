from bs4 import BeautifulSoup, NavigableString
from requests import get
from sys import argv
from queue import Queue
from threading import Thread
from time import time

base = "https://en.wikipedia.org"
midpoint = base + "/wiki/United_States"
prefixes = ["Template", "Template_talk", "Template talk", "Talk", "User", "User talk", "Wikipedia", "Wikipedia talk", "File", "File talk", "MediaWiki", "MediaWiki talk", "Template", "Template talk", "Help", "Help talk", "Category", "Category talk", "Portal", "Portal talk", "Draft", "Draft talk", "TimedText", "TimedText talk", "Module", "Module talk", "Book", "Book talk", "Education Program", "Education Program talk", "Gadget", "Gadget talk", "Gadget definition", "Gadget definition talk", "Special", "Media"]
max_links = 50
midpoint_links = []

def search(start, end):

    def validate(href):
        if href and len(href) > 6 and href[:6] == "/wiki/":
            href = href.split("#")[0]
            if ":" in href:
                prefix = href.split("/wiki/")[1].split(":")[0]
                if prefix in prefixes:
                    return False
            return href
        return False

    def forward_tree(urls, url, done, checked, end, result, midpoint_links):
        response = get(url, allow_redirects=True)
        title = response.url.lower().split("/wiki/")[1].split("#")[0]
        if title == end:
            return done(urls)
        html = response.text
        dom = BeautifulSoup(html, features="html.parser")

        div = dom.find("div", {"class": "mw-parser-output"})
        if not div: return
        links = div.find_all("a")
        parsed_links = []

        for l in links:
            href = validate(l.get("href"))
            if not href: continue
            
            total = urls + [base + href]
            if href.lower().split("/wiki/")[1] == end:
                return done(total)
            if total[-1] not in checked:
                parsed_links.append(total)

        return (title, len(response.text), parsed_links)
    
    def backward_tree(urls, url, done, checked, end, result, midpoint_links):
        title = url.split("/wiki/")[1]
        wlh = f"https://en.wikipedia.org/w/index.php?title=Special:WhatLinksHere/{title}&namespace=0&limit=2000&hideredirs=1&hidetrans=1"
        response = get(wlh, allow_redirects=True)
        html = response.text
        dom = BeautifulSoup(html, features="html.parser")

        parsed_links = []

        ul = dom.find("ul", {"id": "mw-whatlinkshere-list"})
        if not ul: return

        for li in ul.contents:
            if isinstance(li, NavigableString): continue
            if not li.contents: continue
            href = validate(li.contents[0].get("href"))
            if not href: continue

            total = urls + [base + href]
            found_title = href.lower().split("/wiki/")[1]
            if found_title == end:
                return done(total)
            elif found_title in midpoint_links:
                total += [midpoint]
                return done(total)
            if total[-1] not in checked:
                parsed_links.append(total)
        
        return (title, len(response.text), parsed_links)

    def subsearch(start, end, result, tree, midpoint_links = set()):
        end = end.lower().split("/wiki/")[1]
        end_words = set(end.split("_"))

        checked = set()

        unsearched = [[start]]
        nodes = {}
        threads = []

        def done(urls):
            result.append(urls)
        
        def score_page(title, length, links):
            scores = [
                (1,   length / 1e4),
                (10,  2*len(links)),
                (100, 100 if len(set(title.split("_")) & end_words) > 0 else 0),
            ]

            return sum([weight * score for weight, score in scores])
        
        def score_link(urls):
            url = urls[-1]
            title = url.split("/wiki/")[1]

            scores = [
                (3,   100 - (0.01 * (len(title) ** 2))),
                (1,   100 if len(title) > 8 and title[:8] == "list_of_" else 0),
                (100, 100 if len(set(title.split("_")) & end_words) > 0 else 0),
            ]

            return sum([weight * score for weight, score in scores])

        def fetch(urls, url, result, midpoint_links):
            ret = tree(urls, url, done, checked, end, result, midpoint_links)
            if not ret:
                return
            title, length, parsed_links = ret

            parsed_links.sort(key=score_link, reverse=True)
            if len(parsed_links) > max_links:
                parsed_links = parsed_links[:max_links]

            nodes[url] = (score_page(title, length, parsed_links), parsed_links)
            print(f"SEARCHED {title}")

        while not result:
            if len(unsearched) == 0:
                for thr in threads:
                    if thr.is_alive():
                        thr.join()

                if result:
                    break

                best_node = max(nodes, key=lambda k: nodes[k][0])
                print(f"\nSELECTED NEXT BEST NODE: {best_node}\n")
                unsearched = nodes[best_node][1]
                nodes = {}
            
            urls = unsearched.pop(0)
            url = urls[-1]

            if url in checked: continue
            checked.add(url)

            try:
                thr = Thread(target=fetch, daemon=True, args=(urls, url, result, midpoint_links))
                thr.start()
                threads.append(thr)
            except RuntimeError:
                pass
        
        for thr in threads:
            if thr.is_alive():
                thr.join()
        
        print(f"\nCOMPLETED SUBSEARCH FOR MIDPOINT PATH\n")

    print()
    start_time = time()

    _, __, midpoint_links = forward_tree([], midpoint, (lambda x:None), set(), "", [], set())
    midpoint_links = {x[0].split("/wiki/")[1].lower() for x in midpoint_links}

    result1, result2 = [], []
    subsearch(end, midpoint, result2, backward_tree, midpoint_links)
    subsearch(start, midpoint, result1, forward_tree)
    result = result1[0][:-1] + result2[0][::-1]

    end_time = time()
    elapsed_time = round((end_time - start_time) * 100.0) / 100.0

    with open("result.txt", "w+") as file:
        file.write('\n'.join(result))
    
    print(f"RESULT in {elapsed_time}s:")
    print(*result, sep="\n")
    print("\nSAVED TO \"result.txt\"")
    return result

###########################################

if len(argv) > 2:
    start, end = argv[1], argv[2]
else:
    start, end = input("Paste the start URL: "), input("Paste the end URL: ")

search(start, end)