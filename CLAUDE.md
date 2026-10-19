# Kalorien-Tracker – Anleitung für Claude

Jubal schickt in einem Chat, was er gegessen hat: Text, Fotos von Nährwert-Etiketten, Mengen in Gramm.
Deine Aufgabe ist, das in die Daten einzutragen, zu committen und auf `main` zu pushen. Nichts anderes ändern,
außer Jubal will das ausdrücklich.

## 🔒 Verschlüsselung – wichtig
Das Repo ist öffentlich. Die Daten liegen deshalb **nur verschlüsselt** in `data.enc.json` (AES-256-GCM).
Die App entschlüsselt sie im Browser. Das Passwort steht im Skill „kalorien-eintragen“ (nicht im Repo!)
oder Jubal nennt es dir.
- Klartext `data.json` ist per `.gitignore` ausgeschlossen. **Niemals Klartext-Daten committen**, auch nicht
  in Commit-Messages: Die Commit-Message ist neutral, z. B. `Daten aktualisiert`, ohne Lebensmittel.
- Passwort nie in Dateien im Repo schreiben.

Live: https://jubal8010.github.io/kalorien-tracker/

## Ablauf
1. Repo holen (`jubal8010/kalorien-tracker`). Frisch klonen; schlägt `git pull` wegen
   „unrelated histories“ fehl, neu klonen.
   Dann entschlüsseln: `KT_PASS='<passwort>' python3 tools/crypt.py decrypt` → erzeugt `data.json`.
2. Für jedes Lebensmittel die Nährwerte bestimmen (Reihenfolge der Quellen):
   1. Etikett / Werte, die Jubal schickt
   2. Bereits gespeichertes Produkt in `produkte`
   3. Bekannte Standardwerte (z. B. Reis roh, Hühnerbrust roh). Bei Unsicherheit roh/gekocht nachfragen
      oder die Annahme in `notiz` vermerken.
3. Werte auf die gegessene Menge umrechnen: `wert = pro100g × menge / 100`.
   Rechne das in Code (python), nicht im Kopf. kcal ganzzahlig, Makros auf 1 Nachkommastelle runden.
4. Neue Produkte von Etiketten unter `produkte` speichern, damit sie wiederverwendet werden können.
5. Einträge an `eintraege` anhängen. Ohne Datumsangabe gilt der heutige Tag (Europe/Vienna).
   „Gestern“ usw. entsprechend umrechnen.
6. Verschlüsseln: `KT_PASS='<passwort>' python3 tools/crypt.py encrypt` (validiert das JSON).
   Prüfen, dass `git status` nur `data.enc.json` als geändert zeigt, dann committen
   (`Daten aktualisiert`) und pushen.
7. Jubal kurz zurückmelden: was eingetragen wurde und der Tagesstand (kcal / Protein / Carbs / Fett,
   kcal gegen Ziel).

## Datenformat (entschlüsselte `data.json`)
```json
{
  "ziele": { "kcal": 3000, "protein": null, "carbs": null, "fett": null },
  "produkte": {
    "haferflocken-ja-natuerlich": {
      "name": "Haferflocken zart", "marke": "Ja! Natürlich",
      "basis": "100 g", "kcal": 372, "protein": 13.5, "carbs": 58.7, "fett": 7.0,
      "portion": "40 g"
    }
  },
  "eintraege": [
    {
      "id": "2026-10-19-001", "datum": "2026-10-19", "zeit": "08:30",
      "name": "Haferflocken zart", "menge": 100, "einheit": "g",
      "kcal": 372, "protein": 13.5, "carbs": 58.7, "fett": 7.0,
      "produkt": "haferflocken-ja-natuerlich", "notiz": ""
    }
  ]
}
```
- `id`: `<datum>-<laufende Nummer, 3-stellig>`, eindeutig.
- Keine Mahlzeiten-Kategorien (Frühstück/Mittag/Abend): Jubal isst, wann es passt. Die App zeigt eine
  Liste pro Tag, sortiert nach `zeit`. Kein Feld `mahlzeit` anlegen.
- `zeit` (HH:MM): die genannte Uhrzeit, sonst die Uhrzeit seiner Nachricht (Europe/Vienna).
- `produkt`, `notiz` sind optional. `einheit` ist normalerweise `g`, sonst `ml` oder `Stk`.
- `kcal`, `protein`, `carbs`, `fett` sind die **absoluten** Werte für die gegessene Menge.
- Produkt-IDs: Kleinbuchstaben mit Bindestrichen, ä→ae, ö→oe, ü→ue, ß→ss.
- Korrekturen: Den betroffenen Eintrag ändern oder löschen, keinen Gegeneintrag anlegen.
- `ziele` nur ändern, wenn Jubal neue Ziele nennt.
