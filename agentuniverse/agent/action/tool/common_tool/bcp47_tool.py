#!/usr/bin/env python3
"""RFC 5646 (BCP 47) language tag validation and analysis for agents.

Bcp47Tool validates, canonicalizes, matches (RFC 4647 Basic Filtering /
Lookup), and explains BCP 47 language tags offline, using curated tables
embedded from the IANA language subtag registry, ISO 639, ISO 15924, and
ISO 3166-1. Standard library only; fully deterministic.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool


# ---------------------------------------------------------------------------
# Embedded curated registry tables (frozen at import time).
#
# Sources: IANA Language Subtag Registry (curated subset; the script table is
# complete), ISO 639-1/-3 as incorporated into that registry, ISO 15924,
# ISO 3166-1 alpha-2 plus common UN M.49 numeric regions, and the RFC 5646
# grandfathered tag list. Descriptions are informational.
# ---------------------------------------------------------------------------


def _pairs(text: str, key_form: Any = str.lower) -> MappingProxyType:
    """Parse 'code description...' lines into a frozen mapping."""
    table: dict[str, str] = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        code, _, description = line.partition(" ")
        table[key_form(code)] = description.strip()
    return MappingProxyType(table)


def _quad(text: str) -> MappingProxyType:
    """Parse 'code description prefix fold_to' lines into a frozen mapping.

    Each extlang entry records its registered Prefix primary language and the
    primary language subtag it folds to during canonicalization ('-' when the
    extlang has no standalone primary form).
    """
    table: dict[str, dict[str, str]] = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ")
        code = parts[0]
        description = " ".join(parts[1:-2])
        table[code.lower()] = {
            "description": description,
            "prefix": parts[-2].lower(),
            "fold": "" if parts[-1] == "-" else parts[-1].lower(),
        }
    return MappingProxyType(table)


def _tagged(text: str) -> MappingProxyType:
    """Parse 'tag description preferred' lines into a frozen mapping."""
    table: dict[str, dict[str, str]] = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ")
        tag = parts[0].lower()
        description = " ".join(parts[1:-1])
        preferred = parts[-1]
        table[tag] = {
            "description": description,
            "preferred": "" if preferred == "-" else preferred,
        }
    return MappingProxyType(table)


# Curated primary language subtags, restricted to codes registered in the
# IANA language subtag registry. Per RFC 5646 section 2.2.1, when a language
# has both an ISO 639-1 code and a three-letter code, only the ISO 639-1
# code is registered (so 'zho'/'eng'/'fra' style codes are NOT valid BCP 47
# subtags and are deliberately absent).
_LANGUAGES_TEXT = """
aa Afar
ab Abkhazian
ae Avestan
af Afrikaans
ak Akan
am Amharic
an Aragonese
ar Arabic
as Assamese
av Avaric
ay Aymara
az Azerbaijani
ba Bashkir
be Belarusian
bg Bulgarian
bh Bihari languages (deprecated ISO 639-1; use bih)
bih Bihari languages (macrolanguage)
bi Bislama
bm Bambara
bn Bengali
bo Tibetan
br Breton
bs Bosnian
ca Catalan
ce Chechen
ch Chamorro
co Corsican
cr Cree
cs Czech
cu Church Slavic
cv Chuvash
cy Welsh
da Danish
de German
dv Divehi
dz Dzongkha
ee Ewe
el Greek
en English
eo Esperanto
es Spanish
et Estonian
eu Basque
fa Persian
ff Fulah
fi Finnish
fj Fijian
fo Faroese
fr French
fy Western Frisian
ga Irish
gd Scottish Gaelic
gl Galician
gn Guarani
gu Gujarati
gv Manx
ha Hausa
he Hebrew
hi Hindi
ho Hiri Motu
hr Croatian
ht Haitian Creole
hu Hungarian
hy Armenian
hz Herero
ia Interlingua
id Indonesian
ie Interlingue
ig Igbo
ii Sichuan Yi
ik Inupiaq
in Interlingua (deprecated ISO 639-1; use id)
io Ido
is Icelandic
it Italian
iu Inuktitut
iw Hebrew (deprecated ISO 639-1; use he)
ja Japanese
ji Yiddish (deprecated ISO 639-1; use yi)
jv Javanese
jw Javanese (deprecated ISO 639-1; use jv)
ka Georgian
kg Kongo
ki Kikuyu
kj Kuanyama
kk Kazakh
kl Kalaallisut
km Central Khmer
kn Kannada
ko Korean
kr Kanuri
ks Kashmiri
ku Kurdish
kv Komi
kw Cornish
ky Kirghiz
la Latin
lb Luxembourgish
lg Ganda
li Limburgan
ln Lingala
lo Lao
lt Lithuanian
lu Luba-Katanga
lv Latvian
mg Malagasy
mh Marshallese
mi Maori
mk Macedonian
ml Malayalam
mn Mongolian
mo Moldavian (deprecated ISO 639-1; use ro)
mr Marathi
ms Malay
mt Maltese
my Burmese
na Nauru
nb Norwegian Bokmal
nd North Ndebele
ne Nepali
ng Ndonga
nl Dutch
nn Norwegian Nynorsk
no Norwegian
nr South Ndebele
nv Navajo
ny Chichewa
oc Occitan
oj Ojibwa
om Oromo
or Odia
os Ossetian
pa Panjabi
pi Pali
pl Polish
ps Pashto
pt Portuguese
qu Quechua
rm Romansh
rn Rundi
ro Romanian
ru Russian
rw Kinyarwanda
sa Sanskrit
sc Sardinian
sd Sindhi
se Northern Sami
sg Sango
sh Serbo-Croatian (active registry macrolanguage; sr, hr, or bs preferred for most modern uses)
si Sinhala
sk Slovak
sl Slovenian
so Somali
sq Albanian
sr Serbian
ss Swati
st Southern Sotho
su Sundanese
sv Swedish
sw Swahili
ta Tamil
te Telugu
tg Tajik
th Thai
ti Tigrinya
tk Turkmen
tl Tagalog
tn Tswana
to Tongan
tr Turkish
ts Tsonga
tt Tatar
tw Twi
ty Tahitian
ug Uyghur
uk Ukrainian
ur Urdu
uz Uzbek
ve Venda
vi Vietnamese
vo Volapuk
wa Walloon
wo Wolof
xh Xhosa
yi Yiddish
yo Yoruba
za Zhuang
zh Chinese
zu Zulu
cmn Mandarin Chinese
yue Cantonese (Yue Chinese)
hak Hakka Chinese
hsn Xiang Chinese
nan Min Nan Chinese
wuu Wu Chinese
gan Gan Chinese
cdo Min Dong Chinese
arb Standard Arabic
ase American Sign Language
bfi British Sign Language
bzs Brazilian Sign Language
csl Chinese Sign Language
dsl Danish Sign Language
fsl French Sign Language
gsg German Sign Language
jsl Japanese Sign Language
sgn Sign languages (macrolanguage)
sfb Belgian French Sign Language
vgt Flemish Sign Language
sgg Swiss German Sign Language
jbo Lojban
tlh Klingon
xtg Transalpine Gaulish
ami Amis
bnn Bunun
pwn Paiwan
tao Tao
tay Tayal
tsu Tsou
fil Filipino
bho Bhojpuri
mai Maithili
new Newari
mag Magahi
awa Awadhi
sat Santali
kok Konkani
doi Dogri
kha Khasi
mni Meitei
raj Rajasthani
pnb Western Punjabi
ast Asturian
bar Bavarian
gsw Swiss German (Alemannic)
nds Low German
ckb Central Kurdish
kmr Northern Kurdish
sdh Southern Kurdish
zza Zaza
haw Hawaiian
ilo Ilocano
ceb Cebuano
hil Hiligaynon
war Waray
pag Pangasinan
pam Pampangan
ace Acehnese
ban Balinese
bug Buginese
min Minangkabau
zsm Standard Malay
grc Ancient Greek
arc Imperial Aramaic
cop Coptic
got Gothic
pal Pahlavi
phn Phoenician
ang Old English
enm Middle English
gmh Middle High German
fur Friulian
lld Ladin
vec Venetian
lmo Lombard
pms Piedmontese
nap Neapolitan
scn Sicilian
szl Silesian
dsb Lower Sorbian
hsb Upper Sorbian
krl Karelian
liv Livonian
udm Udmurt
kbd Kabardian
ady Adyghe
lez Lezgian
dar Dargwa
myv Erzya
mdf Moksha
chm Mari (macrolanguage)
mhr Meadow Mari
sah Yakut
kum Kumyk
tzm Central Atlas Tamazight
kab Kabyle
shi Tachelhit
rif Tarifit
zgh Standard Moroccan Tamazight
fon Fon
luo Luo
loz Lozi
mos Mossi
nso Northern Sotho (Pedi)
tum Tumbuka
bal Baluchi
swh Swahili (specific code)
und Undetermined (special subtag)
mul Multiple languages (special subtag)
zxx No linguistic content (special subtag)
"""

# Registered extlang subtags (curated): code, description, prefix, fold_to.
_EXTLANGS_TEXT = """
cmn Mandarin Chinese zh cmn
yue Cantonese Yue Chinese zh yue
hak Hakka Chinese zh hak
hsn Xiang Chinese zh hsn
nan Min Nan Chinese zh nan
wuu Wu Chinese zh wuu
gan Gan Chinese zh gan
cdo Min Dong Chinese zh cdo
arb Standard Arabic ar arb
ase American Sign Language sgn ase
bfi British Sign Language sgn bfi
bzs Brazilian Sign Language sgn bzs
csl Chinese Sign Language sgn csl
dsl Danish Sign Language sgn dsl
fsl French Sign Language sgn fsl
gsg German Sign Language sgn gsg
jsl Japanese Sign Language sgn jsl
"""

# Curated ISO 15924 script codes (full common list).
_SCRIPTS_TEXT = """
Adlm Adlam script
Afak Afaka
Aghb Caucasian Albanian
Ahom Ahom script
Arab Arabic script
Aran Arabic (Nastaliq variant) script
Armi Imperial Aramaic script
Armn Armenian script
Avst Avestan script
Bali Balinese script
Bamu Bamum script
Bass Bassa Vah script
Batk Batak script
Beng Bengali script
Berf Beria Erfe
Bhks Bhaiksuki script
Blis Blissymbols
Bopo Bopomofo
Brah Brahmi script
Brai Braille script
Bugi Buginese script
Buhd Buhid script
Cakm Chakma script
Cans Unified Canadian Aboriginal Syllabics script
Cari Carian script
Cham Cham script
Cher Cherokee script
Chis Chisoi
Chrs Chorasmian script
Cirt Cirth
Copt Coptic script
Cpmn Cypro-Minoan
Cprt Cypriot script
Cyrl Cyrillic script
Cyrs Cyrillic (Old Church Slavonic variant)
Deva Devanagari (Nagari) script
Diak Dives Akuru script
Dogr Dogra script
Dsrt Deseret (Mormon) script
Dupl Duployan shorthand script
Egyd Egyptian demotic script
Egyh Egyptian hieratic script
Egyp Egyptian hieroglyphs
Elba Elbasan script
Elym Elymaic script
Ethi Ethiopic (Ge'ez) script
Gara Garay
Geok Khutsuri (Asomtavruli and Nuskhuri)
Geor Georgian (Mkhedruli) script
Glag Glagolitic script
Gong Gunjala Gondi
Gonm Masaram Gondi
Goth Gothic script
Gran Grantha script
Grek Greek script
Gujr Gujarati script
Gukh Gurung Khema
Guru Gurmukhi script
Hanb Han with Bopomofo (alias for Han + Bopomofo)
Hang Hangul script
Hani Han (Hanzi, Kanji, Hanja) script
Hano Hanunoo script
Hans Han (Simplified variant) script
Hant Han (Traditional variant) script
Hatr Hatran script
Hebr Hebrew
Hira Hiragana script
Hluw Anatolian Hieroglyphs (Luwian) script
Hmng Pahawh Hmong script
Hmnp Nyiakeng Puachue Hmong script
Hntl Han (Traditional variant) with Latin (alias for Hant + Latn)
Hrkt Japanese syllabaries (alias for Hiragana + Katakana)
Hung Old Hungarian (Hungarian Runic) script
Inds Indus
Ital Old Italic (Etruscan, Oscan) script
Jamo Jamo (alias for Jamo subset of Hangul)
Java Javanese
Jpan Japanese (Han + Hiragana + Katakana) script
Jurc Jurchen script
Kali Kayah Li script
Kana Katakana script
Kawi Kawi
Khar Kharoshthi script
Khmr Khmer script
Khoj Khojki script
Kitl Khitan large script
Kits Khitan small script
Knda Kannada script
Kore Korean (alias for Hangul + Han)
Kpel Kpelle
Krai Kirat Rai
Kthi Kaithi script
Lana Tai Tham (Lanna) script
Laoo Lao script
Latf Latin (Fraktur variant) script
Latg Latin (Gaelic variant) script
Latn Latin script
Leke Lek Domaing script
Lepc Lepcha (Rong) script
Limb Limbu
Lina Linear A script
Linb Linear B script
Lisu Lisu (Fraser) script
Loma Loma script
Lyci Lycian script
Lydi Lydian script
Mahj Mahajani script
Maka Makasar
Mand Mandaic script
Mani Manichaean script
Marc Marchen script
Maya Mayan hieroglyphs
Medf Medefaidrin script
Mend Mende Kikakui script
Merc Meroitic Cursive script
Mero Meroitic Hieroglyphs script
Mlym Malayalam script
Modi Modi script
Mong Mongolian (Hudum Mongolian) script
Moon Moon
Mroo Mro script
Mtei Meetei Mayek script
Mult Multani script
Mymr Myanmar (Burmese) script
Nagm Nag Mundari
Nand Nandinagari script
Narb Old North Arabian (Ancient North Arabian) script
Nbat Nabataean script
Newa Newa script
Nkdb Naxi Dongba script
Nkgb Nakhi Geba script
Nkoo N'Ko script
Nshu Nushu script
Ogam Ogham script
Olck Ol Chiki script
Onao Ol Onal
Orkh Old Turkic (Orkhon Runic) script
Orya Oriya script
Osge Osage script
Osma Osmanya script
Ougr Old Uyghur
Palm Palmyrene script
Pauc Pau Cin Hau script
Pcun Proto-Cuneiform
Pelm Proto-Elamite
Perm Old Permic script
Phag Phags-pa script
Phli Inscriptional Pahlavi script
Phlp Psalter Pahlavi script
Phlv Book Pahlavi script
Phnx Phoenician script
Piqd Klingon (KLI pIqaD)
Plrd Miao (Pollard) script
Prti Inscriptional Parthian script
Psin Proto-Sinaitic
Ranj Ranjana
Rjng Rejang script
Rohg Hanifi Rohingya script
Roro Rongorongo script
Runr Runic script
Samr Samaritan script
Sara Sarati script
Sarb Old South Arabian script
Saur Saurashtra script
Seal Seal
Sgnw SignWriting script
Shaw Shavian (Shaw) script
Shrd Sharada script
Shui Shuishu
Sidd Siddham script
Sidt Sidetic
Sind Khudawadi script
Sinh Sinhala script
Sogd Sogdian script
Sogo Old Sogdian script
Sora Sora Sompeng script
Soyo Soyombo script
Sund Sundanese script
Sunu Sunuwar
Sylo Syloti Nagri script
Syrc Syriac script
Syre Syriac (Estrangelo variant)
Syrj Syriac (Western variant) script
Syrn Syriac (Eastern variant) script
Tagb Tagbanwa script
Takr Takri script
Tale Tai Le script
Talu New Tai Lue script
Taml Tamil script
Tang Tangut script
Tavt Tai Viet script
Tayo Tai Yo
Telu Telugu script
Teng Tengwar
Tfng Tifinagh (Berber) script
Tglg Tagalog script
Thaa Thaana script
Thai Thai script
Tibt Tibetan script
Tirh Tirhuta script
Tnsa Tangsa script
Todr Todhri
Tols Tolong Siki
Toto Toto script
Tutg Tulu-Tigalari
Ugar Ugaritic script
Vaii Vai script
Visp Visible Speech
Vith Vithkuqi script
Wara Warang Citi script
Wcho Wancho script
Wole Woleai script
Xpeo Old Persian cuneiform script
Xsux Sumero-Akkadian cuneiform script
Yezi Yezidi script
Yiii Yi script
Zanb Zanabazar Square script
Zinh Inherited script
Zmth Mathematical notation
Zsym Symbols
Zsye Emoji symbols
Zxxx Code for unwritten documents
Zyyy Code for undetermined script
Zzzz Code for uncoded script
"""

# Curated ISO 3166-1 alpha-2 regions plus common UN M.49 numeric regions and
# deprecated codes retained for validation of legacy tags.
_REGIONS_TEXT = """
AD Andorra
AE United Arab Emirates
AF Afghanistan
AG Antigua and Barbuda
AI Anguilla
AL Albania
AM Armenia
AO Angola
AQ Antarctica
AR Argentina
AS American Samoa
AT Austria
AU Australia
AW Aruba
AX Aland Islands
AZ Azerbaijan
BA Bosnia and Herzegovina
BB Barbados
BD Bangladesh
BE Belgium
BF Burkina Faso
BG Bulgaria
BH Bahrain
BI Burundi
BJ Benin
BL Saint Barthelemy
BM Bermuda
BN Brunei Darussalam
BO Bolivia
BQ Bonaire, Sint Eustatius and Saba
BR Brazil
BS Bahamas
BT Bhutan
BV Bouvet Island
BW Botswana
BY Belarus
BZ Belize
CA Canada
CC Cocos (Keeling) Islands
CD Congo, Democratic Republic of the
CF Central African Republic
CG Congo
CH Switzerland
CI Cote d'Ivoire
CK Cook Islands
CL Chile
CM Cameroon
CN China
CO Colombia
CR Costa Rica
CU Cuba
CV Cabo Verde
CW Curacao
CX Christmas Island
CY Cyprus
CZ Czechia
DE Germany
DJ Djibouti
DK Denmark
DM Dominica
DO Dominican Republic
DZ Algeria
EC Ecuador
EE Estonia
EG Egypt
EH Western Sahara
ER Eritrea
ES Spain
ET Ethiopia
FI Finland
FJ Fiji
FK Falkland Islands
FM Micronesia
FO Faroe Islands
FR France
GA Gabon
GB United Kingdom
GD Grenada
GE Georgia
GF French Guiana
GG Guernsey
GH Ghana
GI Gibraltar
GL Greenland
GM Gambia
GN Guinea
GP Guadeloupe
GQ Equatorial Guinea
GR Greece
GS South Georgia and the South Sandwich Islands
GT Guatemala
GU Guam
GW Guinea-Bissau
GY Guyana
HK Hong Kong
HM Heard Island and McDonald Islands
HN Honduras
HR Croatia
HT Haiti
HU Hungary
ID Indonesia
IE Ireland
IL Israel
IM Isle of Man
IN India
IO British Indian Ocean Territory
IQ Iraq
IR Iran
IS Iceland
IT Italy
JE Jersey
JM Jamaica
JO Jordan
JP Japan
KE Kenya
KG Kyrgyzstan
KH Cambodia
KI Kiribati
KM Comoros
KN Saint Kitts and Nevis
KP North Korea
KR South Korea
KW Kuwait
KY Cayman Islands
KZ Kazakhstan
LA Laos
LB Lebanon
LC Saint Lucia
LI Liechtenstein
LK Sri Lanka
LR Liberia
LS Lesotho
LT Lithuania
LU Luxembourg
LV Latvia
LY Libya
MA Morocco
MC Monaco
MD Moldova
ME Montenegro
MF Saint Martin (French part)
MG Madagascar
MH Marshall Islands
MK North Macedonia
ML Mali
MM Myanmar
MN Mongolia
MO Macao
MP Northern Mariana Islands
MQ Martinique
MR Mauritania
MS Montserrat
MT Malta
MU Mauritius
MV Maldives
MW Malawi
MX Mexico
MY Malaysia
MZ Mozambique
NA Namibia
NC New Caledonia
NE Niger
NF Norfolk Island
NG Nigeria
NI Nicaragua
NL Netherlands
NO Norway
NP Nepal
NR Nauru
NU Niue
NZ New Zealand
OM Oman
PA Panama
PE Peru
PF French Polynesia
PG Papua New Guinea
PH Philippines
PK Pakistan
PL Poland
PM Saint Pierre and Miquelon
PN Pitcairn
PR Puerto Rico
PS Palestine
PT Portugal
PW Palau
PY Paraguay
QA Qatar
RE Reunion
RO Romania
RS Serbia
RU Russian Federation
RW Rwanda
SA Saudi Arabia
SB Solomon Islands
SC Seychelles
SD Sudan
SE Sweden
SG Singapore
SH Saint Helena
SI Slovenia
SJ Svalbard and Jan Mayen
SK Slovakia
SL Sierra Leone
SM San Marino
SN Senegal
SO Somalia
SR Suriname
SS South Sudan
ST Sao Tome and Principe
SV El Salvador
SX Sint Maarten (Dutch part)
SY Syrian Arab Republic
SZ Eswatini
TC Turks and Caicos Islands
TD Chad
TF French Southern Territories
TG Togo
TH Thailand
TJ Tajikistan
TK Tokelau
TL Timor-Leste
TM Turkmenistan
TN Tunisia
TO Tonga
TR Turkey
TT Trinidad and Tobago
TV Tuvalu
TW Taiwan
TZ Tanzania
UA Ukraine
UG Uganda
UM United States Minor Outlying Islands
US United States
UY Uruguay
UZ Uzbekistan
VA Holy See (Vatican City State)
VC Saint Vincent and the Grenadines
VG Virgin Islands (British)
VI Virgin Islands (U.S.)
VN Viet Nam
VU Vanuatu
WF Wallis and Futuna
WS Samoa
YE Yemen
YT Mayotte
ZA South Africa
ZM Zambia
ZW Zimbabwe
BU Burma (deprecated; use MM)
TP East Timor (deprecated; use TL)
ZR Zaire (deprecated; use CD)
DD German Democratic Republic (deprecated; use DE)
FX France, Metropolitan (deprecated; use FR)
AN Netherlands Antilles (deprecated, no preferred value)
CS Serbia and Montenegro (deprecated, no preferred value)
NT Neutral Zone (deprecated, no preferred value)
SU Soviet Union (deprecated, no preferred value)
YD Democratic Yemen (deprecated; use YE)
YU Yugoslavia (deprecated, no preferred value)
001 World
002 Africa
003 North America
005 South America
009 Oceania
011 Western Africa
013 Central America
014 Eastern Africa
015 Northern Africa
017 Middle Africa
018 Southern Africa
019 Americas
021 Northern America
029 Caribbean
030 Eastern Asia
034 Southern Asia
035 South-Eastern Asia
039 Southern Europe
053 Australia and New Zealand
054 Melanesia
057 Micronesia
061 Polynesia
142 Asia
143 Central Asia
145 Western Asia
150 Europe
151 Eastern Europe
154 Northern Europe
155 Western Europe
419 Latin America and the Caribbean
"""

# Curated registered variant subtags (common subset of the IANA registry).
_VARIANTS_TEXT = """
1694acad French as codified by the Academie in 1694
1901 German orthography of 1901 (traditional)
1994 Resian orthography of 1994
1996 German orthography of 1996
akuapem Akan, Akuapem dialect
alalc97 ALA-LC romanization, 1997 edition
arevela Eastern Armenian
arevmda Western Armenian
asante Akan, Asante (Ashanti) dialect
biske Resian, Biske dialect
bohoric Bohoric alphabet
boont Boontling
dajnko Dajnko alphabet
emodeng Early Modern English
fonipa IPA phonetic notation
fonkirsh Kirshenbaum phonetic notation
fonupa Uralic Phonetic Alphabet notation
fonxsamp X-SAMPA phonetic notation
hepburn Hepburn romanization
heploc Hepburn romanization (deprecated; use alalc97)
hognorsk Norwegian in traditional (Hognoorsk) orthography
kkcor Cornish, Kernewek Kemmyn orthography
kscor Cornish, Standard Written Form orthography
metelko Metelko alphabet
monoton Greek monotonic orthography
nedis Natisone dialect, Nadiza dialect of Slovenian
njiva Gniva/Njiva dialect of Resian
osojs Oseacco/Osojane dialect of Resian
oxendict Oxford English Dictionary spelling
petr1708 Russian orthography of 1708 (civil script)
pinyin Pinyin romanization
polyton Greek polytonic orthography
rozaj Resian dialect of Slovenian
scouse Liverpudlian (Scouse) English
solba Stolvizza/Solbica dialect of Resian
tarask Belarusian in Taraskievica orthography
uccor Cornish, Unified Cornish orthography
ucrcor Cornish, Unified Cornish Revised orthography
ulster Ulster dialect of English or Scots
unifon Unifon phonetic alphabet
vivaraup Vivaro-Alpine Occitan
wadegile Wade-Giles romanization
"""

# Preferred-value substitutions for deprecated language/region/variant
# subtags (curated from the IANA registry). Every entry below is verified
# against the live registry: the subtag is actually deprecated there and the
# preferred value matches the record's Preferred-Value field ('' = the
# registry deprecates the subtag without registering a replacement).
_DEPRECATED_LANG = {
    "in": ("id", ""),
    "iw": ("he", ""),
    "ji": ("yi", ""),
    "jw": ("jv", ""),
    "mo": ("ro", ""),
    "bh": ("bih", ""),
}
_DEPRECATED_REGION = {
    "BU": "MM",
    "TP": "TL",
    "ZR": "CD",
    "DD": "DE",
    "FX": "FR",
    "YD": "YE",
}
# Deprecated region codes the registry keeps WITHOUT a preferred value.
_DEPRECATED_REGION_NO_PREFERRED = frozenset({"AN", "CS", "NT", "SU", "YU"})
_DEPRECATED_VARIANT = {
    "heploc": "alalc97",
    "arevela": "",
    "arevmda": "",
}

# RFC 5646 section 2.2 reserves these subtag ranges for private use; subtags
# in them are usable in valid tags without registration (section 2.2.1
# rule 3 for languages, section 2.2.3 rule 3 for scripts, section 2.2.4
# rule 3 for regions).
_PRIVATE_USE_LANG_RANGE = ("qaa", "qtz")
_PRIVATE_USE_SCRIPT_RANGE = ("Qaaa", "Qabx")
_PRIVATE_USE_REGIONS = frozenset(
    {"AA", "ZZ"}
    | {f"Q{letter}" for letter in "MNOPQRSTUVWXYZ"}
    | {f"X{letter}" for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
)

# RFC 5646 grandfathered (irregular + regular) tags with registry
# Preferred-Values ('-' marks no preferred value registered).
_GRANDFATHERED_TEXT = """
en-GB-oed English, Oxford English Dictionary spelling (deprecated; use en-GB-oxendict) en-GB-oxendict
i-ami Amis (deprecated; use ami) ami
i-bnn Bunun (deprecated; use bnn) bnn
i-default Default Language (RFC 2277) -
i-enochian Enochian (deprecated, no preferred value registered) -
i-hak Hakka (deprecated; use hak) hak
i-klingon Klingon (deprecated; use tlh) tlh
i-lux Luxembourgish (deprecated; use lb) lb
i-mingo Mingo (deprecated, no single preferred value registered) -
i-navajo Navajo (deprecated; use nv) nv
i-pwn Paiwan (deprecated; use pwn) pwn
i-tao Tao (deprecated; use tao) tao
i-tay Tayal (deprecated; use tay) tay
i-tsu Tsou (deprecated; use tsu) tsu
sgn-BE-FR Belgian French Sign Language (deprecated; use sfb) sfb
sgn-BE-NL Belgian Flemish Sign Language (deprecated; use vgt) vgt
sgn-CH-DE Swiss German Sign Language (deprecated; use sgg) sgg
art-lojban Lojban (deprecated; use jbo) jbo
cel-gaulish Gaulish (deprecated, no preferred value registered; see xcg, xga, xtg) -
no-bok Norwegian Bokmal (deprecated; use nb) nb
no-nyn Norwegian Nynorsk (deprecated; use nn) nn
zh-guoyu Mandarin Chinese, national language (deprecated; use cmn) cmn
zh-hakka Hakka Chinese (deprecated; use hak) hak
zh-min Min Chinese (deprecated, no single preferred value registered) -
zh-min-nan Min Nan Chinese (deprecated; use nan) nan
zh-xiang Xiang Chinese (deprecated; use hsn) hsn
"""

# Registered redundant complete tags (curated metadata subset, each verified
# present in the IANA registry as Type: redundant). These are well-formed
# tags registered as a unit under older RFCs; metadata only.
_REDUNDANT_TEXT = """
sr-Cyrl Serbian, Cyrillic script (registered tag) -
sr-Latn Serbian, Latin script (registered tag) -
zh-Hans Chinese, Simplified Han script (registered tag) -
zh-Hant Chinese, Traditional Han script (registered tag) -
zh-cmn Chinese, Mandarin (registered tag; preferred value cmn) cmn
zh-cmn-Hans Chinese, Mandarin, Simplified Han (registered tag; preferred value cmn-Hans) cmn-Hans
zh-cmn-Hant Chinese, Mandarin, Traditional Han (registered tag; preferred value cmn-Hant) cmn-Hant
zh-yue Chinese, Cantonese (registered tag; preferred value yue) yue
zh-gan Chinese, Gan (registered tag; preferred value gan) gan
de-CH-1901 German, Switzerland, 1901 orthography (registered tag) -
de-DE-1901 German, Germany, 1901 orthography (registered tag) -
de-AT-1901 German, Austria, 1901 orthography (registered tag) -
de-CH-1996 German, Switzerland, 1996 orthography (registered tag) -
de-DE-1996 German, Germany, 1996 orthography (registered tag) -
de-AT-1996 German, Austria, 1996 orthography (registered tag) -
sl-rozaj Slovenian, Resian dialect (registered tag) -
sl-nedis Slovenian, Natisone dialect (registered tag) -
en-scouse English, Scouse dialect (registered tag) -
es-419 Spanish, Latin America and the Caribbean (registered tag) -
"""

# Registry Suppress-Script values (RFC 5646 section 4.1) for the primary
# languages in the table above, transcribed from the IANA registry records.
# Languages without a Suppress-Script field in their registry record are
# deliberately absent: the warning must never fire without registry backing.
_SUPPRESS_SCRIPT = {
    "ar": "Arab", "fa": "Arab", "ps": "Arab", "ur": "Arab",
    "hy": "Armn",
    "as": "Beng", "bn": "Beng",
    "ab": "Cyrl", "be": "Cyrl", "bg": "Cyrl", "kk": "Cyrl", "mk": "Cyrl",
    "ru": "Cyrl", "uk": "Cyrl",
    "hi": "Deva", "kok": "Deva", "mai": "Deva", "mr": "Deva", "ne": "Deva",
    "am": "Ethi", "ti": "Ethi",
    "ka": "Geor",
    "el": "Grek",
    "gu": "Gujr",
    "pa": "Guru",
    "he": "Hebr", "iw": "Hebr", "yi": "Hebr",
    "ja": "Jpan",
    "km": "Khmr",
    "kn": "Knda",
    "ko": "Kore",
    "lo": "Laoo",
    "af": "Latn", "ay": "Latn", "bs": "Latn", "ca": "Latn", "ch": "Latn",
    "cs": "Latn", "cy": "Latn", "da": "Latn", "de": "Latn", "dsb": "Latn",
    "en": "Latn", "eo": "Latn", "es": "Latn", "et": "Latn", "eu": "Latn",
    "fi": "Latn", "fj": "Latn", "fo": "Latn", "fr": "Latn", "fy": "Latn",
    "ga": "Latn", "gl": "Latn", "gn": "Latn", "gsw": "Latn", "gv": "Latn",
    "hr": "Latn", "hsb": "Latn", "ht": "Latn", "hu": "Latn", "id": "Latn",
    "in": "Latn", "is": "Latn", "it": "Latn", "kl": "Latn", "la": "Latn",
    "lb": "Latn", "ln": "Latn", "lt": "Latn", "lv": "Latn", "mg": "Latn",
    "mh": "Latn", "mo": "Latn", "ms": "Latn", "mt": "Latn", "na": "Latn",
    "nb": "Latn", "nd": "Latn", "nds": "Latn", "nl": "Latn", "nn": "Latn",
    "no": "Latn", "nr": "Latn", "nso": "Latn", "ny": "Latn", "om": "Latn",
    "pl": "Latn", "pt": "Latn", "qu": "Latn", "rm": "Latn", "rn": "Latn",
    "ro": "Latn", "rw": "Latn", "sg": "Latn", "sk": "Latn", "sl": "Latn",
    "so": "Latn", "sq": "Latn", "ss": "Latn", "st": "Latn", "sv": "Latn",
    "sw": "Latn", "tl": "Latn", "tn": "Latn", "to": "Latn", "tr": "Latn",
    "ts": "Latn", "ve": "Latn", "vi": "Latn", "xh": "Latn", "zu": "Latn",
    "ml": "Mlym",
    "my": "Mymr",
    "or": "Orya",
    "si": "Sinh",
    "ta": "Taml",
    "te": "Telu",
    "dv": "Thaa",
    "th": "Thai",
    "dz": "Tibt",
}

# Registered extension singletons (IANA extensions registry, curated).
_EXTENSIONS = {
    "u": "Unicode Locale Extension (RFC 6067)",
    "t": "Transformed Content Extension (RFC 6497)",
}

# Curated likely-region hints used by the explain mode.
_LIKELY_REGIONS = {
    "en": ["US", "GB", "CA", "AU"], "fr": ["FR", "CA", "BE", "CH"],
    "es": ["ES", "MX", "AR"], "de": ["DE", "AT", "CH"], "pt": ["BR", "PT"],
    "zh": ["CN", "TW", "HK", "SG"], "cmn": ["CN", "TW", "SG"],
    "yue": ["HK", "CN", "MO"], "ja": ["JP"], "ko": ["KR"], "ru": ["RU"],
    "it": ["IT", "CH"], "nl": ["NL", "BE"], "pl": ["PL"], "ar": ["SA", "EG", "AE"],
    "hi": ["IN"], "bn": ["BD", "IN"], "ta": ["IN", "LK", "SG"],
    "te": ["IN"], "ml": ["IN"], "kn": ["IN"], "mr": ["IN"], "gu": ["IN"],
    "pa": ["IN", "PK"], "ur": ["PK", "IN"], "fa": ["IR", "AF"],
    "tr": ["TR", "CY"], "vi": ["VN"], "th": ["TH"], "id": ["ID"],
    "ms": ["MY", "BN"], "tl": ["PH"], "fil": ["PH"], "sv": ["SE", "FI"],
    "da": ["DK"], "fi": ["FI"], "nb": ["NO"], "nn": ["NO"], "no": ["NO"],
    "is": ["IS"], "el": ["GR", "CY"], "he": ["IL"], "cs": ["CZ"],
    "sk": ["SK"], "sl": ["SI"], "hr": ["HR"], "sr": ["RS", "BA"],
    "uk": ["UA"], "ro": ["RO", "MD"], "hu": ["HU"], "bg": ["BG"],
    "ca": ["ES", "AD"], "eu": ["ES"], "gl": ["ES"], "hy": ["AM"],
    "ka": ["GE"], "az": ["AZ"], "kk": ["KZ"], "uz": ["UZ"], "mn": ["MN"],
    "sw": ["KE", "TZ"], "am": ["ET"], "ha": ["NG", "NE"], "yo": ["NG"],
    "ig": ["NG"], "zu": ["ZA"], "af": ["ZA", "NA"], "mt": ["MT"],
    "lt": ["LT"], "lv": ["LV"], "et": ["EE"], "ga": ["IE"],
}

LANGUAGES: MappingProxyType = _pairs(_LANGUAGES_TEXT)
EXTLANGS: MappingProxyType = _quad(_EXTLANGS_TEXT)
SCRIPTS: MappingProxyType = _pairs(_SCRIPTS_TEXT, str.title)
REGIONS: MappingProxyType = _pairs(_REGIONS_TEXT, str.upper)
VARIANTS: MappingProxyType = _pairs(_VARIANTS_TEXT)
GRANDFATHERED: MappingProxyType = _tagged(_GRANDFATHERED_TEXT)
REDUNDANT: MappingProxyType = _tagged(_REDUNDANT_TEXT)


# ---------------------------------------------------------------------------
# Grammar helpers (RFC 5646 section 2.1 / 2.2).
# ---------------------------------------------------------------------------

_ALPHA = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
_DIGIT = frozenset("0123456789")
_ALNUM = _ALPHA | _DIGIT

# RFC 5646 section 2.1: tags consist of ASCII letters and digits, and
# case-insensitive comparison applies to the ASCII alphabet ONLY. Python's
# str.lower() performs full Unicode case folding (e.g. U+212A KELVIN SIGN
# folds to ASCII 'k'), which would wrongly equate non-ASCII look-alikes with
# ASCII subtags, so all tag comparisons use this ASCII-only folding instead.
_ASCII_LOWER_TABLE = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"
)


def _ascii_lower(text: str) -> str:
    """Case-fold only the ASCII letters A-Z, leaving other code points intact."""
    return text.translate(_ASCII_LOWER_TABLE)

# Error codes that break the RFC 5646 grammar (well_formed becomes False).
# Registry-lookup failures (unknown_*) leave the tag well-formed but invalid.
_STRUCTURAL_CODES = frozenset(
    {
        "empty_input",
        "empty_subtag",
        "invalid_characters",
        "too_many_subtags",
        "language_shape",
        "variant_shape",
        "extension_shape",
        "duplicate_singleton",
        "duplicate_variant",
        "privateuse_shape",
    }
)


def _is_alpha(text: str) -> bool:
    return bool(text) and all(ch in _ALPHA for ch in text)


def _is_alnum(text: str) -> bool:
    return bool(text) and all(ch in _ALNUM for ch in text)


def _case_form(subtag: str, kind: str) -> str:
    """Return the RFC 5646 section 2.1.1 recommended case form."""
    if kind == "script":
        return subtag[:1].upper() + subtag[1:].lower()
    if kind == "region":
        return subtag.upper()
    return subtag.lower()


class _Finding:
    __slots__ = ("code", "message", "subtag", "start", "end")

    def __init__(self, code: str, message: str, subtag: str, start: int, end: int) -> None:
        self.code = code
        self.message = message
        self.subtag = subtag
        self.start = start
        self.end = end

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "subtag": self.subtag,
            "span": [self.start, self.end],
        }


def _tokenize(tag: str) -> list[dict[str, Any]]:
    tokens: list[dict[str, Any]] = []
    position = 0
    for segment in tag.split("-"):
        tokens.append(
            {"subtag": segment, "start": position, "end": position + len(segment)}
        )
        position += len(segment) + 1
    return tokens


class _Parsed:
    """Result of a structural walk over one language tag."""

    def __init__(self) -> None:
        self.tag_type = "langtag"
        self.lang: str | None = None
        self.extlangs: list[str] = []
        self.script: str | None = None
        self.region: str | None = None
        self.variants: list[str] = []
        self.extensions: list[dict[str, Any]] = []
        self.privateuse: list[str] = []
        self.extlang_folded = False
        self.script_injected = False
        self.errors: list[_Finding] = []
        self.warnings: list[_Finding] = []

    def clone(self) -> "_Parsed":
        copy = _Parsed()
        copy.tag_type = self.tag_type
        copy.lang = self.lang
        copy.extlangs = list(self.extlangs)
        copy.script = self.script
        copy.region = self.region
        copy.variants = list(self.variants)
        copy.extensions = [dict(item) for item in self.extensions]
        copy.privateuse = list(self.privateuse)
        copy.extlang_folded = self.extlang_folded
        copy.script_injected = self.script_injected
        copy.errors = list(self.errors)
        copy.warnings = list(self.warnings)
        return copy


class Bcp47Validator:
    """Deterministic RFC 5646 structural and registry validator."""

    def __init__(self, max_subtags: int, max_findings: int) -> None:
        self.max_subtags = max_subtags
        self.max_findings = max_findings

    # -- public entry ------------------------------------------------------
    def validate(self, tag: str) -> _Parsed:
        parsed = _Parsed()
        if not tag:
            parsed.errors.append(_Finding("empty_input", "language tag is empty", "", 0, 0))
            return parsed
        entry = GRANDFATHERED.get(_ascii_lower(tag))
        if entry is not None:
            return self._grandfathered(tag, entry, parsed)
        tokens = _tokenize(tag)
        self._check_characters_and_empties(tokens, parsed)
        if len(tokens) > self.max_subtags:
            self._add_error(
                parsed,
                "too_many_subtags",
                f"tag has {len(tokens)} subtags (limit {self.max_subtags})",
                "",
                len(tag),
                len(tag),
            )
        first = tokens[0]["subtag"]
        if first.lower() == "x" and len(first) == 1:
            self._private_use(tokens, parsed)
        else:
            self._langtag(tokens, parsed)
        self._cap_findings(parsed, tag)
        return parsed

    # -- structural pieces --------------------------------------------------
    def _add_error(self, parsed: _Parsed, code: str, message: str, subtag: str, start: int, end: int) -> None:
        parsed.errors.append(_Finding(code, message, subtag, start, end))

    def _add_warning(self, parsed: _Parsed, code: str, message: str, subtag: str, start: int, end: int) -> None:
        parsed.warnings.append(_Finding(code, message, subtag, start, end))

    def _cap_findings(self, parsed: _Parsed, tag: str) -> None:
        for bucket in (parsed.errors, parsed.warnings):
            if len(bucket) > self.max_findings:
                del bucket[self.max_findings :]
                bucket.append(
                    _Finding(
                        "findings_truncated",
                        f"more than {self.max_findings} findings; remaining suppressed",
                        "",
                        len(tag),
                        len(tag),
                    )
                )

    def _check_characters_and_empties(self, tokens: list[dict[str, Any]], parsed: _Parsed) -> None:
        for index, token in enumerate(tokens):
            subtag = token["subtag"]
            if subtag == "":
                where = "leading" if index == 0 else ("trailing" if index == len(tokens) - 1 else "interior")
                self._add_error(
                    parsed,
                    "empty_subtag",
                    f"empty {where} subtag (adjacent hyphens or hyphen at string edge)",
                    "",
                    token["start"],
                    token["end"],
                )
            elif not _is_alnum(subtag):
                self._add_error(
                    parsed,
                    "invalid_characters",
                    f"subtag '{subtag}' contains characters outside [A-Za-z0-9]",
                    subtag,
                    token["start"],
                    token["end"],
                )

    def _grandfathered(self, tag: str, entry: dict[str, str], parsed: _Parsed) -> _Parsed:
        parsed.tag_type = "grandfathered"
        parsed.lang = tag
        code = "grandfathered_deprecated" if entry["preferred"] else "grandfathered"
        message = f"grandfathered tag: {entry['description']}"
        if entry["preferred"]:
            message += f"; preferred value is '{entry['preferred']}'"
        self._add_warning(parsed, code, message, tag, 0, len(tag))
        return parsed

    def _private_use(self, tokens: list[dict[str, Any]], parsed: _Parsed) -> None:
        parsed.tag_type = "privateuse"
        if len(tokens) == 1:
            self._add_error(
                parsed,
                "privateuse_shape",
                "private use singleton 'x' must be followed by at least one subtag",
                "x",
                tokens[0]["start"],
                tokens[0]["end"],
            )
            return
        self._add_warning(
            parsed,
            "private_use",
            "private use subtags have no registry-defined meaning",
            "x",
            tokens[0]["start"],
            tokens[0]["end"],
        )
        for token in tokens[1:]:
            subtag = token["subtag"]
            if subtag == "" or not _is_alnum(subtag):
                continue  # already reported by the character/empty check
            if not 1 <= len(subtag) <= 8:
                self._add_error(
                    parsed,
                    "privateuse_shape",
                    f"private use subtag '{subtag}' must be 1-8 alphanumeric characters",
                    subtag,
                    token["start"],
                    token["end"],
                )
                continue
            parsed.privateuse.append(subtag)

    def _langtag(self, tokens: list[dict[str, Any]], parsed: _Parsed) -> None:
        self._parse_language(tokens, parsed)
        index = self._parse_extlangs(tokens, 1, parsed)
        index = self._parse_script_region(tokens, index, parsed)
        index = self._parse_variants(tokens, index, parsed)
        self._parse_extensions_and_privateuse(tokens, index, parsed)

    def _parse_language(self, tokens: list[dict[str, Any]], parsed: _Parsed) -> None:
        token = tokens[0]
        subtag = token["subtag"]
        if subtag == "" or not _is_alnum(subtag):
            return  # empty/character problems already reported
        if not _is_alpha(subtag):
            self._add_error(
                parsed,
                "language_shape",
                f"first subtag '{subtag}' must consist only of letters to be a language subtag",
                subtag,
                token["start"],
                token["end"],
            )
            return
        if not 2 <= len(subtag) <= 8:
            shape = "a singleton (1 character)" if len(subtag) == 1 else f"{len(subtag)} characters"
            self._add_error(
                parsed,
                "language_shape",
                f"first subtag '{subtag}' is {shape}; a language subtag is 2-8 letters "
                "(single-character subtags can only start the private use sequence 'x')",
                subtag,
                token["start"],
                token["end"],
            )
            return
        normalized = subtag.lower()
        if normalized in LANGUAGES:
            parsed.lang = subtag
            if normalized in _DEPRECATED_LANG:
                preferred_lang, preferred_script = _DEPRECATED_LANG[normalized]
                preferred = "-".join(p for p in (preferred_lang, preferred_script) if p)
                self._add_warning(
                    parsed,
                    "deprecated_subtag",
                    f"language subtag '{subtag}' is deprecated; preferred value is '{preferred}'",
                    subtag,
                    token["start"],
                    token["end"],
                )
        else:
            if len(subtag) == 3 and _PRIVATE_USE_LANG_RANGE[0] <= normalized <= _PRIVATE_USE_LANG_RANGE[1]:
                parsed.lang = subtag
                self._add_warning(
                    parsed,
                    "private_use_range",
                    f"language subtag '{subtag}' is in the 'qaa'..'qtz' private use range "
                    "reserved by RFC 5646 section 2.2.1; usable without registration",
                    subtag,
                    token["start"],
                    token["end"],
                )
                return
            if len(subtag) == 4:
                message = (
                    f"language subtag '{subtag}' has 4 letters, a range reserved for "
                    "future use, and no such subtag is registered"
                )
            else:
                message = f"language subtag '{subtag}' is not in the curated registry tables"
            self._add_error(
                parsed,
                "unknown_language",
                message,
                subtag,
                token["start"],
                token["end"],
            )
            parsed.lang = subtag

    def _parse_extlangs(self, tokens: list[dict[str, Any]], index: int, parsed: _Parsed) -> int:
        count = 0
        while index < len(tokens) and count < 3:
            token = tokens[index]
            subtag = token["subtag"]
            if not _is_alpha(subtag) or len(subtag) != 3:
                break
            entry = EXTLANGS.get(subtag.lower())
            if entry is None:
                self._add_error(
                    parsed,
                    "unknown_extlang",
                    f"subtag '{subtag}' occupies the extended language position but is not a "
                    "registered extlang in the curated tables",
                    subtag,
                    token["start"],
                    token["end"],
                )
            elif parsed.lang and parsed.lang.lower() != entry["prefix"]:
                self._add_warning(
                    parsed,
                    "extlang_prefix",
                    f"extlang '{subtag}' is registered with prefix '{entry['prefix']}', "
                    f"not '{parsed.lang}'",
                    subtag,
                    token["start"],
                    token["end"],
                )
            parsed.extlangs.append(subtag)
            index += 1
            count += 1
        return index

    def _parse_script_region(self, tokens: list[dict[str, Any]], index: int, parsed: _Parsed) -> int:
        token = tokens[index] if index < len(tokens) else None
        if token is None:
            return index
        subtag = token["subtag"]
        if subtag and _is_alpha(subtag) and len(subtag) == 4:
            form = _case_form(subtag, "script")
            if form in SCRIPTS:
                parsed.script = subtag
                suppressed = _SUPPRESS_SCRIPT.get((parsed.lang or "").lower())
                if suppressed == form:
                    self._add_warning(
                        parsed,
                        "suppressed_script",
                        f"script '{form}' is the registry Suppress-Script for "
                        f"'{parsed.lang}'; the subtag is redundant and SHOULD be omitted",
                        subtag,
                        token["start"],
                        token["end"],
                    )
            else:
                if _PRIVATE_USE_SCRIPT_RANGE[0] <= form <= _PRIVATE_USE_SCRIPT_RANGE[1]:
                    parsed.script = subtag
                    self._add_warning(
                        parsed,
                        "private_use_range",
                        f"script subtag '{form}' is in the 'Qaaa'..'Qabx' private use "
                        "range reserved by RFC 5646 section 2.2.3; usable without registration",
                        subtag,
                        token["start"],
                        token["end"],
                    )
                else:
                    self._add_error(
                        parsed,
                        "unknown_script",
                        f"script subtag '{subtag}' is not a known ISO 15924 script code",
                        subtag,
                        token["start"],
                        token["end"],
                    )
                    parsed.script = subtag
            index += 1
            token = tokens[index] if index < len(tokens) else None
        if token is None:
            return index
        subtag = token["subtag"]
        is_alpha_region = _is_alpha(subtag) and len(subtag) == 2
        is_numeric_region = len(subtag) == 3 and subtag.isdigit()
        if subtag and (is_alpha_region or is_numeric_region):
            form = _case_form(subtag, "region")
            if form in REGIONS:
                parsed.region = subtag
                if form in _DEPRECATED_REGION:
                    self._add_warning(
                        parsed,
                        "deprecated_subtag",
                        f"region subtag '{form}' is deprecated; preferred value is "
                        f"'{_DEPRECATED_REGION[form]}'",
                        subtag,
                        token["start"],
                        token["end"],
                    )
                elif form in _DEPRECATED_REGION_NO_PREFERRED:
                    self._add_warning(
                        parsed,
                        "deprecated_subtag",
                        f"region subtag '{form}' is deprecated and has no preferred value "
                        "registered",
                        subtag,
                        token["start"],
                        token["end"],
                    )
            else:
                if form in _PRIVATE_USE_REGIONS:
                    parsed.region = subtag
                    self._add_warning(
                        parsed,
                        "private_use_range",
                        f"region subtag '{form}' is in a private use range reserved by "
                        "RFC 5646 section 2.2.4 ('AA', 'QM'-'QZ', 'XA'-'XZ', 'ZZ'); "
                        "usable without registration",
                        subtag,
                        token["start"],
                        token["end"],
                    )
                else:
                    self._add_error(
                        parsed,
                        "unknown_region",
                        f"region subtag '{subtag}' is not a known ISO 3166-1 or UN M.49 region code",
                        subtag,
                        token["start"],
                        token["end"],
                    )
                    parsed.region = subtag
            index += 1
        return index

    def _parse_variants(self, tokens: list[dict[str, Any]], index: int, parsed: _Parsed) -> int:
        seen: list[str] = []
        while index < len(tokens):
            token = tokens[index]
            subtag = token["subtag"]
            if subtag == "" or not _is_alnum(subtag):
                index += 1
                continue
            if len(subtag) == 1:
                break  # extension singleton or private use marker starts here
            valid_shape = (5 <= len(subtag) <= 8 and _is_alnum(subtag)) or (
                len(subtag) == 4 and subtag[0] in _DIGIT
            )
            if not valid_shape:
                hint = self._misplacement_hint(subtag)
                self._add_error(
                    parsed,
                    "variant_shape",
                f"subtag '{subtag}' does not fit the variant shape (5-8 alphanumeric "
                f"characters or 4 characters starting with a digit){hint}",
                    subtag,
                    token["start"],
                    token["end"],
                )
                index += 1
                continue
            normalized = subtag.lower()
            if normalized in seen:
                self._add_error(
                    parsed,
                    "duplicate_variant",
                    f"variant subtag '{subtag}' occurs more than once in the tag",
                    subtag,
                    token["start"],
                    token["end"],
                )
                index += 1
                continue
            seen.append(normalized)
            parsed.variants.append(subtag)
            if normalized not in VARIANTS:
                self._add_error(
                    parsed,
                    "unknown_variant",
                    f"variant subtag '{subtag}' is not in the curated registry variant table",
                    subtag,
                    token["start"],
                    token["end"],
                )
            elif normalized in _DEPRECATED_VARIANT:
                preferred = _DEPRECATED_VARIANT[normalized]
                tail = (
                    f"preferred value is '{preferred}'"
                    if preferred
                    else "no preferred value is registered"
                )
                self._add_warning(
                    parsed,
                    "deprecated_subtag",
                    f"variant subtag '{subtag}' is deprecated; {tail}",
                    subtag,
                    token["start"],
                    token["end"],
                )
            index += 1
        return index

    @staticmethod
    def _misplacement_hint(subtag: str) -> str:
        if _is_alpha(subtag) and len(subtag) == 4:
            return "; 4-letter subtags are script codes and must appear before the region"
        if _is_alpha(subtag) and len(subtag) == 2:
            return "; 2-letter subtags are region codes and must appear before any variants"
        if len(subtag) == 3 and subtag.isdigit():
            return "; 3-digit subtags are UN M.49 region codes and must appear before any variants"
        if len(subtag) == 3:
            return "; 3-letter subtags are extlang codes and must directly follow the language"
        if len(subtag) > 8:
            return f"; subtags are limited to 8 characters and '{subtag}' has {len(subtag)}"
        return ""

    def _parse_extensions_and_privateuse(self, tokens: list[dict[str, Any]], index: int, parsed: _Parsed) -> None:
        singletons: list[str] = []
        while index < len(tokens):
            token = tokens[index]
            subtag = token["subtag"]
            if subtag == "" or not _is_alnum(subtag):
                index += 1
                continue
            if len(subtag) != 1:
                self._add_error(
                    parsed,
                    "variant_shape",
                    f"subtag '{subtag}' appears after the variant sequence and cannot be parsed "
                    "(variants must be 5-8 alphanumeric characters or 4 characters "
                    "starting with a digit)",
                    subtag,
                    token["start"],
                    token["end"],
                )
                index += 1
                continue
            singleton = subtag.lower()
            if singleton == "x":
                self._consume_privateuse(tokens, index, parsed)
                return
            duplicate = singleton in singletons
            if duplicate:
                self._add_error(
                    parsed,
                    "duplicate_singleton",
                    f"extension singleton '{subtag}' occurs more than once in the tag",
                    subtag,
                    token["start"],
                    token["end"],
                )
            else:
                singletons.append(singleton)
                if singleton not in _EXTENSIONS:
                    self._add_warning(
                        parsed,
                        "unregistered_singleton",
                        f"extension singleton '{subtag}' has no registered extension in the "
                        "curated tables (registered: u, t)",
                        subtag,
                        token["start"],
                        token["end"],
                    )
            extension: dict[str, Any] = {"singleton": singleton, "subtags": []}
            if not duplicate:
                parsed.extensions.append(extension)
            index += 1
            while index < len(tokens):
                inner = tokens[index]
                inner_subtag = inner["subtag"]
                if inner_subtag == "" or not _is_alnum(inner_subtag):
                    index += 1
                    continue
                if len(inner_subtag) == 1:
                    break
                if len(inner_subtag) > 8:
                    self._add_error(
                        parsed,
                        "extension_shape",
                        f"extension subtag '{inner_subtag}' must be 2-8 alphanumeric characters",
                        inner_subtag,
                        inner["start"],
                        inner["end"],
                    )
                else:
                    extension["subtags"].append(inner_subtag)
                index += 1
            if not extension["subtags"] and not duplicate:
                self._add_error(
                    parsed,
                    "extension_shape",
                    f"extension singleton '{subtag}' must be followed by 2-8 character subtags "
                    "before another singleton appears",
                    subtag,
                    token["start"],
                    token["end"],
                )

    def _consume_privateuse(self, tokens: list[dict[str, Any]], index: int, parsed: _Parsed) -> None:
        marker = tokens[index]
        found = False
        for token in tokens[index + 1 :]:
            subtag = token["subtag"]
            if subtag == "" or not _is_alnum(subtag):
                continue
            if not 1 <= len(subtag) <= 8:
                self._add_error(
                    parsed,
                    "privateuse_shape",
                    f"private use subtag '{subtag}' must be 1-8 alphanumeric characters",
                    subtag,
                    token["start"],
                    token["end"],
                )
                continue
            parsed.privateuse.append(subtag)
            found = True
        if not found:
            self._add_error(
                parsed,
                "privateuse_shape",
                "private use singleton 'x' must be followed by at least one subtag",
                "x",
                marker["start"],
                marker["end"],
            )
        else:
            self._add_warning(
                parsed,
                "private_use",
                "private use subtags have no registry-defined meaning",
                "x",
                marker["start"],
                marker["end"],
            )

    def well_formed(self, parsed: _Parsed) -> bool:
        return not any(
            finding.code in _STRUCTURAL_CODES or finding.code == "findings_truncated"
            for finding in parsed.errors
        )


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------


class Bcp47Tool(Tool):
    """Validate, canonicalize, match (RFC 4647), and explain BCP 47 tags.

    All registry data is embedded as frozen tables; the tool is offline,
    standard-library only, and deterministic. Registry-unknown subtags make a
    tag invalid but leave it well-formed; grammar violations make it
    not-well-formed.
    """

    max_tag_length: int = 512
    max_subtags: int = 64
    max_findings: int = 32

    _MODES: ClassVar[tuple[str, ...]] = ("validate", "canonicalize", "match", "explain")

    def execute(
        self,
        mode: str,
        tag: str | None = None,
        range: str | None = None,
        mechanism: str = "auto",
    ) -> dict[str, Any]:
        """Run one BCP 47 analysis mode.

        Args:
            mode: validate, canonicalize, match, or explain.
            tag: the language tag to analyze.
            range: the RFC 4647 language range (or comma-separated list).
            mechanism: match strategy - auto, filtering, or lookup.

        Returns:
            A structured result dictionary for the requested mode.
        """
        try:
            operation = self._mode(mode)
            if operation == "match":
                return self._match_mode(tag, range, mechanism)
            return self._tag_mode(operation, tag)
        except (TypeError, ValueError) as exc:
            return {"status": "error", "error_type": "validation_error", "error": str(exc), "tag": tag}
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "status": "error",
                "error_type": "operation_error",
                "error": f"BCP 47 analysis failed: {exc}",
                "tag": tag,
            }

    async def async_execute(
        self,
        mode: str,
        tag: str | None = None,
        range: str | None = None,
        mechanism: str = "auto",
    ) -> dict[str, Any]:
        """Asynchronously run one BCP 47 analysis mode (same semantics)."""
        return self.execute(mode=mode, tag=tag, range=range, mechanism=mechanism)

    # -- shared plumbing -----------------------------------------------------
    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in Bcp47Tool._MODES:
            raise ValueError("mode must be validate, canonicalize, match, or explain")
        return mode

    def _check_tag(self, tag: Any) -> str:
        if not isinstance(tag, str):
            raise TypeError("tag must be a string")
        tag = tag.strip()
        if not tag:
            raise ValueError("tag must be a non-empty string")
        if len(tag) > self.max_tag_length:
            raise ValueError(f"tag exceeds max_tag_length ({self.max_tag_length})")
        if "," in tag:
            raise ValueError("tag must be a single language tag, not a comma-separated list")
        return tag

    def _validator(self) -> Bcp47Validator:
        return Bcp47Validator(self.max_subtags, self.max_findings)

    def _tag_mode(self, operation: str, tag: Any) -> dict[str, Any]:
        checked = self._check_tag(tag)
        parsed = self._validator().validate(checked)
        if operation == "validate":
            return self._validate_result(checked, parsed)
        if operation == "canonicalize":
            return self._canonicalize_result(checked, parsed)
        return self._explain_result(checked, parsed)

    # -- validate -------------------------------------------------------------
    def _validate_result(self, tag: str, parsed: _Parsed) -> dict[str, Any]:
        well_formed = self._validator().well_formed(parsed)
        canonical = None
        if well_formed:
            canonical = self._canonical_text(tag, parsed.clone())[0]
        result: dict[str, Any] = {
            "status": "ok",
            "mode": "validate",
            "input": tag,
            "well_formed": well_formed,
            "valid": well_formed and not parsed.errors,
            "type": parsed.tag_type,
            "structure": self._structure(parsed),
            "errors": [finding.to_dict() for finding in parsed.errors],
            "warnings": [finding.to_dict() for finding in parsed.warnings],
            "canonical": canonical,
        }
        if canonical is not None and canonical != tag:
            result["warnings"].append(
                {
                    "code": "case_form",
                    "message": (
                        f"recommended form is '{canonical}' (language lowercase, script "
                        "Titlecase, region UPPERCASE, variants lowercase)"
                        if well_formed and not parsed.errors
                        else f"a more conventional form is '{canonical}'"
                    ),
                    "subtag": tag,
                    "span": [0, len(tag)],
                }
            )
        redundant = REDUNDANT.get(_ascii_lower(tag))
        if redundant is not None and parsed.tag_type == "langtag":
            result["registered_tag"] = "redundant"
            note = f"tag is registered as a redundant complete tag: {redundant['description']}"
            if redundant["preferred"]:
                note += f"; preferred value '{redundant['preferred']}'"
            result["warnings"].append(
                {"code": "redundant_tag", "message": note, "subtag": tag, "span": [0, len(tag)]}
            )
        return result

    @staticmethod
    def _structure(parsed: _Parsed) -> dict[str, Any]:
        return {
            "lang": parsed.lang,
            "extlang": "-".join(parsed.extlangs) if parsed.extlangs else None,
            "script": parsed.script,
            "region": parsed.region,
            "variants": list(parsed.variants),
            "extensions": [
                {"singleton": item["singleton"], "subtags": list(item["subtags"])}
                for item in parsed.extensions
            ],
            "privateuse": "-".join(["x", *parsed.privateuse]) if parsed.privateuse else None,
        }

    # -- canonicalize ----------------------------------------------------------
    def _canonicalize_result(self, tag: str, parsed: _Parsed) -> dict[str, Any]:
        if not self._validator().well_formed(parsed):
            return {
                "status": "error",
                "error_type": "invalid_tag",
                "error": "tag is not well-formed; fix the reported errors before canonicalizing",
                "input": tag,
                "errors": [finding.to_dict() for finding in parsed.errors],
            }
        canonical, notes = self._canonical_text(tag, parsed)
        return {
            "status": "ok",
            "mode": "canonicalize",
            "input": tag,
            "canonical": canonical,
            "notes": notes,
        }

    def _canonical_text(self, tag: str, parsed: _Parsed) -> tuple[str, list[str]]:
        notes: list[str] = []
        if parsed.tag_type == "grandfathered":
            entry = GRANDFATHERED[_ascii_lower(tag)]
            if entry["preferred"]:
                notes.append(
                    f"replaced grandfathered tag '{tag}' with preferred value '{entry['preferred']}'"
                )
                inner = self._validator().validate(entry["preferred"])
                text, _ = self._canonical_text(entry["preferred"], inner)
                return text, notes
            text = "-".join(_ascii_lower(part) for part in tag.split("-"))
            if text != tag:
                notes.append("case-normalized the grandfathered tag")
            return text, notes

        if parsed.tag_type == "privateuse":
            text = "-".join(
                part if part == "x" else _ascii_lower(part) for part in tag.split("-")
            )
            if text != tag:
                notes.append("case-normalized private use subtags")
            return text, notes

        parts: list[tuple[str, str]] = []  # (text, kind) for case forming
        language = parsed.lang or "und"
        language_key = language.lower()
        if language_key in _DEPRECATED_LANG:
            preferred, injected_script = _DEPRECATED_LANG[language_key]
            if injected_script and not parsed.script:
                notes.append(
                    f"replaced deprecated language '{language}' with preferred value "
                    f"'{preferred}' and injected script '{injected_script}'"
                )
                parsed.script = injected_script
                parsed.script_injected = True
            else:
                notes.append(
                    f"replaced deprecated language '{language}' with preferred value '{preferred}'"
                )
            language = preferred
        parts.append((_case_form(language, "language"), "language"))

        for extlang in parsed.extlangs:
            entry = EXTLANGS.get(extlang.lower())
            if entry and entry["fold"] and not parsed.extlang_folded:
                if parts[0][0].lower() == entry["prefix"]:
                    notes.append(
                        f"folded extlang '{extlang.lower()}' of macrolanguage "
                        f"'{parts[0][0]}' into primary language '{entry['fold']}'"
                    )
                    parts[0] = (_case_form(entry["fold"], "language"), "language")
                    parsed.extlang_folded = True
                    continue
            parts.append((_case_form(extlang, "extlang"), "extlang"))

        if parsed.script:
            parts.append((_case_form(parsed.script, "script"), "script"))
        if parsed.region:
            region = _case_form(parsed.region, "region")
            if region in _DEPRECATED_REGION:
                preferred = _DEPRECATED_REGION[region]
                notes.append(
                    f"replaced deprecated region '{region}' with preferred value '{preferred}'"
                )
                region = preferred
            parts.append((region, "region"))

        seen_variants: set[str] = set()
        for variant in parsed.variants:
            normalized = variant.lower()
            if normalized in _DEPRECATED_VARIANT:
                preferred = _DEPRECATED_VARIANT[normalized]
                if preferred:
                    notes.append(
                        f"replaced deprecated variant '{normalized}' with preferred value "
                        f"'{preferred}'"
                    )
                    normalized = preferred
                else:
                    notes.append(
                        f"variant '{normalized}' is deprecated with no preferred value; kept"
                    )
            if normalized in seen_variants:
                notes.append(f"dropped duplicate variant '{normalized}'")
                continue
            seen_variants.add(normalized)
            parts.append((normalized, "variant"))

        if parsed.extensions:
            ordered = sorted(parsed.extensions, key=lambda item: item["singleton"])
            if [item["singleton"] for item in ordered] != [
                item["singleton"] for item in parsed.extensions
            ]:
                notes.append("sorted extension sequences by singleton (alphabetical)")
            for item in ordered:
                parts.append((_case_form(item["singleton"], "extension"), "extension"))
                parts.extend(
                    (_case_form(sub, "extension"), "extension") for sub in item["subtags"]
                )

        if parsed.privateuse:
            parts.append(("x", "privateuse"))
            parts.extend((_case_form(sub, "privateuse"), "privateuse") for sub in parsed.privateuse)

        text = "-".join(part for part, _kind in parts)
        if text != tag and not notes:
            notes.append("case-normalized subtags to the RFC 5646 recommended forms")
        return text, notes

    # -- match (RFC 4647) --------------------------------------------------------
    def _match_mode(self, tag: Any, lang_range: Any, mechanism: Any) -> dict[str, Any]:
        checked_tag = self._check_tag(tag)
        if not isinstance(lang_range, str):
            raise TypeError("range must be a string")
        if not lang_range.strip():
            raise ValueError("range must be a non-empty string")
        if len(lang_range) > self.max_tag_length * 8:
            raise ValueError("range list exceeds the allowed length")
        if mechanism is None:
            mechanism = "auto"
        if not isinstance(mechanism, str) or mechanism.strip().lower() not in (
            "auto",
            "filtering",
            "lookup",
        ):
            raise ValueError("mechanism must be auto, filtering, or lookup")
        chosen = mechanism.strip().lower()
        ranges = [item.strip() for item in lang_range.split(",") if item.strip()]
        if not ranges:
            raise ValueError("range must contain at least one non-empty language range")
        if chosen == "auto":
            chosen = "lookup" if len(ranges) > 1 else "filtering"
        parsed = self._validator().validate(checked_tag)
        warnings: list[dict[str, Any]] = []
        if not self._validator().well_formed(parsed):
            warnings.append(
                {
                    "code": "tag_not_well_formed",
                    "message": "tag is not well-formed; matching proceeds on raw subtags",
                    "subtag": checked_tag,
                    "span": [0, len(checked_tag)],
                }
            )
        if chosen == "filtering":
            matched, position, via, notes = self._basic_filtering(checked_tag, ranges)
        else:
            matched, position, via, notes = self._lookup(checked_tag, ranges)
        return {
            "status": "ok",
            "mode": "match",
            "input_tag": checked_tag,
            "ranges": ranges,
            "mechanism": chosen,
            "matched": matched,
            "first_match": position,
            "matched_via": via,
            "notes": notes,
            "warnings": warnings,
        }

    @staticmethod
    def _basic_filtering(tag: str, ranges: list[str]) -> tuple[str | None, int | None, str | None, list[str]]:
        """RFC 4647 section 3.3.1 Basic Filtering against a single tag."""
        lowered = _ascii_lower(tag)
        notes: list[str] = []
        for position, item in enumerate(ranges):
            if item == "*":
                notes.append(
                    f"range {position} '*' matched any non-empty tag (RFC 4647 section 3.3.1)"
                )
                return tag, position, "*", notes
            candidate = _ascii_lower(item)
            if lowered == candidate or lowered.startswith(candidate + "-"):
                notes.append(
                    f"range {position} '{item}' matched tag '{tag}' by subtag-boundary prefix "
                    "(case-insensitive; RFC 4647 section 3.3.1)"
                )
                return tag, position, item, notes
            notes.append(f"range {position} '{item}' did not match tag '{tag}'")
        notes.append(f"basic filtering exhausted {len(ranges)} range(s) without a match")
        return None, None, None, notes

    @staticmethod
    def _lookup(tag: str, ranges: list[str]) -> tuple[str | None, int | None, str | None, list[str]]:
        """RFC 4647 section 3.4 Lookup with progressive truncation (single tag)."""
        lowered = _ascii_lower(tag)
        notes: list[str] = []
        tried: list[str] = []
        for position, item in enumerate(ranges):
            if item == "*":
                notes.append(f"range {position} '*' skipped during lookup (RFC 4647 section 3.4)")
                continue
            subtags = item.split("-")
            for size in range(len(subtags), 0, -1):
                candidate_parts = subtags[:size]
                # Skip candidates that end in a dangling singleton; a
                # well-formed range never has a 1-character leading subtag.
                if len(candidate_parts[-1]) == 1:
                    continue
                candidate = "-".join(candidate_parts)
                tried.append(candidate)
                if _ascii_lower(candidate) == lowered:
                    notes.append(
                        f"range {position} '{item}' matched tag '{tag}' via truncation "
                        f"to '{candidate}' (RFC 4647 section 3.4)"
                    )
                    return tag, position, candidate, notes
        shown = ", ".join(tried[:16]) + ("..." if len(tried) > 16 else "")
        notes.append(
            f"lookup exhausted {len(ranges)} range(s) after candidates {shown} without a match"
        )
        return None, None, None, notes

    # -- explain -------------------------------------------------------------------
    def _explain_result(self, tag: str, parsed: _Parsed) -> dict[str, Any]:
        well_formed = self._validator().well_formed(parsed)
        canonical, _notes = (
            self._canonical_text(tag, parsed.clone()) if well_formed else (None, [])
        )
        breakdown: list[dict[str, Any]] = []
        summary_parts: list[str] = []
        intents: list[str] = []
        related: list[str] = []

        if parsed.tag_type == "grandfathered":
            entry = GRANDFATHERED[_ascii_lower(tag)]
            breakdown.append(
                {
                    "subtag": tag,
                    "type": "grandfathered",
                    "description": entry["description"],
                    "source": "RFC 5646 grandfathered list",
                }
            )
            summary_parts.append(f"Grandfathered legacy tag: {entry['description']}")
            if entry["preferred"]:
                summary_parts.append(f"modern preferred form is '{entry['preferred']}'")
                related.append(entry["preferred"])
                intents.append(
                    f"legacy tag kept for compatibility; prefer '{entry['preferred']}' for new content"
                )
        elif parsed.tag_type == "privateuse":
            breakdown.append(
                {
                    "subtag": tag,
                    "type": "privateuse",
                    "description": "entirely private use; meaning is defined by private agreement",
                    "source": "RFC 5646 private use syntax",
                }
            )
            summary_parts.append("Private use tag with no registry-defined meaning")
            intents.append("only interoperable with systems that share the private convention")
        else:
            language_key = (parsed.lang or "").lower()
            description = LANGUAGES.get(language_key, "unregistered language subtag")
            breakdown.append(
                {
                    "subtag": parsed.lang,
                    "type": "language",
                    "description": description,
                    "source": "ISO 639 / IANA language subtags",
                }
            )
            summary_parts.append(description)
            for extlang in parsed.extlangs:
                entry = EXTLANGS.get(extlang.lower())
                breakdown.append(
                    {
                        "subtag": extlang,
                        "type": "extlang",
                        "description": (entry or {}).get("description", "unregistered extlang"),
                        "source": "IANA extlang subtags",
                    }
                )
            if parsed.script:
                form = _case_form(parsed.script, "script")
                script_name = SCRIPTS.get(form, form)
                breakdown.append(
                    {
                        "subtag": parsed.script,
                        "type": "script",
                        "description": script_name,
                        "source": "ISO 15924 script codes",
                    }
                )
                summary_parts.append(f"written in the {script_name}")
            if parsed.region:
                form = _case_form(parsed.region, "region")
                region_name = REGIONS.get(form, form)
                breakdown.append(
                    {
                        "subtag": parsed.region,
                        "type": "region",
                        "description": region_name,
                        "source": "ISO 3166-1 / UN M.49 region codes",
                    }
                )
                summary_parts.append(f"as used in {region_name}")
            for variant in parsed.variants:
                variant_name = VARIANTS.get(variant.lower(), variant)
                breakdown.append(
                    {
                        "subtag": variant,
                        "type": "variant",
                        "description": variant_name,
                        "source": "IANA variant subtags",
                    }
                )
                summary_parts.append(f"({variant_name})")
            for item in parsed.extensions:
                description = _EXTENSIONS.get(item["singleton"], "unregistered extension singleton")
                breakdown.append(
                    {
                        "subtag": f"{item['singleton']}-{'-'.join(item['subtags'])}",
                        "type": "extension",
                        "description": description,
                        "source": "IANA extension registry",
                    }
                )
                summary_parts.append(f"({description})")
            if parsed.privateuse:
                breakdown.append(
                    {
                        "subtag": "-".join(["x", *parsed.privateuse]),
                        "type": "privateuse",
                        "description": "private use subtags with no registry meaning",
                        "source": "RFC 5646 private use syntax",
                    }
                )
                summary_parts.append("(private use)")

            base_language = canonical.split("-")[0] if canonical else language_key
            if parsed.region:
                region_name = REGIONS.get(_case_form(parsed.region, "region"), parsed.region)
                intents.append(f"locale-specific content: {description} for {region_name}")
                related.append(base_language)
            else:
                hints = _LIKELY_REGIONS.get(base_language, [])
                if hints and isinstance(hints, list):
                    related.extend(f"{base_language}-{hint}" for hint in hints[:3])
                    intents.append(
                        "language-only tag; add a region subtag (e.g. "
                        + ", ".join(f"'{base_language}-{hint}'" for hint in hints[:2])
                        + ") for locale-specific formatting"
                    )
                intents.append(
                    "suitable for language-level negotiation; add script/region/variant "
                    "subtags only when the distinction matters"
                )
        if canonical and canonical.lower() != tag.lower() and canonical not in related:
            related.insert(0, canonical)
        result: dict[str, Any] = {
            "status": "ok",
            "mode": "explain",
            "input": tag,
            "well_formed": well_formed,
            "canonical": canonical,
            "summary": " ".join(summary_parts),
            "breakdown": breakdown,
            "likely_intents": intents,
            "related_tags": related[:8],
        }
        if not well_formed:
            result["errors"] = [finding.to_dict() for finding in parsed.errors]
        return result
