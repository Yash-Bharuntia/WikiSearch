import re

TOKEN_PATTERN = re.compile(r'[a-z0-9]+')

STOPWORDS = {
    "the","is","a","an","and","of","to","in","on","for","with",
    "by","as","at","from","that","this","it","be","are","was","were"
}

# TOKENIZER
def tokenize(text):
    tokens = TOKEN_PATTERN.findall(text.lower())
    return [t for t in tokens if t not in STOPWORDS]