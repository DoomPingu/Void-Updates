import random
import time
import json
import os
import sys
from kampfsystem import kampf_starten

ANSI_STILE = {
    "reset": "\033[0m",
    "fett": "\033[1m",
    "kursiv": "\033[3m",

    "rot": "\033[31m",
    "gruen": "\033[32m",
    "gelb": "\033[33m",
    "blau": "\033[94m",
    "lila": "\033[95m",
    "cyan": "\033[96m",
    "schwarz": "\033[90m"
}


def ansi_stile_aktivieren():
    if os.name != "nt":
        return True

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)

        modus = ctypes.c_uint32()

        if not kernel32.GetConsoleMode(handle, ctypes.byref(modus)):
            return False

        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

        return bool(
            kernel32.SetConsoleMode(
                handle,
                modus.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            )
        )

    except Exception:
        return False


ANSI_STILE_AKTIV = ansi_stile_aktivieren()

TEXT_BASIS = {
    "atmosphaere": 0.055,
    "kampf": 0.30,
    "ereignis": 1.4,
    "menue": 0.0
}

TEXT_FAKTOREN = {
    "sofort": 0.0,
    "schnell": 0.70,
    "normal": 1.0,
    "langsam": 1.35
}
TEXT_SKIP_AKTIV = False

DEV_MODUS = False
DEV_TEST_ITEMS = False
DEV_TEST_KOCHEN = False

STANDARD_EINSTELLUNGEN = {
    "textgeschwindigkeit": "normal",
    "menue_eingabe": "enter",
    "bildschirm_leeren": True,
    "spieler_name_farbe": "standard"
}

ITEMS = {
    "bjorns_lieferung": {
        "name": "Bjorns Lieferung",
        "typ": "Questgegenstand",
        "beschreibung": (
            "Ein schwerer Sack mit frisch geschmiedeten "
            "Keilen und Achsnägeln."
        )
    },

    "mareks_routenmappe": {
        "name": "Mareks Routenmappe",
        "typ": "Reiseunterlage",
        "beschreibung": (
            "Eine robuste Ledermappe mit Mareks Notizen zum Königsring. "
            "Entfernungen, Raststellen, Steigungen und alte Wegzeichen "
            "sind sorgfältig vermerkt."
        )
    },

    "lina_wiegenlied_abschrift": {
        "name": "Abschrift von Linas Wiegenlied",
        "typ": "Aufzeichnung",
        "beschreibung": (
            "Eine saubere Abschrift des Liedblatts aus Eddas alter Truhe. "
            "Das Original bleibt bei Edda."
        ),
        "inhalt": [
            "Wenn die Laterne brennt,",
            "zieht die Möwe heim.",
            "Wenn die Welle schweigt,",
            "steigt die Sonne über den Stein."
        ]
    },

    "holz": {
        "name": "Holz",
        "typ": "Ressource",
        "beschreibung": (
            "Trockenes Holz, das sich zum Entzünden "
            "eines Lagerfeuers eignet."
        )
    },

    "apfel": {
        "name": "Apfel",
        "typ": "Nahrung",
        "beschreibung": (
            "Ein frischer Apfel. Einfach, aber nahrhaft."
        ),
        "heilung": 8
    },

    "brot": {
        "name": "Brot",
        "typ": "Nahrung",
        "beschreibung": (
            "Ein Stück kräftiges Bauernbrot aus Eichenruh."
        ),
        "heilung": 12
    },

    "karotte": {
        "name": "Karotte",
        "typ": "Nahrung",
        "beschreibung": (
            "Eine einfache frische Karotte vom Marktplatz."
        ),
        "heilung": 5
    },

    "kuechenkraeuter": {
        "name": "Küchenkräuter",
        "typ": "Zutat",
        "beschreibung": (
            "Ein kleines Bündel aromatischer Kräuter. "
            "Allein wenig sättigend, aber beim Kochen nützlich."
        )
    },


    "geroestetes_brot": {
        "name": "Geröstetes Brot",
        "typ": "Mahlzeit",
        "beschreibung": (
            "Eine warme Scheibe Brot, über dem Feuer "
            "knusprig geröstet."
        ),
        "heilung": 18
    },

    "apfelkompott": {
        "name": "Apfelkompott",
        "typ": "Mahlzeit",
        "beschreibung": (
            "Weich gekochte Äpfel. Einfach, warm "
            "und überraschend sättigend."
        ),
        "heilung": 22
    },

    "kraeuterbrot": {
        "name": "Kräuterbrot",
        "typ": "Mahlzeit",
        "beschreibung": (
            "Geröstetes Brot mit frischen Küchenkräutern. "
            "Einfach, aber deutlich besser als trockenes Brot."
        ),
        "heilung": 28
    },

    "gemuesesuppe": {
        "name": "Einfache Gemüsesuppe",
        "typ": "Mahlzeit",
        "beschreibung": (
            "Eine warme Suppe aus Karotten und Kräutern. "
            "Nichts Besonderes, aber kräftigend."
        ),
        "heilung": 30
    },

    "versiegeltes_register": {
        "name": "Versiegeltes Register",
        "typ": "Besonderer Fund",
        "beschreibung": (
            "Ein ungewöhnlich gut erhaltenes Register aus einer "
            "verborgenen Kammer der alten Wegstation. "
            "Das Siegel auf dem Einband zeigt ein Zeichen, "
            "das du noch nicht einordnen kannst."
        )
    },


    "fahrtenbuch_haendler": {
        "name": "Fahrtenbuch des Händlers",
        "typ": "Besonderer Fund",
        "beschreibung": (
            "Ein abgegriffenes Fahrtenbuch aus dem verlassenen "
            "Handelskarren. Die letzten Einträge werden zunehmend "
            "unruhig und brechen schließlich mitten im Gedanken ab."
        )
    },

    "alte_wegmarke": {
        "name": "Alte Wegmarke",
        "typ": "Besonderer Fund",
        "beschreibung": (
            "Eine kleine, flache Metallscheibe mit einem "
            "fast abgeschliffenen Symbol. Du weißt nicht, "
            "wozu sie einmal gehörte."
        )
    },

    "altes_kartenstueck": {
        "name": "Altes Kartenstück",
        "typ": "Besonderer Fund",
        "beschreibung": (
            "Ein vergilbtes Stück einer alten Karte. "
            "Einige Linien und Markierungen sind noch zu erkennen, "
            "doch dir fehlt der Rest, um sie einzuordnen."
        )
    },

    "unbekanntes_fragment": {
        "name": "Unbekanntes Fragment",
        "typ": "Unbekannt",
        "beschreibung": (
            "Ein dunkles Stück Stein mit ungewöhnlich "
            "regelmäßigen Einkerbungen. "
            "Du kannst dir nicht erklären, wozu es einmal gehörte."
        )
    }
}


