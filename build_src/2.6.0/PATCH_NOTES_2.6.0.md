# Void - Alpha 2.6.0

## Highlights

- Letzthafen wurde atmosphärisch stark erweitert: Haus der Listen, Gezeitensteg, Namenstein, Klippenweg und Leuchtfeuer besitzen deutlich mehr Ortsidentität und Alltagsszenen.
- Die Quest **Ein Name fehlt** rund um Marek Voss wurde überarbeitet. Erinnerungslücken, erhaltene Gewohnheiten, Sera, Nela und Elian greifen nun stärker ineinander.
- Mareks ehemaliges Dachzimmer, die Rückkehrkerben und Wegmünzen erzählen seine Vergangenheit stärker über Gegenstände und Spuren statt über reine Erklärungstexte.
- Mareks Questabschluss wurde erweitert: Sein neues Notizbuch wird zu einem bewussten Anker für die eigene Identität.
- **Das stumme Wiegenlied** wurde als offene Ermittlungsquest ausgebaut. Hinweise können in Letzthafen in unterschiedlicher Reihenfolge gesammelt werden.
- Edda Rehn, Lina, der Namenstein, Sera und das Haus der Listen wurden stärker miteinander verbunden; der Truhenfund und das Liedblatt erhielten einen neuen Abschluss.
- **Der Schmied des Weges** führt nun organischer vom eigenen Bücherregal über Bjorn zum Pfad des Vergessens und ins verlassene Dorf.
- Der **Pfad des Vergessens** besitzt eine vollständige 12-Schritte-Atmosphäre mit alter Straßenstruktur, Grenzsteinen, Mauern, Gärten und dem Übergang in ein aufgegebenes Dorf.
- Das verlassene Dorf, Wohnhaus, Brunnen und die alte Schmiede wurden überarbeitet.
- Das Schmiederätsel wurde räumlich nachvollziehbarer gestaltet: Esse, Werkbank und Abschreckbecken bilden die Symbolfolge.
- Bjorns Reaktion auf den alten Schmiedehammer wurde erweitert. Das unbekannte Zeichen am Hammer wird zu einer offenen Spur und kann mit dem versiegelten Register verknüpft werden.
- Der Waldwächter wurde vollständig als **Schwellenwächter** neu inszeniert: Vorzeichen, Waldlichtung, Warnung, Kampfabschluss und Nachhall wurden überarbeitet.
- Die alte Freischaltung über vier besiegte Gegner wurde entfernt. Der Waldwächter erscheint nun erzählerisch nach **Das stumme Wiegenlied** und **Der Schmied des Weges**.
- Ein frühes Vorzeichen auf dem Königsring kündigt die spätere Waldwächter-Begegnung bereits vorher an.
- Der Sieg über den Waldwächter erweckt das **Übersinnliche** jetzt auch erzählerisch und nicht nur als Systemwert.
- Erste Nachwirkungen des Erwachens wurden ergänzt: neue Wahrnehmungsmomente in Eichenruh, Tomas-Reaktion und sichtbarer Status **Übersinnliches (erwacht)**.
- **Sensibilität** erhält ihre erste echte Anwendung am alten Wegstein.

## UI, Logik & Konsistenz

- Zahlreiche Dialoge und Ortsbeschreibungen wurden von erklärendem Text auf beobachtbare Handlungen und Umgebungsdetails umgestellt.
- Questbezogene `[!]`-Hinweise wurden an Letzthafen, Eichenruh, Büchern, Schmiede und Reisewegen gezielter eingesetzt.
- Wiederbesuche bleiben kürzer als Erstbesuche.
- Rückwege und Reiseübergänge wurden überarbeitet, damit verschiedene Straßen und Waldwege eine eigene Identität besitzen.
- DEV-Ausgaben am Dorfbrunnen erscheinen nur noch im Entwicklungsmodus.
- Ein doppelter Hammerfund-Altblock wurde vor dem Release entfernt.
- Der Hammer des Weges wird beim Questabschluss gegen doppelte Einträge im Waffeninventar abgesichert.

## Technik

- DEV-Modus und alle DEV-Testflags sind im Release deaktiviert.
- Save-Version bleibt bei **2**; Save-Version **1** wird weiterhin migriert.
- Neue Zustände wurden so ergänzt, dass bestehende Saves über sichere Standardwerte weiterlaufen können.
- Release-QA: **45/45 automatisierte Prüfungen erfolgreich**, darunter Save/Load, Migration, Questzustände, Attributfortschritt und 24 Kampf-Smoke-Tests.

## Hinweis

Für den Attribut- und Übersinnlich-Verlauf ist ein neuer Spielstand weiterhin die sauberste Erfahrung. Bestehende kompatible Spielstände bleiben grundsätzlich ladbar.
