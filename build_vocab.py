#!/usr/bin/env python3
"""Build single-file Sinhala-English vocabulary learning platform."""

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
DICT_FILE = ROOT / "en-si-compact.txt"
FREQ_URL = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt"
OUTPUT = ROOT / "sinhala-english-vocabulary.html"

# Category keyword buckets (English word -> category)
CATEGORY_KEYWORDS = {
    "greetings": {
        "hello", "hi", "goodbye", "bye", "thanks", "thank", "please", "sorry",
        "welcome", "morning", "evening", "night", "yes", "no", "ok", "okay",
    },
    "family": {
        "mother", "father", "parent", "son", "daughter", "brother", "sister",
        "family", "child", "children", "baby", "husband", "wife", "grandfather",
        "grandmother", "uncle", "aunt", "cousin", "friend", "man", "woman", "boy", "girl",
    },
    "food": {
        "food", "eat", "drink", "water", "rice", "bread", "milk", "tea", "coffee",
        "fruit", "vegetable", "meat", "fish", "egg", "sugar", "salt", "cook", "kitchen",
        "breakfast", "lunch", "dinner", "hungry", "thirsty", "apple", "banana", "orange",
    },
    "numbers": {
        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "twenty", "thirty", "hundred", "thousand", "million",
        "first", "second", "third", "number", "count", "zero",
    },
    "colors": {
        "color", "colour", "red", "blue", "green", "yellow", "black", "white",
        "brown", "orange", "pink", "purple", "gray", "grey", "dark", "light",
    },
    "body": {
        "head", "eye", "ear", "nose", "mouth", "hand", "foot", "leg", "arm",
        "finger", "toe", "hair", "face", "heart", "blood", "bone", "skin", "teeth",
        "body", "health", "sick", "pain", "doctor", "hospital", "medicine",
    },
    "nature": {
        "sun", "moon", "star", "sky", "cloud", "rain", "wind", "tree", "flower",
        "plant", "leaf", "grass", "river", "sea", "ocean", "mountain", "earth",
        "fire", "water", "stone", "rock", "animal", "bird", "dog", "cat", "fish",
    },
    "home": {
        "house", "home", "room", "door", "window", "wall", "floor", "roof", "bed",
        "table", "chair", "kitchen", "bathroom", "garden", "key", "light", "clean",
    },
    "school": {
        "school", "student", "teacher", "class", "book", "read", "write", "learn",
        "study", "exam", "test", "paper", "pen", "pencil", "lesson", "education",
        "university", "college", "library", "homework",
    },
    "work": {
        "work", "job", "office", "business", "company", "money", "pay", "salary",
        "boss", "employee", "meeting", "project", "market", "shop", "store", "buy",
        "sell", "price", "cost",
    },
    "travel": {
        "travel", "trip", "road", "car", "bus", "train", "plane", "airport",
        "ticket", "map", "city", "country", "place", "visit", "hotel", "passport",
        "drive", "walk", "run", "fast", "slow", "left", "right", "north", "south",
    },
    "time": {
        "time", "day", "week", "month", "year", "hour", "minute", "second",
        "today", "tomorrow", "yesterday", "now", "before", "after", "early", "late",
        "morning", "afternoon", "evening", "night", "clock", "calendar",
    },
    "emotions": {
        "happy", "sad", "angry", "love", "hate", "fear", "hope", "feel", "think",
        "know", "believe", "want", "need", "like", "enjoy", "worry", "surprise",
    },
    "actions": {
        "go", "come", "see", "look", "hear", "speak", "talk", "say", "tell", "ask",
        "give", "take", "make", "do", "get", "put", "open", "close", "start", "stop",
        "help", "use", "try", "find", "keep", "leave", "call", "wait", "move", "play",
    },
    "technology": {
        "computer", "phone", "internet", "email", "website", "software", "data",
        "digital", "online", "screen", "keyboard", "camera", "video", "photo",
        "machine", "electric", "power", "battery", "network", "system",
    },
}

# Word endings hint at part of speech
POS_SUFFIXES = {
    "verb": ("ing", "ed", "ize", "ise", "ify"),
    "adjective": ("ful", "less", "ous", "ive", "able", "ible", "al", "ic", "ish"),
    "adverb": ("ly",),
    "noun": ("tion", "sion", "ness", "ment", "ity", "ism", "ist", "er", "or"),
}


