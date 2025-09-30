import json
from pathlib import Path

import rag.__init__ as rag_init

FUN_FACTS_SOURCE_PATH = Path("rag", "fun_facts", "fun_facts.json")

fun_facts_source: dict[str, list[str]] = {}
with open(FUN_FACTS_SOURCE_PATH, "r", encoding="utf-8") as read_file:
    fun_facts_source = json.load(read_file)

# Count of how many times each fact has been returned
fun_fact_counts: dict[str, dict[str, int]] = {
    source: {
        fact: 0 for fact in fun_facts_source[source]
    }
    for source in fun_facts_source
}
