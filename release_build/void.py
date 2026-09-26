import random
import time
import json
import os
import sys
from kampfsystem import kampf_starten as kampfsystem_kampf_starten

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
        "heilung": 28,
        "status_effekte": [
            {
                "id": "geschaerfte_sinne",
                "dauer": 4,
                "einheit": "schritte"
            }
        ]
    },

    "gemuesesuppe": {
        "name": "Einfache Gemüsesuppe",
        "typ": "Mahlzeit",
        "beschreibung": (
            "Eine warme Suppe aus Karotten und Kräutern. "
            "Nichts Besonderes, aber kräftigend."
        ),
        "heilung": 30,
        "status_effekte": [
            {
                "id": "kraeftigend",
                "dauer": 3,
                "einheit": "runden"
            }
        ]
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

STATUS_EFFEKTE = {
    "geschaerfte_sinne": {
        "name": "Geschärfte Sinne",
        "art": "buff",
        "beschreibung": (
            "Deine Wahrnehmung ist vorübergehend erhöht."
        ),
        "design": "positiv",
        "standard_dauer": 4,
        "standard_einheit": "schritte",
        "stapelbar": False,
        "modifikatoren": {
            "wahrnehmung": 2
        }
    },

    "kurze_rast": {
        "name": "Kurze Rast",
        "art": "buff",
        "beschreibung": (
            "Ein paar ruhige Minuten und etwas Warmes "
            "haben dir gutgetan."
        ),
        "design": "positiv",
        "standard_dauer": 2,
        "standard_einheit": "kaempfe",
        "stapelbar": False,
        "modifikatoren": {
            "kampf_wahrnehmung": 1
        }
    },


    "kraeftigend": {
        "name": "Kräftigend",
        "art": "buff",
        "beschreibung": (
            "Du fühlst dich für kurze Zeit kräftiger."
        ),
        "design": "positiv",
        "standard_dauer": 3,
        "standard_einheit": "runden",
        "stapelbar": False,
        "modifikatoren": {
            "schaden_bonus": 2
        }
    },

    "benommen": {
        "name": "Benommen",
        "art": "debuff",
        "beschreibung": (
            "Deine Sinne reagieren langsamer als gewöhnlich."
        ),
        "design": "warnung",
        "standard_dauer": 2,
        "standard_einheit": "runden",
        "stapelbar": False,
        "modifikatoren": {
            "wahrnehmung": -2
        }
    },

    "bluten": {
        "name": "Bluten",
        "art": "zustand",
        "beschreibung": (
            "Eine offene Verletzung verursacht fortlaufend Schaden."
        ),
        "design": "gefahr",
        "standard_dauer": 3,
        "standard_einheit": "runden",
        "stapelbar": True,
        "max_stapel": 3,
        "schaden_pro_tick": 2,
        "kampf_einheit": "runden",
        "nach_kampf_einheit": "schritte",
        "schaden_ausserhalb_kampf": True
    },

    "gift": {
        "name": "Vergiftet",
        "art": "zustand",
        "beschreibung": (
            "Gift wirkt in deinem Körper weiter."
        ),
        "design": "gefahr",
        "standard_dauer": 4,
        "standard_einheit": "runden",
        "stapelbar": False,
        "schaden_pro_tick": 3,
        "kampf_einheit": "runden",
        "nach_kampf_einheit": "schritte",
        "schaden_ausserhalb_kampf": True
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

    "pfad_des_vergessens": {
        "name": "Pfad des Vergessens",
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
        "name": "Waldweg zur Köhlerei",
        "gebiet": "Wald",
        "schritte": 12,
        "zufallsereignisse": False,

        "kampfbegegnungen": {
            "aktiv": True,
            "chance": 0.06,
            "garantie_nach": 12,
            "cooldown": 5,
            "erst_nach_prolog": True
        },

        "ereignisse": [
            {
                "id": "koehlerei_bachrinne",
                "schritt": 5,
                "richtung": "Eichenruh>Köhlerei",
                "einmalig": True,
                "titel": "[Bachrinne]",
                "design": "wissen",
                "text": [
                    (
                        "Das Plätschern neben dem Weg wird deutlicher."
def weg_als_gesehen_markieren(weg_id):
    neue_wege = spieler.setdefault(
        "neue_wege",
        []
    )

    if weg_id in neue_wege:
        neue_wege.remove(
            weg_id
        )

def routenkenntnis_bekannt(weg_id):
    return weg_id in spieler.get(
        "routenkenntnis",
        []
    )


def routenkenntnis_lernen(weg_id):
    if weg_id not in WEGE:
        return False

    bekannte_routen = spieler.setdefault(
        "routenkenntnis",
        []
    )

    if weg_id in bekannte_routen:
        return False

    bekannte_routen.append(
        weg_id
    )

    print()
    print("-" * 34)

    design_text(
        "ROUTE VERTRAUT",
        design="wissen",
        art="menue"
    )

    print(
        WEGE[weg_id]["name"]
    )

    print()
    print(
        "Du kennst diese Strecke jetzt gut genug, "
        "um sie auf Wunsch zügig zurückzulegen."
    )

    print("-" * 34)
    print()

    return True

def letzthafen_status():
    daten = spieler.setdefault(
        "letzthafen_status",
        {}
    )

    daten.setdefault(
        "angekommen",
        False
    )

    daten.setdefault(
        "besuchte_bereiche",
        []
    )

    spuren = daten.setdefault(
        "spuren",
        {}
    )

    spuren.setdefault(
        "sera_marek",
        False
    )

    spuren.setdefault(
        "marek_getroffen",
        False
    )

    spuren.setdefault(
        "register_marek",
        False
    )

    spuren.setdefault(
        "marek_adresse_bekannt",
        False
    )

    spuren.setdefault(
        "oros_abschrift",
        False
    )

    spuren.setdefault(
        "marek_zimmer_betreten",
        False
    )

    spuren.setdefault(
        "rueckkehrkerben",
        False
    )

    spuren.setdefault(
        "wegmuenzen_gefunden",
        False
    )

    spuren.setdefault(
        "elian_hinweis",
        False
    )

    spuren.setdefault(
        "elian_getroffen",
        False
    )

    spuren.setdefault(
        "brueder_begegnung",
        False
    )

    spuren.setdefault(
        "marek_notizbuch",
        False
    )

    wiegenlied = daten.setdefault(
        "wiegenlied",
        {}
    )

    wiegenlied.setdefault(
        "melodie_gehoert",
        False
    )

    wiegenlied.setdefault(
        "edda_haus_bekannt",
        False
    )

    wiegenlied.setdefault(
        "edda_getroffen",
        False
    )

    wiegenlied.setdefault(
        "namenstein_lina_gelesen",
        False
    )

    wiegenlied.setdefault(
        "laterne_hinweis",
        False
    )

    wiegenlied.setdefault(
        "truhe_untersucht",
        False
    )

    wiegenlied.setdefault(
        "sera_hinweis",
        False
    )

    wiegenlied.setdefault(
        "namenstein_hinweis",
        False
    )

    wiegenlied.setdefault(
        "register_hinweis",
        False
    )

    wiegenlied.setdefault(
        "truhe_geoeffnet",
        False
    )

    wiegenlied.setdefault(
        "truhe_inhalt_untersucht",
        False
    )

    return daten


def letzthafen_bereich_betreten(bereich_id):
    daten = letzthafen_status()

    besuchte_bereiche = daten[
        "besuchte_bereiche"
    ]

    erstmals = (
        bereich_id not in besuchte_bereiche
    )

    if erstmals:
        besuchte_bereiche.append(
            bereich_id
        )

    return erstmals


def letzthafen_bereich_anzeigen(
    bereich_id,
    titel,
    *zeilen
):
    erstmals = letzthafen_bereich_betreten(
        bereich_id
    )

    ort_titel(
        titel
    )

    text_art = (
        "atmosphaere"
        if erstmals
        else "menue"
    )

    for zeile in zeilen:
        text_ausgeben(
            zeile,
            art=text_art
        )

        print()

    warte_auf_taste(
        "Zurück nach Letzthafen"
    )

def dialog_sera():
    while True:
        ort_titel(
            "Zum letzten Licht"
        )

        dialog_titel(
            "Sera"
        )

        daten = letzthafen_status()
        spuren = daten[
            "spuren"
        ]

        quest_status = spieler.get(
            "quest_ein_name_fehlt"
        )

        marek_name_bekannt = (
            spuren.get(
                "sera_marek",
                False
            )
            or spuren.get(
                "register_marek",
                False
            )
            or besonderer_fund_status(
                "stationsregister"
            ) == "gelesen"
        )

        text_ausgeben(
            "Die Wirtin stellt einen Becher unter "
            "den Tresen und sieht zu dir auf."
        )

        print()

        # -------------------------
        # MAREK WIRD GESUCHT
        # -------------------------

        if quest_status == "marek_spur_suchen":

            if marek_name_bekannt:
                marek_text = (
                    "Ich suche Marek Voss."
                )

            else:
                marek_text = (
                    "Ich suche einen Fuhrmann aus Letzthafen."
                )

            print(
                "1. " + dialog_option(
                    "sera",
                    "marek_voss",
                    marek_text
                )
            )

            print(
                "2. " + dialog_option(
                    "sera",
                    "notizbuecher",
                    "Warum tragen hier so viele Leute Notizbücher?"
                )
            )

            print(
                "3. Gespräch beenden"
            )

            sera_auswahl = eingabe_menu(
                1,
                3,
                sonder_tasten=()
            )

            print()

            # -------------------------
            # MAREK
            # -------------------------

            if sera_auswahl == 1:
                dialog_thema_markieren(
                    "sera",
                    "marek_voss"
                )

                if not spuren.get(
                    "sera_marek",
                    False
                ):

                    if marek_name_bekannt:
                        text_ausgeben(
                            f'[{spieler["name"]}] '
                            "Ich suche Marek Voss."
                        )

                    else:
                        text_ausgeben(
                            f'[{spieler["name"]}] '
                            "Ich suche einen Fuhrmann aus Letzthafen."
                        )

                        print()

                        text_ausgeben(
                            "Du erzählst von Hildas Lieferung, "
                            "dem verlassenen Karren und der Spur "
                            "zurück nach Letzthafen."
                        )

                        print()

                        text_ausgeben(
                            "[Sera] Dann suchst du Marek Voss."
                        )

                    print()

                    text_ausgeben(
                        "[Sera] Marek? Ja. "
                        "Der kommt regelmäßig hier vorbei."
                    )

                    text_ausgeben(
                        "[Sera] Normalerweise sitzt er genau "
                        "da drüben und beschwert sich darüber, "
                        "dass mein Eintopf zu viel Salz hat."
                    )

                    print()

                    text_ausgeben(
                        "Sera deutet auf einen kleinen Tisch "
                        "am Fenster."
                    )

                    print()

                    text_ausgeben(
                        "[Sera] Als er zuletzt hier auftauchte, "
                        "fragte er mich, ob wir uns schon einmal "
                        "begegnet wären."
                    )

                    print()

                    text_ausgeben(
                        "[Sera] Dann legte er genau den Betrag "
                        "für sein übliches Zimmer auf den Tresen."
                    )

                    text_ausgeben(
                        "[Sera] Ohne nach dem Preis zu fragen."
                    )

                    print()

                    text_ausgeben(
                        '[Sera] Ich sagte: '
                        '"Wie immer, oben links."'
                    )

                    print()

                    text_ausgeben(
                        '[Sera] Er sah mich an und fragte nur: '
                        '"Wie immer?"'
                    )

                    print()

                    text_ausgeben(
                        "Für einen Moment schaut Sera zu dem "
                        "leeren Tisch am Fenster."
                    )

                    print()

                    text_ausgeben(
                        "[Sera] Heute Morgen habe ich ihn unten "
                        "am Gezeitensteg gesehen."
                    )

                    text_ausgeben(
                        "[Sera] Er half den Fischern beim Tauwerk, "
                        "als wäre nichts gewesen."
                    )

                    spuren[
                        "sera_marek"
                    ] = True

                    quest_meldung(
                        "update",
                        "Ein Name fehlt",
                        "Sera sah Marek zuletzt am Gezeitensteg."
                    )

                else:
                    text_ausgeben(
                        "[Sera] Wie gesagt: Marek war heute Morgen "
                        "am Gezeitensteg."
                    )

                    print()

                    text_ausgeben(
                        "[Sera] Wenn er nicht mehr dort ist, "
                        "frag die Leute unten am Wasser."
                    )

                warte_auf_taste(
                    "Weiter"
                )

            # -------------------------
            # NOTIZBÜCHER
            # -------------------------

            elif sera_auswahl == 2:
                dialog_thema_markieren(
                    "sera",
                    "notizbuecher"
                )

                text_ausgeben(
                    "[Sera] Die Bücher?"
                )

                print()
                text_ausgeben(
                    "[Sera] Ladungen, Schulden, Gezeiten, "
                    "Bestellungen. In einem Hafen kommt einiges "
                    "zusammen."
                )

                print()
                text_ausgeben(
                    "[Sera] Ein Sturm reicht, und am nächsten "
                    "Morgen behauptet dir jemand, er habe dir "
                    "nie drei Kisten versprochen."
                )

                print()
                text_ausgeben(
                    "[Sera] Also schreibt man auf, was wichtig ist."
                )

                print()
                text_ausgeben(
                    "[Sera] Seit ich denken kann, macht man das "
                    "in Letzthafen so."
                )

                warte_auf_taste(
                    "Weiter"
                )

            elif sera_auswahl == 3:
                return

            continue

        # -------------------------
        # NORMALER DIALOG
        # -------------------------

        wiegenlied = letzthafen_status()[
            "wiegenlied"
        ]

        wiegenlied_aktiv = spieler.get(
            "quest_wiegenlied"
        ) in (
            "lied_rekonstruieren",
            "truhe_geoeffnet",
            "abgeschlossen"
        )

        optionen = [
            (
                "Warum tragen hier so viele Leute Notizbücher?",
                "notizbuecher"
            )
        ]

        if wiegenlied_aktiv:
            optionen.append(
                (
                    "Kennst du Eddas Wiegenlied?",
                    "wiegenlied"
                )
            )

        optionen.append(
            (
                "Gespräch beenden",
                "ende"
            )
        )

        for nummer, (
            text,
            aktion
        ) in enumerate(
            optionen,
            start=1
        ):
            if aktion == "notizbuecher":
                text = dialog_option(
                    "sera",
                    "notizbuecher",
                    text
                )

            elif aktion == "wiegenlied":
                text = dialog_option(
                    "sera",
                    "wiegenlied",
                    text
                )

            print(
                f"{nummer}. {text}"
            )

        sera_auswahl = eingabe_menu(
            1,
            len(optionen),
            sonder_tasten=()
        )

        aktion = optionen[
            sera_auswahl - 1
        ][1]

        print()

        if aktion == "notizbuecher":
            dialog_thema_markieren(
                "sera",
                "notizbuecher"
            )

            text_ausgeben(
                "[Sera] Ladungen, Schulden, Gezeiten, "
                "Bestellungen."
            )

            text_ausgeben(
                "[Sera] In einem Hafen ist es billiger, "
                "etwas aufzuschreiben, als später darüber "
                "zu streiten."
            )

            print()
            text_ausgeben(
                "[Sera] Seit ich denken kann, macht man das "
                "in Letzthafen so."
            )

            warte_auf_taste(
                "Weiter"
            )

        elif aktion == "wiegenlied":
            dialog_thema_markieren(
                "sera",
                "wiegenlied"
            )

            if not wiegenlied.get(
                "sera_hinweis",
                False
            ):
                text_ausgeben(
                    "[Sera] Eddas Lied?"
                )

                print()
                text_ausgeben(
                    "[Sera] Früher hat man es hier häufiger gehört."
                )

                print()
                text_ausgeben(
                    "[Sera] Den Anfang kenne ich noch."
                )

                print()

                text_ausgeben(
                    '[Sera] "Wenn die Laterne brennt, '
                    'zieht die Möwe heim ..."'
                )

                print()
                text_ausgeben(
                    "[Sera] Danach bekomme ich nur noch Wasser "
                    "und Morgenlicht durcheinander."
                )

                wiegenlied[
                    "sera_hinweis"
                ] = True

            else:
                text_ausgeben(
                    "[Sera] Mehr bekomme ich wirklich nicht zusammen."
                )

                print()
                text_ausgeben(
                    '[Sera] "Wenn die Laterne brennt, '
                    'zieht die Möwe heim ..."'
                )

            print()

            design_text(
                "Hinweis: Auf die Laterne folgt die Möwe.",
                design="wissen",
                art="menue"
            )

            warte_auf_taste(
                "Weiter"
            )

        elif aktion == "ende":
            return
        

def letzthafen_letztes_licht():
    while True:
        erstmals = letzthafen_bereich_betreten(
            "letztes_licht"
        )

        ort_titel(
            "Zum letzten Licht"
        )

        # -------------------------
        # ERSTER BESUCH
        # -------------------------

        if erstmals:
            text_ausgeben(
                "Die alte Signallaterne über dem Eingang "
                "schaukelt leise im Wind."
            )

            print()

            text_ausgeben(
                "Das Gebäude wirkt älter als die meisten "
                "Häuser ringsum. Dicke Steinwände tragen "
                "noch die Spuren salziger Jahre."
            )

            print()

            text_ausgeben(
                "Drinnen ist es warm. Eine niedrige Gaststube "
                "öffnet sich zum Meer hin, während eine schmale "
                "Treppe zu den Zimmern im oberen Stock führt."
            )

            print()

            text_ausgeben(
                "Hinter dem Tresen arbeitet eine Frau mit "
                "hochgesteckten dunklen Haaren."
            )

        # -------------------------
        # SPÄTERE BESUCHE
        # -------------------------

        else:
            text_ausgeben(
                "Die Gaststube liegt ruhig hinter den dicken "
                "Steinwänden. Draußen schlägt der Wind gegen "
                "die alte Signallaterne.",
                art="menue"
            )

        menue_trenner()

        print(
            "1. Mit der Wirtin reden"
        )

        print(
            "2. Dich in der Gaststube umsehen"
        )

        print(
            "3. Zurück nach Letzthafen"
        )

        auswahl = eingabe_menu(
            1,
            3,
            sonder_tasten=()
        )

        # -------------------------
        # SERA
        # -------------------------

        if auswahl == 1:
            dialog_sera()

        # -------------------------
        # GASTSTUBE
        # -------------------------

        elif auswahl == 2:
            ort_titel(
                "Zum letzten Licht"
            )

            text_ausgeben(
                "Mehrere schwere Holztische stehen dicht "
                "an den Wänden."
            )

            text_ausgeben(
                "Über einem alten Kamin hängen verblichene "
                "Seekarten, Tauwerk und ein ausgedientes "
                "Signalhorn."
            )

            spuren = letzthafen_status()[
                "spuren"
            ]

            if spuren.get(
                "sera_marek",
                False
            ):
                print()

                text_ausgeben(
                    "Der kleine Tisch am Fenster steht leer."
                )

                text_ausgeben(
                    "Laut Sera sitzt Marek dort sonst regelmäßig."
                )

            warte_auf_taste(
                "Zurück"
            )

        elif auswahl == 3:
            return

def marek_erstbegegnung():
    daten = letzthafen_status()

    spuren = daten[
        "spuren"
    ]

    if spuren.get(
        "marek_getroffen",
        False
    ):
        return

    ort_titel(
        "Gezeitensteg"
    )

    marek_name_bekannt = (
        spuren.get(
            "sera_marek",
            False
        )
        or spuren.get(
            "register_marek",
            False
        )
        or besonderer_fund_status(
            "stationsregister"
        ) == "gelesen"
    )

    if marek_name_bekannt:
        text_ausgeben(
            "Du fragst zwischen Fischern und Trägern "
            "nach Marek Voss."
        )

        print()

        text_ausgeben(
            "[Fischer] Marek? Dort drüben. "
            "Bei den Kisten."
        )

    else:
        text_ausgeben(
            "Du fragst einen der Fischer nach einem "
            "Fuhrmann aus Letzthafen, dessen Karren "
            "auf dem Weg nach Eichenruh zurückblieb."
        )

        print()

        text_ausgeben(
            "[Fischer] Das klingt nach Marek Voss."
        )

        text_ausgeben(
            "[Fischer] Der steht dort drüben bei den Kisten."
        )

    print()

    text_ausgeben(
        "Ein Mann kniet neben einem Stapel Fässer und "
        "zieht ein Tau durch eine einfache Schlaufe."
    )

    text_ausgeben(
        "Als eine der Kisten auf dem nassen Holz verrutscht, "
        "greift er nach dem Seil, zieht einmal daran und "
        "sichert die Ladung, ohne hinzusehen."
    )

    print()

    text_ausgeben(
        "[Fischer] Siehst du? Behauptet, er wisse nicht mehr, "
        "was er gearbeitet hat, aber beim Tauwerk macht ihm "
        "hier kaum einer etwas vor."
    )

    print()

    text_ausgeben(
        f'[{spieler["name"]}] Marek Voss?'
    )

    print()

    text_ausgeben(
        "Der Mann richtet sich langsam auf."
    )

    print()

    text_ausgeben(
        "[Marek] So nennen sie mich hier jedenfalls."
    )

    print()

    text_ausgeben(
        "Du erzählst ihm von Hildas ausgebliebener Lieferung, "
        "dem verlassenen Karren und dem Fahrtenbuch."
    )

    print()

    text_ausgeben(
        "[Marek] Eichenruh sagt mir nichts."
    )

    text_ausgeben(
        "[Marek] Hilda auch nicht."
    )

    print()

    text_ausgeben(
        "[Marek] Aber wenn du mir einen Wagen hinstellst, "
        "kann ich dir sagen, wie du ihn belädst."
    )

    text_ausgeben(
        "[Marek] Ich weiß, wann eine Achse Spiel hat, "
        "wie viel ein Pferd ziehen sollte und welcher "
        "Knoten bei Regen hält."
    )

    print()

    text_ausgeben(
        "[Marek] Ich weiß nur nicht mehr, "
        "wo ich das gelernt habe."
    )

    seite_wechseln(
        "Gezeitensteg",
        "Marek Voss"
    )

    # -------------------------
    # SERA BEREITS BEFRAGT
    # -------------------------

    if spuren.get(
        "sera_marek",
        False
    ):
        print()

        text_ausgeben(
            f'[{spieler["name"]}] Sera sagt, du hättest hier '
            "immer dasselbe Zimmer genommen."
        )

        print()

        text_ausgeben(
            "[Marek] Das hat sie mir auch gesagt."
        )

        text_ausgeben(
            "[Marek] Ich wusste sogar, wie viel "
            "das Zimmer kostet."
        )

        print()

        text_ausgeben(
            "[Marek] Nur erinnern kann ich mich an "
            "keinen einzigen Aufenthalt."
        )

    # -------------------------
    # WEGSTATION BEREITS UNTERSUCHT
    # -------------------------


        ort_titel(
            "Letzthafen"
        )

        ort_nachricht_anzeigen()

        # -------------------------
        # ERSTER BESUCH
        # -------------------------

        if not daten["angekommen"]:

            text_ausgeben(
                "Der Königsring verliert zwischen den ersten "
                "Häusern langsam seine alten Pflastersteine."
            )

            print()

            text_ausgeben(
                "Vor dir klammert sich Letzthafen an hohe, "
                "graue Klippen über dem Meer."
            )

            print()

            text_ausgeben(
                "Kalter Nebel zieht zwischen den Dächern hindurch. "
                "In der Luft liegen Salz, feuchtes Holz und Tang."
            )

            print()

            text_ausgeben(
                "Fast jeder, an dem du vorbeikommst, trägt ein "
                "kleines Buch oder zusammengefaltete Zettel bei sich."
            )

            print()

            text_ausgeben(
                "Niemand scheint dieser Gewohnheit besondere "
                "Beachtung zu schenken."
            )

            daten[
                "angekommen"
            ] = True

            # Hauptquest beim Erreichen von Letzthafen
            if spieler.get(
                "quest_ein_name_fehlt"
            ) == "letzthafen_suchen":

                spieler[
                    "quest_ein_name_fehlt"
                ] = "marek_spur_suchen"

                quest_meldung(
                    "update",
                    "Ein Name fehlt",
                    "Suche in Letzthafen nach Hinweisen "
                    "auf den verschwundenen Händler."
                )

        # -------------------------
        # SPÄTERE BESUCHE
        # -------------------------

        else:
            text_ausgeben(
                "Nebel zieht zwischen den Häusern. "
                "Vom Gezeitensteg dringen Möwenrufe "
                "und das Knarren von Tauwerk herauf.",
                art="menue"
            )

        menue_trenner()

        print("1. Zum letzten Licht")
        print("2. Haus der Listen")
        print("3. Gezeitensteg")
        print("4. Namenstein")
        print("5. Klippenweg und Leuchtfeuer")
        print("6. Zurück nach Eichenruh")

        print()

        print("[S] Status")
        print("[I] Inventar")
        print("[J] Questlog/Erfolge")
        print("[Q] Speichern / Menü")

        auswahl = eingabe_menu(
            1,
            6,
            sonder_tasten=(
                "s",
                "i",
                "j",
                "q"
            )
        )

        # -------------------------
        # ZUM LETZTEN LICHT
        # -------------------------

        if auswahl == 1:
            letzthafen_letztes_licht()

        # -------------------------
        # HAUS DER LISTEN
        # -------------------------

        elif auswahl == 2:
            letzthafen_haus_der_listen()

        # -------------------------
        # GEZEITENSTEG
        # -------------------------

        elif auswahl == 3:
            letzthafen_gezeitensteg()

        # -------------------------
        # NAMENSTEIN
        # -------------------------

        elif auswahl == 4:
            letzthafen_namenstein()

        # -------------------------
        # KLIPPENWEG
        # -------------------------

        elif auswahl == 5:
            letzthafen_klippenweg()

        # -------------------------
        # ZURÜCK NACH EICHENRUH
        # -------------------------

        elif auswahl == 6:
            reise(
                "Eichenruh",
                "Die vertrauten Dächer Eichenruhs "
                "erscheinen wieder vor dir.",
                gebiet_modus=True
            )

            return

        # -------------------------
        # STANDARDMENÜS
        # -------------------------

        elif auswahl == "s":
            status()

        elif auswahl == "i":
            inventar()

        elif auswahl == "j":
            questlog()

        elif auswahl == "q":
            spielmenue()

def wald_erforschung_status():
    daten = spieler.setdefault(
        "wald_erforschung",
        {}
    )

    daten.setdefault(
        "aktueller_knoten",
        None
    )

    daten.setdefault(
        "besuchte_knoten",
        []
    )

    daten.setdefault(
        "abkuerzungen",
        []
    )

    daten.setdefault(
        "funde",
        {}
    )

    return daten


def wald_knoten_name(knoten_id):
    if knoten_id == "hauptweg":
        return "Hauptweg"

    knoten = WALD_SEITENPFAD_KNOTEN.get(
        knoten_id
    )

    if not knoten:
        return knoten_id

    return knoten["name"]


def wald_knoten_betreten(knoten_id):
    if knoten_id not in WALD_SEITENPFAD_KNOTEN:
        return False

    daten = wald_erforschung_status()

    daten[
        "aktueller_knoten"
    ] = knoten_id

    besuchte_knoten = daten[
        "besuchte_knoten"
    ]

    erstmals = (
        knoten_id not in besuchte_knoten
    )

    if erstmals:
        besuchte_knoten.append(
            knoten_id
        )

    return erstmals


def wald_knoten_besucht(knoten_id):
    daten = wald_erforschung_status()

    return knoten_id in daten[
        "besuchte_knoten"
    ]

def wald_gebietskarte_anzeigen():
    daten = wald_erforschung_status()

    aktueller_knoten = daten.get(
        "aktueller_knoten"
    )

    besuchte_knoten = set(
        daten.get(
            "besuchte_knoten",
            []
        )
    )

    # -------------------------
    # SICHTBARKEIT
    # -------------------------

    def knoten_sichtbar(knoten_id):
        if knoten_id in besuchte_knoten:
            return True

        for besucht_id in besuchte_knoten:
            if knoten_id in wald_verbindungen(
                besucht_id
            ):
                return True

        return False

    # -------------------------
    # KARTENFELD
    # -------------------------

    def feld(knoten_id):
        if not knoten_sichtbar(
            knoten_id
        ):
            return None

        if knoten_id not in besuchte_knoten:
            return "[?]"

        name = WALD_SEITENPFAD_KARTENNAMEN[
            knoten_id
        ]

        if knoten_id == aktueller_knoten:
            return f">{name}<"

        return f"[{name}]"

    # -------------------------
    # ZEICHENBEREICH
    # -------------------------

    breite = 60
    hoehe = 13

    karte = [
        [" "] * breite
        for _ in range(hoehe)
    ]

    # -------------------------
    # VERBINDUNGSLINIEN
    # -------------------------

    def mittelpunkt(knoten_id):
        text = feld(
            knoten_id
        )

        if text is None:
            return None

        zeile, spalte = (
            WALD_SEITENPFAD_KARTENPOSITIONEN[
                knoten_id
            ]
        )

        return (
            zeile,
            spalte + len(text) // 2
        )

    def linie_setzen(
        zeile,
        spalte,
        zeichen
    ):
        if not (
            0 <= zeile < hoehe
            and 0 <= spalte < breite
        ):
            return

        if karte[zeile][spalte] == " ":
            karte[zeile][spalte] = zeichen

    def verbindung_zeichnen(
        start_id,
        ziel_id
    ):
        start = mittelpunkt(
            start_id
        )

        ziel = mittelpunkt(
            ziel_id
        )

        if (
            start is None
            or ziel is None
        ):
            return

        start_zeile, start_spalte = start
        ziel_zeile, ziel_spalte = ziel

        # Gleiche Höhe
        if start_zeile == ziel_zeile:
            von = min(
                start_spalte,
                ziel_spalte
            )

            bis = max(
                start_spalte,
                ziel_spalte
            )

            for spalte in range(
                von + 1,
                bis
            ):
                linie_setzen(
                    start_zeile,
                    spalte,
                    "─"
                )

            return

        # Gleiche Spalte
        if start_spalte == ziel_spalte:
            von = min(
                start_zeile,
                ziel_zeile
            )

            bis = max(
                start_zeile,
                ziel_zeile
            )

            for zeile in range(
                von + 1,
                bis
            ):
                linie_setzen(
                    zeile,
                    start_spalte,
                    "│"
                )

            return

        # Unterschiedliche Höhe und Spalte:
        # zuerst waagerecht, dann senkrecht.
        schritt = (
            1
            if ziel_spalte > start_spalte
            else -1
        )

        for spalte in range(
            start_spalte + schritt,
            ziel_spalte,
            schritt
        ):
            linie_setzen(
                start_zeile,
                spalte,
                "─"
            )

        schritt = (
            1
            if ziel_zeile > start_zeile
            else -1
        )

        for zeile in range(
            start_zeile + schritt,
            ziel_zeile,
            schritt
        ):
            linie_setzen(
                zeile,
                ziel_spalte,
                "│"
            )

    # Nur Verbindungen anzeigen,
    # die der Spieler bereits erkennen kann.
    gezeichnete_verbindungen = set()

    for start_id in besuchte_knoten:
        for ziel_id in wald_verbindungen(
            start_id
        ):
            if (
                start_id
                not in WALD_SEITENPFAD_KARTENPOSITIONEN
                or ziel_id
                not in WALD_SEITENPFAD_KARTENPOSITIONEN
            ):
                continue

            if not knoten_sichtbar(
                ziel_id
            ):
                continue

            verbindung = frozenset(
                (
                    start_id,
                    ziel_id
                )
            )

            if verbindung in gezeichnete_verbindungen:
                continue

            gezeichnete_verbindungen.add(
                verbindung
            )

            verbindung_zeichnen(
                start_id,
                ziel_id
            )

    for (
        knoten_id,
        position
    ) in WALD_SEITENPFAD_KARTENPOSITIONEN.items():

        text = feld(
            knoten_id
        )

        if text is None:
            continue

        zeile, spalte = position

        for index, zeichen in enumerate(
            text
        ):
            x = spalte + index

            if (
                0 <= zeile < hoehe
                and 0 <= x < breite
            ):
                karte[
                    zeile
                ][x] = zeichen

    # -------------------------
    # KARTE AUSGEBEN
    # -------------------------

    ort_titel(
        "Gebietskarte - Alter Seitenpfad"
    )

    print()
    sichtbare_zeilen = [
        index
        for index, zeile in enumerate(karte)
        if any(
            zeichen != " "
            for zeichen in zeile
        )
    ]

    if sichtbare_zeilen:
        erste_zeile = min(
            sichtbare_zeilen
        )

        letzte_zeile = max(
            sichtbare_zeilen
        )

        sichtbarer_bereich = karte[
            erste_zeile:
            letzte_zeile + 1
        ]

        belegte_spalten = []

        for zeile in sichtbarer_bereich:
            for index, zeichen in enumerate(
                zeile
            ):
                if zeichen != " ":
                    belegte_spalten.append(
                        index
                    )

        if belegte_spalten:
            erste_spalte = min(
                belegte_spalten
            )

            letzte_spalte = max(
                belegte_spalten
            )

            for zeile in sichtbarer_bereich:
                print(
                    "  "
                    + "".join(
                        zeile[
                            erste_spalte:
                            letzte_spalte + 1
                        ]
                    ).rstrip()
                )

    # -------------------------
    # AKTUELLER STANDORT
    # -------------------------

    if aktueller_knoten:
        print()
        print("-" * 34)

        print(
            "Standort: "
            + wald_knoten_name(
                aktueller_knoten
            )
        )

        print()

    print()
    print("-" * 34)
    print()

    print(
        ">XX< = Dein Standort"
    )

    print(
        "[XX] = Erkundeter Bereich"
    )

    print(
        "[?] = Bekannter, noch nicht erkundeter Weg"
    )

    warte_auf_taste(
        "Zurück"
    )

def wald_abkuerzung_offen(abkuerzung_id):
    daten = wald_erforschung_status()

    return abkuerzung_id in daten[
        "abkuerzungen"
    ]


def wald_abkuerzung_freischalten(
    abkuerzung_id
):
    if (
        abkuerzung_id
        not in WALD_SEITENPFAD_ABKUERZUNGEN
    ):
        return False

    daten = wald_erforschung_status()

    abkuerzungen = daten[
        "abkuerzungen"
    ]

    if abkuerzung_id in abkuerzungen:
        return False

    abkuerzungen.append(
        abkuerzung_id
    )

    abkuerzung = (
        WALD_SEITENPFAD_ABKUERZUNGEN[
            abkuerzung_id
        ]
    )

    von_name = wald_knoten_name(
        abkuerzung["von"]
    )

    nach_name = wald_knoten_name(
        abkuerzung["nach"]
    )

    print()
    print("-" * 34)

    design_text(
        "NEUE ABKÜRZUNG ENTDECKT",
        design="wissen",
        art="menue"
    )

    print(
        abkuerzung["name"]
    )

    print(
        f"{von_name} ↔ {nach_name}"
    )

    print("-" * 34)
    print()

    return True


def wald_verbindungen(knoten_id):
    knoten = WALD_SEITENPFAD_KNOTEN.get(
        knoten_id
    )

    if not knoten:
        return []

    verbindungen = list(
        knoten.get(
            "wege",
            []
        )
    )

    for (
        abkuerzung_id,
        abkuerzung
    ) in WALD_SEITENPFAD_ABKUERZUNGEN.items():

        if not wald_abkuerzung_offen(
            abkuerzung_id
        ):
            continue

        von = abkuerzung["von"]
        nach = abkuerzung["nach"]

        if (
            knoten_id == von
            and nach not in verbindungen
        ):
            verbindungen.append(
                nach
            )

        elif (
            knoten_id == nach
            and von not in verbindungen
        ):
            verbindungen.append(
                von
            )

    # Der Wegstein ist beim ersten Durchgang
    # noch nicht als Weg erkennbar.
    if knoten_id == "wegmarken":
        funde = wald_erforschung_status()[
            "funde"
        ]

        if not funde.get(
            "wegmarken_untersucht",
            False
        ):
            if "wegstein" in verbindungen:
                verbindungen.remove(
                    "wegstein"
                )

    if (
        knoten_id == "bachufer"
        and wald_fund_bekannt(
            "bach_geheimweg_entdeckt"
        )
        and "verborgenes_bachufer"
        not in verbindungen
    ):
        verbindungen.append(
            "verborgenes_bachufer"
        )

    return verbindungen


def wald_ist_abkuerzung(
    start_id,
    ziel_id
):
    for (
        abkuerzung_id,
        abkuerzung
    ) in WALD_SEITENPFAD_ABKUERZUNGEN.items():

        if not wald_abkuerzung_offen(
            abkuerzung_id
        ):
            continue

        verbindung = {
            abkuerzung["von"],
            abkuerzung["nach"]
        }

        if {
            start_id,
            ziel_id
        } == verbindung:
            return True

    return False

def item_anzahl(item_id):
    return spieler.get(
        "inventar_items",
        {}
    ).get(
        item_id,
        0
    )


def item_besitzt(item_id, anzahl=1):
    return item_anzahl(item_id) >= anzahl


def item_hinzufuegen(item_id, anzahl=1):
    if item_id not in ITEMS:
        return False

    inventar_items = spieler.setdefault(
        "inventar_items",
        {}
    )

    inventar_items[item_id] = (
        inventar_items.get(item_id, 0)
        + anzahl
    )

    return True


def item_entfernen(item_id, anzahl=1):
    inventar_items = spieler.setdefault(
        "inventar_items",
        {}
    )

    vorhandene_anzahl = inventar_items.get(
        item_id,
        0
    )

    if vorhandene_anzahl < anzahl:
        return False

    neue_anzahl = vorhandene_anzahl - anzahl

    if neue_anzahl <= 0:
        inventar_items.pop(
            item_id,
            None
        )

    else:
        inventar_items[item_id] = neue_anzahl

    return True

def item_benutzen(item_id):
    if item_id not in ITEMS:
        return False

    if not item_besitzt(item_id):
        return False

    item_daten = ITEMS[item_id]

    heilung = item_daten.get(
        "heilung",
        0
    )

    status_eintraege = item_daten.get(
        "status_effekte",
        []
    )

    if not isinstance(
        status_eintraege,
        list
    ):
        status_eintraege = []

    gueltige_status = []

    for effekt in status_eintraege:
        if not isinstance(
            effekt,
            dict
        ):
            continue

        status_id = effekt.get(
            "id"
        )

        if status_id not in STATUS_EFFEKTE:
            continue

        gueltige_status.append(
            effekt
        )

    hat_status = bool(
        gueltige_status
    )

    if heilung <= 0 and not hat_status:
        print()
        print(
            "Diesen Gegenstand kannst du "
            "momentan nicht benutzen."
        )

        warte_auf_taste()
        return False

    if (
        spieler["lebenspunkte"] >= 100
        and not hat_status
    ):
        print()
        print(
            "Du bist bereits vollständig erholt."
        )

        warte_auf_taste()
        return False

    alte_lebenspunkte = spieler[
        "lebenspunkte"
    ]

    if heilung > 0:
        spieler["lebenspunkte"] = min(
            100,
            spieler["lebenspunkte"] + heilung
        )

    geheilt = (
        spieler["lebenspunkte"]
        - alte_lebenspunkte
    )

    item_entfernen(
        item_id,
        1
    )

    print()

    if geheilt > 0:
        design_text(
            (
                f"Du regenerierst "
                f"{geheilt} Lebenspunkte."
            ),
            design="positiv",
            art="menue"
        )

        print(
            f"Lebenspunkte: "
            f"{spieler['lebenspunkte']}/100"
        )

    elif heilung > 0:
        print(
            "Deine Lebenspunkte sind bereits voll."
        )

    for effekt in gueltige_status:
        status_hinzufuegen(
            effekt["id"],
            dauer=effekt.get(
                "dauer"
            ),
            einheit=effekt.get(
                "einheit"
            ),
            stapel=effekt.get(
                "stapel",
                1
            ),
            quelle=item_id
        )

    print()

    print(
        f"{item_daten['name']} verbleibend: "
        f"{item_anzahl(item_id)}"
    )

    warte_auf_taste()

    return True

def speicherdatei_sicher_schreiben(
    speicher_daten,
    slot=None
):
    if slot is None:
        slot = AKTIVER_SPEICHER_SLOT

    if slot is None:
        return (
            False,
            ValueError(
                "Kein aktiver Speicherplatz ausgewählt."
            )
        )

        elif auswahl == "q":
            spielmenue()
            return

        elif auswahl == 1:
            print()

            text_ausgeben(
                "Du setzt dich auf und lässt deinen Blick durch das kleine Zimmer wandern."
            )

            text_ausgeben(
                "Dein Bett steht an der Wand, noch ungemacht vom Schlaf."
            )

            text_ausgeben(
                "In einer Ecke steht eine alte Holztruhe."
            )

            text_ausgeben(
                "Daneben lehnt ein Bücherregal leicht schief an der Wand."
            )

            text_ausgeben(
                "Durch das Fenster fällt warmes Morgenlicht auf den Holzboden."
            )

            print()

            warte_auf_taste()

            spieler["prolog_status"] = "haus_erkundet"
            
            return

    # -------------------------
    # STUFE 2: HAUS ERKUNDET
    # -------------------------

    elif prolog_status == "haus_erkundet":
        menue_trenner()

        print("1. Bücherregal ansehen")
        print("2. Alte Truhe untersuchen")
        print("3. Aus dem Fenster schauen")
        print("4. Haus verlassen")

        print()
        print("[S] Status")
        print("[I] Inventar")
        print("[J] Questlog/Erfolge")
        print("[Q] Speichern / Menü")

        auswahl = eingabe_menu(
            1,
            4,
            sonder_tasten=("s", "i", "j", "q")
        )

        if auswahl == "s":
            status()
            return

        elif auswahl == "i":
            inventar()
            return

        elif auswahl == "j":
            questlog()
            return

        elif auswahl == "q":
            spielmenue()
            return

        # Bücherregal
        elif auswahl == 1:
            
            print()

            text_ausgeben(
                "Du trittst vor das alte Bücherregal."
            )

            text_ausgeben(
                "Zwischen einigen abgegriffenen Büchern stehen kleine Erinnerungsstücke und allerlei Krimskrams."
            )

            text_ausgeben(
                "Einige der Bücher hast du seit Jahren nicht mehr geöffnet."
            )
            warte_auf_taste()
            return

        # Truhe
        elif auswahl == 2:
            print()

            text_ausgeben(
                "Du öffnest die alte Holztruhe."
            )

            text_ausgeben(
                "Darin liegen zusammengefaltete Kleidung, eine alte Decke und einige Dinge, für die du bisher keinen besseren Platz gefunden hast."
            )

            text_ausgeben(
                "Nichts davon scheint heute besonders wichtig zu sein."
            )
            warte_auf_taste()
            return

        # Fenster
        elif auswahl == 3:
            print()

            text_ausgeben(
                "Du trittst ans Fenster und blickst hinaus."
            )

            text_ausgeben(
                "Über einigen Schornsteinen steigt bereits dünner Rauch auf."
            )

            text_ausgeben(
                "Vom Marktplatz dringen Stimmen herüber."
            )

            text_ausgeben(
                "Aus Richtung der Schmiede hörst du regelmäßig Bjorns Hammer."
            )

            text_ausgeben(
                "Eichenruh beginnt einen weiteren gewöhnlichen Tag."
            )
            warte_auf_taste()
            return

        # Erst jetzt darf der Spieler hinaus
        elif auswahl == 4:
            spieler["prolog_status"] = "dorf_freigeschaltet"
            spieler["ort"] = "Eichenruh"

            ort_nachricht_setzen(
                "Du ziehst dich um und öffnest die Tür.",
                "Kühle Morgenluft schlägt dir entgegen.",
                "Vor dir liegt Eichenruh."
            )

            return

def spielerhaus():
    ort_titel("Dein Haus")

    ort_nachricht_anzeigen()

    if spieler.get("prolog_status") in [
        "aufgewacht",
        "haus_erkundet"
    ]:
        prolog_haus()
        return

    menue_trenner()
    print("1. Bücherregal anschauen")
    print("2. Kochen")
    print("3. Inventar öffnen")
    print("4. Lager öffnen")
    print("5. Schlafen")
    print("6. Spiel speichern")
    print("7. Optionen")
    print("8. Speichern & Hauptmenü")
    print("9. Haus verlassen")

    haus_auswahl = eingabe_menu(
        1,
        9,
        sonder_tasten=()
    )

    if haus_auswahl == 1:
        if prolog_laeuft():
            ort_titel("Dein Haus")

            text_ausgeben(
                "Du trittst vor das alte Bücherregal."
            )

            text_ausgeben(
                "Zwischen abgegriffenen Büchern stehen kleine Erinnerungsstücke und allerlei Krimskrams."
            )

            text_ausgeben(
                "Im Moment hast du allerdings wenig Lust, dich in eines der alten Bücher zu vertiefen."
            )

            warte_auf_taste()

        else:
            buecherregal()

    elif haus_auswahl == 2:
        kochen()

    elif haus_auswahl == 4:
        print("Noch nicht verfügbar")
        warte_auf_taste()

    elif haus_auswahl == 3:
        inventar()

    elif haus_auswahl == 5:
        if spieler["lebenspunkte"] < 100:
            print()
            print("Du legst dich in dein Bett und ruhst dich eine Weile aus.")
            print("Du fühlst dich wieder vollständig erholt.")

            spieler["lebenspunkte"] = 100

            print("Deine Lebenspunkte wurden vollständig wiederhergestellt.")
        else:
            print("Du fühlst dich bereits vollständig erholt.")
        warte_auf_taste()

    elif haus_auswahl == 6:
        spiel_speichern(spieler)
        warte_auf_taste()

    elif haus_auswahl == 7:
        optionen()

    elif haus_auswahl == 8:
        if spiel_speichern(spieler):
            print()
            print("Du kehrst zum Hauptmenü zurück.")

            warte_auf_taste("Zum Hauptmenü")

            zum_hauptmenue()
            return

        else:
            warte_auf_taste()

    elif haus_auswahl == 9:
        spieler["ort"] = "Eichenruh"

        ort_nachricht_setzen(
            "Du trittst hinaus.",
            "Eichenruh... ein ruhiges kleines Dorf."
    )

def startwaffe_waehlen():
    ort_titel("Bjorns Schmiede")

    text_ausgeben(
        "Bjorn öffnet eine längliche Holzkiste "
        "neben seiner Werkbank."
    )

    print()
    text_ausgeben(
        "[Bjorn] Nichts Besonderes. "
        "Aber besser als mit bloßen Händen herumzulaufen."
    )

    print()
    print("1. Schweres Handbeil")
    print("   Wuchtig, aber etwas schwerfällig.")
    print()
    print("2. Beschlagener Wanderstab")
    print("   Ausgewogen und gut zum Abstandhalten.")
    print()
    print("3. Langes Jagdmesser")
    print("   Leicht und für schnelle, präzise Bewegungen geeignet.")

    auswahl = eingabe_menu(
        1,
        3,
        sonder_tasten=()
    )

    if auswahl == 1:
        neue_waffe = {
            "name": "Schweres Handbeil",
            "min_schaden": 8,
            "max_schaden": 16,
            "verkaufswert": 5,
            "typ": "Beil",
            "wendigkeit": 1,
            "parade": 1,
            "reichweite": 1
        }

    elif auswahl == 2:
        neue_waffe = {
            "name": "Beschlagener Wanderstab",
            "min_schaden": 10,
            "max_schaden": 14,
            "verkaufswert": 5,
            "typ": "Stab",
            "wendigkeit": 2,
            "parade": 3,
            "reichweite": 3
        }

    else:
        neue_waffe = {
            "name": "Langes Jagdmesser",
            "min_schaden": 11,
            "max_schaden": 13,
            "verkaufswert": 5,
            "typ": "Messer",
            "wendigkeit": 3,
            "parade": 1,
            "reichweite": 1
        }

    spieler["waffe"] = neue_waffe

    print()
    design_text(
        "NEUE WAFFE",
        design="positiv",
        art="ereignis"
    )

    print(neue_waffe["name"])
    print(
        f"Schaden: {neue_waffe['min_schaden']} - "
        f"{neue_waffe['max_schaden']}"
    )

    print()
    print(
        "Du befestigst die Waffe an deinem Gürtel."
    )
    
def waffeninventar():
    aktuelle_waffe = spieler.get("waffe")

    if aktuelle_waffe:
        print(
            f"Ausgerüstet: {aktuelle_waffe['name']} "
            f"({aktuelle_waffe['min_schaden']}-"
            f"{aktuelle_waffe['max_schaden']} Schaden)"
        )
    else:
        print("Ausgerüstet: Keine")

    if len(spieler["waffen_inventar"]) == 0:
        print()
        print("Du hast keine weiteren Waffen.")
        warte_auf_taste()
        return

    for i, waffe in enumerate(spieler["waffen_inventar"]):
        print(
            f"{i + 1}. {waffe['name']} "
            f"({waffe['min_schaden']}-"
            f"{waffe['max_schaden']} Schaden)"
        )

    print(f"{len(spieler['waffen_inventar']) + 1}. Zurück")

    auswahl = eingabe_menu(
        1,
        len(spieler["waffen_inventar"]) + 1,
        sonder_tasten=()
    )

    if auswahl == len(spieler["waffen_inventar"]) + 1:
        return

    neue_waffe = spieler["waffen_inventar"].pop(auswahl - 1)

    alte_waffe = spieler["waffe"]

    spieler["waffe"] = neue_waffe

    if alte_waffe is not None:
        spieler["waffen_inventar"].append(alte_waffe)

    print()
    print(f"Du rüstest {neue_waffe['name']} aus.")

    if alte_waffe is not None:
        print(f"{alte_waffe['name']} wurde ins Inventar gelegt.")
    else:
        print("Du bist jetzt bewaffnet.")

    warte_auf_taste()

def waffe_verkaufen():
    while True:
        ort_titel(
            "Bjorns Schmiede - Waffen verkaufen"
        )

        print(
            f"Gold: {spieler['gold']}"
        )

        print()

        if len(
            spieler["waffen_inventar"]
        ) == 0:
            print(
                "Du hast keine Waffe, "
                "die du verkaufen kannst."
            )

            warte_auf_taste(
                "Zurück"
            )

            return

        for i, waffe in enumerate(
            spieler["waffen_inventar"]
        ):
            if (
                waffe["name"]
                == "Hammer des Weges"
            ):
                print(
                    f"{i + 1}. {waffe['name']} "
                    "- unverkäuflich"
                )

            else:
                print(
                    f"{i + 1}. {waffe['name']} "
                    f"- {waffe['verkaufswert']} Gold"
                )

        zurueck_nummer = (
            len(
                spieler["waffen_inventar"]
            ) + 1
        )

        print()
        print(
            f"{zurueck_nummer}. Zurück"
        )

        auswahl = eingabe_menu(
            1,
            zurueck_nummer,
            sonder_tasten=()
        )

        if auswahl == zurueck_nummer:
            return

        waffe = spieler[
            "waffen_inventar"
        ][
            auswahl - 1
        ]

        if (
            waffe["name"]
            == "Hammer des Weges"
        ):
            design_text(
                "Diese Waffe kannst du nicht verkaufen.",
                design="warnung",
                art="menue"
            )

            warte_auf_taste(
                "Weiter"
            )

            continue

        waffe = spieler[
            "waffen_inventar"
        ].pop(
            auswahl - 1
        )

        spieler["gold"] += (
            waffe["verkaufswert"]
        )

        design_text(
            f"{waffe['name']} verkauft",
            design="positiv",
            art="menue"
        )

        print()
        print(
            f"Du erhältst "
            f"{waffe['verkaufswert']} Gold."
        )

        print(
            f"Gold: {spieler['gold']}"
        )

        warte_auf_taste(
            "Weiter"
        )

def ressourcen_vorkommen_status(vorkommen_id):
    if vorkommen_id not in RESSOURCEN_VORKOMMEN:
        return None

    alle_vorkommen = spieler.setdefault(
        "ressourcen_vorkommen",
        {}
    )

    status = alle_vorkommen.setdefault(
        vorkommen_id,
        {}
    )

    daten = RESSOURCEN_VORKOMMEN[
        vorkommen_id
    ]

    status.setdefault(
        "vorrat",
        daten["maximum"]
    )

    status.setdefault(
        "regeneration",
        0
    )

    return status


def ressourcen_vorkommen_regenerieren(
    vorkommen_id,
    schritte=1
):
    status = ressourcen_vorkommen_status(
        vorkommen_id
    )

    if status is None:
        return 0

    daten = RESSOURCEN_VORKOMMEN[
        vorkommen_id
    ]

    maximum = daten[
        "maximum"
    ]

    if status["vorrat"] >= maximum:
        status["vorrat"] = maximum
        status["regeneration"] = 0
        return 0

    status["regeneration"] += schritte

    regeneriert = 0

    while (
        status["regeneration"]
        >= daten["regeneration_schritte"]
        and status["vorrat"] < maximum
    ):
        status["regeneration"] -= (
            daten["regeneration_schritte"]
        )

        status["vorrat"] += 1
        regeneriert += 1

    if status["vorrat"] >= maximum:
        status["vorrat"] = maximum
        status["regeneration"] = 0

    return regeneriert

def holz_sammeln():
    ort_titel("Wald - Holzsuche")

    vorkommen_id = "wald_holz"

    status = ressourcen_vorkommen_status(
        vorkommen_id
    )

    daten = RESSOURCEN_VORKOMMEN[
        vorkommen_id
    ]

    if status["vorrat"] <= 0:
        print(
            "In diesem Teil des Waldes findest du "
            "kaum noch brauchbares Totholz."
        )

        print()
        print(
            "Der Abschnitt braucht etwas Zeit, "
            "bevor sich wieder genug trockenes Holz "
            "finden lässt."
        )

        warte_auf_taste()
        return

    text_ausgeben(
        "Du verlässt den Weg für einen Moment und suchst "
        "zwischen Wurzeln und trockenem Unterholz."
    )

    text_ausgeben(
        "Du achtest darauf, nur trockenes Holz mitzunehmen, "
        "das sich später gut entzünden lässt."
    )

    gefundene_menge = min(
        random.randint(
            daten["fund_min"],
            daten["fund_max"]
        ),
        status["vorrat"]
    )

    item_hinzufuegen(
        daten["item_id"],
        gefundene_menge
    )

    status["vorrat"] -= (
        gefundene_menge
    )

    print()

    design_text(
        f"{gefundene_menge}x Holz gesammelt",
        design="positiv",
        art="menue"
    )

    print(
        f"Holz insgesamt: "
        f"{item_anzahl('holz')}"
    )

    if status["vorrat"] == 0:
        print()
        print(
            "Viel brauchbares Totholz ist hier "
            "vorerst nicht mehr übrig."
        )

    elif status["vorrat"] == 1:
        print()
        print(
            "In diesem Teil des Waldes wird "
            "brauchbares Totholz langsam knapp."
        )

    warte_auf_taste()

def lagerfeuer():
    ort_titel("Lagerfeuer")

    holz_kosten = 2
    heilung = 25

    print(
        f"Für ein Lagerfeuer brauchst du "
        f"{holz_kosten} Holz."
    )

    print(
        f"Du besitzt: "
        f"{item_anzahl('holz')} Holz"
    )

    print()

    if not item_besitzt(
        "holz",
        holz_kosten
    ):
        print(
            "Du hast nicht genug trockenes Holz."
        )

        warte_auf_taste()
        return

    print("1. Lagerfeuer entzünden")
    print("2. Zurück")

    auswahl = eingabe_menu(
        1,
        2,
        sonder_tasten=()
    )

    if auswahl == 2:
        return

    item_entfernen(
        "holz",
        holz_kosten
    )

    ort_titel("Lagerfeuer")

    text_ausgeben(
        "Du sammelst das trockene Holz zu einer "
        "kleinen Feuerstelle."
    )

    text_ausgeben(
        "Nach einigen Versuchen greifen die Flammen."
    )

    print()

    print(
        f"Verbleibendes Holz: "
        f"{item_anzahl('holz')}"
    )

    warte_auf_taste(
        "Am Feuer Platz nehmen"
    )

    geruht = False

    while True:
        ort_titel("Lagerfeuer")

        print(
            f"Lebenspunkte: "
            f"{spieler['lebenspunkte']}/100"
        )

        print()
        print(
            "Das Feuer brennt ruhig vor dir."
        )

        print()
        print("1. Am Feuer ausruhen")
        print("2. Am Feuer kochen")
        print("3. Feuer verlassen")

        feuer_auswahl = eingabe_menu(
            1,
            3,
            sonder_tasten=()
        )

        if feuer_auswahl == 1:
            if geruht:
                print()
                print(
                    "Du hast dich an diesem Feuer "
                    "bereits ausgeruht."
                )

                warte_auf_taste()
                continue

            if spieler["lebenspunkte"] >= 100:
                print()
                print(
                    "Du bist bereits vollständig erholt."
                )

                warte_auf_taste()
                continue

            alte_lebenspunkte = spieler[
                "lebenspunkte"
            ]

            spieler["lebenspunkte"] = min(
                100,
                spieler["lebenspunkte"] + heilung
            )

            geheilt = (
                spieler["lebenspunkte"]
                - alte_lebenspunkte
            )

            geruht = True

            print()

            text_ausgeben(
                "Du setzt dich in die Wärme und ruhst "
                "dich eine Weile aus."
            )

            print()

            design_text(
                f"Du regenerierst {geheilt} Lebenspunkte.",
                design="positiv",
                art="menue"
            )

            print(
                f"Lebenspunkte: "
                f"{spieler['lebenspunkte']}/100"
            )

            warte_auf_taste()

        elif feuer_auswahl == 2:
            kochen(
                titel="Kochen am Lagerfeuer"
            )

        elif feuer_auswahl == 3:
            return

def gegenstaende_inventar():
    while True:
        ort_titel("Inventar - Gegenstände")

        inventar_items = spieler.get(
            "inventar_items",
            {}
        )

        sichtbare_items = []

        for item_id, anzahl in inventar_items.items():
            if item_id in ITEMS:
                sichtbare_items.append(
                    (item_id, anzahl)
                )

        if not sichtbare_items:
            print(
                "Du trägst momentan keine "
                "Gegenstände bei dir."
            )

            warte_auf_taste()
            return

        print("Wähle einen Gegenstand:")
        print()

        for nummer, (item_id, anzahl) in enumerate(
            sichtbare_items,
            start=1
        ):
            item_daten = ITEMS[item_id]

            if anzahl > 1:
                print(
                    f"{nummer}. "
                    f"{item_daten['name']} x{anzahl}"
                )

            else:
                print(
                    f"{nummer}. "
                    f"{item_daten['name']}"
                )

            print(
                f"   {item_daten['typ']}"
            )

        zurueck_nummer = len(sichtbare_items) + 1

        print()
        print(f"{zurueck_nummer}. Zurück")

        auswahl = eingabe_menu(
            1,
            zurueck_nummer,
            sonder_tasten=()
        )

        if auswahl == zurueck_nummer:
            return

        item_id, anzahl = sichtbare_items[
            auswahl - 1
        ]

        item_daten = ITEMS[item_id]

        ort_titel(item_daten["name"])

        print(
            f"Typ: {item_daten['typ']}"
        )

        print(
            f"Anzahl: {anzahl}"
        )

        print()
        print(
            item_daten["beschreibung"]
        )

        inhalt = item_daten.get(
            "inhalt"
        )

        if inhalt:
            print()

            design_text(
                "Inhalt:",
                design="wissen",
                art="menue"
            )

            print()

            for zeile in inhalt:
                print(
                    zeile
                )

        if (
            item_id == "mareks_routenmappe"
            and routenkenntnis_bekannt(
                "koenigsring"
            )
        ):
            print()

            design_text(
                "Routenkenntnis: Königsring",
                design="wissen",
                art="menue"
            )

            print(
                "Bei Reisen zwischen Eichenruh und Letzthafen "
                "kannst du die vertraute Strecke zügig zurücklegen."
            )

        heilung = item_daten.get(
            "heilung",
            0
        )

        status_eintraege = item_daten.get(
            "status_effekte",
            []
        )

        if not isinstance(
            status_eintraege,
            list
        ):
            status_eintraege = []

        if heilung > 0:
            print()
            print(
                f"Heilung: {heilung} HP"
            )

        for effekt in status_eintraege:
            if not isinstance(
                effekt,
                dict
            ):
                continue

            status_id = effekt.get(
                "id"
            )

            definition = STATUS_EFFEKTE.get(
                status_id
            )

            if not definition:
                continue

            print()

            design_text(
                )
                dialog_thema_markieren(
                    "tomas",
                    "frueh_hier"
                )

                warte_auf_taste("Weiter")

            elif tomas_auswahl == 2:
                text_ausgeben("Tomas lächelt.")

                print()
                text_ausgeben(
                    "[Tomas] Irgendjemand muss schließlich wissen, "
                    "was hier vor sich geht."
                )

                text_ausgeben(
                    "[Tomas] Und die Leute erzählen erstaunlich viel, "
                    "wenn sie glauben das niemand zuhört."
                )
                dialog_thema_markieren(
                    "tomas",
                    "dorf_beobachten"
                )
                warte_auf_taste("Weiter")

            elif tomas_auswahl == 3:
                return

            continue

        # -------------------------
        # HAUPTQUEST: EIN NAME FEHLT
        # -------------------------

        if spieler.get(
            "quest_ein_name_fehlt"
        ) == "tomas_befragen":
            text_ausgeben(
                "Tomas sitzt auf seiner Bank und dreht "
                "seinen Spazierstock langsam zwischen den Händen."
            )

            print()
            print(
                "1. Hildas Händler ist verschwunden."
            )
            print(
                "2. Gespräch beenden"
            )

            tomas_auswahl = eingabe_menu(
                1,
                2,
                sonder_tasten=()
            )

            if tomas_auswahl == 2:
                return

            print()
            text_ausgeben(
                "Du erzählst Tomas vom verlassenen Karren "
                "und davon, dass Hilda sich nicht mehr an "
                "den Händler erinnern kann."
            )

            print()
            text_ausgeben(
                "Tomas' Gesicht verliert sein Lächeln."
            )

            print()
            text_ausgeben(
                "[Tomas] Hildas Händler? Natürlich. Das war..."
            )

            print()

            text_ausgeben(
                "Er verstummt."
            )

            print()
            text_ausgeben(
                "[Tomas] Einen Moment."
            )

            print()
            text_ausgeben(
                "Tomas öffnet die kleine Ledertasche neben der Bank "
                "und zieht mehrere gefaltete Blätter hervor."
            )

            print()
            text_ausgeben(
                "[Tomas] Ich habe die Liefervereinbarung selbst geschrieben."
            )

            text_ausgeben(
                "[Tomas] Wenigstens daran erinnere ich mich."
            )

            print()

            text_ausgeben(
                "Auf dem Blatt stehen Hildas Name, mehrere Waren, "
                "Mengen und ein vereinbarter Preis."
            )

            print()

            text_ausgeben(
                "Ganz unten befindet sich eine hastige Unterschrift."
            )

            print()
            text_ausgeben(
                "[Tomas] Das ist meine Handschrift."
            )

            text_ausgeben(
                "[Tomas] Und ich weiß, dass ich mit diesem Mann "
                "hier gesessen und gesprochen habe."
            )

            print()
            text_ausgeben(
                "Du deutest auf die Unterschrift."
            )

            print()
            text_ausgeben(
                "[Tomas] Ich kann sie lesen."
            )

            text_ausgeben(
                "[Tomas] Aber der Name bedeutet mir nichts."
            )

            print()

            text_ausgeben(
                "Tomas presst zwei Finger an seine Schläfe."
            )

            print()
            text_ausgeben(
                "[Tomas] Verdammt... jetzt fängt auch noch "
                "mein Kopf an zu hämmern."
            )

            if item_besitzt(
                "fahrtenbuch_haendler"
            ):
                print()
                text_ausgeben(
                    "Du zeigst ihm das Fahrtenbuch aus dem Karren."
                )

                print()
                text_ausgeben(
                    "Tomas überfliegt die letzten Einträge."
                )

                print()
                text_ausgeben(
                    "[Tomas] Klippen. Ein Hafen."
                )

                text_ausgeben(
                    "[Tomas] Das reicht mir nicht. Aber dir vielleicht."
                )

            print()
            text_ausgeben(
                "[Tomas] Bei dir zuhause stehen doch alte "
                "Wegverzeichnisse und Karten."
            )

            text_ausgeben(
                "[Tomas] Nimm das Fahrtenbuch mit."
            )

            text_ausgeben(
                "[Tomas] Vergleich die Einträge mit dem, "
                "was du dort findest."
            )

            print()
            text_ausgeben(
                "[Tomas] Und schreib auf, was du herausfindest."
            )

            text_ausgeben(
                "[Tomas] Im Moment traue ich meinem eigenen "
                "Gedächtnis nicht besonders."
            )

            spieler[
                "quest_ein_name_fehlt"
            ] = "fahrtenbuch_untersuchen"

            quest_meldung(
                "update",
                "Ein Name fehlt",
                "Untersuche das Fahrtenbuch an deinem Bücherregal."
            )

            warte_auf_taste(
                "Weiter"
            )

            return

        # -------------------------
        # NACH DEM PROLOG
        # -------------------------

        if nach_prolog_besuch is None:
            tomas_daten = npc_status(
                "tomas"
            )

            tomas_daten["nach_prolog_besuche"] = (
                tomas_daten.get(
                    "nach_prolog_besuche",
                    0
                ) + 1
            )

            nach_prolog_besuch = tomas_daten[
                "nach_prolog_besuche"
            ]

        ereignis_begruessung = False

        if (
            erste_runde
            and spieler.get(
                "quest_ein_name_fehlt"
            ) == "abgeschlossen"
            and not npc_reaktion_gezeigt(
                "tomas",
                "marek_abschluss"
            )
        ):
            text_ausgeben(
                "Tomas merkt sofort, dass du etwas zu erzählen hast."
            )

            print()

            text_ausgeben(
                f'[{spieler["name"]}] '
                "Ich habe Hildas Händler gefunden."
            )

            print()

            text_ausgeben(
                "Du erzählst Tomas von Marek Voss, "
                "Letzthafen und den Aufzeichnungen."
            )

            print()

            text_ausgeben(
                "Tomas hört ungewöhnlich still zu."
            )

            print()

            text_ausgeben(
                "[Tomas] Marek Voss."
            )

            text_ausgeben(
                "[Tomas] Also hatte der Mann einen Namen."
            )

            print()

            text_ausgeben(
                "[Tomas] Und ein Leben, selbst wenn sein eigener "
                "Kopf ihm kaum noch etwas davon sagt."
            )

            print()

            text_ausgeben(
                "Tomas legt beide Hände auf den Spazierstock."
            )

            print()

            text_ausgeben(
                "[Tomas] Gut, dass jemand es aufgeschrieben hat."
            )

            npc_reaktion_markieren(
                "tomas",
                "marek_abschluss"
            )

            warte_auf_taste(
                "Weiter"
            )

            ereignis_begruessung = True

        if (
            erste_runde
            and not ereignis_begruessung
            and besonderer_fund_status(
                "altes_kartenstueck"
            ) == "zugeordnet"
            and spieler.get(
                "wegstation_status",
                {}
            ).get(
                "entdeckt",
                False
            )
            and not npc_reaktion_gezeigt(
                "tomas",
                "wegstation_gefunden"
            )
        ):
            text_ausgeben(
                f'[{spieler["name"]}] '
                "Das Kartenstück hat tatsächlich zu einer "
                "alten Wegstation am Königsring geführt."
            )

            print()

            text_ausgeben(
                "Tomas richtet sich etwas auf."
            )

            print()

            text_ausgeben(
                "[Tomas] Die Wegstation steht also noch."
            )

            print()

            text_ausgeben(
                "[Tomas] Dann ist von den alten Straßen "
                "mehr übrig, als ich gedacht habe."
            )

            print()

            text_ausgeben(
                "Für einen Moment schaut Tomas nachdenklich "
                "über den Marktplatz."
            )

            print()

            text_ausgeben(
                "[Tomas] Vielleicht sollten wir vorsichtiger damit sein, "
                "was wir für längst verschwunden halten."
            )

            npc_reaktion_markieren(
                "tomas",
                "wegstation_gefunden"
            )

            warte_auf_taste(
                "Weiter"
            )

            ereignis_begruessung = True

        if erste_runde and not ereignis_begruessung:
            direkte_besuche = npc_status(
                "tomas"
            ).get(
                "direkte_besuche",
                0
            )

            if spieler["lebenspunkte"] <= 50:
                begruessung = npc_variante_waehlen(
                    "tomas",
                    "letzte_begruessung_verletzt",
                    [
                        (
                            "Tomas' Lächeln verschwindet, "
                            "als er dich genauer ansieht.\n\n"
                            "[Tomas] Du siehst aus, als könntest du "
                            "eine Pause gebrauchen."
                        ),
                        (
                            "Tomas mustert dich über den Griff "
                            "seines Spazierstocks hinweg.\n\n"
                            "[Tomas] Der Wald war wohl weniger "
                            "freundlich als sonst."
                        ),
                        (
                            "Tomas rückt ein Stück auf der Bank zur Seite.\n\n"
                            "[Tomas] Setz dich erstmal. "
                            "Reden kannst du danach immer noch."
                        )
                    ]
                )

                for zeile in begruessung.split("\n"):
                    if zeile:
                        text_ausgeben(
                            zeile
                        )
                    else:
                        print()

            elif direkte_besuche >= 5:
                begruessung = npc_variante_waehlen(
                    "tomas",
                    "letzte_dauerbesuch_begruessung",
                    [
                        (
                            "Tomas schaut dich an und dann auf "
                            "den freien Platz neben sich.\n\n"
                            "[Tomas] Setz dich doch einfach. "
                            "Dann musst du nicht dauernd wiederkommen."
                        ),
                        (
                            "Tomas stützt beide Hände auf seinen Stock.\n\n"
                            "[Tomas] Wenn du noch einmal zurückkommst, "
                            "fange ich an, deine Besuche zu zählen."
                        ),
                        (
                            "Tomas lächelt, noch bevor du etwas sagst.\n\n"
                            "[Tomas] Wieder etwas vergessen?"
                        )
                    ]
                )

                for zeile in begruessung.split("\n"):
                    if zeile:
                        text_ausgeben(
                            zeile
                        )
                    else:
                        print()

            elif nach_prolog_besuch == 1:
                text_ausgeben(
                    "Tomas sitzt auf seiner üblichen Bank "
                    "am Rand des Marktplatzes."
                )

                text_ausgeben(
                    "Neben ihm lehnt sein knorriger Spazierstock."
                )

                print()

                text_ausgeben(
                    "[Tomas] Du bist doch derjenige, "
                    "der ständig durch den Wald streift?"
                )

            elif nach_prolog_besuch == 2:
                text_ausgeben(
                    "Tomas hebt kurz die Hand, als er dich sieht."
                )

                print()

                text_ausgeben(
                    "[Tomas] Wieder da?"
                )

                text_ausgeben(
                    "[Tomas] Setz dich. Was beschäftigt dich?"
                )

            else:
                begruessung = npc_begruessung_waehlen(
                    "tomas",
                    [
                        "[Tomas] Na, was gibt es?",
                        "[Tomas] Setz dich.",
                        "[Tomas] Was möchtest du wissen?",
                        "[Tomas] Wieder unterwegs gewesen?",
                        (
                            "[Tomas] Das Dorf läuft nicht weg. "
                            "Zumindest meistens nicht."
                        )
                    ]
                )

                text_ausgeben(
                    begruessung
                )

        else:
            text_ausgeben(
                "[Tomas] Noch etwas?"
            )

        print()
        optionen = []

        kartenstueck_status = besonderer_fund_status(
            "altes_kartenstueck"
        )

        if "wald_ungewoehnlich" not in themen_dieses_gespraech:
            optionen.append(
                (
                    "wald_ungewoehnlich",
                    "Was ist daran so ungewöhnlich?"
                )
            )

        if "wald_kennen" not in themen_dieses_gespraech:
            optionen.append(
                (
                    "wald_kennen",
                    "Kennst du den Wald gut?"
                )
            )

        if "eichenruh_geschichte" not in themen_dieses_gespraech:
            optionen.append(
                (
                    "eichenruh_geschichte",
                    "Gibt es etwas Interessantes über Eichenruh zu erzählen?"
                )
            )

        if (
            "kartenstueck" not in themen_dieses_gespraech
            and kartenstueck_status in (
                "erhalten",
                "zugeordnet"
            )
        ):
            if kartenstueck_status == "zugeordnet":
                kartenstueck_text = (
                    "Das Kartenstück gehört zum Königsring."
                )
            else:
                kartenstueck_text = (
                    "Wegen des alten Kartenstücks ..."
                )

            optionen.append(
                (
                    "kartenstueck",
                    kartenstueck_text
                )
            )

        wegmarke_zeigen = (
            item_besitzt(
                "alte_wegmarke"
            )
            and not wald_fund_bekannt(
                "alte_wegmarke_tomas_gezeigt"
            )
        )

        if wegmarke_zeigen:
            optionen.append(
                (
                    "wegmarke",
                    "Ich habe im Wald etwas gefunden."
                )
            )

        optionen.append(
            (
                "ende",
                "Gespräch beenden"
            )
        )

        for nummer, (aktion_id, text) in enumerate(
            optionen,
            start=1
        ):
            if aktion_id in (
                "wald_ungewoehnlich",
                "wald_kennen",
                "eichenruh_geschichte",
                "kartenstueck"
            ):
                text = dialog_option(
                    "tomas",
                    aktion_id,
                    text
                )

            print(
                f"{nummer}. {text}"
            )

        tomas_auswahl = eingabe_menu(
            1,
            len(optionen),
            sonder_tasten=()
        )

        aktion = optionen[
            tomas_auswahl - 1
        ][0]

        erste_runde = False

        if aktion not in (
            "ende",
            "wegmarke"
        ):
            themen_dieses_gespraech.add(
                aktion
            )

        print()

        if aktion == "wald_ungewoehnlich":
            text_ausgeben(
                f'[{spieler["name"]}] '
                "Was ist daran so ungewöhnlich?"
            )

            print()

            text_ausgeben(
                "Tomas schmunzelt."
            )

            print()
            text_ausgeben(
                "[Tomas] Ungewöhnlich? Nein."
            )

            text_ausgeben(
                "[Tomas] Die meisten meiden den Wald nur, "
                "wenn sie keinen Grund haben hineinzugehen."
            )

            print()
            text_ausgeben(
                "[Tomas] Ob es klug ist, so oft dort herumzustreifen, "
                "ist eine andere Frage."
            )
            dialog_thema_markieren(
                "tomas",
                "wald_ungewoehnlich"
            )
            warte_auf_taste("Weiter")

        elif aktion == "wald_kennen":

            text_ausgeben(
                f'[{spieler["name"]}] '
                "Kennst du den Wald gut?"
            )

            print()

            text_ausgeben(
                "Tomas schaut über die Dächer hinweg "
                "in Richtung der Bäume."
            )

            print()
            text_ausgeben(
                "[Tomas] Gut genug, um zu wissen, "
                "dass sich dort etwas verändert."
            )

            print()
            text_ausgeben(
                "[Tomas] Manche Wege verschwinden."
            )

            text_ausgeben(
                "[Tomas] Andere tauchen plötzlich auf, "
                "wo gestern noch keiner war."
            )

            print()
            text_ausgeben(
                "Er schweigt einen Moment."
            )

            print()
            text_ausgeben(
                "[Tomas] Aber vielleicht werde ich auch einfach alt."
            )
            dialog_thema_markieren(
                "tomas",
                "wald_kennen"
            )
            warte_auf_taste("Weiter")

        elif aktion == "eichenruh_geschichte":
            text_ausgeben(
                f'[{spieler["name"]}] '
                "Gibt es etwas Interessantes über Eichenruh zu erzählen?"
            )

            print()
            text_ausgeben(
                "Tomas lehnt sich auf seinem Stock zurück."
            )

            print()
            text_ausgeben(
                "[Tomas] Eichenruh war nicht immer so groß wie heute."
            )

            text_ausgeben(
                "[Tomas] Früher standen hier kaum mehr als ein Gasthaus, "
                "ein paar Häuser und die Schmiede."
            )

            print()
            text_ausgeben(
                "[Tomas] Die alten Wege im Wald stammen noch aus dieser Zeit."
            )

            text_ausgeben(
                "[Tomas] Die meisten Leute haben längst vergessen, "
                "wohin sie einmal führten."
            )
            dialog_thema_markieren(
                "tomas",
                "eichenruh_geschichte"
            )
            warte_auf_taste("Weiter")

        elif aktion == "kartenstueck":
            if kartenstueck_status == "zugeordnet":
                text_ausgeben(
                    f'[{spieler["name"]}] '
                    "Das Kartenstück gehört zum Königsring."
                )

                print()

                text_ausgeben(
                    "Tomas nickt langsam."
                )

                print()

                text_ausgeben(
                    "[Tomas] Dann stammt es tatsächlich "
                    "von den alten Straßen."
                )

                text_ausgeben(
                    "[Tomas] Gut zu wissen, dass die Linien "
                    "darauf nicht völlig bedeutungslos geworden sind."
                )

            else:
                text_ausgeben(
                    f'[{spieler["name"]}] '
                    "Wegen des alten Kartenstücks ..."
                )

                print()

                text_ausgeben(
                    "Tomas betrachtet dich einen Moment."
                )

                print()

                text_ausgeben(
                    "[Tomas] Mehr als das, was ich dir gesagt habe, "
                    "weiß ich darüber leider auch nicht."
                )

                text_ausgeben(
                    "[Tomas] Vergleich es mit alten Karten "
                    "oder Wegverzeichnissen."
                )

                print()

                text_ausgeben(
                    "[Tomas] Irgendwo muss dieses Stück "
                    "einmal dazugehört haben."
                )

            dialog_thema_markieren(
                "tomas",
                "kartenstueck"
            )

            warte_auf_taste(
                "Weiter"
            )

        elif aktion == "wegmarke":
            text_ausgeben(
                f'[{spieler["name"]}] '
                "Ich habe im Wald etwas gefunden."
            )

            print()

            text_ausgeben(
                "Du legst die kleine Metallscheibe "
                "in Tomas' Hand."
            )

            print()
            text_ausgeben(
                "Tomas reibt mit dem Daumen über "
                "das verwitterte Zeichen."
            )

            print()
            text_ausgeben(
                "[Tomas] Wo hast du das gefunden?"
            )

            print()
            text_ausgeben(
                "Du erzählst ihm von dem stillen "
                "Seitenarm des Bachs."
            )

            print()
            text_ausgeben(
                "[Tomas] Das habe ich lange nicht mehr gesehen."
            )

            text_ausgeben(
                "[Tomas] Solche Marken hingen früher "
                "an den alten Wegen."
            )

            text_ausgeben(
                "[Tomas] Noch bevor die heutigen Pfade "
                "regelmäßig benutzt wurden."
            )

            print()
            text_ausgeben(
                "Tomas steht langsam auf und durchsucht "
                "eine kleine Ledertasche neben der Bank."
            )

            print()
            text_ausgeben(
                "[Tomas] Behalten muss ich sie nicht."
            )

            text_ausgeben(
                "[Tomas] Aber wenn du schon dort draußen "
                "herumstöberst, kannst du hiermit vielleicht "
                "mehr anfangen."
            )

            if item_besitzt(
                "alte_wegmarke"
            ):
                item_entfernen(
                    "alte_wegmarke"
                )

            if not item_besitzt(
                "altes_kartenstueck"
            ):
                item_hinzufuegen(
                    "altes_kartenstueck"
                )

            wald_fund_setzen(
                "alte_wegmarke_tomas_gezeigt"
            )

            wald_fund_setzen(
                "altes_kartenstueck_erhalten"
            )

            besonderen_fund_dokumentieren(
                "alte_wegmarke",
                "erkannt"
            )

            besonderen_fund_dokumentieren(
                "altes_kartenstueck",
                "erhalten"
            )

            print()

            design_text(
                "Alte Wegmarke abgegeben",
                design="wissen",
                art="menue"
            )

            design_text(
                "Altes Kartenstück erhalten",
                design="positiv",
                art="menue"
            )

            print()
            text_ausgeben(
                "Auf dem vergilbten Stück erkennst du "
                "einige alte Linien und Markierungen."
            )

            text_ausgeben(
                "Ohne den Rest der Karte kannst du "
                "sie noch nicht einordnen."
            )

            besonderen_fund_hinweis_anzeigen(
                "altes_kartenstueck"
            )


            warte_auf_taste(
                "Weiter"
            )

        elif aktion == "ende":
            direkte_besuche = npc_status(
                "tomas"
            ).get(
                "direkte_besuche",
                0
            )

            if spieler["lebenspunkte"] <= 50:
                abschied = npc_variante_waehlen(
                    "tomas",
                    "letzter_abschied_verletzt",
                    [
                        (
                            "[Tomas] Und jetzt suchst du dir "
                            "einen ruhigen Platz."
                        ),
                        (
                            "[Tomas] Der Wald läuft dir nicht weg.\n"
                            "[Tomas] Hoffentlich."
                        ),
                        (
                            "[Tomas] Pass auf dich auf.\n"
                            "[Tomas] Alte Geschichten brauche ich genug. "
                            "Du musst nicht gleich eine werden."
                        )
                    ]
                )

            elif direkte_besuche >= 5:
                abschied = npc_variante_waehlen(
                    "tomas",
                    "letzter_abschied_dauerbesuch",
                    [
                        "[Tomas] Bis gleich, nehme ich an.",
                        (
                            "[Tomas] Ich bleibe einfach sitzen.\n"
                            "[Tomas] Spart Zeit, wenn du wiederkommst."
                        ),
                        "[Tomas] Du kennst den Weg zur Bank."
                    ]
                )

            else:
                abschied = npc_variante_waehlen(
                    "tomas",
                    "letzter_abschied_normal",
                    [
                        "[Tomas] Bis später.",
                        "[Tomas] Gute Wege.",
                        "[Tomas] Pass auf dich auf.",
                        "[Tomas] Komm wieder vorbei."
                    ]
                )

            for zeile in abschied.split("\n"):
                if zeile:
                    text_ausgeben(
                        zeile
                    )
                else:
                    print()

            warte_auf_taste(
                "Weiter"
            "alte Pfad zwischen dichtem Farn fort."
        ),

        "bachufer": (
            "Zwischen Wurzeln und dunklen Steinen "
            "fließt ein schmaler Bach.",

            "Weiter unten wird das Wasser flacher. "
            "Am Ufer zieht sich ein schlammiger Streifen "
            "zwischen den Bäumen entlang."
        ),

        "verborgenes_bachufer": (
            "Du zwängst dich zwischen zwei dicken "
            "Wurzeln hindurch.",

            "Dahinter teilt sich der Bach in einen "
            "schmalen Seitenarm. Das Wasser fließt hier "
            "fast lautlos zwischen Moos und Stein."
        ),

        "lagerplatz": (
            "Unter hohen Buchen liegen die Reste "
            "eines alten Lagers.",

            "Ein verrußter Steinkreis, morsche Stoffreste "
            "und niedergetretenes Gras zeigen, dass hier "
            "einmal regelmäßig Menschen gerastet haben."
        ),

        "furt": (
            "Der Bach wird hier breit und flach.",

            "Mehrere Steine ragen aus dem Wasser, "
            "während auf der anderen Seite dichtes "
            "Unterholz beginnt."
        ),

        "schlammweg": (
            "Der Boden wird weich und feucht.",

            "Zwischen den Abdrücken von Tieren erkennst "
            "du stellenweise ältere Spuren, die sich in "
            "verschiedene Richtungen verlieren."
        ),

        "wildspur": (
            "Eine schmale Wildspur windet sich zwischen "
            "jungen Bäumen hindurch.",

            "Abgebrochene Zweige und aufgewühltes Laub "
            "zeigen, dass hier regelmäßig Tiere entlangziehen."
        ),

        "felshang": (
            "Der Waldboden steigt plötzlich steil an.",

            "Zwischen freiliegenden Wurzeln und grauen "
            "Felsen führen mehrere schmale Passagen nach oben."
        ),

        "unterholz": (
            "Farn und niedrige Äste stehen hier so dicht, "
            "dass kaum noch ein richtiger Weg zu erkennen ist.",

            "Erst beim genaueren Hinsehen bemerkst du "
            "mehrere schmale Durchgänge."
        ),

        "quellmulde": (
            "Zwischen den Wurzeln liegt eine kleine, "
            "geschützte Mulde.",

            "Klares Wasser sammelt sich dort in einem "
            "flachen Becken. Dahinter steigt das Gelände "
            "zu steil an, um weiterzugehen."
        ),

        "felsspalte": (
            "Zwei große Felswände rücken immer näher "
            "zusammen.",

            "Nach wenigen Metern endet der Durchgang "
            "vor blankem Stein."
        ),

        "steinstufen": (
            "Unter Moos und Erde erkennst du mehrere "
            "flache Steinstufen.",

            "Sie sind eindeutig von Menschenhand gesetzt "
            "worden und führen tiefer zwischen die Bäume."
        ),

        "wegmarken": (
            "Mehrere niedrige Steine stehen in auffällig "
            "regelmäßigen Abständen.",

            "Verwitterte Kerben auf ihren Oberflächen "
            "scheinen alle in dieselbe Richtung zu weisen."
        ),

        "wegstein": (
            "Zwischen zwei alten Bäumen erhebt sich ein "
            "hoher, halb eingesunkener Stein.",

            "Moos bedeckt seine Oberfläche, doch seine Form "
            "wirkt zu regelmäßig für einen natürlichen Felsen."
        )
    }

    wiederholungen = {
        "eingang":
            "Du erkennst die erste Teilung des alten "
            "Seitenpfades wieder.",

        "bachufer":
            "Das leise Rauschen des Bachs begleitet "
            "dich wieder.",

        "verborgenes_bachufer":
            "Du findest den stillen Seitenarm "
            "des Bachs wieder.",

        "lagerplatz":
            "Du erreichst erneut die Reste des "
            "verlassenen Lagers.",

        "furt":
            "Vor dir liegt wieder die flache Furt.",

        "schlammweg":
            "Der weiche Schlammweg ist dir inzwischen "
            "vertraut.",

        "wildspur":
            "Du erkennst die schmale Wildspur wieder.",

        "felshang":
            "Der felsige Hang erhebt sich erneut vor dir.",

        "unterholz":
            "Du findest den bekannten Durchgang durch "
            "das dichte Unterholz.",

        "quellmulde":
            "Du erreichst wieder die verborgene Quellmulde.",

        "felsspalte":
            "Die enge Felsspalte endet noch immer vor "
            "derselben Felswand.",

        "steinstufen":
            "Die überwachsenen Steinstufen tauchen wieder "
            "zwischen dem Moos auf.",

        "wegmarken":
            "Du erkennst die Reihe alter Wegmarken wieder.",

        "wegstein":
            "Du stehst erneut vor dem alten Wegstein."
    }

    ort_titel(
        f"Wald - {wald_knoten_name(knoten_id)}"
    )

    if erstmals:
        for zeile in texte.get(
            knoten_id,
            ()
        ):
            text_ausgeben(
                zeile,
                art="atmosphaere"
            )

    else:
        text_ausgeben(
            wiederholungen.get(
                knoten_id,
                "Du erkennst diesen Abschnitt "
                "des Waldes wieder."
            ),
            art="menue"
        )


def wald_weg_text(
    start_id,
    ziel_id
):
    texte = {
        "hauptweg":
            "Zum Hauptweg zurückkehren",

        "eingang":
            "Zum Beginn des alten Seitenpfades zurückkehren",

        "bachufer":
            "Dem Geräusch des Wassers folgen",

        "verborgenes_bachufer":
            "Zwischen den Wurzeln hindurchschlüpfen",

        "lagerplatz":
            "Dem alten Pfad zwischen den Bäumen folgen",

        "furt":
            "Zur flachen Furt weitergehen",

        "schlammweg":
            "Am schlammigen Ufer entlanggehen",

        "wildspur":
            "Der Wildspur folgen",

        "felshang":
            "Zum felsigen Hang aufsteigen",

        "unterholz":
            "Ins dichte Unterholz gehen",

        "quellmulde":
            "Der feuchten Senke zwischen den "
            "Wurzeln folgen",

        "felsspalte":
            "Zur schmalen Felsspalte gehen",

        "steinstufen":
            "Den überwachsenen Steinstufen folgen",

        "wegmarken":
            "Den alten Steinmarkierungen folgen",

        "wegstein":
            "Dem alten Weg bis zum hohen Stein folgen"
    }

    text = texte.get(
        ziel_id,
        (
            f"In Richtung "
            f"{wald_knoten_name(ziel_id)} "
            f"weitergehen"
        )
    )

    if wald_ist_abkuerzung(
        start_id,
        ziel_id
    ):
        text += " [Abkürzung]"

    return text

def wald_fund_bekannt(fund_id):
    funde = wald_erforschung_status()[
        "funde"
    ]

    return bool(
        funde.get(
            fund_id,
            False
        )
    )


def wald_fund_setzen(
    fund_id,
    wert=True
):
    funde = wald_erforschung_status()[
        "funde"
    ]

    funde[
        fund_id
    ] = wert


def wald_hinweis_anzeigen(
    titel,
    text=None
):
    print()
    print("-" * 34)

    design_text(
        "NEUER HINWEIS",
        design="wissen",
        art="menue"
    )

    print()
    print(titel)

    if text:
        print()
        print(text)

    print("-" * 34)

def wald_knoten_aktionen(knoten_id):
    aktionen = []

    # -------------------------
    # VERBORGENER SEITENARM
    # -------------------------

    if knoten_id == "verborgenes_bachufer":

        if not wald_fund_bekannt(
            "alte_wegmarke_gefunden"
        ):
            aktionen.append(
                (
                    "bacharm_untersuchen",
                    "Den stillen Seitenarm untersuchen"
                )
            )

    # -------------------------
    # VERLASSENES LAGER
    # -------------------------

    elif knoten_id == "lagerplatz":

        if not wald_fund_bekannt(
            "lager_durchsucht"
        ):
            aktionen.append(
                (
                    "lager_durchsuchen",
                    "Das alte Lager durchsuchen"
                )
            )

        if (
            wald_knoten_besucht(
                "furt"
            )
            and not wald_abkuerzung_offen(
                "lager_furt"
            )
        ):
            aktionen.append(
                (
                    "lager_zaunlinie",
                    "Die alten Holzpfosten verfolgen"
                )
            )

    # -------------------------
    # QUELLMULDE
    # -------------------------

    elif knoten_id == "quellmulde":

        if not wald_fund_bekannt(
            "quellmulde_belag"
        ):
            aktionen.append(
                (
                    "quelle_untersuchen",
                    "Die Quellmulde genauer untersuchen"
                )
            )

    # -------------------------
    # FELSSPALTE
    # -------------------------

    elif knoten_id == "felsspalte":

        if not wald_fund_bekannt(
            "ausgeloeschter_name"
        ):
            aktionen.append(
                (
                    "namen_untersuchen",
                    "Die Felswand untersuchen"
                )
            )

    # -------------------------
    # STEINSTUFEN
    # -------------------------

    elif knoten_id == "steinstufen":

        if not wald_fund_bekannt(
            "steinstufen_untersucht"
        ):
            aktionen.append(
                (
                    "stufen_untersuchen",
                    "Die alten Steinstufen untersuchen"
                )
            )

        elif (
            wald_knoten_besucht(
                "bachufer"
            )
            and not wald_abkuerzung_offen(
                "bach_steinstufen"
            )
        ):
            aktionen.append(
                (
                    "stufen_abstieg",
                    "Den schmalen Abstieg untersuchen"
                )
            )

    # -------------------------
    # WEGMARKEN
    # -------------------------

    elif knoten_id == "wegmarken":

        if not wald_fund_bekannt(
            "wegmarken_untersucht"
        ):
            aktionen.append(
                (
                    "wegmarken_untersuchen",
                    "Die Wegmarken genauer untersuchen"
                )
            )

    # -------------------------
    # ALTER WEGSTEIN
    # -------------------------

    elif knoten_id == "wegstein":

        if not spieler.get(
            "wald_wegstein_untersucht",
            False
        ):
            aktionen.append(
                (
                    "wegstein_zeichen",
                    "Die Einkerbungen untersuchen"
                )
            )

        elif not spieler.get(
            "wald_fragment_gefunden",
            False
        ):
            aktionen.append(
                (
                    "wegstein_sockel",
                    "Den Linien bis zum Sockel folgen"
                )
            )

        if (
            spieler.get(
                "wald_fragment_gefunden",
                False
            )
            and not wald_abkuerzung_offen(
                "wegstein_hauptweg"
            )
        ):
            aktionen.append(
                (
                    "wegstein_rueckweg",
                    "Den alten Steinen hinter dem Wegstein folgen"
                )
            )

    return aktionen


def wald_knoten_aktion_ausfuehren(
    knoten_id,
    aktion_id
):

    # -------------------------
    # VERBORGENER SEITENARM - WEGMARKE
    # -------------------------

    if aktion_id == "bacharm_untersuchen":
        ort_titel(
            "Wald - Verborgener Seitenarm"
        )

        text_ausgeben(
            "Du folgst dem stillen Wasser ein Stück "
            "zwischen den Wurzeln entlang."
        )

        print()

        text_ausgeben(
            "Zwischen zwei dunklen Steinen fällt dir "
            "ein matter Metallrand auf."
        )

        print()

        text_ausgeben(
            "Du löst eine kleine, flache Scheibe aus "
            "Schlamm und Moos."
        )

        print()

        text_ausgeben(
            "Auf einer Seite ist ein fast abgeschliffenes "
            "Symbol eingeritzt."
        )

        if not item_besitzt(
            "alte_wegmarke"
        ):
            item_hinzufuegen(
                "alte_wegmarke"
            )

        wald_fund_setzen(
            "alte_wegmarke_gefunden"
        )

        besonderen_fund_dokumentieren(
            "alte_wegmarke"
        )

        print()
        print("-" * 34)

        design_text(
            "BESONDERER FUND",
            design="wissen",
            art="ereignis"
        )

        print()
        print("Alte Wegmarke")
        print("-" * 34)

        print()

        besonderen_fund_hinweis_anzeigen(
            "alte_wegmarke"
        )

        warte_auf_taste(
            "Weiter"
        )

        return

    # -------------------------
    # LAGER DURCHSUCHEN
    # -------------------------

    if aktion_id == "lager_durchsuchen":
        ort_titel(
            "Wald - Verlassenes Lager"
        )

        text_ausgeben(
            "Du gehst zwischen den Resten "
            "des alten Lagers umher."
        )

        text_ausgeben(
            "Unter einer halb verrotteten Plane "
            "findest du einige trockene Äste."
        )

        menge = random.randint(
            1,
            2
        )

        item_hinzufuegen(
            "holz",
            menge
        )

        wald_fund_setzen(
            "lager_durchsucht"
        )

        print()

        design_text(
            f"{menge}x Holz gefunden",
            design="positiv",
            art="menue"
        )

        print()

        text_ausgeben(
            "Unter einer halb zerfallenen Stoffbahn "
            "entdeckst du außerdem ein Stück Papier."
        )

        print()

        text_ausgeben(
            "Die Schrift ist verblasst, "
            "aber einige Zeilen lassen sich noch lesen."
        )

        print()
        print(
            '"Brot kurz über die Glut halten. '
            'Danach mit frischen Kräutern bestreuen."'
        )

        if not rezept_ist_gelernt(
            "kraeuterbrot"
        ):
            rezept_lernen(
                "kraeuterbrot"
            )

        else:
            print()
            print(
                "Das beschriebene Rezept kennst du bereits."
            )

        print()
        text_ausgeben(
            "Zwischen dem Gras erkennst du außerdem "
            "mehrere alte Holzpfosten."
        )

        text_ausgeben(
            "Sie könnten einmal zu einem Zaun "
            "oder einer Wegbegrenzung gehört haben."
        )

        warte_auf_taste(
            "Weiter"
        )

    # -------------------------
    # LAGER -> FURT ABKÜRZUNG
    # -------------------------

    elif aktion_id == "lager_zaunlinie":
        ort_titel(
            "Wald - Verlassenes Lager"
        )

        text_ausgeben(
            "Du folgst den schiefen Holzpfosten "
            "zwischen den Bäumen."
        )

        text_ausgeben(
            "Einige sind fast vollständig im "
            "Unterholz verschwunden."
        )

        print()

        text_ausgeben(
            "Nach kurzer Zeit erkennst du das "
            "flache Wasser der Furt."
        )

        print()

        text_ausgeben(
            "Offenbar verlief hier früher einmal "
            "eine direkte Verbindung."
        )

        print()

        wald_abkuerzung_freischalten(
            "lager_furt"
        )

        warte_auf_taste(
            "Weiter"
        )

    # -------------------------
    # QUELLMULDE
    # -------------------------

    elif aktion_id == "quelle_untersuchen":
        ort_titel(
            "Wald - Verborgene Quellmulde"
        )

        text_ausgeben(
            "Du kniest dich an das flache "
            "Wasserbecken."
        )

        text_ausgeben(
            "Das Wasser selbst wirkt vollkommen klar."
        )

        print()

        text_ausgeben(
            "Am Rand der Mulde fällt dir jedoch "
            "eine dünne helle Ablagerung auf."
        )

        print()

        text_ausgeben(
            "Sie zieht sich in ungewöhnlich "
            "regelmäßigen Linien über mehrere Steine."
        )

        print()

        text_ausgeben(
            "Du kannst nicht erkennen, ob sie "
            "natürlich entstanden ist."
        )

        wald_fund_setzen(
            "quellmulde_belag"
        )

        print()

        wald_hinweis_anzeigen(
            "Ungewöhnliche Ablagerung",
            (
                "Die regelmäßigen Linien wirken nicht natürlich. "
                "Falls du ähnliche Spuren findest, könnte sich "
                "ein Zusammenhang erkennen lassen."
            )
        )

        warte_auf_taste(
            "Weiter"
        )

    # -------------------------
    # FELSSPALTE
    # -------------------------

    elif aktion_id == "namen_untersuchen":
        ort_titel(
            "Wald - Felsspalte"
        )

        text_ausgeben(
            "Du streichst Moos von der "
            "glatten Felswand."
        )

        print()

        text_ausgeben(
            "Darunter kommen mehrere Namen "
            "zum Vorschein."
        )

        print()

        print(
            "Edda"
        )

        print(
            "Marek"
        )

        print(
            "Silva"
        )

        print(
            "Oren"
        )

        print()

        text_ausgeben(
            "Darunter befindet sich eine fünfte Stelle."
        )

        print()

        text_ausgeben(
            "Dort wurde der Stein so tief bearbeitet, "
            "dass kein Buchstabe mehr zu erkennen ist."
        )

        print()

        text_ausgeben(
            "Jemand hat den Namen nicht einfach "
            "durchgestrichen."
        )

        text_ausgeben(
            "Er wurde vollständig entfernt."
        )

        wald_fund_setzen(
            "ausgeloeschter_name"
        )

        print()

        wald_hinweis_anzeigen(
            "Ausgelöschter Name",
            (
                "Der Name wurde offenbar absichtlich vollständig entfernt. "
                "Vielleicht findest du dieselbe Art von Spuren "
                "noch an einem anderen Ort."
            )
        )

        warte_auf_taste(
            "Weiter"
        )

    # -------------------------
    # STEINSTUFEN
    # -------------------------

    elif aktion_id == "stufen_untersuchen":
        ort_titel(
            "Wald - Überwachsene Steinstufen"
        )

        text_ausgeben(
            "Du entfernst Moos und Erde "
            "von einer der Stufen."
        )

        print()

        text_ausgeben(
            "Im Stein verlaufen mehrere "
            "schmale Einkerbungen."
        )

        text_ausgeben(
            "Die Winkel wirken zu regelmäßig, "
            "um zufällige Schäden zu sein."
        )

        print()

        text_ausgeben(
            "Einige Linien setzen sich sogar "
            "über mehrere Stufen hinweg fort."
        )

        wald_fund_setzen(
            "steinstufen_untersucht"
        )

        print()

        wald_hinweis_anzeigen(
            "Zeichen auf den Steinstufen",
            (
                "Die regelmäßigen Linien wurden offenbar bewusst gesetzt. "
                "Vielleicht gehören sie zu einem größeren System "
                "von Wegzeichen."
            )
        )

        warte_auf_taste(
            "Weiter"
        )

    # -------------------------
    # STEINSTUFEN -> BACH
    # -------------------------

    elif aktion_id == "stufen_abstieg":
        ort_titel(
            "Wald - Überwachsene Steinstufen"
        )

        text_ausgeben(
            "Seitlich der Stufen bemerkst du "
            "eine schmale Lücke zwischen zwei Felsen."
        )

        text_ausgeben(
            "Du zwängst dich hindurch und folgst "
            "dem steilen Abstieg."
        )

        print()

        text_ausgeben(
            "Mit jedem Schritt wird das Geräusch "
            "von Wasser deutlicher."
        )

        print()

        text_ausgeben(
            "Wenig später stehst du oberhalb "
            "des bekannten Bachlaufs."
        )

        print()

        wald_abkuerzung_freischalten(
            "bach_steinstufen"
        )

        warte_auf_taste(
            "Weiter"
        )

    # -------------------------
    # WEGMARKEN
    # -------------------------

    elif aktion_id == "wegmarken_untersuchen":
        ort_titel(
            "Wald - Alte Wegmarken"
        )

        text_ausgeben(
            "Du gehst von Stein zu Stein "
            "und entfernst vorsichtig etwas Moos."
        )

        print()

        text_ausgeben(
            "Auf mehreren Steinen erkennst du "
            "dieselben schmalen Linien wie zuvor "
            "auf den überwachsenen Stufen."
        )

        print()

        text_ausgeben(
            "Die Markierungen scheinen nicht "
            "wahllos verteilt zu sein."
        )

        text_ausgeben(
            "Sie weisen alle tiefer in denselben "
            "Teil des Waldes."
        )

        wald_fund_setzen(
            "wegmarken_untersucht"
        )

        print()

        wald_hinweis_anzeigen(
            "Alte Wegmarken",
            (
                "Die Markierungen gehören offenbar zu einem alten Wegsystem. "
                "Ihre Ausrichtung weist tiefer in den Wald."
            )
        )

        warte_auf_taste(
            "Weiter"
        )

    # -------------------------
    # WEGSTEIN - ZEICHEN
    # -------------------------

    elif aktion_id == "wegstein_zeichen":
        ort_titel(
            "Wald - Alter Wegstein"
        )

        text_ausgeben(
            "Du trittst näher an den halb eingesunkenen "
            "Stein heran."
        )

        text_ausgeben(
            "Mit der Hand entfernst du vorsichtig "
            "Moos und feuchte Erde von seiner Oberfläche."
        )

        print()