def load_frequency_list() -> list[str]:
    try:
        with urllib.request.urlopen(FREQ_URL, timeout=30) as resp:
            text = resp.read().decode("utf-8")
        return [w.strip().lower() for w in text.splitlines() if w.strip()]
    except Exception:
        local = ROOT / "google-10000-english-no-swears.txt"
        if local.exists():
            return [w.strip().lower() for w in local.read_text(encoding="utf-8").splitlines() if w.strip()]
        return []


def load_dictionary() -> dict[str, str]:
    """Load English -> Sinhala (shortest meaning per word)."""
    mapping: dict[str, str] = {}
    if not DICT_FILE.exists():
        raise FileNotFoundError(f"Dictionary not found: {DICT_FILE}")

    with DICT_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "\t" not in line:
                continue
            en, si = line.split("\t", 1)
            en = en.strip().lower()
            si = si.strip()
            if not en or not si:
                continue
            # Skip hyphenated / technical compound entries for beginners
            if "-" in en and len(en) > 12:
                continue
            # Keep shortest Sinhala gloss (usually clearest)
            if en not in mapping or len(si) < len(mapping[en]):
                mapping[en] = si
    return mapping


def is_simple_word(word: str) -> bool:
    if not word or len(word) > 20:
        return False
    if re.search(r"[^a-z]", word):
        return False
    return True


