"""
Run this file to create the fun facts JSON file based on given texts in backend/rag/cleaned_data.
Fun facts will be written to rag/fun_facts/fun_facts.json. Fictional texts or texts that already
have fun facts will be skipped.

Note that this file will take some time to run.
"""

from pathlib import Path
from time import sleep
import json
import logging

from pydantic import BaseModel

from llm.generate import call_ollama

FOLDER = Path("rag", "cleaned_data")
FUN_FACT_DEST = Path("rag", "fun_facts", "fun_facts.json")
METADATA = Path("rag", "cleaned_data", "metadata", "other_metadata.json")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FunFactList(BaseModel):
    facts: list[str]


def get_fiction_sources():
    """Return a list of filenames which are fiction sources so should not have fun facts generated."""
    content: dict
    with open(METADATA, "r", encoding="utf-8") as read_file:
        content: dict = json.load(read_file)
    fiction = [
        filename
        for (filename, meta) in content.items()
        if meta.get("is_fiction")
        is True  # could be None, which should be interpreted as False
    ]
    return fiction


def main() -> None:
    """
    For all files that don't have fun facts, create fun facts for them. Save these fun facts to
    FUN_FACT_DEST. Skip fiction texts.
    """

    fiction = get_fiction_sources()
    filename_to_facts: dict[str, list[str]]

    with open(FUN_FACT_DEST, "r", encoding="utf-8") as read_file:
        filename_to_facts = json.load(read_file)
        assert isinstance(filename_to_facts, dict)

    logger.info("Reading text files...")
    for file_path in FOLDER.glob("*.txt"):


        basename = file_path.name
        if basename in filename_to_facts:
            logger.debug(f"{basename} already done, continuing...")
            continue
        if basename in fiction:
            logger.debug(f"{basename} skipped as it is fiction. Continuing...")
            continue

        sleep(2)  # Wait a bit to avoid overloading the API
        logger.info(f"Now processing {basename}...")
        file_contents: str
        with open(file_path, "r", encoding="utf-8") as file:
            file_contents = file.read()

        response = None
        prompt = (
            "Given the below content, list 5 fun facts about the content. "
            "The fun facts should be written in a friendly, informative tone, based only on the below content and factual information. "
            "The fun facts should be clear and written in simple language. Avoid jargon. "
            "The fun facts should preferably be one sentence each and each about 30 words long. "
            "Use only ASCII characters in your response. "
            "Each fun fact should be self-contained. Each fact should make sense on its own without needing the below content or any other context. E.g. do not say 'The study found...' because it is unclear what study is being referred to. "
            "Return your output in the given JSON format. "
            f"\n\n{file_contents}"
        )
        try:
            response = call_ollama(prompt, json_schema=FunFactList.model_json_schema())
        except Exception:
            logger.exception(f"Got exception when calling the API:")
            continue

        facts: list[str] = response["facts"]
        assert isinstance(facts, list)
        logger.debug(f"Got these facts from the API: {facts}")
        filename_to_facts[basename] = facts

    with open(FUN_FACT_DEST, "w", encoding="utf-8") as file:
        json.dump(filename_to_facts, file, ensure_ascii=True, indent=4)

    logger.info("Done reading text files and generating fun facts.")


if __name__ == "__main__":
    main()
