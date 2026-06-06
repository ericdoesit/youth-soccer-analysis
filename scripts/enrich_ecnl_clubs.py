#!/usr/bin/env python3
"""
Clean up ecnl_clubs.csv:
  - Normalize conference names (strip "ECNL Boys X 2025-26" → "X")
  - Add state column derived from conference + club name hints
  - Fill known websites
Output: data/ecnl_clubs.csv (in place)
"""

import csv
import re
from pathlib import Path

CLUBS_FILE = Path(__file__).parent.parent / "data" / "ecnl_clubs.csv"

# ── Conference name normalizer ────────────────────────────────────────────────
CONF_LONG_RE = re.compile(r'^ECNL Boys (.+?) \d{4}-\d{2}$')

CONF_STATES = {
    "Far West":      ["AZ", "CA", "NV"],
    "Florida":       ["FL"],
    "Heartland":     ["IL", "IN", "KY", "OH", "TN"],
    "Mid-America":   ["AL", "AR", "LA", "MO", "MS", "TN"],
    "Mid-Atlantic":  ["DC", "DE", "MD", "NC", "NJ", "PA", "VA"],
    "Midwest":       ["IL", "IA", "MI", "MN", "MO", "WI"],
    "Mountain":      ["CO", "MT", "NM", "UT", "WY"],
    "New England":   ["CT", "MA", "ME", "NH", "NY", "RI", "VT"],
    "North Atlantic":["CT", "DE", "NJ", "NY", "PA"],
    "Northern Cal":  ["CA"],
    "Northwest":     ["ID", "OR", "WA"],
    "Ohio Valley":   ["IN", "KY", "OH", "WV"],
    "Southeast":     ["AL", "FL", "GA", "NC", "SC", "TN"],
    "Southwest":     ["AZ", "CA", "NV"],
    "Texas":         ["TX"],
}

# ── State corrections (club_id → state) ─────────────────────────────────────
# Override when automated inference from name/conference is wrong
STATE_OVERRIDES = {
    46:   "PA",   # HEX FC Dominion — Quakertown PA, not VA
    106:  "OK",   # Tulsa SC — Tulsa Oklahoma, in TX ECNL conference
    329:  "TX",   # NTH-NASA (NASA TopHat) — North Texas
    628:  "VA",   # Beach FC (VA) — Virginia Beach VA, not CA
    893:  "MN",   # St Croix — Stillwater MN, not WI
    1936: "AZ",   # CCV Stars — Christ's Church of the Valley, AZ
    2133: "OK",   # OK Energy FC — Oklahoma City, in TX ECNL conference
    2235: "TN",   # Lobos Rush — Collierville TN
    2229: "WA",   # 3RSC (Three Rivers) — Pasco WA
    2257: "IN",   # Indiana Elite FC — Crown Point IN
    3407: "GA",   # United Futbol Academy — Georgia
    3476: "WA",   # XF Academy (Crossfire Premier) — Redmond WA
    4012: "NC",   # Highland FC — Asheville NC
    16:   "CA",   # Beach FC (CA) — Manhattan Beach / SoCal
    428:  "NJ",   # STA Soccer — Mount Olive NJ
    1409: "NH",   # East Coast Surf SC — New England (NH/MA)
    3956: "OR",   # Capital FC — Salem OR (Far West conference)
}

