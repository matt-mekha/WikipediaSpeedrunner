## Algorithm Basics
Wikipedia pages have lots of links, so simply using a depth-first search or breadth-first search would take way too long. If you were to search every linked page recursively in a BFS, that would result in **x^y** searches where **x** is the number of links per page (let's say 50 on average) and **y** is the depth of the search. After 4 layers, you would already be at over six million searches.

The solution to this problem is to determine which links on a page are most likely to result in a shorter path, and only search the first few. To determine this, the algorithm checks how long the title is (the assumption here is that shorter titles tend to be more general) along with some other factors. After searching the those pages, the algorithm then determine which page is best to be the new "parent" page using factors like content length and number of links. The algorithm will very quickly begin to reach general pages such as "United States".

... to be continued
