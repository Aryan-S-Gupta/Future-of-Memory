"""Run this file to create the fun facts JSON file based on given texts.

Before running this file, run:
export GEMINI_API_KEY=<YOUR_API_KEY_HERE>
(bash/zsh)

Note that this file will take some time to run, about 5 minutes currently.
"""

from pathlib import Path
from time import sleep
import json
import logging

from pydantic import BaseModel
from google import genai

FOLDER = Path("rag", "cleaned_data")
DEST = Path("rag", "fun_facts", "fun_facts.json")
METADATA = Path("rag", "cleaned_data", "metadata", "other_metadata.json")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FunFact(BaseModel):
    fact_text: str


def get_fiction_sources():
    """Return a list of filenames which are fiction sources so should not have fun facts generated."""
    content: dict
    with open(METADATA, "r", encoding="utf-8") as read_file:
        content: dict = json.load(read_file)
    fiction = [
        filename
        for (filename, meta) in content.items()
        if meta.get("is_fiction") is True
    ]
    return fiction


if __name__ == "__main__":

    fiction = get_fiction_sources()
    filename_to_facts: dict[str, list[str]] = {}
    client = genai.Client()

    # Find filenames of sources that already have fun facts so we can skip them
    done: list[str] = []
    with open(DEST, "r", encoding="utf-8") as read_file:
        content: dict = json.load(read_file)
        assert isinstance(content, dict)
        done = list(content.keys())

    logger.info("Reading text files...")
    for file_path in FOLDER.glob("*.txt"):

        basename = file_path.name
        if basename in done:
            logger.debug(f"{basename} already done, continuing...")
            continue
        if basename in fiction:
            logger.debug(f"{basename} skipped as it is fiction. Continuing...")
            continue

        logger.debug(f"Now processing {basename}...")
        file_contents: str
        with open(file_path, "r", encoding="utf-8") as file:
            file_contents = file.read()

        response = None
        prompt = (
            "Given the below content, list 5 fun facts about the content. "
            "The fun facts should be written in a friendly, informative tone, based only on the below content and factual information. The fun facts should be clear and written in relatively simple language. Try to avoid jargon. "
            "The fun facts should preferably be one sentence each and each about 30 words long. Use only ASCII characters in your response. "
            "Each fun fact should be self-contained. Each fact should make sense on its own without needing the below content or any other context. E.g. do not say 'The study found...' because it is unclear what study is being referred to. "
            f"\n\n{file_contents}"
        )
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[FunFact],
                },
            )
        except Exception as e:
            logger.exception(f"Got exception when calling the Gemini API:")
            sleep(2)  # Wait a bit to avoid overloading the API
            continue

        facts_parsed: list[FunFact] = response.parsed
        assert facts_parsed is not None
        facts = list(fact.fact_text for fact in facts_parsed)
        filename_to_facts[basename] = facts

        with open(DEST, "w", encoding="utf-8") as file:
            json.dump(filename_to_facts, file, ensure_ascii=True, indent=4)
        sleep(2)  # Wait a bit to avoid overloading the API

    logger.info("Done reading text files and generating fun facts.")