MARA_SORTIMENT = {
    "apfel": {
        "preis": 4
    },

    "brot": {
        "preis": 6
    }
}

HILDA_SORTIMENT = {
    "karotte": {
        "preis": 3
    },

    "kuechenkraeuter": {
        "preis": 4
    }
}

REZEPTE = {
    "geroestetes_brot": {
        "name": "Geröstetes Brot",
        "zutaten": {
            "brot": 1
        },
        "ergebnis": "geroestetes_brot",
        "anzahl": 1
    },

    "apfelkompott": {
        "name": "Apfelkompott",
        "zutaten": {
            "apfel": 2
        },
        "ergebnis": "apfelkompott",
        "anzahl": 1
    },

    "kraeuterbrot": {
        "name": "Kräuterbrot",
        "zutaten": {
            "brot": 1,
            "kuechenkraeuter": 1
        },
        "ergebnis": "kraeuterbrot",
        "anzahl": 1
    },

    "gemuesesuppe": {
        "name": "Einfache Gemüsesuppe",
        "zutaten": {
            "karotte": 2,
            "kuechenkraeuter": 1
        },
        "ergebnis": "gemuesesuppe",
        "anzahl": 1
    }
}

REZEPT_SAMMLUNGEN = {
    "eichenruh": {
        "name": "Rezepte von Eichenruh",
        "rezepte": [
            "geroestetes_brot",
            "apfelkompott",
            "kraeuterbrot",
            "gemuesesuppe"
        ]
    }
}

RESSOURCEN_VORKOMMEN = {
    "wald_holz": {
        "item_id": "holz",
        "maximum": 5,
        "fund_min": 1,
        "fund_max": 2,
        "regeneration_schritte": 2
    }
}


