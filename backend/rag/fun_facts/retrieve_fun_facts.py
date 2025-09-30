import rag.__init__ as rag_init
import rag.fun_facts.__init__ as fun_facts_init
from queue import PriorityQueue

# Number of fun facts to retrieve at each function call
NUM_FUN_FACTS = 3


def retrieve_fun_facts() -> list[str]:
    """Retrieve fun facts based on the last retrieved chunks. Prioritise new, unseen fun facts."""
    options: PriorityQueue[tuple[int, str, str]] = PriorityQueue()
    for info in rag_init.last_retrieved_files:
        source = info["source"]
        for fact, count in fun_facts_init.fun_fact_counts[source].items():
            options.put((count, fact, source))

    result: list[str] = []
    for _ in range(NUM_FUN_FACTS):
        _, fact, source = options.get()
        # update counts
        fun_facts_init.fun_fact_counts[source][fact] += 1

    return result
