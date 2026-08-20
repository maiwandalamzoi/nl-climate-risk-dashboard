"""
Locations sampled from the Climate Impact Atlas (klimaateffectatlas.nl) WMS
service. Nationwide coverage (at least one point per province) plus extra
density in Gelderland / the Arnhem-Nijmegen region, matching Alamzoi
Consultancy's local-market positioning.

Coordinates are city/town centers (WGS84 lon, lat), not exact addresses.
"""

# name, province, lat, lon, featured (True = Gelderland/Arnhem-Nijmegen spotlight)
LOCATIONS = [
    # --- Gelderland / Arnhem-Nijmegen region (featured, extra density) ---
    ("Arnhem",        "Gelderland", 51.9851, 5.8987, True),
    ("Nijmegen",       "Gelderland", 51.8425, 5.8528, True),
    ("Leuth",          "Gelderland", 51.8503, 5.9553, True),
    ("Zevenaar",       "Gelderland", 51.9308, 6.0733, True),
    ("Doetinchem",     "Gelderland", 51.9645, 6.2885, True),
    ("Ede",            "Gelderland", 52.0454, 5.6656, True),
    ("Apeldoorn",      "Gelderland", 52.2112, 5.9699, True),
    ("Wageningen",     "Gelderland", 51.9692, 5.6650, True),
    ("Tiel",           "Gelderland", 51.8878, 5.4267, True),
    ("Harderwijk",     "Gelderland", 52.3417, 5.6203, True),

    # --- Rest of the Netherlands: one major city per remaining province ---
    ("Amsterdam",      "Noord-Holland",  52.3676, 4.9041, False),
    ("Haarlem",        "Noord-Holland",  52.3874, 4.6462, False),
    ("Rotterdam",      "Zuid-Holland",   51.9244, 4.4777, False),
    ("Den Haag",       "Zuid-Holland",   52.0705, 4.3007, False),
    ("Utrecht",        "Utrecht",        52.0907, 5.1214, False),
    ("Amersfoort",     "Utrecht",        52.1561, 5.3878, False),
    ("Eindhoven",      "Noord-Brabant",  51.4416, 5.4697, False),
    ("Tilburg",        "Noord-Brabant",  51.5555, 5.0913, False),
    ("Breda",          "Noord-Brabant",  51.5719, 4.7683, False),
    ("Maastricht",     "Limburg",        50.8514, 5.6910, False),
    ("Venlo",          "Limburg",        51.3704, 6.1724, False),
    ("Groningen",      "Groningen",      53.2194, 6.5665, False),
    ("Leeuwarden",     "Friesland",      53.2012, 5.7999, False),
    ("Assen",          "Drenthe",        52.9925, 6.5641, False),
    ("Zwolle",         "Overijssel",     52.5168, 6.0830, False),
    ("Enschede",       "Overijssel",     52.2215, 6.8937, False),
    ("Lelystad",       "Flevoland",      52.5185, 5.4714, False),
    ("Almere",         "Flevoland",      52.3508, 5.2647, False),
    ("Middelburg",     "Zeeland",        51.4988, 3.6136, False),
    ("Vlissingen",     "Zeeland",        51.4426, 3.5736, False),

    # --- Extra low-lying / flood-relevant spots (below sea level, deltas) ---
    ("Dordrecht",      "Zuid-Holland",   51.8133, 4.6901, False),
    ("Schiedam",       "Zuid-Holland",   51.9165, 4.3988, False),
    ("Zaanstad",       "Noord-Holland",  52.4389, 4.8262, False),
    ("Alkmaar",        "Noord-Holland",  52.6324, 4.7534, False),
]

FEELS_LIKE_YEAR = "2022"
