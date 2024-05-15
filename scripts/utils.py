"""Module des fonctions utilitaires"""

import calendar

def months_Fr2En(mois):
    """Convertit le mois du français à anglais."""

    mois_francais = [
        'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ]

    #liste contenant les mois en anglais
    mois_anglais = list(calendar.month_name)[1:]
    equivalence_mois = dict(zip(mois_francais, mois_anglais))

    return equivalence_mois[mois.lower()]


def encode(string: str) ->str:
    """Encodage d'une chaine de caractère en ISO-8859-1 ('latin-1) puis decodage en utf-8"""
    return string.encode('latin-1').decode('utf-8')
