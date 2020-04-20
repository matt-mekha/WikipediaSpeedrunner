from bs4 import BeautifulSoup
from requests import get
from sys import argv

base = "https://en.wikipedia.org"
prefixes = ["Talk", "User", "User talk", "Wikipedia", "Wikipedia talk", "File", "File talk", "MediaWiki", "MediaWiki talk", "Template", "Template talk", "Help", "Help talk", "Category", "Category talk", "Portal", "Portal talk", "Draft", "Draft talk", "TimedText", "TimedText talk", "Module", "Module talk", "Book", "Book talk", "Education Program", "Education Program talk", "Gadget", "Gadget talk", "Gadget definition", "Gadget definition talk", "Special", "Media"]

def bfs(start, end):
    checked = set()
    queue = [[start]]

    while queue:
        urls = queue.pop(0)
        url = urls[-1]

        if url in checked: continue
        checked.add(url)

        response = get(url, allow_redirects=True)
        print(response.url)
        if response.url.split("/wiki/")[1] == end:
            return urls
        html = response.text
        dom = BeautifulSoup(html, features="html.parser")
        div = dom.find("div", {"class": "mw-parser-output"})
        if not div: continue
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
                    return total
                queue.append(total)

start, end = argv[1], argv[2].split("/wiki/")[1]
print(bfs(start, end))