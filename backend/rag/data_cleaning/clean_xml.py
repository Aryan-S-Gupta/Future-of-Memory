"""Clean XML files from PubMed Central."""

import xml.etree.ElementTree as ET
import logging
import os
from rag.utils.utils import sanitise_string
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

RAG_DIR = os.path.abspath("rag")

# Path to source_data folder
SOURCE_DATA_PATH = os.path.join(RAG_DIR, "source_data")

# Path to all XML files to parse
XML_PATHS = [os.path.join("pmc_2025_08_17", "pmc_result.xml")]

# XPath (XML path) to license tag, relative to article tag (for XML files sourced from PMC)
LICENCE_XPATH = "./front/article-meta/permissions/license//license-p"

# XPath to article title tag, relative to article tag
TITLE_XPATH = "./front/article-meta/title-group/article-title"

# path for output txt files
TXT_PATH = os.path.join(RAG_DIR, "cleaned_data")

# where to put licence information
LICENCE_PATH = os.path.join(TXT_PATH, "licences", "licenses.txt")


def xml_to_txt() -> None:
    """Parse all given PMC-sourced XML fils to text. Include licensing information and article
    titles as filenames.
    """

    for xml_path in XML_PATHS:
        xml_path = os.path.join(SOURCE_DATA_PATH, xml_path)
        logger.debug(f"Parsing {xml_path} to txt...")
        tree = ET.parse(xml_path)
        root = tree.getroot()

        for article in root:

            # Find article title
            title_elem = article.find(TITLE_XPATH)
            assert (
                title_elem is not None and title_elem.text is not None
            ), "Article doesn't have title"
            article_title = title_elem.text
            sanitised_article_title = sanitise_string(article_title)

            # Find licence info
            licence_tag = article.find(LICENCE_XPATH)
            assert licence_tag is not None, "Article doesn't have licence"
            licence = "".join(licence_tag.itertext())
            body = article.find("body")
            assert body is not None, "Article doesn't have body"

            # Remove inline-formula elements from body to remove LaTeX content
            for parent in body.findall(".//inline-formula/.."):
                # Find each inline-formula element
                for element in parent.findall("inline-formula"):
                    # Remove the inline-formula element from its parent element
                    parent.remove(element)

            body_text = "".join(body.itertext())

            # Remove excessive whitespace
            body_text = re.sub(r"\s*\n+\s*", "\n", body_text)
            body_text = re.sub(r"\n+", "\n", body_text)
            body_text = re.sub(r"[ \t]+", " ", body_text)

            # Write txt and licence files
            with open(
                os.path.join(TXT_PATH, f"{sanitised_article_title}.txt"), "w"
            ) as txt_file:
                txt_file.write(body_text)
            with open(os.path.join(LICENCE_PATH), "a") as licence_file:
                licence_file.write(f"{article_title}\n{licence}\n\n")
            # todo add article references, authors, etc.
            # todo remove headings from articles?
