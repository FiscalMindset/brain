"""Ingestion: normalize, fingerprint, chunk, metadata extraction."""
from __future__ import annotations
import hashlib, re
from collections import Counter
DEFAULT_CHUNK_SIZE = 800
_WS = re.compile(r"\s+")
def normalize(text: str) -> str:
    return _WS.sub(" ", text or "").strip()
def fingerprint(text: str) -> str:
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()
def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> list[str]:
    cleaned = normalize(text)
    if not cleaned: return []
    chunk_size = max(1, chunk_size)
    chunks, current = [], ""
    for sentence in re.split(r"(?<=[.!?]) ", cleaned):
        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= chunk_size: current = candidate
        else:
            if current: chunks.append(current)
            while len(sentence) > chunk_size:
                chunks.append(sentence[:chunk_size]); sentence = sentence[chunk_size:]
            current = sentence
    if current: chunks.append(current)
    return chunks

STOP_WORDS = set("the a an and or but if then else of at by for with about to from in on is are was were be been being have has had do does did will would shall should can could may might must this that these those i you he she it we they me him her us them my your his its our their as not no yes so than too very".split())
# simple stop-word sets per language (small heuristic)
LANG_STOPS = {
 "en": STOP_WORDS,
 "es": set("el la los las un una unos unas de en y o que es se del al por para con no su al lo como más pero sus le ya o este sí porque esta entre cuando muy sin sobre también me hasta hay donde quien desde todo nos durante todos uno les ni contra otros ese eso ante ellos esto mí antes algunos qué unos yo otro otras otra él tanto esa estos mucho quienes nada mucho cual poco ella estar estas algunas algo nosotros mi mis tú te ti tu tus ellas nosotros vosotros vosotras os mío tuyo suyo nuestro vuestro esos esas estoy si".split()),
 "fr": set("le la les un une des de du en au aux et ou que qui est dans sur plus pas pour par au avec ce cette ces il elle nous vous ils elles je tu on ne se sa son ses leur leurs y à être avoir faire comme mais aussi très bien alors si".split()),
 "de": set("der die das den dem des ein eine einen einem einer eines und oder aber wenn dann als ob wie so dass weil nicht kein keine ist sind war waren sein ihre ihr seinen seiner einem einer wurde werden hat haben hatte hatten kann können könnte sollten soll muss dürfen darf bei von zu zur zum am an in im ins auf durch für mit nach über unter vor zwischen".split()),
}
def detect_language(text: str) -> str:
    words = re.findall(r"[a-zà-ÿ]+", (text or "").lower())
    if not words: return "en"
    best, best_score = "en", -1
    for lang, stops in LANG_STOPS.items():
        score = sum(1 for w in words if w in stops)
        if score > best_score: best, best_score = lang, score
    return best
def extract_summary(text: str, max_sentences: int = 2) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", normalize(text)) if s.strip()]
    return " ".join(sentences[:max_sentences])
def extract_topics(text: str, n: int = 5) -> list[str]:
    words = re.findall(r"[a-zà-ÿ]{4,}", (text or "").lower())
    stops = STOP_WORDS
    freq = Counter(w for w in words if w not in stops)
    return [w for w, _ in freq.most_common(n)]
def extract_metadata(text: str) -> dict:
    return {"language": detect_language(text), "summary": extract_summary(text), "topics": extract_topics(text), "word_count": len((text or "").split())}
