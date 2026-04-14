import re

COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
REF_RE = re.compile(r"<ref.*?>.*?</ref>", re.DOTALL)
REF_SELF_RE = re.compile(r"<ref.*?/>")
TEMPLATE_RE = re.compile(r"\{\{.*?\}\}", re.DOTALL)
TABLE_RE = re.compile(r"\{\|.*?\|\}", re.DOTALL)
FILE_RE = re.compile(r"\[\[(file|image):.*?\]\]", re.IGNORECASE)
LINK_TEXT_RE = re.compile(r"\[\[.*?\|(.*?)\]\]")
LINK_RE = re.compile(r"\[\[(.*?)\]\]")
FORMAT_RE = re.compile(r"'{2,}")
HEADER_RE = re.compile(r"={2,}.*?={2,}")
HTML_RE = re.compile(r"<.*?>")
BULLET_RE = re.compile(r"^\s*\*.*$", re.MULTILINE)
URL_RE = re.compile(r"http\S+")
TEMPLATE_LEFTOVER_RE = re.compile(r"\|\s*\w+=\w+")
INFOBOX_RE = re.compile(r"^\|.*$", re.MULTILINE)
TABLE_ROW_RE = re.compile(r"\|[-].*")
MATH_RE = re.compile(r"[=\{\}\^\_]+")
WHITESPACE_RE = re.compile(r"\s+")

def clean_text(text):
    if not text:
        return ""

    text = COMMENT_RE.sub(" ", text)
    text = REF_RE.sub(" ", text)
    text = REF_SELF_RE.sub(" ", text)
    text = TEMPLATE_RE.sub(" ", text)
    text = TABLE_RE.sub(" ", text)
    text = FILE_RE.sub(" ", text)

    text = LINK_TEXT_RE.sub(r"\1", text)
    text = LINK_RE.sub(r"\1", text)

    text = FORMAT_RE.sub("", text)
    text = HEADER_RE.sub(" ", text)
    text = HTML_RE.sub(" ", text)

    text = BULLET_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)

    text = TEMPLATE_LEFTOVER_RE.sub(" ", text)
    text = INFOBOX_RE.sub(" ", text)
    text = TABLE_ROW_RE.sub(" ", text)

    text = MATH_RE.sub(" ", text)

    text = WHITESPACE_RE.sub(" ", text).strip()

    return text