# ── Known websites (hardcoded from research) ─────────────────────────────────
KNOWN_WEBSITES = {
    # ── Pre-existing ──────────────────────────────────────────────────────────
    9:    "https://susafc.org",
    10:   "https://albionhurricanes.org",
    13:   "https://sportingcausa.com",
    14:   "https://atlantafire.com",
    16:   "https://beachfc.com",
    18:   "https://alabamafc.org",
    22:   "https://ncfcyouth.com",
    26:   "https://charlottesa.com",
    28:   "https://coloradorush.com",
    29:   "https://www.coloradorapidscentral.com",
    30:   "https://concordefire.com",
    31:   "https://ctfcunited.com",
    35:   "https://dksc.com",
    37:   "https://dallastexans.com",
    39:   "https://legendsfc.com",
    42:   "https://eastmeadowsc.com",
    43:   "https://eclipseselect.com",
    47:   "https://fcdallas.com",
    # ── Extended from training knowledge ─────────────────────────────────────
    52:   "https://starsofma.org",                 # FC Stars (MA)
    56:   "https://gsa-soccer.com",                # GSA (GA)
    57:   "https://lvheat.com",                    # LV Heat Surf
    61:   "https://legendsfc.com",                 # Legends FC (same as 39, different region?)
    62:   "https://lonestarsoccer.com",            # Lonestar Soccer Club Red
    64:   "https://matchfitacademy.com",           # Match Fit Surf
    67:   "https://mnthunder.com",                 # Minnesota Thunder
    69:   "https://mustangsc.com",                 # Mustang SC
    71:   "https://ncfusion.com",                  # NC Fusion
    75:   "https://ohioelite.com",                 # Ohio Elite SA
    79:   "https://pennfusion.com",                # Penn Fusion SA
    81:   "https://realcolorado.com",              # Real Colorado Academy
    82:   "https://lafcsocal.com",                 # LAFC So Cal
    86:   "https://sdscsurfclub.com",              # SDSC Surf
    87:   "https://surfsoccer.com",                # San Diego Surf
    96:   "https://slammersfc.com",                # Slammers FC
    101:  "https://solarsc.com",                   # Solar SC Academy
    107:  "https://utahavalanche.com",             # Utah Avalanche
    112:  "https://washingtonpremierfc.com",       # Washington Premier
    113:  "https://westcoastfc.com",               # West Coast FC
    116:  "https://worldclassfc.com",              # World Class FC
    186:  "https://pateadores.com",                # Pateadores
    300:  "https://rebelssc.com",                  # Rebels SC
    343:  "https://wnyflash.com",                  # WNY Flash
    398:  "https://eastsidefc.org",                # Eastside FC
    417:  "https://richmondunitedfc.com",          # Richmond United
    419:  "https://marylandunitedfc.com",          # Maryland United FC
    431:  "https://fsafc.com",                     # FSA FC (CT)
    494:  "https://balticceltic.com",              # Baltimore Celtic
    525:  "https://arlingtonva.soccer",            # Arlington Soccer
    538:  "https://riverhoundssoccer.com",         # Pittsburgh Riverhounds
    592:  "https://arizonaarsenalyouth.com",       # Arizona Arsenal
    603:  "https://fcportland.com",                # FC Portland
    1040: "https://sfeafc.com",                    # SF Elite Academy
    1353: "https://sportingjax.com",               # Sporting Jax
    1354: "https://tennesseesc.com",               # Tennessee SC
    1425: "https://davislegacysc.com",             # Davis Legacy
    1643: "https://seattleunited.com",             # Seattle United
    1689: "https://scunitedsoccer.com",            # South Carolina United
    1693: "https://fcalliancetn.com",              # FC Alliance
    1730: "https://missourirush.com",              # Missouri Rush
    1760: "https://larocafc.org",                  # La Roca FC
    1785: "https://vdava.com",                     # VDA
    1797: "https://fcwisconsin.com",               # FC Wisconsin
    2106: "https://chicagomagicsc.com",            # Chicago Magic
    2181: "https://wilmingtonhammerheads.com",     # Wilmington Hammerheads
    2237: "https://doralsoccer.com",               # Doral Soccer Club
    2289: "https://labreakersfc.com",              # LA Breakers FC
    2322: "https://columbiapremiersc.com",         # Columbia Premier SC
    2331: "https://pacnwsc.com",                   # PacNW SC
    2335: "https://pridesc.com",                   # Pride SC (CO)
    2522: "https://snohomishunited.com",           # Snohomish United
    2701: "https://delawarefc.com",                # Delaware FC
    3054: "https://placerunited.com",              # Placer United
    3232: "https://chattanoogarwsc.com",           # Chattanooga Red Wolves SC
    3405: "https://pipelinesc.org",                # Pipeline SC
    3475: "https://louisvillecityfc.com",          # Louisville City Academy
    3478: "https://clevelandforcefc.com",          # Cleveland Force SC
    3480: "https://unionkc.com",                   # Union KC
    3483: "https://sportingiowa.com",              # Sporting Iowa
    3486: "https://fcwichita.com",                 # FC Wichita
    3639: "https://coloradoedgesc.com",            # Colorado EDGE SC
    3644: "https://scsurfclub.com",                # South Carolina Surf
    3696: "https://kansasrush.com",                # Kansas Rush
    3956: "https://cfcsalem.com",                  # Capital FC (OR/CA – Far West)
    4338: "https://psamonmouth.org",               # PSA Monmouth
    4368: "https://elpasolomotive.com",            # El Paso Locomotive
    4370: "https://acct.us",                       # AC Connecticut
    4603: "https://fairfaxvaunion.com",            # Fairfax VA Union
    5147: "https://stlouisstars.com",              # St. Louis Stars
    # ── Batch search findings ─────────────────────────────────────────────────
    46:   "https://hexfc.com",                    # HEX FC Dominion (PA, not VA)
    51:   "https://boisetimbersthorns.org",       # Boise Timbers FC
    52:   "https://starsofma.org",               # FC Stars (MA)
    56:   "https://gsa-soccer.com",              # GSA (GA)
    57:   "https://lvheat.com",                  # LV Heat Surf
    62:   "https://lonestarsoccer.com",          # Lonestar Soccer Club Red
    64:   "https://matchfitacademy.com",         # Match Fit Surf
    67:   "https://mnthunder.com",               # Minnesota Thunder
    69:   "https://mustangsc.com",               # Mustang SC
    71:   "https://ncfusion.com",                # NC Fusion
    75:   "https://ohioelite.com",               # Ohio Elite SA
    79:   "https://pennfusion.com",              # Penn Fusion SA
    81:   "https://realcolorado.com",            # Real Colorado Academy
    82:   "https://lafcsocal.com",               # LAFC So Cal
    86:   "https://sdscsurfclub.com",            # SDSC Surf
    87:   "https://surfsoccer.com",              # San Diego Surf
    88:   "https://sanjuansc.org",               # San Juan SC
    91:   "https://srunited.com",                # Santa Rosa United
    94:   "https://scorpionssoccer.org",         # Scorpions SC (MA)
    96:   "https://slammersfc.com",              # Slammers FC
    101:  "https://solarsc.com",                 # Solar SC Academy
    106:  "https://tulsasc.com",                 # Tulsa SC (OK)
    107:  "https://utahavalanche.com",           # Utah Avalanche
    112:  "https://washingtonpremierfc.com",     # Washington Premier
    113:  "https://westcoastfc.com",             # West Coast FC
    116:  "https://worldclassfc.com",            # World Class FC
    186:  "https://pateadores.com",              # Pateadores
    294:  "https://mvlasc.org",                  # MVLA
    300:  "https://rebelssc.com",                # Rebels SC
    329:  "https://nasatophat.com",              # NTH-NASA
    343:  "https://wnyflash.com",                # WNY Flash
    373:  "https://gretnaeliteacademy.com",      # Gretna Elite Academy (LA)
    379:  "https://floridakrazekrush.com",       # Florida Kraze Krush
    380:  "https://carolinaelitesc.com",         # CESA Triumph (SC)
    398:  "https://eastsidefc.org",              # Eastside FC
    417:  "https://richmondunitedfc.com",        # Richmond United
    419:  "https://marylandunitedfc.com",        # Maryland United FC
    428:  "https://stasoccer.org",               # STA Soccer (NJ)
    431:  "https://fsafc.com",                   # FSA FC (CT)
    437:  "https://opsoccer.com",                # Ohio Premier
    451:  "https://lvurush.com",                 # LVU Rush
    494:  "https://baltimoreCeltic.com",         # Baltimore Celtic
    518:  "https://manhattansc.org",             # Manhattan SC (NY)
    525:  "https://arlingtonva.soccer",          # Arlington Soccer
    538:  "https://riverhoundssoccer.com",       # Pittsburgh Riverhounds
    592:  "https://arizonaarsenalyouth.com",     # Arizona Arsenal
    603:  "https://fcportland.org",              # FC Portland (OR)
    628:  "https://beachfutbolclub.com",         # Beach FC (VA)
    893:  "https://stcroixsoccer.org",           # St Croix (MN)
    1040: "https://sfeafc.com",                  # SF Elite Academy
    1345: "https://ukrainiannationals.com",      # Philadelphia Ukrainian Nationals
    1353: "https://sportingjax.com",             # Sporting Jax
    1354: "https://tennesseesc.com",             # Tennessee SC
    1409: "https://ecsurfsoccer.com",            # East Coast Surf SC
    1425: "https://davislegacysc.com",           # Davis Legacy
    1470: "https://californiaodyssey.org",       # COSC
    1501: "https://fcpride.org",                 # FC Pride Elite (IN)
    1560: "https://nmrapids.org",                # NM Rapids
    1585: "https://marinfc.org",                 # Marin FC
    1643: "https://seattleunited.com",           # Seattle United
    1689: "https://scunitedsoccer.com",          # South Carolina United
    1693: "https://fcalliancetn.com",            # FC Alliance
    1713: "https://nationalssoccer.com",         # Nationals Soccer Club
    1726: "https://sportingnebraskafc.com",      # Sporting Nebraska FC
    1730: "https://missourirush.com",            # Missouri Rush
    1760: "https://larocafc.org",                # La Roca FC
    1771: "https://bvbia-northamerica.com",      # BVBIA
    1772: "https://risesc.org",                  # RISE SC
    1785: "https://vdava.com",                   # VDA
    1797: "https://fcwisconsin.com",             # FC Wisconsin
    1813: "https://idahorush.com",               # Idaho Rush
    1919: "https://spacecoastsoccer.org",        # Space Coast United
    1925: "https://ftlutd.com",                  # Fort Lauderdale United FC
    1936: "https://ccvstars.com",                # CCV Stars (AZ)
    1940: "https://potomacsoccer.org",           # Potomac SA
    2017: "https://rockfordraptors.org",         # Rockford Raptors
    2106: "https://chicagomagicsc.com",          # Chicago Magic
    2133: "https://okenergyfc.org",              # OK Energy FC
    2167: "https://chicagointersoccer.com",      # Chicago Inter Soccer
    2181: "https://wilmingtonhammerheads.com",   # Wilmington Hammerheads
    2229: "https://3rsc.org",                    # 3RSC (WA)
    2235: "https://lobosrush.com",               # Lobos Rush (TN)
    2237: "https://doralsoccerclub.com",         # Doral Soccer Club
    2257: "https://indianaelitefc.com",          # Indiana Elite FC
    2258: "https://htxsoccer.com",               # HTX
    2289: "https://labreakersfc.com",            # LA Breakers FC
    2322: "https://columbiapremiersc.com",       # Columbia Premier SC
    2329: "https://fc-prime.com",               # FC Prime (FL)
    2330: "https://athleticskc.com",             # Kansas City Athletics
    2331: "https://pacnwsc.com",                 # PacNW SC
    2335: "https://pridesc.com",                 # Pride SC (CO)
    2519: "https://sacitysc.com",               # San Antonio City SC
    2522: "https://snohomishunited.com",         # Snohomish United
    2536: "https://unitedpdx.com",              # United PDX
    2548: "https://santaclarasporting.com",      # Santa Clara Sporting
    2701: "https://delawarefc.com",              # Delaware FC
    2731: "https://floridapremierfc.com",        # FL Premier FC
    2937: "https://oregonpremierfc.com",         # Oregon Premier
    2955: "https://riverislandssurf.com",        # River Islands Surf
    3054: "https://placerunited.com",            # Placer United
    3065: "https://associationfc.com",           # Association FC (estimate)
    3109: "https://palmbeachunited.org",         # Palm Beach United
    3231: "https://losgatosunited.com",          # Los Gatos United
    3232: "https://chattanoogarwsc.com",         # Chattanooga Red Wolves SC
    3234: "https://fcwestlake.com",              # FC Westlake
    3384: "https://floridawestfc.com",           # Florida West FC
    3387: "https://parklandtravelsoccer.com",    # Parkland SC
    3405: "https://pipelinesc.org",              # Pipeline SC
    3407: "https://unitedfa.org",               # United Futbol Academy (GA)
    3475: "https://louisvillecityfc.com",        # Louisville City Academy
    3476: "https://crossfiresoccer.org",         # XF Academy (Crossfire Premier, WA)
    3478: "https://clevelandforcefc.com",        # Cleveland Force SC
    3480: "https://unionkcsoccer.com",           # Union KC
    3483: "https://sportingiowa.com",            # Sporting Iowa
    3486: "https://fcwichita.com",               # FC Wichita
    3589: "https://germantownlegends.com",       # Germantown Legends
    3639: "https://edgesoccer.net",              # Colorado EDGE SC
    3644: "https://scsurfclub.com",              # South Carolina Surf (estimate)
    3696: "https://kansasrush.com",              # Kansas Rush (estimate)
    3723: "https://vsarush.com",                 # VSA Rush
    3739: "https://skylineelitesc.org",          # Skyline Elite
    4012: "https://highlandfc.com",              # Highland FC (NC, estimate)
    4063: "https://ecfcsalinas.com",             # El Camino Futbol Club Salinas
    4304: "https://sanantoniofc.com",            # SAFC
    4327: "https://msrushunited.com",            # Mississippi Rush United
    4330: "https://emfc.org",                   # Eugene Metro FC
    4338: "https://psamonmouth.org",             # PSA Monmouth
    4342: "https://newarksoccer.org",            # 1974 Newark FC
    4355: "https://sjebfc.com",                  # SJEBFC
    4368: "https://elpasolomotive.com",          # El Paso Locomotive
    4370: "https://acct.us",                     # AC Connecticut
    4603: "https://fairfaxvaunion.com",          # Fairfax VA Union
    5213: "https://lafiresoccer.com",            # Louisiana Fire Soccer Club
}

