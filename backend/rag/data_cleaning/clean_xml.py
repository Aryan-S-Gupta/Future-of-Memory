"""Clean XML files from PubMed Central."""

import logging
import os
import json

import xml.etree.ElementTree as ET

from rag.utils.utils import sanitise_string

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RAG_DIR = os.path.abspath("rag")

# Path to source_data folder
SOURCE_DATA_PATH = os.path.join(RAG_DIR, "source_data")

# Path to all XML files to parse, relative to source data folder
XML_PATHS = [os.path.join("pmc_2025_08_17", "pmc_result.xml")]

# path for output txt files
TXT_PATH = os.path.join(RAG_DIR, "cleaned_data")

# where to put article metadata
METADATA_PATH = os.path.join(TXT_PATH, "metadata", "pmc_metadata.json")


class XPath:
    """XPaths (XML paths) for relevant article information in pmc_result.xml"""

    LICENCE = "./front/article-meta/permissions/license//license-p"
    TITLE = "./front/article-meta/title-group/article-title"
    AUTHOR = "./front/article-meta//contrib[@contrib-type='author']/name"


def clean_body_tag(body_tag: ET.Element) -> str:
    """Extract textual content from an article body.

    Args:
        body_tag (ET.Element): The article's XML body tag.
        root (ET.Element): The XML document's root.

    Returns:
        str: Cleaned text from the article body.
    """

    # Remove non-textual content (e.g. LaTeX content)
    tags_to_remove = {"inline-formula", "xref", "tex-math", "ext-link", "fig"}
    for tag_to_remove in tags_to_remove:
        for parent in body_tag.findall(f".//{tag_to_remove}"):
            parent.text = ""
            for child in parent:
                parent.remove(child)

    text = ""
    for elem in body_tag.iter():
        if elem.tag not in {"title", "p"}:
            continue
        text += "".join(elem.itertext()).strip() + (
            " - " if elem.tag == "title" else "\n"
        )

    return text


def xml_to_txt() -> dict[str, dict]:
    """Parse all given PMC-sourced XML files to text. Return a dict mapping filename to metadata
    (article title, author/s, licence info, link text, link). Also write this dict to JSON.
    """

    file_metadata: dict[str, dict] = {}

    for xml_path in XML_PATHS:

        xml_path = os.path.join(SOURCE_DATA_PATH, xml_path)
        logger.debug(f"Parsing {xml_path} to txt...")
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Parse each article
        for article in root:

            article_metadata: dict[str, str | list] = {}

            # Find article title
            title_elem = article.find(XPath.TITLE)
            assert (
                title_elem is not None and title_elem.text is not None
            ), "Article doesn't have title"
            article_title = title_elem.text
            sanitised_article_title = sanitise_string(article_title)
            filename = sanitised_article_title + ".txt"
            article_metadata["title"] = article_title

            # Find licence info
            licence_tag = article.find(XPath.LICENCE)
            licence: str
            if licence_tag is not None:
                licence = "".join(licence_tag.itertext()).strip()
            else:
                licence = "Not found"
            article_metadata["licence"] = licence

            # Find authors
            authors: list[str] = []
            author_names = article.findall(XPath.AUTHOR)
            if author_names is not None:
                for author_name in author_names:
                    given_names_text = ""
                    surname_text = ""
                    given_names = author_name.find("given-names")
                    if given_names is not None and given_names.text is not None:
                        given_names_text = given_names.text
                    surname = author_name.find("surname")
                    if surname is not None and surname.text is not None:
                        surname_text = surname.text
                    full_name = " ".join([given_names_text, surname_text]).strip()
                    authors.append(full_name)
            article_metadata["authors"] = authors

            # Get and clean article body
            body = article.find("body")
            assert body is not None, "Article doesn't have body"
            body_text = clean_body_tag(body)

            article_metadata["link"] = "https://www.ncbi.nlm.nih.gov/pmc"
            article_metadata["link_text"] = "PubMed Central article"

            # Write cleaned txt files
            with open(
                os.path.join(TXT_PATH, f"{sanitised_article_title}.txt"),
                "w",
                encoding="utf-8",
            ) as txt_file:
                txt_file.write(body_text)

            file_metadata[filename] = article_metadata

    # Write metadata
    with open(os.path.join(METADATA_PATH), "w", encoding="utf-8") as metadata_file:
        json.dump(file_metadata, metadata_file, indent=4)

    return file_metadata


if __name__ == "__main__":
    xml_to_txt()
