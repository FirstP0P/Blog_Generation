import os
import re


SAVE_DIR = "generated_blogs"


def save_blog(title: str, content: str, topic: str, language: str | None = None) -> str:
    """Save blog content as a Markdown file. Returns the saved file path."""
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Build filename from topic + language
    slug = re.sub(r"[^\w\s-]", "", topic.lower())
    slug = re.sub(r"[\s]+", "_", slug).strip("_")[:50]
    lang_suffix = f"_{language.lower()}" if language else ""
    filename = f"{slug}{lang_suffix}.md"
    filepath = os.path.join(SAVE_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(content)

    print(f"[file_saver] Blog saved → {filepath}")
    return filepathimport os
import re


SAVE_DIR = "generated_blogs"


def save_blog(title: str, content: str, topic: str, language: str | None = None) -> str:
    """Save blog content as a Markdown file. Returns the saved file path."""
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Build filename from topic + language
    slug = re.sub(r"[^\w\s-]", "", topic.lower())
    slug = re.sub(r"[\s]+", "_", slug).strip("_")[:50]
    lang_suffix = f"_{language.lower()}" if language else ""
    filename = f"{slug}{lang_suffix}.md"
    filepath = os.path.join(SAVE_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(content)

    print(f"[file_saver] Blog saved → {filepath}")
    return filepath