ERFOLGE = {
    
    "wo_das_wasser_schweigt": {
        "name": "Wo das Wasser schweigt",
        "kategorie": "entdeckt",
        "verborgen": True
    },

    "immer_wieder_nach_hause": {
        "name": "Immer wieder nach Hause",
        "kategorie": "entdeckt",
        "verborgen": True
    },

    "ein_lied_das_blieb": {
        "name": "Ein Lied, das blieb",
        "kategorie": "entdeckt",
        "verborgen": True
    }
}


RUECKKEHR_HINWEISE = {
    "wegstation_archiv_kartenstueck": {
        "name": "Alte Wegstation",
        "text": (
            "Der Grundriss auf dem alten Kartenstück erinnert dich "
            "an die Mauern der alten Wegstation. Vielleicht lohnt "
            "sich dort ein zweiter Blick."
        )
    }
}

BESONDERE_FUNDE = {
    "unbekanntes_fragment": {
        "name": "Unbekanntes Fragment",
        "status_texte": {
            "gefunden": (
                "Am Sockel des alten Wegsteins "
                "im Wald gefunden"
            )
        },
        "ansatz_texte": {
            "gefunden": (
                "Material und Zeichen sind dir unbekannt. "
                "Vielleicht kann jemand mit Kenntnissen über "
                "alte Schriften oder Artefakte mehr erkennen."
            )
        }
    },

    "fahrtenbuch_haendler": {
        "name": "Fahrtenbuch des Händlers",
        "status_texte": {
            "archiviert": (
                "Im Bücherregal deines Hauses archiviert"
            )
        }
    },

    "strassenkarte_wegstation": {
        "name": "Straßenkarte der Wegstation",
        "status_texte": {
            "gelesen": (
                "Alte Verbindung zwischen "
                "Eichenruh und Letzthafen untersucht"
            )
        }
    },

    "versiegeltes_register": {
        "name": "Versiegeltes Register",
        "status_texte": {
            "geborgen": (
                "Aus der verborgenen Kammer "
                "der Wegstation geborgen"
            )
        }
    },


    "stationsregister": {
        "name": "Register der Wegstation",
        "status_texte": {
            "gelesen": (
                "Altes Reiseverzeichnis "
                "des Königsrings gelesen"
            )
        }
    },

    "alte_wegmarke": {
        "name": "Alte Wegmarke",
        "status_texte": {
            "gefunden": (
                "Am verborgenen Seitenarm "
                "des Bachs gefunden"
            ),
            "erkannt": (
                "Von Tomas als alte "
                "Wegmarkierung erkannt"
            )
        },
        "ansatz_texte": {
            "gefunden": (
                "Vielleicht kennt sich jemand in Eichenruh "
                "mit den alten Wegen und ihren Zeichen aus."
            )
        }
    },

    "altes_kartenstueck": {
        "name": "Altes Kartenstück",
        "status_texte": {
            "erhalten": (
                "Von Tomas für die gefundene "
                "Wegmarke erhalten"
            ),
            "zugeordnet": (
                "Als Abschnitt des alten "
                "Königsrings erkannt"
            )
        },
        "ansatz_texte": {
            "erhalten": (
                "Der Ausschnitt ist unvollständig. "
                "Vielleicht lässt er sich mit alten Karten "
                "oder Wegunterlagen vergleichen."
            )
        }
    },

    "linas_wiegenlied": {
        "name": "Linas Wiegenlied",
        "status_texte": {
            "abgeschrieben": (
                "Aus Edda Rehns altem Liedblatt abgeschrieben"
            )
        }
    },

        "mareks_wegmuenzen": {
        "name": "Mareks Wegmünzen",
        "status_texte": {
            "gefunden": (
                "In Mareks ehemaligem Dachzimmer gefunden"
            )
        }
    }
}

WEGE = {
    "alter_seitenpfad": {
        "name": "Alter Seitenpfad",
        "gebiet": "Wald"
    },

    "ueberwucherter_weg": {
        "name": "Überwucherter Weg",
        "gebiet": "Wald"
    },

    "koenigsring": {
        "name": "Königsring",
        "gebiet": "Alte Straße"
    }
}

