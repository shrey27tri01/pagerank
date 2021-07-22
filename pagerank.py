import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    linked_pages = corpus[page]
    no_of_linked_pages = len(linked_pages)
    total_no_of_pages = len(corpus)
    prob_dist = dict()
    # print(linked_pages, no_of_linked_pages, total_no_of_pages)

    if no_of_linked_pages == 0:
        for key in corpus:
            probability = 1 / total_no_of_pages
            prob_dist[key] = probability
        return prob_dist

    for key in corpus:
        probability = 0
        if key in linked_pages:
            probability += damping_factor / no_of_linked_pages
        probability += (1 - damping_factor) / total_no_of_pages
        prob_dist[key] = probability
    
    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # print(f"Corpus: {corpus}")
    
    samples = []
    
    list_of_pages = []
    for key in corpus:
        list_of_pages.append(key)
    
    first_sample = random.choice(list_of_pages)
    samples.append(first_sample)
    
    # print(f"First Sample: {first_sample}")

    for i in range(n - 1):
        # print(f"Sample {i+1}")
        previous_sample = samples[-1]
        prob_dist_previous_sample = transition_model(corpus, previous_sample, damping_factor)
        # print(f"Probability distribution of previous sample: {prob_dist_previous_sample}")
        
        next_state_choices = []
        probabilities = []
        
        for key, value in prob_dist_previous_sample.items():
            next_state_choices.append(key)
            probabilities.append(value)
    
        next_state = random.choices(next_state_choices, weights=probabilities, k=1)
        next_state = next_state[0]
        samples.append(next_state)
        # print(f"Next State: {next_state}\n")
    
    # print(samples)

    counts = dict()
    for page in list_of_pages:
        counts[page] = samples.count(page)
    
    # print(counts, len(samples))

    pageranks = dict()

    sum = 0

    if len(samples) == n:
        for key, value in counts.items():
            sum += value / n
            pageranks[key] = value / n
        # print(pageranks)
        # print(int(round(sum)))
        if int(round(sum)) == 1:
            return pageranks

    print(samples, len(samples))
    raise ValueError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    corpus = clean_corpus(corpus)
    # print(f"Corpus: {corpus}\n")
    list_of_pages = []
    for key in corpus:
        list_of_pages.append(key)

    no_of_pages = len(list_of_pages)

    pageranks = dict()

    for page in list_of_pages:
        pageranks[page] = 1 / no_of_pages
    
    # print(f"Initial pageranks: {pageranks}\n")

    flag = True
    count = 0
    while flag:
        count += 1
        # print(f"Iteration {count}")
        old_pageranks = pageranks
        new_pageranks = dict()

        for page in list_of_pages:
            old_value = old_pageranks[page]
            new_pagerank = (1 - damping_factor) / no_of_pages
            in_pages = incoming_pages(corpus, page)
            # print(f"Page: {page}, inpages: {in_pages}")
            for in_page in in_pages:
                prev_pagerank = old_pageranks[in_page]
                new_pagerank += damping_factor * (prev_pagerank / num_links(corpus, in_page))
                # print(abs(new_pagerank - prev_pagerank))

            new_pageranks[page] = new_pagerank
            # print(f"Old value: {old_value}, new value: {new_pagerank}\n")
            if abs(new_pagerank - old_value) <= 0.001:
                flag = False

        # print(f"Old pageranks: {old_pageranks},\n new pageranks: {new_pageranks}\n\n\n")
        pageranks = new_pageranks
        # print(pageranks)

    sum = 0
    for key, value in pageranks.items():
        sum += value
    # print(sum, pageranks)
    if int(round(sum)) == 1:
        return pageranks

    raise ValueError

def num_links(corpus, page):
    """
    Given a corpus and a page, return the number of links present on the page
    """
    no_of_linked_pages = len(corpus[page])
    if no_of_linked_pages == 0:
        return len(corpus.keys())
    # if page in corpus[page]:
    #     no_of_linked_pages = no_of_linked_pages - 1
    return no_of_linked_pages

def incoming_pages(corpus, page):
    """
    Given a corpus and a page, return the list of pages that link to the page 
    """
    list_of_pages = []
    for key in corpus:
        list_of_pages.append(key)

    pages = []
    
    for key, value in corpus.items():
        if page in value:
            pages.append(key)
        # print(key, value)
    
    # if page in pages:
    #     pages.remove(page)

    return pages

def clean_corpus(corpus):
    list_of_pages = []
    for key in corpus:
        list_of_pages.append(key)
    for key, value in corpus.items():
        if len(value) == 0:
            corpus[key] = set(list_of_pages)
    return corpus


if __name__ == "__main__":
    main()