# ── State hint from club name ─────────────────────────────────────────────────
NAME_STATE_HINTS = [
    # Texas
    ("dallas",          "TX"),
    ("texas",           "TX"),
    ("lonestar",        "TX"),
    ("albion hurricanes", "TX"),
    ("fc dallas",       "TX"),
    ("dksc",            "TX"),
    ("el paso",         "TX"),
    ("nth-nasa",        "TX"),
    # Georgia
    ("atlanta",         "GA"),
    ("concorde fire",   "GA"),
    ("gsa",             "GA"),
    # North Carolina
    ("north carolina",  "NC"),
    ("nc fusion",       "NC"),
    ("ncfc",            "NC"),
    ("charlotte",       "NC"),
    ("wilmington hammerheads", "NC"),
    # Virginia
    ("virginia",        "VA"),
    ("hex fc",          "VA"),
    ("richmond united", "VA"),
    ("arlington soccer","VA"),
    ("vda",             "VA"),
    ("vsa rush",        "VA"),
    ("fairfax",         "VA"),
    ("skyline elite",   "VA"),
    ("highland fc",     "VA"),
    # Maryland / DC
    ("maryland",        "MD"),
    ("baltimore celtic","MD"),
    ("pipeline sc",     "MD"),
    ("potomac sa",      "MD"),
    # Pennsylvania
    ("penn fusion",     "PA"),
    ("philadelphia",    "PA"),
    ("pittsburgh",      "PA"),
    ("lvu rush",        "PA"),
    # New Jersey
    ("match fit",       "NJ"),
    ("psa monmouth",    "NJ"),
    ("sjebfc",          "NJ"),
    # New York
    ("east meadow",     "NY"),
    ("wny flash",       "NY"),
    ("manhattan sc",    "NY"),
    ("susa fc",         "NY"),
    # New England / MA
    ("new england",     "MA"),
    ("boston",          "MA"),
    ("fc stars",        "MA"),
    ("world class fc",  "MA"),
    # Connecticut
    ("connecticut",     "CT"),
    ("fsa fc",          "CT"),
    # Massachusetts
    ("scorpions sc",    "MA"),
    # Delaware
    ("delaware fc",     "DE"),
    # Colorado
    ("colorado",        "CO"),
    ("real colorado",   "CO"),
    ("pride sc",        "CO"),
    ("edge soccer",     "CO"),
    ("colorado edge",   "CO"),
    # Illinois
    ("chicago",         "IL"),
    ("eclipse select",  "IL"),
    ("rockford",        "IL"),
    # Ohio
    ("ohio",            "OH"),
    ("cleveland force", "OH"),
    ("nationals soccer","OH"),
    # Kentucky
    ("louisville city", "KY"),
    # Indiana
    ("fc pride elite",  "IN"),
    ("indiana elite",   "IN"),
    # Michigan
    ("michigan",        "MI"),
    # Tennessee
    ("tennessee",       "TN"),
    ("chattanooga",     "TN"),
    ("fc alliance",     "TN"),
    ("germantown legends","TN"),
    ("memphis",         "TN"),
    # Alabama
    ("alabama",         "AL"),
    # Mississippi
    ("mississippi",     "MS"),
    # Louisiana
    ("louisiana",       "LA"),
    ("gretna elite",    "LA"),
    # Nebraska
    ("nebraska",        "NE"),
    ("sporting nebraska","NE"),
    # Kansas
    ("kansas",          "KS"),
    ("fc wichita",      "KS"),
    ("union kc",        "MO"),
    # Iowa
    ("sporting iowa",   "IA"),
    # Missouri
    ("kansas city",     "MO"),
    ("st. louis",       "MO"),
    ("missouri",        "MO"),
    # Wisconsin
    ("st croix",        "WI"),
    ("wisconsin",       "WI"),
    # Minnesota
    ("minnesota",       "MN"),
    # South Carolina
    ("south carolina",  "SC"),
    ("cesa triumph",    "SC"),
    # Florida
    ("florida",         "FL"),
    ("orlando",         "FL"),
    # Arizona
    ("arizona arsenal", "AZ"),
    ("phoenix",         "AZ"),
    # Nevada
    ("las vegas",       "NV"),
    ("lv heat",         "NV"),
    # Utah
    ("utah",            "UT"),
    ("real salt lake",  "UT"),
    ("la roca",         "UT"),
    # New Mexico
    ("nm rapids",       "NM"),
    ("new mexico",      "NM"),
    # Idaho
    ("idaho rush",      "ID"),
    ("boise",           "ID"),
    # Oregon
    ("portland",        "OR"),
    ("united pdx",      "OR"),
    ("oregon premier",  "OR"),
    ("eugene metro",    "OR"),
    ("columbia premier","OR"),
    # Washington
    ("seattle",         "WA"),
    ("eastside fc",     "WA"),
    ("washington premier","WA"),
    ("pacnw",           "WA"),
    ("snohomish",       "WA"),
    # California
    ("san diego",       "CA"),
    ("legends fc san diego", "CA"),
    ("legends fc",      "CA"),
    ("san jose",        "CA"),
    ("los angeles",     "CA"),
    ("la breakers",     "CA"),
    ("lafc",            "CA"),
    ("sdsc surf",       "CA"),
    ("slammers fc",     "CA"),
    ("west coast fc",   "CA"),
    ("pateadores",      "CA"),
    ("rebels sc",       "CA"),
    ("mustang sc",      "CA"),
    ("sporting ca",     "CA"),
    ("northern cal",    "CA"),
    ("santa rosa",      "CA"),
    ("marin fc",        "CA"),
    ("san juan sc",     "CA"),
    ("mvla",            "CA"),
    ("placer united",   "CA"),
    ("davis legacy",    "CA"),
    ("los gatos",       "CA"),
    ("santa clara sporting", "CA"),
    ("cosc",            "CA"),
    ("river islands",   "CA"),
    ("el camino futbol", "CA"),
    ("1974 newark",     "CA"),
    ("newark fc",       "CA"),
    ("sf elite",        "CA"),
    # Oregon
    ("columbia premier","OR"),
    ("united pdx",      "OR"),
    ("oregon premier",  "OR"),
    ("eugene metro",    "OR"),
    ("fc portland",     "OR"),
    ("3rsc",            "WA"),  # Three Rivers SC, Pasco WA
    # Georgia (non-Atlanta)
    ("united futbol",   "GA"),
    ("gsa",             "GA"),
    # Tennessee (Lobos Rush)
    ("lobos rush",      "TN"),
    # Arizona (CCV Stars)
    ("ccv stars",       "AZ"),
    # Minnesota (St Croix based in Stillwater MN)
    ("st croix",        "MN"),
    # Oklahoma (in Texas ECNL conference)
    ("tulsa sc",        "OK"),
    ("ok energy",       "OK"),
    ("okc",             "OK"),
    # North Carolina (Highland FC in Asheville)
    ("highland fc",     "NC"),
]


