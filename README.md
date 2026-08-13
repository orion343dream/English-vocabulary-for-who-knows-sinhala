# English Vocabulary for Sinhala Speakers

> **සිංහල භාෂාව දන්නා අයට English** — A free, offline-ready vocabulary learning platform with **10,000 English words** and Sinhala meanings.

[![Words](https://img.shields.io/badge/words-10%2C000-blue?style=flat-square)](https://github.com/orion343dream/English-vocabulary-for-who-knows-sinhala)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](#license)
[![HTML](https://img.shields.io/badge/built%20with-single%20HTML-orange?style=flat-square)](#quick-start)
[![Python](https://img.shields.io/badge/build-Python%203-yellow?style=flat-square)](#rebuild-from-source)

---

## Overview

This project helps **Sinhala speakers who are beginning to learn English**. Everything runs in **one HTML file** — no install, no server, no account. Open it in any modern browser and start learning immediately.

Words are ordered from **simple and common** to **more advanced**, so beginners always see easy vocabulary first.

---

## Features

| Feature | Description |
|--------|-------------|
| **10,000 words** | Curated English vocabulary with Sinhala translations |
| **Smart ordering** | Simple, high-frequency words first; harder words later |
| **Dual search** | Search in English **or** Sinhala |
| **Categories** | Greetings, Family, Food, Numbers, Colors, Body, Nature, Home, School, Work, Travel, Time, Feelings, Actions, Technology, and more |
| **Difficulty levels** | Beginner → Easy → Medium → Advanced |
| **Word types** | Filter by noun, verb, adjective, adverb, and general |
| **Progress tracking** | Checkbox each word when you have learned it |
| **Persistent storage** | Progress saved in your browser (`localStorage`) — survives refresh and restart |
| **Progress dashboard** | Total, learned, remaining counts and a visual progress bar |
| **Hide learned** | Focus only on words you have not mastered yet |
| **Responsive UI** | Works on desktop, tablet, and mobile |
| **Pagination** | Loads 80 words at a time for smooth performance |

---

## Quick Start

### Option 1 — Use the app (recommended)

1. Clone or download this repository.
2. Open **`sinhala-english-vocabulary.html`** in Chrome, Edge, or Firefox.
3. Start with **Beginner** difficulty and work your way up.

```bash
git clone https://github.com/orion343dream/English-vocabulary-for-who-knows-sinhala.git
cd English-vocabulary-for-who-knows-sinhala
# Then double-click sinhala-english-vocabulary.html
```

### Option 2 — GitHub Pages (optional)

You can enable **GitHub Pages** on this repo and set the source to the `main` branch. The app will be available at:

`https://orion343dream.github.io/English-vocabulary-for-who-knows-sinhala/sinhala-english-vocabulary.html`

---

## How to Use

1. **Browse** — Words appear from easiest to hardest by default.
2. **Filter** — Use category chips (e.g. Food, Family, Travel) to study by topic.
3. **Search** — Type an English word or Sinhala meaning to find it instantly.
4. **Mark as learned** — Check the box next to a word when you know it.
5. **Track progress** — Watch the progress bar and stats at the top update in real time.
6. **Hide learned** — Toggle **Hide Learned** to see only words you still need.
7. **Reset** — Use **Reset Progress** to clear all checkmarks (with confirmation).

> **Note:** Progress is stored locally on your device. It is not synced across browsers or devices.

---

## Project Structure

```
English-vocabulary-for-who-knows-sinhala/
├── sinhala-english-vocabulary.html   # Main app — open this file
├── build_vocab.py                    # Script to rebuild the HTML from source data
├── en-si-compact.txt                 # English–Sinhala dictionary source
└── README.md
```

| File | Purpose |
|------|---------|
| `sinhala-english-vocabulary.html` | Complete learning app (HTML + CSS + JS + embedded word data) |
| `build_vocab.py` | Generates the HTML file from the dictionary and frequency list |
| `en-si-compact.txt` | Tab-separated English → Sinhala dictionary |

---

## Rebuild from Source

If you modify the dictionary or build script, regenerate the HTML file:

**Requirements:** Python 3.8+

```bash
python build_vocab.py
```

This produces an updated `sinhala-english-vocabulary.html` with up to 10,000 words, sorted by frequency and difficulty.

---

## Data Sources

| Source | Use |
|--------|-----|
| [Niweera/en-si](https://github.com/Niweera/en-si) | English–Sinhala dictionary (`en-si-compact.txt`) |
| [google-10000-english](https://github.com/first20hours/google-10000-english) | Word frequency list for beginner-friendly ordering |

---

## Tech Stack

- **Single-file architecture** — No frameworks, no build step required to use the app
- **Vanilla JavaScript** — Search, filters, and progress logic
- **localStorage** — Persistent learned-word tracking
- **Google Fonts** — Noto Sans Sinhala + Inter (with system font fallbacks offline)

---

## Author

**Dilusha Sandaruwan**

- GitHub: [@orion343dream](https://github.com/orion343dream)

---

## License

Dictionary data is derived from open community sources (see [Data Sources](#data-sources)). Project code is provided for educational use. Please respect the licenses of the original dictionary repositories when redistributing.

---

## Contributing

Contributions are welcome. You can:

- Improve Sinhala translations or categorization in `build_vocab.py`
- Report incorrect meanings or missing common words
- Suggest UI improvements or new study modes (flashcards, quizzes, etc.)

Open an issue or pull request on this repository.

---

<p align="center">
  <strong>Happy learning! · <em>ඉගෙනීම සතුටක්!</em></strong>
</p>