WEGSTATION_RAEUME = {
    "vorhof": {
        "name": "Vorhof",
        "wege": [
            "haupthalle"
        ],
        "beschreibung": [
            (
                "Zwischen Gras und herabgefallenen Steinen "
                "ziehen sich alte Radspuren durch den Vorhof."
            ),
            (
                "Mehrere verwitterte Steinpfosten markieren noch "
                "die Stelle, an der früher Wagen gehalten haben müssen."
            )
        ],
        "kurztext": (
            "Der überwucherte Vorhof liegt still vor der Ruine."
        )
    },

    "haupthalle": {
        "name": "Haupthalle",
        "wege": [
            "vorhof",
            "wachraum",
            "schreibstube",
            "keller"
        ],
        "beschreibung": [
            (
                "Die Haupthalle ist breiter, als die Ruine von außen "
                "vermuten lässt. Staub liegt auf den alten Steinplatten."
            ),
            (
                "Links führt eine niedrige Tür in einen Wachraum. "
                "Auf der anderen Seite liegt eine ehemalige Schreibstube."
            ),
            (
                "Am hinteren Ende führt eine steinerne Treppe "
                "in die Dunkelheit hinab."
            )
        ],
        "kurztext": (
            "Von der Haupthalle aus führen mehrere Wege tiefer "
            "in die alte Station."
        )
    },

    "wachraum": {
        "name": "Wachraum",
        "wege": [
            "haupthalle"
        ],
        "beschreibung": [
            (
                "Der kleine Wachraum enthält zwei zerfallene Bänke "
                "und die Reste eines schmalen Waffengestells."
            ),
            (
                "Durch einen Mauerriss fällt ein dünner Streifen "
                "Tageslicht auf den Boden."
            )
        ],
        "kurztext": (
            "Im Wachraum stehen nur noch die Reste der alten Einrichtung."
        )
    },

    "schreibstube": {
        "name": "Schreibstube",
        "wege": [
            "haupthalle"
        ],
        "beschreibung": [
            (
                "Mehrere schmale Tische stehen unter einer dicken "
                "Schicht aus Staub und herabgefallenem Putz."
            ),
            (
                "An den Wänden erkennst du leere Fächer, in denen "
                "früher Bücher, Listen und Reiseunterlagen gelegen haben."
            )
        ],
        "kurztext": (
            "Die staubigen Tische der Schreibstube stehen noch immer "
            "an ihren alten Plätzen."
        )
    },

    "keller": {
        "name": "Keller",
        "wege": [
            "haupthalle",
            "archivkammer"
        ],
        "beschreibung": [
            (
                "Die Luft wird merklich kühler, als du die letzten "
                "Stufen in den Keller hinabsteigst."
            ),
            (
                "Alte Regale lehnen schief an den Wänden. Weiter hinten "
                "führt ein steinerner Durchgang zu einer schweren Tür."
            )
        ],
        "kurztext": (
            "Feuchte Kälte liegt zwischen den alten Kellerregalen."
        )
    },

    "archivkammer": {
        "name": "Archivkammer",
        "wege": [
            "keller"
        ],
        "beschreibung": [
            (
                "Hinter der schweren Tür liegt ein überraschend "
                "trockener Raum."
            ),
            (
                "Steinerne Fächer bedecken die Wände. Einige enthalten "
                "noch zusammengerollte Karten und verschnürte Register."
            )
        ],
        "kurztext": (
            "Die trockene Archivkammer wirkt besser erhalten "
            "als der Rest der Station."
        )
    },

    "versiegelte_kammer": {
        "name": "Versiegelte Kammer",
        "wege": [
            "archivkammer"
        ],
        "verborgen": True,
        "beschreibung": [
            (
                "Hinter der verborgenen Öffnung liegt eine schmale, "
                "fensterlose Kammer."
            )
        ],
        "kurztext": (
            "Die verborgene Kammer liegt still hinter der Archivwand."
        )
    }
}

WEGSTATION_KARTENNAMEN = {
    "vorhof": "Vorhof",
    "haupthalle": "Halle",
    "wachraum": "Wachraum",
    "schreibstube": "Schreibstube",
    "keller": "Keller",
    "archivkammer": "Archiv",
    "versiegelte_kammer": "Geheimraum"
}


