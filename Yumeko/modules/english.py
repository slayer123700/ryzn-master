__module__ = "English"

__help__ = """
 ❍ /define <text>*:* Type the word or expression you want to search.
    For example: /define kill
 ❍ /spell*:* Reply to a message, will reply with a grammar-corrected version.
 ❍ /synonyms <word>*:* Find the synonyms of a word.
 ❍ /antonyms <word>*:* Find the antonyms of a word.
"""

import difflib
from pyrogram import filters
from pyrogram.types import Message
from Yumeko import app
import nltk
from nltk.corpus import wordnet

# Make sure you run this once:
# nltk.download("wordnet")
# nltk.download("omw-1.4")

# ---------------- SPELLCHECKER FOR COMMANDS -----------------
VALID_COMMANDS = ["define", "synonyms", "antonyms", "spell"]

def correct_command(cmd: str):
    """Find closest valid command using difflib"""
    match = difflib.get_close_matches(cmd.lower(), VALID_COMMANDS, n=1, cutoff=0.7)
    return match[0] if match else cmd

@app.on_message(filters.command(VALID_COMMANDS, prefixes=["/", "."]))
async def command_handler(_, message: Message):
    cmd = message.command[0].lower()
    corrected = correct_command(cmd)
    if corrected != cmd:
        # Replace and re-run
        message.command[0] = corrected
        if corrected == "define":
            await define(_, message)
        elif corrected == "synonyms":
            await synonyms(_, message)
        elif corrected == "antonyms":
            await antonyms(_, message)
        elif corrected == "spell":
            await spell(_, message)

# ---------------- DEFINE -----------------
async def define(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /define <word>")
    word = message.text.split(None, 1)[1]
    synsets = wordnet.synsets(word)
    if not synsets:
        return await message.reply_text("❌ No definition found.")
    defs = [f"• {s.definition()}" for s in synsets[:5]]  # Limit 5
    await message.reply_text("\n".join(defs))

# ---------------- SYNONYMS -----------------
async def synonyms(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /synonyms <word>")
    word = message.text.split(None, 1)[1]
    syns = {lemma.name() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}
    if not syns:
        return await message.reply_text("❌ No synonyms found.")
    await message.reply_text(", ".join(list(syns)[:20]))  # Limit 20

# ---------------- ANTONYMS -----------------
async def antonyms(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /antonyms <word>")
    word = message.text.split(None, 1)[1]
    ants = {lemma.antonyms()[0].name() for syn in wordnet.synsets(word) for lemma in syn.lemmas() if lemma.antonyms()}
    if not ants:
        return await message.reply_text("❌ No antonyms found.")
    await message.reply_text(", ".join(list(ants)))

# ---------------- SPELL -----------------
@app.on_message(filters.command("spell", prefixes=["/", "."]))
async def spell(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /spell <word>")
    word = message.text.split(None, 1)[1]

    # Collect dictionary words from WordNet
    dictionary_words = set(wordnet.words())
    suggestions = difflib.get_close_matches(word, dictionary_words, n=5, cutoff=0.7)

    if not suggestions:
        return await message.reply_text("❌ No spelling suggestions found.")

    await message.reply_text(
        f"🔎 **Did you mean:**\n" + "\n".join([f"• {s}" for s in suggestions])
    )