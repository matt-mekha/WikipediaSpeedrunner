## Algorithm Basics
- make GET request for start page
- find all links within the content box of that page
- discard links to meta articles, external sites, or links we already searched
- make a GET request for all the links we just found and score the pages based on length
- take the highest scoring page and restart the process with that as the starting point until we find the end point

## To do list
[ ] make another thread go in reverse from the end point by using the "What links here" thing
[ ] restructure