WEGSTATION_KARTENPOSITIONEN = {
    "wachraum": (0, 20),

    "vorhof": (2, 0),
    "haupthalle": (2, 20),
    "schreibstube": (2, 36),

    "keller": (4, 20),
    "archivkammer": (6, 20),
    "versiegelte_kammer": (8, 20)
}

WALD_SEITENPFAD_KNOTEN = {
    "eingang": {
        "name": "Alter Seitenpfad",
        "wege": [
            "bachufer",
            "lagerplatz"
        ]
    },

    "bachufer": {
        "name": "Bachlauf",
        "wege": [
            "eingang",
            "furt",
            "schlammweg"
        ]
    },

    "verborgenes_bachufer": {
        "name": "Verborgener Seitenarm",
        "wege": [
            "bachufer"
        ],
        "sackgasse": True
    },

    "lagerplatz": {
        "name": "Verlassenes Lager",
        "wege": [
            "eingang",
            "wildspur",
            "felshang",
            "unterholz"
        ]
    },

    "furt": {
        "name": "Furt",
        "wege": [
            "bachufer",
            "unterholz",
            "wegmarken"
        ]
    },

    "schlammweg": {
        "name": "Schlammweg",
        "wege": [
            "bachufer",
            "wildspur",
            "quellmulde"
        ]
    },

    "wildspur": {
        "name": "Wildspur",
        "wege": [
            "lagerplatz",
            "schlammweg",
            "felsspalte",
            "steinstufen"
        ]
    },

    "felshang": {
        "name": "Felsiger Hang",
        "wege": [
            "lagerplatz",
            "unterholz",
            "steinstufen"
        ]
    },

    "unterholz": {
        "name": "Dichtes Unterholz",
        "wege": [
            "lagerplatz",
            "furt",
            "felshang",
            "steinstufen"
        ]
    },

    "quellmulde": {
        "name": "Verborgene Quellmulde",
        "wege": [
            "schlammweg"
        ],
        "sackgasse": True
    },

    "felsspalte": {
        "name": "Felsspalte",
        "wege": [
            "wildspur"
        ],
        "sackgasse": True
    },

    "steinstufen": {
        "name": "Überwachsene Steinstufen",
        "wege": [
            "wildspur",
            "felshang",
            "unterholz",
            "wegmarken"
        ]
    },

    "wegmarken": {
        "name": "Alte Wegmarken",
        "wege": [
            "furt",
            "steinstufen",
            "wegstein"
        ]
    },

    "wegstein": {
        "name": "Alter Wegstein",
        "wege": [
            "wegmarken"
        ],
        "ziel": True
    }
}

WALD_SEITENPFAD_KARTENNAMEN = {
    "eingang": "Eingang",
    "bachufer": "Bach",
    "verborgenes_bachufer": "Seitenarm",
    "lagerplatz": "Lager",
    "furt": "Furt",
    "schlammweg": "Schlamm",
    "wildspur": "Wildspur",
    "felshang": "Felshang",
    "unterholz": "Unterholz",
    "quellmulde": "Quelle",
    "felsspalte": "Felsspalte",
    "steinstufen": "Stufen",
    "wegmarken": "Wegmarken",
    "wegstein": "Wegstein"
}

WALD_SEITENPFAD_KARTENPOSITIONEN = {
    "quellmulde": (0, 16),
    "felsspalte": (0, 48),

    "schlammweg": (2, 16),
    "wildspur": (2, 36),

    "verborgenes_bachufer": (4, 0),
    "bachufer": (4, 16),
    "eingang": (4, 28),
    "lagerplatz": (4, 40),

    "furt": (6, 16),
    "unterholz": (6, 32),
    "felshang": (6, 48),

    "steinstufen": (8, 40),

    "wegmarken": (10, 24),
    "wegstein": (12, 24)
}

WALD_SEITENPFAD_ABKUERZUNGEN = {
    "lager_furt": {
        "von": "lagerplatz",
        "nach": "furt",
        "name": "Alte Zaunlücke"
    },

    "bach_steinstufen": {
        "von": "bachufer",
        "nach": "steinstufen",
        "name": "Verdeckter Übergang"
    },

    "wegstein_hauptweg": {
        "von": "wegstein",
        "nach": "hauptweg",
        "name": "Alter Rückweg"
    }
}

