import json
from pathlib import Path
from random import choice

from queue import PriorityQueue

import rag.__init__ as rag_init
import rag.fun_facts.__init__ as fun_facts_init

# Number of fun facts to retrieve at each function call
NUM_FUN_FACTS = 2
assert NUM_FUN_FACTS <= 5  # there are only 5 fun facts per source


def retrieve_fun_facts() -> list[dict[str, str]]:
    """Retrieve fun facts based on the last retrieved chunks. Prioritise new, unseen fun facts."""
    total_facts = 0
    options: PriorityQueue[tuple[int, str, str]] = PriorityQueue()
    added_sources: set[str] = set()
    for source in rag_init.last_retrieved_files:
        for fact, count in fun_facts_init.fun_fact_counts[source].items():
            options.put((count, fact, source))
            added_sources.add(source)
            total_facts += 1
    
    # we may need more fun facts, just pick some at random
    while total_facts < NUM_FUN_FACTS:
        source = choice(list(fun_facts_init.fun_fact_counts.keys()))
        if source in added_sources:
            continue
        for fact, count in fun_facts_init.fun_fact_counts[source].items():
            options.put((count, fact, source))
            total_facts += 1

    json_files = ["other_metadata.json", "pmc_metadata.json"]
    metadata: dict[str, dict[str, str]] = {}
    for file in json_files:
        with open(Path("rag", "cleaned_data", "metadata", file), "r") as f:
            metadata.update(json.load(f))
                
    result: list[dict[str, str]] = []
    for _ in range(NUM_FUN_FACTS):
        _, fact, source = options.get()
        # update counts
        fun_facts_init.fun_fact_counts[source][fact] += 1
        # get result
        result.append({
            "fact": fact,
            "link": metadata[source]["link"],
            "link_text": metadata[source]["link_text"]
        })

    return result
