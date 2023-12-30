from aqt import mw
from aqt.utils import showInfo, showWarning
from aqt.qt import *
import requests
import json
import os
import time
# from aqt.utils import ImportHelper

API_URL = "https://libretranslate.de/translate"

def translate(kanji):
    data = {"q": kanji, "source": "ja", "target": "en", "format": "text"}

    try:
        response = requests.post(API_URL, data=data)
        response.raise_for_status()
        time.sleep(1)
    except requests.exceptions.RequestException as e:
        showWarning("Error connecting to translation API: " + str(e))
        return ""

    try: 
        romaji = json.loads(response.text)["translatedText"]
    except json.decoder.JSONDecodeError:
        showWarning("Invalid response from API")
        return ""

    return romaji

# def backup_deck():
#     backup_name = mw.col.decks.name + "_backup"
#     mw.col.decks.check(backup_name)
#     ImportHelper.backup_name(backup_name)
#     mw.col.decks.save(ImportHelper.get_backup_path(backup_name))

def show_progress(current, total):
    # Show the percentage of progress in the status bar
    percent = round((current / total) * 100, 2)
    mw.progress.update(label=f"Updating deck: {percent}%")

def select_deck():
    # Show a dialog to select a deck from the available decks
    deck, ok = QInputDialog.getItem(None, 'Select Deck',  
                            'Deck:', mw.col.decks.allNames())
    if ok:
        return deck
    else:
        return None

def select_fields():
    # Show a dialog to select two fields: one for Kanji and one for Romaji
    fields = mw.col.models.fieldNames(mw.col.models.current())
    kanji_field, ok1 = QInputDialog.getItem(None, 'Select Kanji Field',  
                            'Field:', fields)
    if ok1:
        romaji_field, ok2 = QInputDialog.getItem(None, 'Select Romaji Field',  
                            'Field:', fields)
        if ok2:
            return kanji_field, romaji_field
    return None, None

def show_progress(current, total):
    # Show the percentage of progress in the status bar
    percent = round((current / total) * 100, 2)
    mw.progress.update(label=f"Updating deck: {percent}%")

def log_errors(error):
    # Write the errors to a file called "errors.log" in the addon folder
    error_file = os.path.join(mw.pm.addonFolder(), "errors.log")
    with open(error_file, 'a') as f:
        f.write(error + '\n')

def update_deck():
    # Update the selected deck with Romaji translations
    deck = select_deck()
    if not deck:
        return

    # backup_deck()

    kanji_field, romaji_field = select_fields()
    if not kanji_field or not romaji_field:
        return

    notes = mw.col.findNotes(f'"deck:{deck}"') 

    total = len(notes)

    for idx, note_id in enumerate(notes):
        note = mw.col.getNote(note_id)
        kanji = note[kanji_field]
        romaji = translate(kanji)
        if romaji:
            note[romaji_field] = romaji
            note.flush()
        else:
            error = f"Failed to translate note {note_id}: {kanji}"
            log_errors(error)
        show_progress(idx+1, total)

    showInfo("Update complete")

# Add menu item
action = QAction("Update Deck (✿◡‿◡)", mw)
action.triggered.connect(update_deck)
mw.form.menuTools.addAction(action)