REISE_STRECKEN = {
    frozenset(("Eichenruh", "Köhlerei")): {
        "gebiet": "Waldrand",
        "schritte": 3,
        "zufallsereignisse": False,

        "schritt_texte": {
            "Eichenruh>Köhlerei": [
                (
                    "Die letzten Häuser Eichenruhs bleiben hinter dir. "
                    "Der Weg führt zwischen kleinen Feldern und "
                    "Weidezäunen hindurch."
                ),
                (
                    "Die Felder werden seltener. "
                    "Birken und junge Eichen säumen den Weg. "
                    "Zwischen den Bäumen liegt bereits ein "
                    "schwacher Geruch nach Rauch."
                ),
                (
                    "Der Rauch wird deutlicher. "
                    "Zwischen den ersten Bäumen erkennst du "
                    "schwarze Erdmeiler."
                )
            ],

            "Köhlerei>Eichenruh": [
                (
                    "Du lässt die rauchenden Erdmeiler hinter dir. "
                    "Der schwere Geruch nach Kohle wird langsam schwächer."
                ),
                (
                    "Der Wald lichtet sich. "
                    "Zwischen den Bäumen tauchen wieder Felder "
                    "und niedrige Weidezäune auf."
                ),
                (
                    "Vor dir erscheinen die ersten Dächer Eichenruhs. "
                    "Aus der Ferne hörst du vertraute Stimmen."
                )
            ]
        }
    },

    frozenset(("Eichenruh", "Letzthafen")): {
        "name": "Königsring",
        "weg_id": "koenigsring",
        "schnellreise": True,
        "gebiet": "Wald",
        "schritte": 7,
        "zufallsereignisse": False,
        "wegstation_schritt": 4,

        "schritt_texte": {
            "Eichenruh>Letzthafen": [
                (
                    "Die letzten Häuser Eichenruhs bleiben hinter dir. "
                    "Unter Gras und Erde sind stellenweise noch die "
                    "breiten Steine einer alten Straße zu erkennen."
                ),
                (
                    "Felder und Weidezäune werden seltener. "
                    "Der Königsring führt zwischen alten Eichen "
                    "weiter nach Osten."
                ),
                (
                    "Der Wald rückt näher an die Straße heran. "
                    "Zwischen Wurzeln und Moos tauchen immer wieder "
                    "verwitterte Randsteine auf."
                ),
                (
                    "Zwischen den Bäumen erkennst du Mauerreste. "
                    "Ein alter Seitenweg führt von der Straße weg."
                ),
                (
                    "Der Königsring steigt langsam an. "
                    "Der Wind zwischen den Bäumen wird kühler."
                ),
                (
                    "Die Baumkronen werden lichter. "
                    "In der Luft liegt ein schwacher Geruch nach "
                    "Salz und feuchtem Stein."
                ),
                (
                    "Vor dir öffnet sich der Wald. "
                    "Jenseits der Straße zeichnen sich im Nebel "
                    "erste Dächer vor hohen Klippen ab."
                )
            ],

            "Letzthafen>Eichenruh": [
                (
                    "Die Dächer Letzthafens verschwinden langsam "
                    "hinter dir im Nebel."
                ),
                (
                    "Der salzige Geruch der Klippen wird schwächer, "
                    "während der Königsring wieder zwischen "
                    "die Bäume führt."
                ),
                (
                    "Die Straße fällt langsam ab. "
                    "Alte Randsteine begleiten deinen Weg."
                ),
                (
                    "Zwischen den Bäumen liegen wieder die "
                    "Mauerreste der alten Wegstation."
                ),
                (
                    "Der Wald wird lichter und die ersten offenen "
                    "Flächen erscheinen zwischen den Bäumen."
                ),
                (
                    "Weidezäune und kleine Felder tauchen "
                    "am Rand der Straße auf."
                ),
                (
                    "Vor dir erscheinen die vertrauten "
                    "Dächer Eichenruhs."
                )
            ]
        }
    },

    frozenset(("Eichenruh", "Wald")): {
        "gebiet": "Waldweg",
        "schritte": 3,
        "zufallsereignisse": False,

        "schritt_texte": {
            "Eichenruh>Wald": [
                (
                    "Du lässt die letzten Häuser Eichenruhs hinter dir. "
                    "Der Weg führt zwischen Feldern und Weidezäunen weiter."
                ),
                (
                    "Die Felder werden seltener. "