def difficulty_score(word: str, freq_rank: int | None) -> int:
    """1 = easiest, 4 = hardest."""
    length = len(word)
    score = 0
    if freq_rank is not None:
        if freq_rank < 500:
            score += 0
        elif freq_rank < 2000:
            score += 1
        elif freq_rank < 5000:
            score += 2
        else:
            score += 3
    else:
        score += 2

    if length <= 4:
        score += 0
    elif length <= 6:
        score += 1
    elif length <= 9:
        score += 2
    else:
        score += 3

    return min(4, max(1, (score // 2) + 1))


def sort_key(word: str, freq_rank: int | None) -> tuple:
    rank = freq_rank if freq_rank is not None else 99999
    return (rank, len(word), word)


def guess_category(word: str) -> str:
    for cat, words in CATEGORY_KEYWORDS.items():
        if word in words:
            return cat
    # Prefix match for related forms
    for cat, words in CATEGORY_KEYWORDS.items():
        for w in words:
            if word.startswith(w) and len(word) - len(w) <= 3:
                return cat
    return "general"


def guess_pos(word: str) -> str:
    for pos, suffixes in POS_SUFFIXES.items():
        for suf in suffixes:
            if word.endswith(suf) and len(word) > len(suf) + 2:
                return pos
    return "general"


def build_vocabulary(target: int = 10000) -> list[dict]:
    dictionary = load_dictionary()
    freq_list = load_frequency_list()
    freq_index = {w: i for i, w in enumerate(freq_list)}

    selected: list[dict] = []
    seen: set[str] = set()

    # Phase 1: frequency-ordered common words
    for rank, word in enumerate(freq_list):
        if len(selected) >= target:
            break
        if word in seen or not is_simple_word(word):
            continue
        if word not in dictionary:
            continue
        seen.add(word)
        selected.append({
            "id": len(selected),
            "en": word,
            "si": dictionary[word],
            "cat": guess_category(word),
            "pos": guess_pos(word),
            "diff": difficulty_score(word, rank),
            "rank": rank,
        })

    # Phase 2: fill with remaining simple dictionary words sorted by simplicity
    extras = []
    for word, meaning in dictionary.items():
        if word in seen or not is_simple_word(word):
            continue
        rank = freq_index.get(word)
        extras.append((sort_key(word, rank), word, meaning, rank))

    extras.sort(key=lambda x: x[0])
    for _, word, meaning, rank in extras:
        if len(selected) >= target:
            break
        seen.add(word)
        selected.append({
            "id": len(selected),
            "en": word,
            "si": meaning,
            "cat": guess_category(word),
            "pos": guess_pos(word),
            "diff": difficulty_score(word, rank),
            "rank": rank if rank is not None else 99999,
        })

    # Final sort: simple first (by rank, length, difficulty)
    selected.sort(key=lambda w: (w["rank"], w["diff"], len(w["en"]), w["en"]))
    for i, item in enumerate(selected):
        item["id"] = i
    return selected


def compact_vocab_json(words: list[dict]) -> str:
    """Minified array: [id, en, si, cat, pos, diff]"""
    rows = [[w["id"], w["en"], w["si"], w["cat"], w["pos"], w["diff"]] for w in words]
    return json.dumps(rows, ensure_ascii=False, separators=(",", ":"))


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="si">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>English Vocabulary for Sinhala Speakers | 10,000 Words</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Sinhala:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0f1419;
  --surface: #1a2332;
  --surface2: #243044;
  --border: #2d3a4f;
  --text: #e8edf4;
  --muted: #8b9cb3;
  --accent: #3b82f6;
  --accent-hover: #2563eb;
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
  --radius: 12px;
  --shadow: 0 4px 24px rgba(0,0,0,.35);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Inter', 'Noto Sans Sinhala', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.5;
}
.app { max-width: 1200px; margin: 0 auto; padding: 16px 20px 48px; }

header {
  text-align: center;
  padding: 28px 0 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
}
header h1 {
  font-size: clamp(1.4rem, 4vw, 2rem);
  font-weight: 700;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
header p { color: var(--muted); margin-top: 8px; font-size: .95rem; }

.stats-bar {
  display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;
  margin: 20px 0;
}
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 20px;
  min-width: 120px;
  text-align: center;
}
.stat-card .num { font-size: 1.5rem; font-weight: 700; color: var(--accent); }
.stat-card .lbl { font-size: .75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }

.controls {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
}
.search-row { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.search-wrap { flex: 1; min-width: 200px; position: relative; }
.search-wrap svg {
  position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
  width: 18px; height: 18px; color: var(--muted); pointer-events: none;
}
#searchInput {
  width: 100%; padding: 12px 14px 12px 42px;
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 10px; color: var(--text); font-size: 1rem;
  font-family: inherit;
}
#searchInput:focus { outline: 2px solid var(--accent); border-color: transparent; }
#searchInput::placeholder { color: var(--muted); }

.filter-section { margin-bottom: 14px; }
.filter-section:last-child { margin-bottom: 0; }
.filter-label {
  font-size: .72rem; font-weight: 600; color: var(--muted);
  text-transform: uppercase; letter-spacing: .08em; margin-bottom: 8px;
}
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  padding: 6px 14px; border-radius: 999px; font-size: .82rem;
  border: 1px solid var(--border); background: var(--surface2);
  color: var(--text); cursor: pointer; transition: all .15s;
  user-select: none;
}
.chip:hover { border-color: var(--accent); color: var(--accent); }
.chip.active { background: var(--accent); border-color: var(--accent); color: #fff; }

.toolbar {
  display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
  justify-content: space-between; margin-bottom: 16px;
}
.result-info { color: var(--muted); font-size: .9rem; }
.toolbar-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.btn {
  padding: 8px 16px; border-radius: 8px; font-size: .85rem; font-weight: 500;
  border: 1px solid var(--border); background: var(--surface2);
  color: var(--text); cursor: pointer; font-family: inherit;
  transition: all .15s;
}
.btn:hover { border-color: var(--accent); }
.btn-primary { background: var(--accent); border-color: var(--accent); color: #fff; }
.btn-primary:hover { background: var(--accent-hover); }
.btn-danger { border-color: var(--danger); color: var(--danger); }
.btn-danger:hover { background: var(--danger); color: #fff; }

.word-list { display: flex; flex-direction: column; gap: 8px; }
.word-card {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 14px; align-items: start;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  transition: border-color .15s, opacity .15s;
}
.word-card.learned { opacity: .65; border-color: rgba(34,197,94,.35); }
.word-card.learned .en-word { text-decoration: line-through; color: var(--muted); }

.check-wrap { padding-top: 4px; }
.check-wrap input[type="checkbox"] {
  width: 20px; height: 20px; cursor: pointer; accent-color: var(--success);
}
.word-body { min-width: 0; }
.en-word {
  font-size: 1.15rem; font-weight: 600; color: #fff;
  margin-bottom: 4px; word-break: break-word;
}
.si-meaning {
  font-family: 'Noto Sans Sinhala', sans-serif;
  font-size: 1.05rem; color: #cbd5e1; word-break: break-word;
}
.meta-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.tag {
  font-size: .68rem; padding: 3px 8px; border-radius: 6px;
  font-weight: 500; text-transform: capitalize;
}
.tag-cat { background: rgba(59,130,246,.15); color: #93c5fd; }
.tag-pos { background: rgba(167,139,250,.15); color: #c4b5fd; }
.tag-diff-1 { background: rgba(34,197,94,.15); color: #86efac; }
.tag-diff-2 { background: rgba(34,197,94,.2); color: #4ade80; }
.tag-diff-3 { background: rgba(245,158,11,.15); color: #fcd34d; }
.tag-diff-4 { background: rgba(239,68,68,.15); color: #fca5a5; }

.diff-badge {
  font-size: .7rem; padding: 4px 10px; border-radius: 8px;
  white-space: nowrap; font-weight: 600;
}
.rank-num { font-size: .75rem; color: var(--muted); min-width: 36px; text-align: right; padding-top: 6px; }

.empty-state {
  text-align: center; padding: 60px 20px; color: var(--muted);
}
.empty-state h3 { font-size: 1.2rem; margin-bottom: 8px; color: var(--text); }

.load-more-wrap { text-align: center; margin-top: 24px; }
#loadMoreBtn { min-width: 200px; }

.progress-wrap {
  height: 6px; background: var(--surface2); border-radius: 99px;
  overflow: hidden; margin-top: 12px;
}
.progress-bar {
  height: 100%; background: linear-gradient(90deg, var(--accent), var(--success));
  border-radius: 99px; transition: width .3s;
}

@media (max-width: 600px) {
  .word-card { grid-template-columns: auto 1fr; }
  .rank-num { display: none; }
}
</style>
</head>
<body>
<div class="app">
  <header>
    <h1>🇱🇰 English Vocabulary Learner</h1>
    <p>සිංහල භාෂාව දන්නා අයට English — 10,000 words with Sinhala meanings</p>
    <div class="stats-bar">
      <div class="stat-card"><div class="num" id="totalWords">0</div><div class="lbl">Total Words</div></div>
      <div class="stat-card"><div class="num" id="learnedCount">0</div><div class="lbl">Learned</div></div>
      <div class="stat-card"><div class="num" id="remainingCount">0</div><div class="lbl">Remaining</div></div>
      <div class="stat-card"><div class="num" id="shownCount">0</div><div class="lbl">Showing</div></div>
    </div>
    <div class="progress-wrap"><div class="progress-bar" id="progressBar" style="width:0%"></div></div>
  </header>

  <div class="controls">
    <div class="search-row">
      <div class="search-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input type="search" id="searchInput" placeholder="Search English or Sinhala (ඉංග්‍රීසි හෝ සිංහල)...">
      </div>
      <button class="btn" id="clearSearchBtn" type="button">Clear</button>
    </div>

    <div class="filter-section">
      <div class="filter-label">Category / කාණ්ඩය</div>
      <div class="chip-row" id="categoryFilters"></div>
    </div>
    <div class="filter-section">
      <div class="filter-label">Difficulty / දුෂ්කරතාව</div>
      <div class="chip-row" id="difficultyFilters"></div>
    </div>
    <div class="filter-section">
      <div class="filter-label">Word Type / වචන වර්ගය</div>
      <div class="chip-row" id="posFilters"></div>
    </div>
    <div class="filter-section">
      <div class="filter-label">Status / තත්වය</div>
      <div class="chip-row" id="statusFilters">
        <span class="chip active" data-status="all">All</span>
        <span class="chip" data-status="pending">To Learn</span>
        <span class="chip" data-status="learned">Learned ✓</span>
      </div>
    </div>
  </div>

  <div class="toolbar">
    <span class="result-info" id="resultInfo">Loading...</span>
    <div class="toolbar-actions">
      <button class="btn" id="hideLearnedBtn" type="button">Hide Learned</button>
      <button class="btn btn-danger" id="resetProgressBtn" type="button">Reset Progress</button>
    </div>
  </div>

  <div class="word-list" id="wordList"></div>
  <div class="load-more-wrap" id="loadMoreWrap" style="display:none">
    <button class="btn btn-primary" id="loadMoreBtn" type="button">Load More Words</button>
  </div>
</div>

<script>
(function() {
  const STORAGE_KEY = 'sinhala_vocab_learned_v1';
  const PAGE_SIZE = 80;

  // Compact data: [id, en, si, cat, pos, diff]
  const RAW = __VOCAB_DATA__;

  const WORDS = RAW.map(([id, en, si, cat, pos, diff]) => ({ id, en, si, cat, pos, diff }));

  const CATEGORIES = [...new Set(WORDS.map(w => w.cat))].sort();
  const POS_TYPES = [...new Set(WORDS.map(w => w.pos))].sort();
  const DIFF_LABELS = { 1: 'Beginner', 2: 'Easy', 3: 'Medium', 4: 'Advanced' };
  const CAT_LABELS = {
    greetings: 'Greetings', family: 'Family', food: 'Food & Drink', numbers: 'Numbers',
    colors: 'Colors', body: 'Body & Health', nature: 'Nature', home: 'Home',
    school: 'School', work: 'Work & Business', travel: 'Travel', time: 'Time & Dates',
    emotions: 'Feelings', actions: 'Common Actions', technology: 'Technology', general: 'General'
  };

  let learned = loadLearned();
  let state = {
    search: '',
    category: 'all',
    difficulty: 'all',
    pos: 'all',
    status: 'all',
    hideLearned: false,
    displayCount: PAGE_SIZE
  };

  function loadLearned() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? new Set(JSON.parse(raw)) : new Set();
    } catch { return new Set(); }
  }

  function saveLearned() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...learned]));
    updateStats();
  }

  function isLearned(id) { return learned.has(id); }

  function getFiltered() {
    const q = state.search.trim().toLowerCase();
    return WORDS.filter(w => {
      if (state.category !== 'all' && w.cat !== state.category) return false;
      if (state.difficulty !== 'all' && w.diff !== +state.difficulty) return false;
      if (state.pos !== 'all' && w.pos !== state.pos) return false;
      const done = isLearned(w.id);
      if (state.status === 'learned' && !done) return false;
      if (state.status === 'pending' && done) return false;
      if (state.hideLearned && done) return false;
      if (q) {
        const matchEn = w.en.includes(q);
        const matchSi = w.si.includes(q) || w.si.includes(state.search.trim());
        if (!matchEn && !matchSi) return false;
      }
      return true;
    });
  }

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function renderFilters() {
    const catEl = document.getElementById('categoryFilters');
    catEl.innerHTML = '<span class="chip active" data-cat="all">All</span>' +
      CATEGORIES.map(c => `<span class="chip" data-cat="${esc(c)}">${esc(CAT_LABELS[c] || c)}</span>`).join('');

    const diffEl = document.getElementById('difficultyFilters');
    diffEl.innerHTML = '<span class="chip active" data-diff="all">All</span>' +
      [1,2,3,4].map(d => `<span class="chip" data-diff="${d}">${DIFF_LABELS[d]}</span>`).join('');

    const posEl = document.getElementById('posFilters');
    posEl.innerHTML = '<span class="chip active" data-pos="all">All</span>' +
      POS_TYPES.map(p => `<span class="chip" data-pos="${esc(p)}">${esc(p)}</span>`).join('');
  }

  function renderList() {
    const filtered = getFiltered();
    const slice = filtered.slice(0, state.displayCount);
    const list = document.getElementById('wordList');

    document.getElementById('shownCount').textContent = slice.length;
    document.getElementById('resultInfo').textContent =
      `Showing ${slice.length} of ${filtered.length} words (simple → advanced order)`;

    const loadWrap = document.getElementById('loadMoreWrap');
    loadWrap.style.display = state.displayCount < filtered.length ? 'block' : 'none';

    if (!slice.length) {
      list.innerHTML = `<div class="empty-state"><h3>No words found</h3><p>Try changing filters or search term</p></div>`;
      return;
    }

    list.innerHTML = slice.map((w, i) => {
      const done = isLearned(w.id);
      return `<article class="word-card${done ? ' learned' : ''}" data-id="${w.id}">
        <div class="check-wrap">
          <input type="checkbox" aria-label="Mark as learned" ${done ? 'checked' : ''} data-id="${w.id}">
        </div>
        <div class="word-body">
          <div class="en-word">${esc(w.en)}</div>
          <div class="si-meaning">${esc(w.si)}</div>
          <div class="meta-tags">
            <span class="tag tag-cat">${esc(CAT_LABELS[w.cat] || w.cat)}</span>
            <span class="tag tag-pos">${esc(w.pos)}</span>
            <span class="tag tag-diff-${w.diff}">${esc(DIFF_LABELS[w.diff])}</span>
          </div>
        </div>
        <div class="rank-num">#${i + 1}</div>
      </article>`;
    }).join('');

    list.querySelectorAll('input[type=checkbox]').forEach(cb => {
      cb.addEventListener('change', e => {
        const id = +e.target.dataset.id;
        if (e.target.checked) learned.add(id); else learned.delete(id);
        saveLearned();
        renderList();
      });
    });
  }

  function updateStats() {
    const total = WORDS.length;
    const learnedN = learned.size;
    document.getElementById('totalWords').textContent = total.toLocaleString();
    document.getElementById('learnedCount').textContent = learnedN.toLocaleString();
    document.getElementById('remainingCount').textContent = (total - learnedN).toLocaleString();
    document.getElementById('progressBar').style.width = total ? ((learnedN / total) * 100).toFixed(1) + '%' : '0%';
  }

  function resetFilters() {
    state.search = '';
    state.category = 'all';
    state.difficulty = 'all';
    state.pos = 'all';
    state.status = 'all';
    state.displayCount = PAGE_SIZE;
    document.getElementById('searchInput').value = '';
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('[data-cat="all"],[data-diff="all"],[data-pos="all"],[data-status="all"]').forEach(c => c.classList.add('active'));
  }

  function bindEvents() {
    let searchTimer;
    document.getElementById('searchInput').addEventListener('input', e => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        state.search = e.target.value;
        state.displayCount = PAGE_SIZE;
        renderList();
      }, 180);
    });

    document.getElementById('clearSearchBtn').addEventListener('click', () => {
      state.search = '';
      document.getElementById('searchInput').value = '';
      state.displayCount = PAGE_SIZE;
      renderList();
    });

    document.getElementById('categoryFilters').addEventListener('click', e => {
      const chip = e.target.closest('[data-cat]');
      if (!chip) return;
      state.category = chip.dataset.cat;
      state.displayCount = PAGE_SIZE;
      document.querySelectorAll('#categoryFilters .chip').forEach(c => c.classList.toggle('active', c === chip));
      renderList();
    });

    document.getElementById('difficultyFilters').addEventListener('click', e => {
      const chip = e.target.closest('[data-diff]');
      if (!chip) return;
      state.difficulty = chip.dataset.diff;
      state.displayCount = PAGE_SIZE;
      document.querySelectorAll('#difficultyFilters .chip').forEach(c => c.classList.toggle('active', c === chip));
      renderList();
    });

    document.getElementById('posFilters').addEventListener('click', e => {
      const chip = e.target.closest('[data-pos]');
      if (!chip) return;
      state.pos = chip.dataset.pos;
      state.displayCount = PAGE_SIZE;
      document.querySelectorAll('#posFilters .chip').forEach(c => c.classList.toggle('active', c === chip));
      renderList();
    });

    document.getElementById('statusFilters').addEventListener('click', e => {
      const chip = e.target.closest('[data-status]');
      if (!chip) return;
      state.status = chip.dataset.status;
      state.displayCount = PAGE_SIZE;
      document.querySelectorAll('#statusFilters .chip').forEach(c => c.classList.toggle('active', c === chip));
      renderList();
    });

    document.getElementById('hideLearnedBtn').addEventListener('click', e => {
      state.hideLearned = !state.hideLearned;
      e.target.textContent = state.hideLearned ? 'Show Learned' : 'Hide Learned';
      e.target.classList.toggle('btn-primary', state.hideLearned);
      state.displayCount = PAGE_SIZE;
      renderList();
    });

    document.getElementById('loadMoreBtn').addEventListener('click', () => {
      state.displayCount += PAGE_SIZE;
      renderList();
    });

    document.getElementById('resetProgressBtn').addEventListener('click', () => {
      if (confirm('Reset all learned words? This cannot be undone.')) {
        learned = new Set();
        saveLearned();
        renderList();
      }
    });
  }

  renderFilters();
  bindEvents();
  updateStats();
  renderList();
})();
</script>
</body>
</html>
"""


def main():
    print("Loading dictionary...")
    words = build_vocabulary(10000)
    print(f"Built {len(words)} vocabulary entries")

    vocab_json = compact_vocab_json(words)
    html = HTML_TEMPLATE.replace("__VOCAB_DATA__", vocab_json)

    OUTPUT.write_text(html, encoding="utf-8")
    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"Written: {OUTPUT} ({size_mb:.2f} MB)")

    # Stats
    cats = {}
    diffs = {}
    for w in words:
        cats[w["cat"]] = cats.get(w["cat"], 0) + 1
        diffs[w["diff"]] = diffs.get(w["diff"], 0) + 1
    print("Categories:", dict(sorted(cats.items(), key=lambda x: -x[1])[:8]))
    print("Difficulty:", diffs)


if __name__ == "__main__":
    main()
