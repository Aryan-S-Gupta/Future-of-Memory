"""Run this file to create fun facts based on given texts."""

from pydantic import BaseModel
from pathlib import Path
from time import sleep
import json

from google import genai

FOLDER = Path("rag", "cleaned_data")
DEST = Path("rag", "fun_facts", "fun_facts.json")
METADATA = Path("rag", "cleaned_data", "metadata", "other_metadata.json")


class FunFact(BaseModel):
    fact_text: str


def get_fiction():
    with open(METADATA, "r", encoding="utf-8") as read_file:
        content: dict = json.load(read_file)
        fiction = [
            filename
            for (filename, meta) in content.items()
            if meta.get("is_fiction") is True
        ]
    return fiction


if __name__ == "__main__":

    fiction = get_fiction()
    print(f"{fiction = }")

    # Run export GEMINI_API_KEY=<YOUR_API_KEY_HERE> (bash/zsh)
    client = genai.Client()

    filename_to_facts: dict[str, list[str]] = {}

    done: list[str] = []
    with open(DEST, "r", encoding="utf-8") as read_file:
        content: dict = json.load(read_file)
        assert isinstance(content, dict)
        done = list(content.keys())
    print(f"{done = }")

    for file_path in FOLDER.glob("*.txt"):

        basename = file_path.name

        if basename in done:
            print(f"{basename} already done, continuing...")
            continue
        if basename in fiction:
            print(f"{basename} skipped as it is fiction. Continuing...")
            continue

        print(f"Now processing {basename}...")
        file_contents: str
        with open(file_path, "r", encoding="utf-8") as file:
            file_contents = file.read()

        response = None
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Given the below content, list 5 fun facts about the content. "
                "The fun facts should be written in a friendly, informative tone, based only on the below content and factual information. The fun facts should be clear and written in relatively simple language. Try to avoid jargon. "
                "The fun facts should preferably be one sentence each and each about 30 words long. Use only ASCII characters in your response. "
                "Each fun fact should be self-contained. Each fact should make sense on its own without needing the below content or any other context. E.g. do not say 'The study found...' because it is unclear what study is being referred to. "
                f"\n\n{file_contents}",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[FunFact],
                },
            )
        except Exception as e:
            print(f"Got exception: {type(e)}, {e}")
            sleep(2)
            continue

        # Use the response as a JSON string.
        print(response.text)

        # Use instantiated objects.
        facts_parsed: list[FunFact] = response.parsed
        assert facts_parsed is not None
        facts = list(fact.fact_text for fact in facts_parsed)
        filename_to_facts[basename] = facts

        print("---")
        print(filename_to_facts)
        print("---")
        with open(DEST, "w", encoding="utf-8") as file:
            json.dump(filename_to_facts, file, ensure_ascii=True, indent=4)
        sleep(2)