def normalize_conf(raw: str) -> str:
    """'ECNL Boys Far West 2025-26' → 'Far West'"""
    m = CONF_LONG_RE.match(raw.strip())
    return m.group(1) if m else raw.strip()


def normalize_conferences(confs_str: str) -> str:
    parts = [normalize_conf(c) for c in confs_str.split(" | ")]
    # Deduplicate while preserving order
    seen, result = set(), []
    for p in parts:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return " | ".join(result)


def guess_state(club_name: str, conferences: str) -> str:
    name_lower = club_name.lower()
    for hint, state in NAME_STATE_HINTS:
        if hint in name_lower:
            return state

    # Fall back to first conference
    first_conf = conferences.split(" | ")[0]
    states = CONF_STATES.get(first_conf, [])
    if len(states) == 1:
        return states[0]
    return ""


def main():
    with open(CLUBS_FILE) as f:
        clubs = list(csv.DictReader(f))

    for c in clubs:
        # Normalize conference names
        c["conferences"] = normalize_conferences(c["conferences"])
        cid = int(c["club_id"])
        # State: inference then override
        c["state"] = guess_state(c["club_name"], c["conferences"])
        if cid in STATE_OVERRIDES:
            c["state"] = STATE_OVERRIDES[cid]
        # Fill known websites
        if not c["website"] and cid in KNOWN_WEBSITES:
            c["website"] = KNOWN_WEBSITES[cid]

    # Write back with state column added
    fields = ["club_id", "club_name", "region", "state", "conferences", "age_groups", "website"]
    with open(CLUBS_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(clubs)

    total = len(clubs)
    with_site = sum(1 for c in clubs if c["website"])
    with_state = sum(1 for c in clubs if c["state"])
    print(f"{total} clubs written → {CLUBS_FILE.name}")
    print(f"  With website: {with_site}")
    print(f"  With state:   {with_state}")
    print(f"  Missing state: {total - with_state}")

    # Show clubs missing state
    missing = [c for c in clubs if not c["state"]]
    if missing:
        print("\nMissing state (multi-state conference):")
        for c in missing:
            print(f"  {c['club_name']:40s} [{c['conferences']}]")


if __name__ == "__main__":
    main()
