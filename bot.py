import os
os.environ["GRPC_DNS_RESOLVER"] = "native"

import requests
import time
import json
import zipfile
import io
import glob
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import threading
import random
import re
import html
import pyotp
import sqlite3
import shutil
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
from contextlib import contextmanager

# ==========================================
# Configuration
# ==========================================
TOKEN = "8979274305:AAFZW02islSVKhvBQTjwYUFHozbacE1xmhc"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = 8744359777
BOT_USERNAME = ""

# ==========================================
# Premium Emoji Dictionary
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5353032893096567467">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5352862640592949843">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>',
    "i_info": '<tg-emoji emoji-id="6309655288261644098">ℹ️</tg-emoji>',
    "o_zero": '<tg-emoji emoji-id="6307374961275180239">🅾️</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5199885118214255386", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔟": "5353060913463204207",
    "ℹ️": "6309655288261644098",
    "🅾️": "6307374961275180239",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598932337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607",
    "🤔": "5314563983422798645",
    "📩": "5472239203590888751",
    "🤑": "5805602131176069048",
    "🙈": "5818715087237549366",
    "🔴": "5318840353510408444",
    "⏳": "5337172996211648018",
    "🏳️": "5780471598932337683",
    "🔧": "5818967150278218011",
    "✉️": "6235307467337635626",
    "🐸": "6307777408300753473",
    "🕸️": "6206245785877616415",
    "🪲": "6267107057304868214",
    "🐷": "6204104220694550861",
    "㊙️": "6267262260243076354",
    "🦕": "5226560988291019577",
    "☁️": "6266764202950530136",
    "📵": "6266787022111773140",
    "🐚": "6203886371363364022",
    "⏫": "6206046503690048595",
    "🆘": "6206108815075579644",
    "❓": "6203773684306418660",
    "💷": "5190576863226933563",
    "☎️": "5197474438970363734",
    "🪨": "6267152480878990865",
    "💵": "6267068789146260253",
    "🪙": "5348469219761626211",
    "📞": "5337132498965010628",
    "🟡": "5339082633160703625",
    "🔘": "6217469007868465305",
    "🥂": "6266794310671275367",
    "🎯": "6267186570034419608",
    "🐯": "6267008582294705964"
}

# ==========================================
# air.py Style Constants
# ==========================================
BROADCAST_HEADER_PRE = "6271473763439612077"
BROADCAST_HEADER_SUF = "5118734498590098251"
BROADCAST_TOTAL_EMOJI = "5203993413346680064"
BROADCAST_MONEY_PRE = "6190336264940559752"
BROADCAST_MONEY_SUF = "6204104220694550861"
BROADCAST_BTN_EMOJI = "6204108584381322968"
COPY_EMOJI = "6206420230269310869"
TAKA_EMOJI = "6267068789146260253"
HIDDEN_EMOJI = "6235253239080555488"
MESSAGE_EMOJI = "6235307467337635626"
CHANNEL_EMOJI = "6204010762206189094"
NUMBER_BTN_EMOJI = "5339267587337370029"

WITHDRAW_SELECT_EMOJI = "6217469007868465305"
WITHDRAW_BALANCE_EMOJI = "6217469007868465305"
WITHDRAW_METHOD_ICON = "6266794310671275367"
SEARCH_TARGET_EMOJI = "6267186570034419608"
SEARCH_TIGER_EMOJI = "6267008582294705964"
SEARCH_WORLD_EMOJI = "5780471598922337683"
ROCK_EMOJI = "6267152480878990865"

LEADERBOARD_NUM_EMOJI = {
    1:  "5352651766288652742",
    2:  "5355186458418257716",
    3:  "5352867219028091093",
    4:  "5352566657216714037",
    5:  "5353086880835474989",
    6:  "5354859211975071385",
    7:  "5352859127309707652",
    8:  "5352957533600389988",
    9:  "5353060913463204207",
    10: "6309655288261644098",
}
LEADERBOARD_10_SECOND_EMOJI = "6307374961275180239"

LANG_FULL_NAMES = {
    "EN":"English","AR":"Arabic","BN":"Bangla","HI":"Hindi","PA":"Punjabi",
    "GU":"Gujarati","OR":"Odia","TA":"Tamil","TE":"Telugu","KN":"Kannada",
    "ML":"Malayalam","SI":"Sinhala","TH":"Thai","LO":"Lao","BO":"Tibetan",
    "MY":"Burmese","AM":"Amharic","KM":"Khmer","KA":"Georgian","HY":"Armenian",
    "HE":"Hebrew","EL":"Greek","RU":"Russian","ZH":"Chinese","JA":"Japanese",
    "KO":"Korean","ID":"Indonesian","MS":"Malay","VN":"Vietnamese","TL":"Tagalog",
    "ES":"Spanish","PT":"Portuguese","FR":"French","DE":"German","IT":"Italian",
    "PL":"Polish","TR":"Turkish","NL":"Dutch","SV":"Swedish","DA":"Danish",
    "NO":"Norwegian","FI":"Finnish","CS":"Czech","SK":"Slovak","HU":"Hungarian",
    "RO":"Romanian","HR":"Croatian","BG":"Bulgarian","UK":"Ukrainian",
    "SW":"Swahili","AF":"Afrikaans","FA":"Persian"
}

def lang_full(lang_code):
    if not lang_code: return "English"
    code = str(lang_code).strip().upper().replace("#", "")
    return LANG_FULL_NAMES.get(code, code.title() if code else "English")

def fmt_payout(val):
    """Exact balance display with up to 20 decimal places.
    Preserves tiny values like 0.000000001 (1e-9) or 0.00000000001 (1e-11).
    Falls back gracefully for zero/invalid."""
    try:
        f = float(val)
    except Exception:
        return "0.00"

    if f == 0:
        return "0.00"

    try:
        s = f"{f:.20f}"
        s = s.rstrip('0').rstrip('.')
        if not s:
            s = "0"
        if '.' not in s:
            s += ".00"
        else:
            int_part, dec_part = s.split('.')
            if len(dec_part) == 1:
                s = f"{int_part}.{dec_part}0"
        return s
    except Exception:
        return "0.00"

def get_by_path(obj, path):
    if not path or not str(path).strip(): return None
    parts = str(path).split('.')
    cur = obj
    for p in parts:
        if p == "": continue
        if isinstance(cur, dict):
            if p in cur: cur = cur[p]
            else: return None
        elif isinstance(cur, list):
            try: cur = cur[int(p)]
            except: return None
        else:
            return None
    return cur

def _extract_by_paths(data, p_config):
    number_path = p_config.get("number_path", "").strip()
    message_path = p_config.get("message_path", "").strip()
    service_path = p_config.get("service_path", "").strip()
    otp_list_path = p_config.get("otp_list_path", "").strip()
    if not (number_path or message_path or service_path):
        return None
    root = data
    if otp_list_path:
        try:
            dr = get_by_path(data, otp_list_path)
            if dr is not None: root = dr
        except: pass
    items = root if isinstance(root, list) else [root]
    results = []
    for it in items:
        if not isinstance(it, (dict, list)): continue
        num_raw = get_by_path(it, number_path) if number_path else None
        msg_raw = get_by_path(it, message_path) if message_path else None
        svc_raw = get_by_path(it, service_path) if service_path else None
        if num_raw is None: continue
        clean_num = re.sub(r'\D', '', str(num_raw))
        if not (5 <= len(clean_num) <= 18): continue
        msg_str = str(msg_raw) if msg_raw is not None else ""
        if len(msg_str) < 4: continue
        otp = extract_otp_code(msg_str)
        if not otp: otp = "N/A"
        svc_str = str(svc_raw).strip() if svc_raw is not None else ""
        results.append({"number": clean_num, "message": msg_str, "otp": otp, "service_name": svc_str})
    return results if results else None

assigned_number_meta = {}
_last_upload_bcast = {}
_upload_in_progress = {}

API_PANEL_FIELDS = [
    ("NAME",           "name",               "5818775306974006843"),
    ("BASE URL",       "api_url",            "6285048454255220485"),
    ("CURL COMMAND",   "curl_command",       "5978568938156461643"),
    ("ENDPOINT",       "endpoint",           "6267172559851099903"),
    ("TOKEN",          "token",              "5821453562680448557"),
    ("METHOD",         "method",             "5926860096008098405"),
    ("INTERVAL",       "interval_sec",       "6093456762113888541"),
    ("MAX RECORDS",    "records",            "5868569066154757449"),
    ("OTP LIST PATH",  "otp_list_path",      "5818955300463447293"),
    ("NUMBER PATH",    "number_path",        "5877410604225924969"),
    ("MESSAGE PATH",   "message_path",       "5980911993140284450"),
    ("SERVICE PATH",   "service_path",       "5818967150278218011"),
]

def parse_curl_command(curl_str):
    result = {"url": "", "method": "GET", "headers": {}}
    if not curl_str:
        return result
    s = str(curl_str).replace("\\\n", " ").replace("\\", " ").strip()
    if s.lower().startswith("curl"):
        s = s[4:].strip()
    m = re.search(r'["\']((?:https?://)[^\s"\']+)["\']', s)
    if m:
        result["url"] = m.group(1)
    else:
        m = re.search(r'((?:https?://)[^\s"\']+)', s)
        if m:
            result["url"] = m.group(1)
    method_m = re.search(r'-X\s+["\']?([A-Z]+)["\']?', s, re.I)
    if method_m:
        result["method"] = method_m.group(1).upper()
    for hm in re.findall(r'-H\s+["\']([^"\']+)["\']', s):
        if ": " in hm:
            k, v = hm.split(": ", 1)
            result["headers"][k.strip()] = v.strip()
    return result

# ==========================================
# World Country Database
# ==========================================
COUNTRY_DB = {
    "1":{"iso":"US","name":"United States"},"7":{"iso":"RU","name":"Russia"},
    "20":{"iso":"EG","name":"Egypt"},"27":{"iso":"ZA","name":"South Africa"},
    "30":{"iso":"GR","name":"Greece"},"31":{"iso":"NL","name":"Netherlands"},
    "32":{"iso":"BE","name":"Belgium"},"33":{"iso":"FR","name":"France"},
    "34":{"iso":"ES","name":"Spain"},"36":{"iso":"HU","name":"Hungary"},
    "39":{"iso":"IT","name":"Italy"},"40":{"iso":"RO","name":"Romania"},
    "41":{"iso":"CH","name":"Switzerland"},"43":{"iso":"AT","name":"Austria"},
    "44":{"iso":"GB","name":"United Kingdom"},"45":{"iso":"DK","name":"Denmark"},
    "46":{"iso":"SE","name":"Sweden"},"47":{"iso":"NO","name":"Norway"},
    "48":{"iso":"PL","name":"Poland"},"49":{"iso":"DE","name":"Germany"},
    "51":{"iso":"PE","name":"Peru"},"52":{"iso":"MX","name":"Mexico"},
    "53":{"iso":"CU","name":"Cuba"},"54":{"iso":"AR","name":"Argentina"},
    "55":{"iso":"BR","name":"Brazil"},"56":{"iso":"CL","name":"Chile"},
    "57":{"iso":"CO","name":"Colombia"},"58":{"iso":"VE","name":"Venezuela"},
    "60":{"iso":"MY","name":"Malaysia"},"61":{"iso":"AU","name":"Australia"},
    "62":{"iso":"ID","name":"Indonesia"},"63":{"iso":"PH","name":"Philippines"},
    "64":{"iso":"NZ","name":"New Zealand"},"65":{"iso":"SG","name":"Singapore"},
    "66":{"iso":"TH","name":"Thailand"},"81":{"iso":"JP","name":"Japan"},
    "82":{"iso":"KR","name":"South Korea"},"84":{"iso":"VN","name":"Vietnam"},
    "86":{"iso":"CN","name":"China"},"90":{"iso":"TR","name":"Turkey"},
    "91":{"iso":"IN","name":"India"},"92":{"iso":"PK","name":"Pakistan"},
    "93":{"iso":"AF","name":"Afghanistan"},"94":{"iso":"LK","name":"Sri Lanka"},
    "95":{"iso":"MM","name":"Myanmar"},"98":{"iso":"IR","name":"Iran"},
    "212":{"iso":"MA","name":"Morocco"},"213":{"iso":"DZ","name":"Algeria"},
    "216":{"iso":"TN","name":"Tunisia"},"218":{"iso":"LY","name":"Libya"},
    "220":{"iso":"GM","name":"Gambia"},"221":{"iso":"SN","name":"Senegal"},
    "222":{"iso":"MR","name":"Mauritania"},"223":{"iso":"ML","name":"Mali"},
    "224":{"iso":"GN","name":"Guinea"},"225":{"iso":"CI","name":"Ivory Coast"},
    "226":{"iso":"BF","name":"Burkina Faso"},"227":{"iso":"NE","name":"Niger"},
    "228":{"iso":"TG","name":"Togo"},"229":{"iso":"BJ","name":"Benin"},
    "230":{"iso":"MU","name":"Mauritius"},"231":{"iso":"LR","name":"Liberia"},
    "232":{"iso":"SL","name":"Sierra Leone"},"233":{"iso":"GH","name":"Ghana"},
    "234":{"iso":"NG","name":"Nigeria"},"235":{"iso":"TD","name":"Chad"},
    "236":{"iso":"CF","name":"Central African Republic"},"237":{"iso":"CM","name":"Cameroon"},
    "238":{"iso":"CV","name":"Cape Verde"},"239":{"iso":"ST","name":"Sao Tome and Principe"},
    "240":{"iso":"GQ","name":"Equatorial Guinea"},"241":{"iso":"GA","name":"Gabon"},
    "242":{"iso":"CG","name":"Congo"},"243":{"iso":"CD","name":"DR Congo"},
    "244":{"iso":"AO","name":"Angola"},"245":{"iso":"GW","name":"Guinea-Bissau"},
    "248":{"iso":"SC","name":"Seychelles"},"249":{"iso":"SD","name":"Sudan"},
    "250":{"iso":"RW","name":"Rwanda"},"251":{"iso":"ET","name":"Ethiopia"},
    "252":{"iso":"SO","name":"Somalia"},"253":{"iso":"DJ","name":"Djibouti"},
    "254":{"iso":"KE","name":"Kenya"},"255":{"iso":"TZ","name":"Tanzania"},
    "256":{"iso":"UG","name":"Uganda"},"257":{"iso":"BI","name":"Burundi"},
    "258":{"iso":"MZ","name":"Mozambique"},"260":{"iso":"ZM","name":"Zambia"},
    "261":{"iso":"MG","name":"Madagascar"},"263":{"iso":"ZW","name":"Zimbabwe"},
    "264":{"iso":"NA","name":"Namibia"},"265":{"iso":"MW","name":"Malawi"},
    "266":{"iso":"LS","name":"Lesotho"},"267":{"iso":"BW","name":"Botswana"},
    "268":{"iso":"SZ","name":"Eswatini"},"269":{"iso":"KM","name":"Comoros"},
    "290":{"iso":"SH","name":"Saint Helena"},"291":{"iso":"ER","name":"Eritrea"},
    "297":{"iso":"AW","name":"Aruba"},"298":{"iso":"FO","name":"Faroe Islands"},
    "299":{"iso":"GL","name":"Greenland"},"350":{"iso":"GI","name":"Gibraltar"},
    "351":{"iso":"PT","name":"Portugal"},"352":{"iso":"LU","name":"Luxembourg"},
    "353":{"iso":"IE","name":"Ireland"},"354":{"iso":"IS","name":"Iceland"},
    "355":{"iso":"AL","name":"Albania"},"356":{"iso":"MT","name":"Malta"},
    "357":{"iso":"CY","name":"Cyprus"},"358":{"iso":"FI","name":"Finland"},
    "359":{"iso":"BG","name":"Bulgaria"},"370":{"iso":"LT","name":"Lithuania"},
    "371":{"iso":"LV","name":"Latvia"},"372":{"iso":"EE","name":"Estonia"},
    "373":{"iso":"MD","name":"Moldova"},"374":{"iso":"AM","name":"Armenia"},
    "375":{"iso":"BY","name":"Belarus"},"376":{"iso":"AD","name":"Andorra"},
    "377":{"iso":"MC","name":"Monaco"},"378":{"iso":"SM","name":"San Marino"},
    "380":{"iso":"UA","name":"Ukraine"},"381":{"iso":"RS","name":"Serbia"},
    "382":{"iso":"ME","name":"Montenegro"},"385":{"iso":"HR","name":"Croatia"},
    "386":{"iso":"SI","name":"Slovenia"},"387":{"iso":"BA","name":"Bosnia and Herzegovina"},
    "389":{"iso":"MK","name":"North Macedonia"},"420":{"iso":"CZ","name":"Czech Republic"},
    "421":{"iso":"SK","name":"Slovakia"},"423":{"iso":"LI","name":"Liechtenstein"},
    "500":{"iso":"FK","name":"Falkland Islands"},"501":{"iso":"BZ","name":"Belize"},
    "502":{"iso":"GT","name":"Guatemala"},"503":{"iso":"SV","name":"El Salvador"},
    "504":{"iso":"HN","name":"Honduras"},"505":{"iso":"NI","name":"Nicaragua"},
    "506":{"iso":"CR","name":"Costa Rica"},"507":{"iso":"PA","name":"Panama"},
    "509":{"iso":"HT","name":"Haiti"},"591":{"iso":"BO","name":"Bolivia"},
    "592":{"iso":"GY","name":"Guyana"},"593":{"iso":"EC","name":"Ecuador"},
    "595":{"iso":"PY","name":"Paraguay"},"597":{"iso":"SR","name":"Suriname"},
    "598":{"iso":"UY","name":"Uruguay"},"670":{"iso":"TL","name":"East Timor"},
    "673":{"iso":"BN","name":"Brunei"},"675":{"iso":"PG","name":"Papua New Guinea"},
    "676":{"iso":"TO","name":"Tonga"},"677":{"iso":"SB","name":"Solomon Islands"},
    "678":{"iso":"VU","name":"Vanuatu"},"679":{"iso":"FJ","name":"Fiji"},
    "680":{"iso":"PW","name":"Palau"},"682":{"iso":"CK","name":"Cook Islands"},
    "685":{"iso":"WS","name":"Samoa"},"686":{"iso":"KI","name":"Kiribati"},
    "688":{"iso":"TV","name":"Tuvalu"},"689":{"iso":"PF","name":"French Polynesia"},
    "691":{"iso":"FM","name":"Micronesia"},"692":{"iso":"MH","name":"Marshall Islands"},
    "850":{"iso":"KP","name":"North Korea"},"852":{"iso":"HK","name":"Hong Kong"},
    "853":{"iso":"MO","name":"Macau"},"855":{"iso":"KH","name":"Cambodia"},
    "856":{"iso":"LA","name":"Laos"},"880":{"iso":"BD","name":"Bangladesh"},
    "886":{"iso":"TW","name":"Taiwan"},"960":{"iso":"MV","name":"Maldives"},
    "961":{"iso":"LB","name":"Lebanon"},"962":{"iso":"JO","name":"Jordan"},
    "963":{"iso":"SY","name":"Syria"},"964":{"iso":"IQ","name":"Iraq"},
    "965":{"iso":"KW","name":"Kuwait"},"966":{"iso":"SA","name":"Saudi Arabia"},
    "967":{"iso":"YE","name":"Yemen"},"968":{"iso":"OM","name":"Oman"},
    "970":{"iso":"PS","name":"Palestine"},"971":{"iso":"AE","name":"United Arab Emirates"},
    "972":{"iso":"IL","name":"Israel"},"973":{"iso":"BH","name":"Bahrain"},
    "974":{"iso":"QA","name":"Qatar"},"975":{"iso":"BT","name":"Bhutan"},
    "976":{"iso":"MN","name":"Mongolia"},"977":{"iso":"NP","name":"Nepal"},
    "992":{"iso":"TJ","name":"Tajikistan"},"993":{"iso":"TM","name":"Turkmenistan"},
    "994":{"iso":"AZ","name":"Azerbaijan"},"995":{"iso":"GE","name":"Georgia"},
    "996":{"iso":"KG","name":"Kyrgyzstan"},"998":{"iso":"UZ","name":"Uzbekistan"},
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "<blockquote>👋 <b>WELCOME TO 𝐒𝐓𝐎𝐑𝐌 𝐗 𝐎𝐍𝐄</b> 🤔</blockquote>\n\n📩 <b>RECEIVE OTP'S AND START EARNING MONEY</b> 🤑", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []},
    "search_number": {"text": "╔═══════════╗\n     🔍 <b>SEARCH NUMBER</b>\n╚═══════════╝\n✅ Enter 3 to 9 digits  \nto search for a number.\n━━━━━━━━━━━━━\n📝 Example:\n➥ 880\n➥ 9227373\n━━━━━━━━━━━━━\n🔍 Fast Number Lookup System", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>${{ref_reward}}</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖\n《 🙈 <b>USER ID</b> : <code>{user_id}</code>  》\n➖➖➖➖➖➖➖\n☁️ <b>Total Otp:</b> <code>{total_otp}</code>\n➖➖➖➖➖➖➖\n🫂 <b>Reffer :</b><code>{total_ref}</code>\n➖➖➖➖➖➖➖\n📅 <b>BALANCE:</b> <code>${bal}</code>\n➖➖➖➖➖➖➖\n🔐 <b>MINIMUM:</b> <code>${min_w}</code>\n➖➖➖➖➖➖➖\n<blockquote><b>📱 SELECT METHOD ☎️</b></blockquote>", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []}
}

# ==========================================
# 💾 STROM_DATA — Centralized Persistent Storage
# ==========================================
STROM_DATA_DIR = "STROM_DATA"
try:
    os.makedirs(STROM_DATA_DIR, exist_ok=True)
except Exception as _e:
    print(f"⚠️  Cannot create {STROM_DATA_DIR}: {type(_e).__name__}")

STROM_SQLITE_FILE = os.path.join(STROM_DATA_DIR, "storm_bot.db")
DB_FILE = os.path.join(STROM_DATA_DIR, "bot_data.json")
USERS_LIST_FILE = os.path.join(STROM_DATA_DIR, "users_list.json")
FLAG_TXT_FILE = os.path.join(STROM_DATA_DIR, "flag.txt")
SERVICE_TXT_FILE = os.path.join(STROM_DATA_DIR, "service.txt")

for _legacy_name, _new_path in (("bot_data.json", DB_FILE),
                                ("users_list.json", USERS_LIST_FILE),
                                ("flag.txt", FLAG_TXT_FILE),
                                ("service.txt", SERVICE_TXT_FILE)):
    try:
        if os.path.exists(_legacy_name) and not os.path.exists(_new_path):
            shutil.move(_legacy_name, _new_path)
            print(f"📦 Migrated {_legacy_name} → {_new_path}")
    except Exception as _e:
        print(f"⚠️  Migrate {_legacy_name}: {type(_e).__name__}")

current_db_mode = "sqlite"

_sqlite_lock = threading.RLock()
_sqlite_conn = None


def _sqlite_open():
    global _sqlite_conn
    try:
        _sqlite_conn = sqlite3.connect(
            STROM_SQLITE_FILE,
            timeout=30.0,
            check_same_thread=False,
            isolation_level=None,
        )
        _sqlite_conn.row_factory = sqlite3.Row
        cur = _sqlite_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA foreign_keys=ON;")
        cur.execute("PRAGMA busy_timeout=30000;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id       INTEGER PRIMARY KEY,
                balance       REAL     DEFAULT 0.0,
                total_refers  INTEGER  DEFAULT 0,
                total_otps    INTEGER  DEFAULT 0,
                banned        INTEGER  DEFAULT 0,
                verified      INTEGER  DEFAULT 0,
                referred_by   INTEGER,
                ref_paid      INTEGER  DEFAULT 0,
                created_at    REAL,
                updated_at    REAL
            );
            CREATE TABLE IF NOT EXISTS pending_referrals (
                new_user_id   INTEGER PRIMARY KEY,
                inviter_id    INTEGER NOT NULL,
                created_at    REAL
            );
            CREATE TABLE IF NOT EXISTS referral_paid_users (
                user_id       INTEGER PRIMARY KEY,
                paid_at       REAL
            );
            CREATE TABLE IF NOT EXISTS settings (
                key           TEXT PRIMARY KEY,
                value         TEXT,
                updated_at    REAL
            );
            CREATE TABLE IF NOT EXISTS kv_store (
                k             TEXT PRIMARY KEY,
                v             TEXT,
                updated_at    REAL
            );
            CREATE TABLE IF NOT EXISTS withdrawals (
                req_id        TEXT PRIMARY KEY,
                user_id       INTEGER,
                amount        REAL,
                method        TEXT,
                number        TEXT,
                full_name     TEXT,
                status        TEXT DEFAULT 'pending',
                timestamp     REAL
            );
            CREATE INDEX IF NOT EXISTS idx_users_refers ON users(total_refers);
            CREATE INDEX IF NOT EXISTS idx_users_otps   ON users(total_otps);
            CREATE INDEX IF NOT EXISTS idx_wd_status    ON withdrawals(status);
        """)
        print(f"✅ SQLite initialized (WAL) → {STROM_SQLITE_FILE}")
        return True
    except Exception as e:
        print(f"❌ SQLite init failed: {type(e).__name__}: {e}")
        _sqlite_conn = None
        return False


_sqlite_open()


def sqlite_exec(query, params=(), fetch=None):
    if _sqlite_conn is None:
        return None
    try:
        with _sqlite_lock:
            cur = _sqlite_conn.cursor()
            cur.execute(query, params)
            if fetch == "one":
                r = cur.fetchone()
                return dict(r) if r else None
            if fetch == "all":
                return [dict(x) for x in cur.fetchall()]
            return cur.lastrowid
    except Exception as e:
        print(f"⚠️  SQLite op failed [{query[:60]}]: {type(e).__name__}: {e}")
        return None


@contextmanager
def sqlite_tx():
    if _sqlite_conn is None:
        yield None
        return
    with _sqlite_lock:
        try:
            _sqlite_conn.execute("BEGIN IMMEDIATE;")
            yield _sqlite_conn
            _sqlite_conn.execute("COMMIT;")
        except Exception as e:
            try:
                _sqlite_conn.execute("ROLLBACK;")
            except Exception:
                pass
            print(f"⚠️  SQLite tx rolled back: {type(e).__name__}: {e}")
            raise


def sqlite_kv_get(key, default=None):
    row = sqlite_exec("SELECT v FROM kv_store WHERE k=?", (key,), fetch="one")
    if not row:
        return default
    try:
        return json.loads(row["v"])
    except Exception:
        return default


def sqlite_kv_set(key, value):
    try:
        v = json.dumps(value, default=str)
    except Exception:
        v = json.dumps(str(value))
    return sqlite_exec(
        "INSERT INTO kv_store(k,v,updated_at) VALUES(?,?,?) "
        "ON CONFLICT(k) DO UPDATE SET v=excluded.v, updated_at=excluded.updated_at",
        (key, v, time.time()),
    )


# ==========================================
# 🔥 Firebase Setup — OPTIONAL, NON-DESTRUCTIVE
# ==========================================
db = None
_fb_result = {"db": None, "done": False}


def _try_firebase_init():
    global current_db_mode
    try:
        json_files = (glob.glob("*firebase-adminsdk*.json")
                      + glob.glob("*storm_bot_data*.json")
                      + glob.glob("*storm-bot-data*.json")
                      + glob.glob("*sadikul*.json")
                      + glob.glob("*serviceAccount*.json"))
        valid_files = []
        for f in json_files:
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    d = json.load(fh)
                    if d.get("type") == "service_account" and "private_key" in d:
                        valid_files.append(f)
            except Exception:
                continue
        if not valid_files:
            print("⚠️  Firebase JSON not found — SQLite-only mode")
            _fb_result["done"] = True
            return
        creds_path = valid_files[0]
        print(f"📁 Firebase credentials: {creds_path}")
        cred = credentials.Certificate(creds_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
        try:
            _db.collection('_health_check_').document('x').get(timeout=10.0)
        except Exception:
            pass
        _fb_result["db"] = _db
        _fb_result["done"] = True
        current_db_mode = "firebase"
        print("✅ Firebase Connected (SQLite remains primary local cache)")
    except Exception as e:
        print(f"⚠️  Firebase unavailable: {type(e).__name__}")
        print("✅ SQLite-only mode active")
        current_db_mode = "sqlite"
        _fb_result["done"] = True


_fb_thread = threading.Thread(target=_try_firebase_init, daemon=True)
_fb_thread.start()
_fb_thread.join(timeout=15.0)

if _fb_result["done"] and _fb_result["db"] is not None:
    db = _fb_result["db"]
    current_db_mode = "firebase"
else:
    if not _fb_result["done"]:
        print("⏱️  Firebase timeout (15s) — SQLite-only mode")
    db = None
    current_db_mode = "sqlite"
    # ==========================================
# Bot Settings
# ==========================================
bot_settings = {
    "admins": [OWNER_ID],
    "panels": [], "fw_groups": [],
    "otp_link": "https://t.me/your_otp_group",
    "main_channel_link": "",
    "withdraw_on": True, "min_withdraw": 30.0,
    "otp_reward": 0.1, "refer_reward": 0.2,
    "cooldown": 10, "num_req": 3, "num_share": 1,
    "support_link": "https://t.me/your_support",
    "w_methods": ["bKash", "Nagad"], "w_group": "",
    "fj_on": False, "fj_channels": [],
    "stex_keys": [], "voltx_keys": [],
    "search_countries": [], "stex_services": {}, "voltx_services": {},
    "otp_pair_rates": {}, "maintenance": False,
    "premium_flags": {}, "premium_apps": {},
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
}

FS_KEYS = [
    "admins","panels","fw_groups","otp_link","main_channel_link","withdraw_on",
    "min_withdraw","otp_reward","refer_reward","cooldown","num_req","num_share",
    "support_link","w_methods","w_group","stex_keys","voltx_keys","search_countries",
    "stex_services","voltx_services","fj_on","fj_channels","otp_pair_rates","maintenance"
]

number_batches = {}
used_numbers_list = []
stex_assigned_numbers = {}
voltx_assigned_numbers = {}
STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set()
recent_traffic = []
user_banned_cache = {}
panel_sessions = {}
user_active_sessions = {}


def load_flag_txt():
    path = FLAG_TXT_FILE
    loaded = {}
    if not os.path.exists(path):
        try:
            with open(path, "w", encoding='utf-8') as f:
                f.write("# flag.txt\n# Format: CountryName (calling_code) (ISO) { \"emoji\": \"🇧🇩\", \"id\": \"5911365056594973179\" }\n")
                f.write("United States (1) (US) { \"emoji\": \"🇺🇸\", \"id\": \"5913463998522592692\" }\n")
                f.write("Bangladesh (880) (BD) { \"emoji\": \"🇧🇩\", \"id\": \"5911365056594973179\" }\n")
                f.write("India (91) (IN) { \"emoji\": \"🇮🇳\", \"id\": \"5913754823643107921\" }\n")
                f.write("Pakistan (92) (PK) { \"emoji\": \"🇵🇰\", \"id\": \"5913705895375672082\" }\n")
                f.write("United Kingdom (44) (GB) { \"emoji\": \"🇬🇧\", \"id\": \"5913443365499703513\" }\n")
                f.write("Madagascar (261) (MG) { \"emoji\": \"🇲🇬\", \"id\": \"5780471598932337683\" }\n")
                f.write("Kyrgyzstan (996) (KG) { \"emoji\": \"🇰🇬\", \"id\": \"5780471598932337683\" }\n")
                f.write("Afghanistan (93) (AF) { \"emoji\": \"🇦🇫\", \"id\": \"5780471598932337683\" }\n")
            print(f"{path} created with defaults")
        except Exception as e:
            print(f"Could not create {path}: {e}")
            return loaded
    try:
        with open(path, "r", encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                json_match = re.search(r'(\{.*\})', line)
                if not json_match: continue
                try:
                    data = json.loads(json_match.group(1))
                    char = data.get("emoji")
                    eid = data.get("id")
                    prefix_str = line[:json_match.start()].strip()
                    code_match = re.search(r'\((\d+)\)', prefix_str)
                    iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                    if code_match and iso_match and char and eid:
                        code = code_match.group(1)
                        iso = iso_match.group(1).upper()
                        name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                        if re.match(r'^[A-Za-z0-9#]{1,4}$', str(char)):
                            try:
                                char = ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in iso.upper()[:2])
                            except: char = "🌍"
                        loaded[code] = {"char": char, "iso": iso, "name": name, "id": str(eid)}
                except: continue
        print(f"{path} loaded ({len(loaded)} flags)")
    except Exception as e:
        print(f"Error loading {path}: {e}")
    return loaded


def load_service_txt():
    path = SERVICE_TXT_FILE
    loaded = {}
    if not os.path.exists(path):
        try:
            with open(path, "w", encoding='utf-8') as f:
                f.write("# service.txt\n# Format: ServiceName { \"emoji\": \"📱\", \"id\": \"5334807341109908955\" }\n")
                f.write("Facebook { \"emoji\": \"📱\", \"id\": \"5334807341109908955\" }\n")
                f.write("WhatsApp { \"emoji\": \"📱\", \"id\": \"5334759662677957452\" }\n")
                f.write("Instagram { \"emoji\": \"📱\", \"id\": \"5420130255174145507\" }\n")
            print(f"{path} created with defaults")
        except Exception as e:
            print(f"Could not create {path}: {e}")
            return loaded
    try:
        with open(path, "r", encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                json_match = re.search(r'(\{.*\})', line)
                if not json_match: continue
                try:
                    data = json.loads(json_match.group(1))
                    char = data.get("emoji", "📱")
                    eid = data.get("id")
                    name_part = line[:json_match.start()].strip()
                    name = name_part.replace(char, '').strip() if char else name_part
                    if char and re.match(r'^[A-Za-z0-9#]{1,4}$', str(char)):
                        char = "📱"
                    if char and eid and name:
                        loaded[name.upper()] = {"char": char, "id": str(eid), "name": name}
                except: continue
        print(f"{path} loaded ({len(loaded)} services)")
    except Exception as e:
        print(f"Error loading {path}: {e}")
    return loaded


COUNTRIES_DATA = {}
try:
    if os.path.exists("countries.json"):
        with open("countries.json", "r", encoding='utf-8') as f:
            COUNTRIES_DATA = json.load(f)
except: pass


def fetch_cpt_panel_cdrs(p, session, check_url):
    res = session.get(check_url, timeout=15)
    html_text = res.text
    if "login" in html_text.lower() or "signin" in html_text.lower() or any(x in html_text for x in ["Sign in to your account", "Please sign in", "Welcome back!"]):
        raise Exception("Session expired")
    soup = BeautifulSoup(html_text, 'html.parser')
    s_ajax_source = ""
    for script in soup.find_all("script"):
        script_text = script.string or ""
        match = re.search(r'sAjaxSource":\s*"([^"]+)"', script_text)
        if match:
            s_ajax_source = match.group(1)
            break
    results = []
    n_col_name = p.get("num_col_name", "number").lower()
    m_col_name = p.get("msg_col_name", "message").lower()
    s_col_name = p.get("service_col_name", "service").lower()
    n_idx = int(p.get("num_col_idx", 1)) - 1 if p.get("num_col_idx") else 1
    m_idx = int(p.get("msg_col_idx", 2)) - 1 if p.get("msg_col_idx") else 2
    s_idx = int(p.get("service_col_idx", 3)) - 1 if p.get("service_col_idx") else 3

    def _extract_row(row_val):
        if not isinstance(row_val, list): return None
        if len(row_val) < max(n_idx, m_idx) + 1: return None
        num_val = row_val[n_idx] if (0 <= n_idx < len(row_val)) else row_val[2]
        msg_val = row_val[m_idx] if (0 <= m_idx < len(row_val)) else row_val[4]
        svc_val = row_val[s_idx] if (0 <= s_idx < len(row_val)) else ""
        clean_num = re.sub(r'\D', '', str(num_val))
        if not (clean_num and 5 <= len(clean_num) <= 18): return None
        otp = extract_otp_code(msg_val)
        if not otp: otp = "N/A"
        if not (len(str(msg_val)) > 4): return None
        return {"number": clean_num, "message": str(msg_val), "otp": otp, "service_name": str(svc_val).strip()}

    if s_ajax_source:
        baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
        if not baseUrl.startswith("http"): baseUrl = "http://" + baseUrl
        if s_ajax_source.startswith("http"):
            full_ajax_url = s_ajax_source
        elif s_ajax_source.startswith("/"):
            full_ajax_url = f"{baseUrl}{s_ajax_source}"
        else:
            current_dir = check_url[:check_url.rfind("/")]
            full_ajax_url = f"{current_dir}/{s_ajax_source}"
        if "iDisplayLength" not in full_ajax_url:
            divider = "&" if "?" in full_ajax_url else "?"
            full_ajax_url += f"{divider}sEcho=1&iColumns=7&iDisplayStart=0&iDisplayLength=250&sSearch=&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc"
        ajax_headers = {"Referer": check_url, "X-Requested-With": "XMLHttpRequest"}
        ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
        rows = ajax_res.json().get("aaData", [])
        for row_val in rows:
            item = _extract_row(row_val)
            if item: results.append(item)
    else:
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue
            final_n_idx, final_m_idx, final_s_idx = n_idx, m_idx, s_idx
            header_cells = rows[0].find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                c_text = cell.get_text(strip=True).lower()
                if n_col_name in c_text: final_n_idx = i
                if m_col_name in c_text: final_m_idx = i
                if s_col_name in c_text: final_s_idx = i
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if all(c.name == 'th' for c in cols): continue
                if len(cols) > max(final_n_idx, final_m_idx):
                    num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                    msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                    svc_text = cols[final_s_idx].get_text(separator=" ", strip=True) if len(cols) > final_s_idx else ""
                    clean_num = re.sub(r'\D', '', num_text)
                    if clean_num and 5 <= len(clean_num) <= 18:
                        otp = extract_otp_code(msg_text)
                        if not otp: otp = "N/A"
                        if len(msg_text) > 4:
                            results.append({"number": clean_num, "message": msg_text, "otp": otp, "service_name": svc_text.strip()})
    return results, html_text


# ==========================================
# 🗄️ load_db / save_db
# ==========================================
def _load_settings_from_sqlite():
    try:
        rows = sqlite_exec("SELECT key, value FROM settings", fetch="all")
        if not rows:
            return False
        loaded_any = False
        for row in rows:
            k = row["key"]
            if k in FS_KEYS:
                try:
                    bot_settings[k] = json.loads(row["value"])
                    loaded_any = True
                except Exception:
                    continue
        return loaded_any
    except Exception as e:
        print(f"⚠️  _load_settings_from_sqlite: {type(e).__name__}")
        return False


def _persist_all_settings_to_sqlite():
    try:
        with sqlite_tx() as conn:
            if conn is None:
                return False
            now = time.time()
            cur = conn.cursor()
            for k in FS_KEYS:
                if k not in bot_settings:
                    continue
                try:
                    v = json.dumps(bot_settings[k], default=str)
                except Exception:
                    continue
                cur.execute(
                    "INSERT INTO settings(key,value,updated_at) VALUES(?,?,?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                    (k, v, now),
                )
        return True
    except Exception as e:
        print(f"⚠️  _persist_all_settings_to_sqlite: {type(e).__name__}")
        return False


def load_db():
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic
    global stex_assigned_numbers, voltx_assigned_numbers, current_db_mode
    print("Loading DB...")

    if db:
        try:
            doc = db.collection('settings').document('bot_config').get(timeout=8.0)
            if doc.exists:
                fs_data = doc.to_dict() or {}
                for k in FS_KEYS:
                    if k in fs_data:
                        bot_settings[k] = fs_data[k]
                print("✅ Config merged from Firestore (non-destructive)")
            else:
                try:
                    initial = {k: bot_settings[k] for k in FS_KEYS if k in bot_settings}
                    db.collection('settings').document('bot_config').set(initial, timeout=8.0)
                    print("✅ Firestore Config Initialized (first-time)")
                except Exception as _ie:
                    print(f"⚠️  Firestore init skipped: {type(_ie).__name__}")
        except Exception as e:
            print(f"⚠️  Firestore load skipped ({type(e).__name__}) — SQLite remains authoritative")

    try:
        _load_settings_from_sqlite()
    except Exception as e:
        print(f"⚠️  SQLite settings load skipped: {type(e).__name__}")

    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
            saved_settings = data.get("bot_settings", {})
            for key, val in saved_settings.items():
                if key not in FS_KEYS:
                    if key == "custom_messages":
                        for m_key, m_val in val.items():
                            bot_settings["custom_messages"][m_key] = m_val
                    else:
                        bot_settings[key] = val
            for m_key, m_val in DEFAULT_CUSTOM_MESSAGES.items():
                if m_key not in bot_settings["custom_messages"]:
                    bot_settings["custom_messages"][m_key] = m_val
            number_batches = data.get("number_batches", {}) or {}
            used_numbers_list = data.get("used_numbers_list", []) or []
            total_uploaded_stats = data.get("total_uploaded_stats", 0)
            total_assigned_stats = data.get("total_assigned_stats", 0)
            recent_traffic = data.get("recent_traffic", []) or []
            stex_assigned_numbers = data.get("stex_assigned_numbers", {}) or {}
            voltx_assigned_numbers = data.get("voltx_assigned_numbers", {}) or {}
            assigned_number_meta.update(data.get("assigned_number_meta", {}) or {})
            print("✅ Local JSON state loaded")
        except Exception as e:
            print(f"⚠️  Local JSON load failed: {type(e).__name__}")

    try:
        ul = sqlite_kv_get("all_known_users")
        if isinstance(ul, list) and ul:
            all_known_users.update(str(x) for x in ul)
    except Exception as e:
        print(f"⚠️  all_known_users cache load: {type(e).__name__}")

    try:
        flag_data = load_flag_txt()
        if flag_data:
            for code, fd in flag_data.items():
                bot_settings["premium_flags"][code] = fd
    except Exception as e:
        print(f"⚠️  Flag load error: {type(e).__name__}")

    try:
        service_data = load_service_txt()
        if service_data:
            for name, sd in service_data.items():
                bot_settings["premium_apps"][name] = sd
    except Exception as e:
        print(f"⚠️  Service load error: {type(e).__name__}")

    try:
        _persist_all_settings_to_sqlite()
    except Exception as e:
        print(f"⚠️  SQLite settings persist: {type(e).__name__}")


def save_local_db():
    local_data = {
        "bot_settings": {k: v for k, v in bot_settings.items() if k not in FS_KEYS},
        "number_batches": number_batches,
        "used_numbers_list": used_numbers_list,
        "total_uploaded_stats": total_uploaded_stats,
        "total_assigned_stats": total_assigned_stats,
        "recent_traffic": recent_traffic,
        "stex_assigned_numbers": stex_assigned_numbers,
        "voltx_assigned_numbers": voltx_assigned_numbers,
        "assigned_number_meta": assigned_number_meta
    }
    try:
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump(local_data, f, indent=4, default=str)
    except Exception as e:
        print(f"⚠️  save_local_db (json): {type(e).__name__}")

    try:
        sqlite_kv_set("number_batches", number_batches)
        sqlite_kv_set("used_numbers_list", used_numbers_list)
        sqlite_kv_set("total_uploaded_stats", total_uploaded_stats)
        sqlite_kv_set("total_assigned_stats", total_assigned_stats)
        sqlite_kv_set("recent_traffic", recent_traffic)
        sqlite_kv_set("stex_assigned_numbers", stex_assigned_numbers)
        sqlite_kv_set("voltx_assigned_numbers", voltx_assigned_numbers)
        sqlite_kv_set("assigned_number_meta", assigned_number_meta)
    except Exception as e:
        print(f"⚠️  save_local_db (sqlite): {type(e).__name__}")


def _sync_fs():
    if not db:
        return
    try:
        payload = {k: bot_settings[k] for k in FS_KEYS if k in bot_settings}
        db.collection('settings').document('bot_config').set(payload, merge=True, timeout=8.0)
    except Exception as e:
        print(f"⚠️  Firestore sync failed: {type(e).__name__}")


def save_db():
    save_local_db()
    _persist_all_settings_to_sqlite()
    if db:
        threading.Thread(target=_sync_fs, daemon=True).start()


def _bg_load_db():
    try:
        load_db()
        print("✅ load_db() completed in background.")
    except Exception as e:
        print(f"⚠️  load_db() crashed: {type(e).__name__}: {e}")


threading.Thread(target=_bg_load_db, daemon=True).start()
print("🚀 load_db() started in background - bot starting now.")

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}
pending_search_prompts = {}

tg_session = requests.Session()


def _strip_premium(text):
    return re.sub(r'<tg-emoji[^>]*>([^<]*)</tg-emoji>', r'\1', str(text))


def _strip_all_html(text):
    return re.sub(r'<[^>]+>', '', str(text))


def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    try:
        res = tg_session.post(url, json=payload, timeout=15)
        return res.json()
    except Exception:
        return {}


def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    res = api_call("sendMessage", payload)
    if res and not res.get("ok"):
        err = str(res.get("description", "")).lower()
        if "entity" in err or "parse" in err or "emoji" in err or "unsupported" in err:
            payload["text"] = _strip_premium(text)
            res = api_call("sendMessage", payload)
            if res and not res.get("ok"):
                payload["text"] = _strip_all_html(text)
                payload.pop("parse_mode", None)
                res = api_call("sendMessage", payload)
    return res


def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "photo": photo_url_or_file_id, "caption": caption, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendPhoto", payload)


def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    res = api_call("editMessageText", payload)
    if res and not res.get("ok"):
        err = str(res.get("description", "")).lower()
        if "entity" in err or "parse" in err or "emoji" in err or "unsupported" in err:
            payload["text"] = _strip_premium(text)
            res = api_call("editMessageText", payload)
            if res and not res.get("ok"):
                payload["text"] = _strip_all_html(text)
                payload.pop("parse_mode", None)
                res = api_call("editMessageText", payload)
    return res


def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})


def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})


def send_document(chat_id, filename, text_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, text_content)}
    data = {'chat_id': chat_id}
    try: requests.post(url, data=data, files=files)
    except: pass


def send_document_bytes(chat_id, filename, bytes_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, bytes_content)}
    data = {'chat_id': chat_id}
    try: return requests.post(url, data=data, files=files).json()
    except: return {}


all_known_users = set()


def sync_users_list():
    global all_known_users
    try:
        ul = sqlite_kv_get("all_known_users")
        if isinstance(ul, list) and ul:
            all_known_users.update(str(x) for x in ul)
        if os.path.exists(USERS_LIST_FILE):
            try:
                with open(USERS_LIST_FILE, "r") as f:
                    all_known_users.update(str(x) for x in json.load(f))
            except Exception as _fe:
                print(f"⚠️  users_list.json read: {type(_fe).__name__}")
        if not all_known_users and db:
            try:
                for doc in db.collection('users').select([]).stream():
                    all_known_users.add(str(doc.id))
            except Exception as _fse:
                print(f"⚠️  Firestore user-list read: {type(_fse).__name__}")
        if all_known_users:
            try:
                with open(USERS_LIST_FILE, "w") as f:
                    json.dump(list(all_known_users), f)
            except Exception: pass
            sqlite_kv_set("all_known_users", list(all_known_users))
    except Exception as e:
        print(f"⚠️  sync_users_list: {type(e).__name__}")


threading.Thread(target=sync_users_list, daemon=True).start()


def _save_users_list():
    try:
        with open(USERS_LIST_FILE, "w") as f:
            json.dump(list(all_known_users), f)
    except Exception: pass
    try:
        sqlite_kv_set("all_known_users", list(all_known_users))
    except Exception: pass


def register_user_local(uid):
    uid_str = str(uid)
    if uid_str not in all_known_users:
        all_known_users.add(uid_str)
        threading.Thread(target=_save_users_list, daemon=True).start()


def broadcast_copymessage(from_chat_id, msg_id):
    success = 0; failed = 0; last_err = ""
    users = list(all_known_users)
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): success += 1
            else:
                failed += 1
                last_err = str(res.get("description", "?"))[:80]
        except Exception as e:
            failed += 1; last_err = str(e)[:80]
        time.sleep(0.035)
    send_message(from_chat_id, render_body_text(f"📢 <b>Broadcast Completed!</b>\n✅ Success: {success}\n❌ Failed: {failed}\n👥 Total Sent: {len(users)}\n⚠️ Last Error: {last_err}"))


def broadcast_text_all(txt, kb=None):
    users = list(all_known_users)
    b_session = requests.Session()
    url = f"{BASE_URL}/sendMessage"
    ok = 0; fail = 0
    for u_id in users:
        try:
            payload = {"chat_id": u_id, "text": txt, "parse_mode": "HTML", "disable_web_page_preview": True}
            if kb: payload["reply_markup"] = kb
            r = b_session.post(url, json=payload, timeout=5).json()
            if r.get("ok"): ok += 1
            else: fail += 1
        except: fail += 1
        time.sleep(0.035)
    return ok, fail


def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)


def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities: return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception:
        return text


def get_flag_info_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data["char"], data.get("iso", "XX"), data.get("id")
    return "🌍", "XX", None


def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso


def get_flag_info_html(num_or_iso):
    s = str(num_or_iso).strip()
    s_up = s.upper()

    if len(s) == 2:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso", "").upper() == s_up:
                eid = data.get("id")
                char = data.get("char")
                if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        return "🌍"

    for code, data in bot_settings.get("premium_flags", {}).items():
        if data.get("name", "").upper() == s_up:
            eid = data.get("id")
            char = data.get("char")
            if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            return char

    resolved_iso = ""
    try:
        for b in number_batches.values():
            if b.get("country", "").upper() == s_up:
                ri = b.get("country_iso", "")
                if ri:
                    resolved_iso = ri.upper()
                    break
    except: pass

    if not resolved_iso:
        for cname, cinfo in COUNTRIES_DATA.items():
            if cname.upper() == s_up:
                resolved_iso = cinfo.get("iso", "").upper()
                break
    if not resolved_iso:
        for ccode, cinfo in COUNTRY_DB.items():
            if cinfo["name"].upper() == s_up:
                resolved_iso = cinfo["iso"].upper()
                break

    if resolved_iso:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso", "").upper() == resolved_iso:
                eid = data.get("id")
                char = data.get("char")
                if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        return get_flag_emoji(resolved_iso)

    char, _, eid = get_flag_info_from_num(s)
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char if char else "🌍"


def get_flag_emoji(iso2):
    try:
        return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in str(iso2).upper()[:2])
    except:
        return "🌍"


def _find_dial_code(clean_num):
    sorted_prem = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_prem:
        if clean_num.startswith(code):
            return code, "premium"
    sorted_db = sorted(COUNTRY_DB.keys(), key=len, reverse=True)
    for code in sorted_db:
        if clean_num.startswith(code):
            return code, "db"
    return "", "none"


def get_country_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    dial_code, src = _find_dial_code(clean)
    if src == "premium":
        data = bot_settings["premium_flags"][dial_code]
        flag_char = data["char"]
        iso = data.get("iso", "XX")
        eid = data.get("id")
        flag_html = f'<tg-emoji emoji-id="{eid}">{flag_char}</tg-emoji>' if eid else flag_char
        return flag_html, iso, dial_code
    if src == "db":
        info = COUNTRY_DB[dial_code]
        iso = info["iso"]
        flag_char = get_flag_emoji(iso)
        return flag_char, iso, dial_code
    return "🌍", "XX", ""


def mask_smart(num):
    clean = num.replace("+", "").replace(" ", "")
    dial_code, _ = _find_dial_code(clean)
    rest = clean[len(dial_code):]
    if len(rest) > 4:
        middle_len = len(rest) - 4
        last4 = rest[-4:]
        return f"{dial_code}{'x' * middle_len}{last4}"
    return f"{dial_code}{rest}" if dial_code else clean


def mask_number(num):
    return mask_smart(num)


def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))
    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part: return multi_part.group(0).replace(" ", "")
    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit(): return keyword_match.group(1)
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|কোড)', clean_text, re.I)
    if keyword_match_rev and keyword_match_rev.group(1).isdigit(): return keyword_match_rev.group(1)
    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match: return g_match.group(1)
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches: return digit_matches[0]
    return None


def parse_panel_response(response_text, p_config=None):
    results = []
    p_type = p_config.get("type", "API Panel") if p_config else "API Panel"

    if p_type == "Auto Captcha Panel":
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            tables = soup.find_all('table')
            n_col_name = p_config.get("num_col_name", "number").lower() if p_config else "number"
            m_col_name = p_config.get("msg_col_name", "message").lower() if p_config else "message"
            s_col_name = p_config.get("service_col_name", "service").lower() if p_config else "service"
            n_idx = int(p_config.get("num_col_idx", 1)) - 1 if p_config and p_config.get("num_col_idx") else 1
            m_idx = int(p_config.get("msg_col_idx", 2)) - 1 if p_config and p_config.get("msg_col_idx") else 2
            s_idx = int(p_config.get("service_col_idx", 3)) - 1 if p_config and p_config.get("service_col_idx") else 3
            for table in tables:
                rows = table.find_all('tr')
                if not rows: continue
                final_n_idx = n_idx; final_m_idx = m_idx; final_s_idx = s_idx
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(strip=True).lower()
                    if n_col_name in c_text: final_n_idx = i
                    if m_col_name in c_text: final_m_idx = i
                    if s_col_name in c_text: final_s_idx = i
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if all(c.name == 'th' for c in cols): continue
                    if len(cols) > max(final_n_idx, final_m_idx):
                        num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                        msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                        svc_text = cols[final_s_idx].get_text(separator=" ", strip=True) if len(cols) > final_s_idx else ""
                        clean_num = re.sub(r'\D', '', num_text)
                        if clean_num and 5 <= len(clean_num) <= 18:
                            otp = extract_otp_code(msg_text)
                            if not otp: otp = "N/A"
                            if len(msg_text) > 4:
                                results.append({"number": clean_num, "message": msg_text, "otp": otp, "service_name": svc_text.strip()})
        except Exception: pass
        return results

    try:
        data = json.loads(response_text)
    except Exception:
        return results

    if p_config:
        try:
            path_results = _extract_by_paths(data, p_config)
            if path_results:
                return path_results
        except Exception: pass

    temp_results = []

    def process_item(item):
        pot_nums_list = []; pot_msg = None; pot_svc = ""
        values = []
        if isinstance(item, dict):
            lower_keys = {str(k).lower(): v for k, v in item.items()}
            for k in ["number", "num", "phone", "msisdn", "sender"]:
                if k in lower_keys:
                    clean_val = re.sub(r'\D', '', str(lower_keys[k]))
                    if 5 <= len(clean_val) <= 18 and clean_val not in pot_nums_list:
                        pot_nums_list.append(clean_val)
            for k in ["service", "app", "application", "type", "site"]:
                if k in lower_keys:
                    pot_svc = str(lower_keys[k]).strip(); break
            for k in ["message", "msg", "sms", "content", "text"]:
                if k in lower_keys:
                    val = str(lower_keys[k])
                    if len(val) > 4:
                        pot_msg = val; break
            values = list(item.values())
        elif isinstance(item, list):
            values = item

        for v in values:
            if isinstance(v, (dict, list)) or v is None: continue
            v_str = str(v).strip()
            clean_v = re.sub(r'\D', '', v_str)
            if 7 <= len(clean_v) <= 18 and not re.search(r'[a-zA-Z]', v_str):
                if not re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', v_str) and not re.search(r'\d{2}:\d{2}:\d{2}', v_str) and "." not in v_str:
                    if clean_v not in pot_nums_list: pot_nums_list.append(clean_v)
            if len(v_str) > 4 and not v_str.isdigit():
                if extract_otp_code(v_str):
                    if pot_msg is None or len(v_str) > len(pot_msg): pot_msg = v_str

        pot_num = None
        if pot_nums_list:
            matched_user_num = None
            for n in pot_nums_list:
                if n in stex_assigned_numbers or any(n in str(key) for key in stex_assigned_numbers.keys()):
                    matched_user_num = n; break
            if matched_user_num: pot_num = matched_user_num
            elif len(pot_nums_list) >= 2: pot_num = pot_nums_list[1]
            else: pot_num = pot_nums_list[0]
        if pot_num and pot_msg:
            otp = extract_otp_code(pot_msg)
            if not otp: otp = "N/A"
            temp_results.append({"number": pot_num, "message": pot_msg, "otp": otp, "service_name": pot_svc})

    def traverse_json(node):
        if isinstance(node, list):
            if len(node) > 0 and not isinstance(node[0], (dict, list)):
                process_item(node)
            for child in node:
                if isinstance(child, (dict, list)): traverse_json(child)
        elif isinstance(node, dict):
            process_item(node)
            for val in node.values():
                if isinstance(val, (dict, list)): traverse_json(val)

    traverse_json(data)
    seen = set()
    for r in temp_results:
        uid = f"{r['number']}_{r['otp']}"
        if uid not in seen:
            seen.add(uid); results.append(r)
    return results


def attempt_auto_login(p, idx):
    login_url = p.get("login_url", "").strip()
    if not login_url.startswith("http"):
        login_url = "http://" + login_url
    if not login_url.lower().endswith('/login') and not login_url.lower().endswith('.php'):
        login_url = f"{login_url.rstrip('/')}/login"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    try:
        res = session.get(login_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        all_text = res.text
        captcha_match = re.search(r'(\d+\s*[\+\-\*]\s*\d+)\s*[=\?:]', all_text)
        if not captcha_match:
            captcha_match = re.search(r'what is\s*(\d+\s*[\+\-\*]\s*\d+)', all_text, re.I)
        if not captcha_match:
            elements = soup.find_all(["label", "div", "span", "p", "strong"])
            for el in elements:
                txt = el.get_text(separator=" ", strip=True)
                if any(op in txt for op in ["+", "-", "*"]):
                    m = re.search(r'(\d+\s*[\+\-\*]\s*\d+)', txt)
                    if m:
                        captcha_match = m; break
        captcha_text = captcha_match.group(1) if captcha_match else "0 + 0"
        answer = "0"
        m2 = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', captcha_text)
        if m2:
            a, op, b = int(m2.group(1)), m2.group(2), int(m2.group(3))
            if op == '+': answer = str(a + b)
            elif op == '-': answer = str(a - b)
            elif op == '*': answer = str(a * b)

        form = soup.find("form")
        if not form:
            p["login_status"] = "❌ No login form found"
            return False
        action = form.get("action")
        post_url = urljoin(login_url, action) if action else login_url

        form_data = {}
        for hidden in form.find_all("input", type="hidden"):
            name = hidden.get("name")
            if name: form_data[name] = hidden.get("value") or ""

        user_input = form.find("input", {"name": re.compile(r"user|email|id", re.I)}) or \
                     form.find("input", {"type": "text", "placeholder": re.compile(r"user|email", re.I)}) or \
                     form.find("input", {"type": "text"})
        pass_input = form.find("input", {"name": re.compile(r"pass", re.I)}) or \
                     form.find("input", {"type": "password"})
        captcha_input = form.find("input", {"placeholder": re.compile(r"answer|ans|code|verification|value|captcha", re.I)}) or \
                        form.find("input", {"name": re.compile(r"ans|captcha|ver|code", re.I)})

        user_field = user_input.get("name") if user_input else "username"
        pass_field = pass_input.get("name") if pass_input else "password"
        captcha_field = captcha_input.get("name") if captcha_input else "answer"

        form_data[user_field] = p.get("username", "")
        form_data[pass_field] = p.get("password", "")
        if captcha_field:
            form_data[captcha_field] = answer

        login_req = session.post(post_url, data=form_data, allow_redirects=True, timeout=15)

        msg_link = p.get("msg_link", "").strip()
        if not msg_link.startswith("http") and msg_link != "":
            msg_link = "http://" + msg_link
        check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
        check_res = session.get(check_url, timeout=10)

        if 'logout' in login_req.text.lower() or 'logout' in check_res.text.lower() or 'sms reports' in check_res.text.lower() or 'dashboard' in check_res.text.lower() or 'cdrs' in check_res.text.lower():
            panel_sessions[idx] = session
            p["login_status"] = "✅ Active & Fetching"
            return True
        else:
            p["login_status"] = f"❌ Login Failed (Math: {captcha_text} = {answer})"
            return False
    except Exception as e:
        p["login_status"] = f"❌ Error: {str(e)[:20]}"
    return False


# ==========================================
# User Cache / Balance / OTP Credit
# ==========================================
user_cache = {}


def _sqlite_user_exists(user_id):
    row = sqlite_exec("SELECT user_id FROM users WHERE user_id=?", (int(user_id),), fetch="one")
    return row is not None


def _sqlite_ensure_user(user_id):
    uid = int(user_id)
    try:
        with sqlite_tx() as conn:
            if conn is None:
                return False
            cur = conn.cursor()
            now = time.time()
            cur.execute(
                "INSERT OR IGNORE INTO users(user_id, balance, total_refers, total_otps, banned, verified, created_at, updated_at) "
                "VALUES(?, 0.0, 0, 0, 0, 0, ?, ?)",
                (uid, now, now),
            )
        return True
    except Exception as e:
        print(f"⚠️  _sqlite_ensure_user: {type(e).__name__}")
        return False


def get_user(user_id):
    if user_id in user_cache:
        return user_cache[user_id]

    row = sqlite_exec(
        "SELECT user_id,balance,total_refers,total_otps,banned,verified,referred_by,ref_paid "
        "FROM users WHERE user_id=?", (int(user_id),), fetch="one"
    )
    if row:
        data = {
            "user_id": int(row["user_id"]),
            "balance": float(row.get("balance") or 0.0),
            "total_refers": int(row.get("total_refers") or 0),
            "total_otps": int(row.get("total_otps") or 0),
            "banned": bool(row.get("banned") or 0),
            "verified": bool(row.get("verified") or 0),
        }
        if row.get("referred_by"):
            data["referred_by"] = int(row["referred_by"])
        user_cache[int(user_id)] = data
        return data

    if db:
        try:
            doc_ref = db.collection('users').document(str(user_id))
            doc = doc_ref.get(timeout=5.0)
            if doc.exists:
                data = doc.to_dict() or {}
                data.setdefault("user_id", int(user_id))
                data.setdefault("balance", 0.0)
                data.setdefault("total_refers", 0)
                data.setdefault("total_otps", 0)
                data.setdefault("banned", False)
                data.setdefault("verified", False)
                user_cache[int(user_id)] = data
                _sqlite_ensure_user(user_id)
                try:
                    with sqlite_tx() as conn:
                        if conn:
                            conn.cursor().execute(
                                "UPDATE users SET balance=?, total_refers=?, total_otps=?, banned=?, verified=?, "
                                "referred_by=?, ref_paid=?, updated_at=? WHERE user_id=?",
                                (float(data.get("balance", 0.0)),
                                 int(data.get("total_refers", 0)),
                                 int(data.get("total_otps", 0)),
                                 1 if data.get("banned") else 0,
                                 1 if data.get("verified") else 0,
                                 int(data["referred_by"]) if data.get("referred_by") else None,
                                 1 if data.get("ref_paid") else 0,
                                 time.time(), int(user_id))
                            )
                except Exception:
                    pass
                return data
        except Exception as e:
            print(f"⚠️  get_user Firebase read ({user_id}): {type(e).__name__}")

    new_user = {"user_id": int(user_id), "balance": 0.0, "total_refers": 0,
                "total_otps": 0, "banned": False, "verified": False}
    user_cache[int(user_id)] = new_user
    _sqlite_ensure_user(user_id)
    if db:
        try:
            db.collection('users').document(str(user_id)).set(new_user, merge=True, timeout=5.0)
        except Exception as e:
            print(f"⚠️  get_user Firestore create ({user_id}): {type(e).__name__}")
    return new_user


def update_balance(user_id, amount):
    uid = int(user_id)
    amt = float(amount)

    try:
        _sqlite_ensure_user(uid)
        with sqlite_tx() as conn:
            if conn:
                conn.cursor().execute(
                    "UPDATE users SET balance = COALESCE(balance,0) + ?, updated_at=? WHERE user_id=?",
                    (amt, time.time(), uid)
                )
    except Exception as e:
        print(f"⚠️  update_balance SQLite ({uid}): {type(e).__name__}")

    if uid not in user_cache:
        get_user(uid)
    if uid in user_cache:
        user_cache[uid]["balance"] = float(user_cache[uid].get("balance", 0.0)) + amt

    if db:
        try:
            db.collection('users').document(str(uid)).set(
                {"user_id": uid, "balance": firestore.Increment(amt)},
                merge=True, timeout=5.0
            )
        except Exception as e:
            print(f"⚠️  update_balance Firestore ({uid}): {type(e).__name__}")


def credit_otp_to_user(owner_id, reward, app_full_name=""):
    try:
        reward = float(reward)
    except Exception:
        reward = 0.0
    uid = int(owner_id)

    try:
        _sqlite_ensure_user(uid)
        with sqlite_tx() as conn:
            if conn:
                conn.cursor().execute(
                    "UPDATE users SET balance = COALESCE(balance,0) + ?, "
                    "total_otps = COALESCE(total_otps,0) + 1, updated_at=? WHERE user_id=?",
                    (reward, time.time(), uid)
                )
    except Exception as e:
        print(f"⚠️  credit_otp_to_user SQLite ({uid}): {type(e).__name__}")

    if uid not in user_cache:
        get_user(uid)
    if uid in user_cache:
        user_cache[uid]["balance"] = float(user_cache[uid].get("balance", 0.0)) + reward
        user_cache[uid]["total_otps"] = int(user_cache[uid].get("total_otps", 0)) + 1

    if db:
        try:
            db.collection('users').document(str(uid)).set({
                "user_id": uid,
                "balance": firestore.Increment(reward),
                "total_otps": firestore.Increment(1)
            }, merge=True, timeout=5.0)
        except Exception as e:
            print(f"⚠️  credit_otp_to_user Firestore ({uid}): {type(e).__name__}")

    return reward


# ==========================================
# 🎁 REFERRAL SYSTEM
# ==========================================
def process_referral_for_user(new_user_id, inviter_id):
    try:
        nuid = int(new_user_id)
        iid = int(inviter_id)
        if nuid == iid:
            return False
        row = sqlite_exec("SELECT user_id FROM referral_paid_users WHERE user_id=?", (nuid,), fetch="one")
        if row:
            return False
        row2 = sqlite_exec("SELECT inviter_id FROM pending_referrals WHERE new_user_id=?", (nuid,), fetch="one")
        if row2 and int(row2["inviter_id"]) == iid:
            return False
        if row2:
            return False
        with sqlite_tx() as conn:
            if conn is None:
                return False
            conn.cursor().execute(
                "INSERT OR IGNORE INTO pending_referrals(new_user_id, inviter_id, created_at) VALUES(?,?,?)",
                (nuid, iid, time.time()),
            )
        try:
            _sqlite_ensure_user(nuid)
            with sqlite_tx() as conn:
                if conn:
                    conn.cursor().execute(
                        "UPDATE users SET referred_by=? WHERE user_id=? AND (referred_by IS NULL OR referred_by=0)",
                        (iid, nuid)
                    )
        except Exception:
            pass
        if db:
            try:
                db.collection('users').document(str(nuid)).set(
                    {"referred_by": iid, "ref_paid": False}, merge=True, timeout=5.0
                )
            except Exception as e:
                print(f"⚠️  process_referral Firestore ({nuid}): {type(e).__name__}")
        return True
    except Exception as e:
        print(f"⚠️  process_referral_for_user: {type(e).__name__}")
        return False


def check_and_pay_referral_for_user(new_user_id):
    try:
        nuid = int(new_user_id)
        paid = sqlite_exec("SELECT user_id FROM referral_paid_users WHERE user_id=?", (nuid,), fetch="one")
        if paid:
            return False
        pend = sqlite_exec("SELECT inviter_id FROM pending_referrals WHERE new_user_id=?", (nuid,), fetch="one")
        if not pend:
            return False
        iid = int(pend["inviter_id"])
        reward = float(bot_settings.get("refer_reward", 0.2))

        try:
            _sqlite_ensure_user(iid)
            with sqlite_tx() as conn:
                if conn is None:
                    return False
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR IGNORE INTO referral_paid_users(user_id, paid_at) VALUES(?,?)",
                    (nuid, time.time())
                )
                if cur.rowcount == 0:
                    return False
                cur.execute(
                    "UPDATE users SET balance = COALESCE(balance,0) + ?, "
                    "total_refers = COALESCE(total_refers,0) + 1, updated_at=? WHERE user_id=?",
                    (reward, time.time(), iid)
                )
                cur.execute(
                    "UPDATE users SET ref_paid=1 WHERE user_id=?", (nuid,)
                )
                cur.execute("DELETE FROM pending_referrals WHERE new_user_id=?", (nuid,))
        except Exception as e:
            print(f"⚠️  check_and_pay_referral SQLite: {type(e).__name__}")
            return False

        if iid not in user_cache:
            get_user(iid)
        if iid in user_cache:
            user_cache[iid]["balance"] = float(user_cache[iid].get("balance", 0.0)) + reward
            user_cache[iid]["total_refers"] = int(user_cache[iid].get("total_refers", 0)) + 1

        if db:
            try:
                db.collection('users').document(str(iid)).set({
                    "user_id": iid,
                    "balance": firestore.Increment(reward),
                    "total_refers": firestore.Increment(1)
                }, merge=True, timeout=5.0)
                db.collection('users').document(str(nuid)).set(
                    {"ref_paid": True}, merge=True, timeout=5.0
                )
            except Exception as e:
                print(f"⚠️  check_and_pay_referral Firestore: {type(e).__name__}")

        ref_msg = (
            f"{PEM['gift']} <b>New Referral !</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔥 <b>You Received ${fmt_payout(reward)}</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{PEM['user']} <b>From User ID:</b> <code>{nuid}</code>"
        )
        send_message(iid, render_body_text(ref_msg))
        return True
    except Exception as e:
        print(f"⚠️  check_and_pay_referral_for_user: {type(e).__name__}")
        return False


def add_referral(inviter_id, new_user_id):
    process_referral_for_user(new_user_id, inviter_id)
    return check_and_pay_referral_for_user(new_user_id)


# ==========================================
# Payout Lookup — 9 Layer Fallback
# ==========================================
def get_payout_for_number(clean_api_num, service_hint=""):
    reward = float(bot_settings.get("otp_reward", 0.0))
    meta = assigned_number_meta.get(clean_api_num, {})

    if "payout" in meta:
        try:
            return float(meta["payout"])
        except: pass

    oc = str(meta.get("country", "") or "").strip()
    osvc = str(meta.get("service", "") or service_hint or "").strip()
    meta_iso = str(meta.get("iso", "") or "").strip().upper()
    pr = bot_settings.get("otp_pair_rates", {})

    if oc and osvc:
        key = f"{oc.upper()}|{osvc.upper()}"
        if key in pr:
            try: return float(pr[key])
            except: pass

    if meta_iso:
        for k, v in pr.items():
            try:
                kc, ks = k.split("|", 1)
                if kc.upper() == meta_iso:
                    if osvc and ks.upper() != osvc.upper(): continue
                    return float(v)
            except: continue

    if meta_iso:
        for k, v in pr.items():
            try:
                kc, ks = k.split("|", 1)
                if kc.upper() == meta_iso: return float(v)
            except: continue

    if oc:
        for k, v in pr.items():
            try:
                kc, ks = k.split("|", 1)
                if kc.upper() == oc.upper():
                    if osvc and ks.upper() != osvc.upper(): continue
                    return float(v)
            except: continue

    if oc:
        for k, v in pr.items():
            try:
                if k.split("|")[0].upper() == oc.upper(): return float(v)
            except: continue

    try:
        _, iso_det, _ = get_country_from_num(clean_api_num)
        if iso_det and iso_det != "XX":
            iso_det = iso_det.upper()
            detected_name = None
            for _c, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso", "").upper() == iso_det:
                    detected_name = fdata.get("name", ""); break
            if not detected_name:
                for _c, cinfo in COUNTRY_DB.items():
                    if cinfo["iso"].upper() == iso_det:
                        detected_name = cinfo["name"]; break

            for k, v in pr.items():
                try:
                    kc, ks = k.split("|", 1)
                    if kc.upper() == iso_det:
                        if osvc and ks.upper() != osvc.upper(): continue
                        return float(v)
                except: continue

            if detected_name:
                for k, v in pr.items():
                    try:
                        kc, ks = k.split("|", 1)
                        if kc.upper() == detected_name.upper():
                            if osvc and ks.upper() != osvc.upper(): continue
                            return float(v)
                    except: continue
                for k, v in pr.items():
                    try:
                        if k.split("|")[0].upper() == detected_name.upper(): return float(v)
                    except: continue
    except: pass

    return reward


# ==========================================
# Withdrawal Method Emoji Helpers
# ==========================================
def get_wmethod_emoji_html(method_name):
    for m in bot_settings.get("w_methods", []):
        if isinstance(m, dict):
            if m.get("name", "").lower() == method_name.lower():
                eid = m.get("emoji_id", "")
                char = m.get("char", "🔘")
                if eid and str(eid).isdigit() and len(str(eid)) >= 10:
                    return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return f'<tg-emoji emoji-id="{WITHDRAW_SELECT_EMOJI}">🔘</tg-emoji>'


def get_wmethod_display_list():
    out = []
    for m in bot_settings.get("w_methods", []):
        if isinstance(m, dict):
            name = m.get("name", "")
            eid = m.get("emoji_id", "")
            char = m.get("char", "🔘")
            if eid and str(eid).isdigit() and len(str(eid)) >= 10:
                emoji_html = f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                icon_id = eid
            else:
                emoji_html = f'<tg-emoji emoji-id="{WITHDRAW_SELECT_EMOJI}">🔘</tg-emoji>'
                icon_id = WITHDRAW_SELECT_EMOJI
            out.append((name, emoji_html, icon_id))
        else:
            out.append((str(m), f'<tg-emoji emoji-id="{WITHDRAW_SELECT_EMOJI}">🔘</tg-emoji>', WITHDRAW_SELECT_EMOJI))
    return out


# ==========================================
# Group OTP Display Formatter
# 🇳🇬NG | 📱 | +2348🔹334 | ✉️English
# ==========================================
def format_otp_display(num, app_full_name, lang, masked=True):
    clean = str(num).lstrip('+').replace(" ", "")
    flag_html, iso, dial_code = get_country_from_num(num)

    svc_app = get_premium_app(app_full_name)
    svc_id = svc_app.get("id", "")
    svc_char = svc_app.get("emoji", "📱")
    if re.match(r'^[A-Za-z0-9#]{1,4}$', str(svc_char)):
        svc_char = "📱"
    if svc_id and str(svc_id).isdigit() and len(str(svc_id)) >= 10:
        svc_html = f'<tg-emoji emoji-id="{svc_id}">{svc_char}</tg-emoji>'
    else:
        svc_html = svc_char

    if masked:
        first4 = clean[:4] if len(clean) >= 4 else clean
        last3 = clean[-3:] if len(clean) >= 3 else clean
        num_part = f'+<b>{first4}</b><tg-emoji emoji-id="{HIDDEN_EMOJI}">🔹</tg-emoji><b>{last3}</b>'
    else:
        num_part = f'+<b>{clean}</b>'

    lang_display = lang_full(lang)

    return (
        f"{flag_html}<b>{iso}</b> | "
        f"{svc_html} | "
        f"{num_part} | "
        f'<tg-emoji emoji-id="{MESSAGE_EMOJI}">✉️</tg-emoji><b>{lang_display}</b>'
    )


# ==========================================
# Deliver OTP to user DM
# ==========================================
def deliver_to_inbox(user_id, service_name, raw_number, msg_text, current_balance, reward, lang):
    app = get_premium_app(service_name)
    sid = app.get("id", "")
    svc_char = app.get("emoji", "📱")
    if re.match(r'^[A-Za-z0-9#]{1,4}$', str(svc_char)):
        svc_char = "📱"
    if sid and str(sid).isdigit() and len(str(sid)) >= 10:
        set_html = f'<tg-emoji emoji-id="{sid}">{svc_char}</tg-emoji>'
    else:
        set_html = svc_char
    snu = app.get("name", service_name).upper()
    clean_number = str(raw_number).lstrip('+')
    flag_html, iso, _ = get_country_from_num(raw_number)
    reward_str = fmt_payout(reward)
    amount_display = f"${reward_str}"
    otp = extract_otp_code(msg_text)
    if not otp:
        otp = "N/A"
    dollar_tag = ""
    if TAKA_EMOJI and str(TAKA_EMOJI).isdigit() and len(str(TAKA_EMOJI)) >= 10:
        dollar_tag = f'<tg-emoji emoji-id="{TAKA_EMOJI}">💵</tg-emoji>'
    text = (
        f"{set_html} <b>{snu}</b>\n"
        f" ┃  {dollar_tag} <b>+ {amount_display}</b>\n"
        f" ┗━➢ {flag_html} <b>+{clean_number}</b>\n\n"
    )
    btn = {"text": otp, "copy_text": {"text": otp}, "style": "success",
           "icon_custom_emoji_id": COPY_EMOJI}
    return text, {"inline_keyboard": [[btn]]}


# ==========================================
# Broadcast Stock builder
# ==========================================
def build_stock_broadcast_new(country_display, service_name, count, per_otp,
                               flag_html=None, app_emoji_html=None):
    if not flag_html:
        flag_html = get_flag_info_html(country_display)
    if not app_emoji_html:
        _, app_emoji_html = get_service_info_html(service_name)

    HP = f'<tg-emoji emoji-id="{BROADCAST_HEADER_PRE}">📢</tg-emoji>'
    HS = f'<tg-emoji emoji-id="{BROADCAST_HEADER_SUF}">✨</tg-emoji>'
    TE = f'<tg-emoji emoji-id="{BROADCAST_TOTAL_EMOJI}">📊</tg-emoji>'
    MP = f'<tg-emoji emoji-id="{BROADCAST_MONEY_PRE}">💰</tg-emoji>'
    MS = f'<tg-emoji emoji-id="{BROADCAST_MONEY_SUF}">💰</tg-emoji>'

    payout_str = f"${fmt_payout(per_otp)}"

    text = (
        f"{HP} <b>New Stock Added</b> {HS}\n\n"
        f"{flag_html} <b>{country_display.upper()} | {service_name.upper()}</b> {app_emoji_html}\n"
        f"{TE} <b>TOTAL'S : {count} Numbers</b>\n"
        f"{MP} <b>{payout_str}/OTP</b> {MS}"
    )
    cb_data = f"g_bs|{service_name.upper()}|{country_display.upper()}"
    kb = {"inline_keyboard": [[{
        "text": "Get Numbers",
        "icon_custom_emoji_id": BROADCAST_BTN_EMOJI,
        "callback_data": cb_data,
        "style": "success"
    }]]}
    return text, kb


# ==========================================
# build_numbers_header — 10 braille blanks indent
# ==========================================
def build_numbers_header(country, service=None):
    HEADER_EMOJI_1 = "6282641460093260838"
    HEADER_EMOJI_2 = "6267315814190290529"
    PHONE_END_ICON = "5197474438970363734"
    MONEY_ICON     = "5190576863226933563"
    ROCK_ICON      = "6267152480878990865"

    flag_html = get_flag_info_html(country)

    payout_val = float(bot_settings.get("otp_reward", 0.0))
    pr = bot_settings.get("otp_pair_rates", {})
    if service:
        key = f"{str(country).upper()}|{str(service).upper()}"
        if key in pr:
            try: payout_val = float(pr[key])
            except: pass
        else:
            for k, v in pr.items():
                try:
                    if k.split("|")[0] == str(country).upper():
                        payout_val = float(v); break
                except: pass

    payout_str = fmt_payout(payout_val)

    money_icon = f'<tg-emoji emoji-id="{MONEY_ICON}">💷</tg-emoji>'
    rock_icon  = f'<tg-emoji emoji-id="{ROCK_ICON}">🪨</tg-emoji>'
    gear_icon  = f'<tg-emoji emoji-id="{HEADER_EMOJI_1}">⚙️</tg-emoji>'
    phone_icon_2 = f'<tg-emoji emoji-id="{HEADER_EMOJI_2}">📱</tg-emoji>'
    phone_icon_end = f'<tg-emoji emoji-id="{PHONE_END_ICON}">☎️</tg-emoji>'

    country_display = html.escape(str(country).upper())

    indent = "⠀⠀⠀⠀"   # 10 braille blanks

    header = (
        f"{indent}{money_icon}<b>{payout_str}$/OTP</b>{rock_icon}\n"
        f"\n"
        f"{gear_icon}<b>THIS IS YOUR</b>{phone_icon_2}<b>{country_display}</b>"
        f"{flag_html}<b>NUMBERS</b>{phone_icon_end}"
    )
    return render_body_text(header)


# ==========================================
# Service Keyword Database
# ==========================================
SERVICE_SMS_KEYWORDS = {
    "whatsapp": ["whatsapp", "wa", "wap", "w/a", "whatsapp business", "wa.me", "wa code", "wh"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code"],
    "snapchat": ["snapchat", "snap", "snap code"],
    "twitter": ["twitter", "x.com", "x code", "twitter code"],
    "discord": ["discord", "discord code"],
    "viber": ["viber", "viber code"],
    "line": ["line", "line code", "line verification"],
    "wechat": ["wechat", "we chat", "wechat code"],
    "signal": ["signal", "signal code"],
    "linkedin": ["linkedin", "linked in"],
    "imo": ["imo", "imo code", "imo verification"],
    "kakaotalk": ["kakao", "kakaotalk"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],
    "google": ["google", "gmail", "youtube", "g-", "google voice"],
    "microsoft": ["microsoft", "ms", "outlook", "live.com", "hotmail"],
    "apple": ["apple", "icloud", "itunes", "apple id"],
    "yahoo": ["yahoo", "yahoo code", "ymail"],
    "protonmail": ["proton", "protonmail"],
    "binance": ["binance", "bnb", "binances"],
    "coinbase": ["coinbase"],
    "okx": ["okx", "okex"],
    "kucoin": ["kucoin"],
    "bybit": ["bybit"],
    "huobi": ["huobi", "htx"],
    "mexc": ["mexc"],
    "trustwallet": ["trust wallet", "trustwallet"],
    "bkash": ["bkash", "b-kash", "bkash code"],
    "nagad": ["nagad", "nagad code"],
    "rocket": ["rocket", "dutch bangla"],
    "upay": ["upay", "upay code"],
    "paypal": ["paypal", "pay pal"],
    "paytm": ["paytm"],
    "cashapp": ["cash app", "cashapp"],
    "wise": ["wise", "transferwise"],
    "amazon": ["amazon", "amzn", "amazon code"],
    "ebay": ["ebay"],
    "aliexpress": ["aliexpress", "ali express"],
    "alibaba": ["alibaba"],
    "daraz": ["daraz", "daraz code"],
    "foodpanda": ["foodpanda", "food panda"],
    "uber": ["uber", "uber code", "uber verification", "uber eats"],
    "pathao": ["pathao", "pathao ride"],
    "netflix": ["netflix", "netflix code"],
    "spotify": ["spotify", "spotify code"],
    "steam": ["steam", "steam guard"],
    "epicgames": ["epic games", "epicgames"],
    "roblox": ["roblox", "roblox code"],
    "riotgames": ["riot", "riot games", "valorant", "league of legends"],
    "garena": ["garena", "free fire", "freefire"],
    "playstation": ["playstation", "psn"],
    "1xbet": ["1xbet", "1x bet"],
    "melbet": ["melbet", "melbet code"],
    "linebet": ["linebet"],
    "bet365": ["bet365"],
    "megapari": ["megapari"],
    "tinder": ["tinder", "tinder code"],
    "bumble": ["bumble"],
    "badoo": ["badoo"]
}


def detect_service(text):
    text_lower = str(text).lower()
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return service_key.upper()
    return None


def get_service_info_html(service_text, msg_text=""):
    s = str(service_text).upper().strip()
    m = str(msg_text).lower().strip()
    apps = bot_settings.get("premium_apps", {})
    detected_service = s
    if m:
        for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
            for kw in keywords:
                if kw in m:
                    detected_service = service_key.upper()
                    break
            if detected_service != s: break
    clean_s = re.sub(r'[^\w\s]', '', detected_service).strip()
    for app_name, data in apps.items():
        if app_name == detected_service or app_name == clean_s or app_name in detected_service or detected_service in app_name:
            full_name = data.get("name", app_name.title())
            char = data.get("char", "📱")
            if re.match(r'^[A-Za-z0-9#]{1,4}$', str(char)):
                char = "📱"
            eid = data.get("id")
            if eid: return full_name, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            return full_name, char
    if len(detected_service) > 20:
        return "Message", "💬"
    return detected_service.title(), "📱"


def get_premium_app(service_name):
    if not service_name: service_name = "Other"
    apps = bot_settings.get("premium_apps", {})
    ku = service_name.upper().strip()
    for ak, ad in apps.items():
        if ak == ku or ak in ku or ku in ak:
            char = ad.get("char", "📱")
            if re.match(r'^[A-Za-z0-9#]{1,4}$', str(char)):
                char = "📱"
            return {"name": ad.get("name", ak.title()), "emoji": char, "id": ad.get("id")}
    for sk in SERVICE_SMS_KEYWORDS.keys():
        if sk.upper() == ku or sk.upper() in ku or ku in sk.upper():
            return {"name": sk.title(), "emoji": "📱", "id": None}
    return {"name": service_name, "emoji": "📱", "id": None}


def detect_language(text):
    if not text: return "#EN"
    text_str = str(text)
    if any('\u0600' <= c <= '\u06ff' for c in text_str): return "#AR"
    if any('\u0980' <= c <= '\u09ff' for c in text_str): return "#BN"
    if any('\u0900' <= c <= '\u097f' for c in text_str): return "#HI"
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str): return "#PA"
    if any('\u0a80' <= c <= '\u0aff' for c in text_str): return "#GU"
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str): return "#OR"
    if any('\u0b80' <= c <= '\u0bff' for c in text_str): return "#TA"
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str): return "#TE"
    if any('\u0c80' <= c <= '\u0cff' for c in text_str): return "#KN"
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str): return "#ML"
    if any('\u0d80' <= c <= '\u0dff' for c in text_str): return "#SI"
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str): return "#TH"
    if any('\u0e80' <= c <= '\u0eff' for c in text_str): return "#LO"
    if any('\u0f00' <= c <= '\u0fff' for c in text_str): return "#BO"
    if any('\u1000' <= c <= '\u109f' for c in text_str): return "#MY"
    if any('\u1200' <= c <= '\u137f' for c in text_str): return "#AM"
    if any('\u1780' <= c <= '\u17ff' for c in text_str): return "#KM"
    if any('\u10a0' <= c <= '\u10ff' for c in text_str): return "#KA"
    if any('\u0530' <= c <= '\u058f' for c in text_str): return "#HY"
    if any('\u0590' <= c <= '\u05ff' for c in text_str): return "#HE"
    if any('\u0370' <= c <= '\u03ff' for c in text_str): return "#EL"
    if any('\u0400' <= c <= '\u04ff' for c in text_str): return "#RU"
    if any('\u4e00' <= c <= '\u9fff' for c in text_str): return "#ZH"
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str): return "#JA"
    if any('\uac00' <= c <= '\ud7af' for c in text_str): return "#KO"
    text_lower = text_str.lower()
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]): return "#ID"
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]): return "#MS"
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR"
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE"
    if any(w in text_lower for w in ["tu código", "verificación", "no compartas"]): return "#ES"
    if any(w in text_lower for w in ["seu código", "não compartilhe"]): return "#PT"
    return "#EN"


def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text


def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID


def check_force_join(user_id):
    if not bot_settings["fj_on"] or not bot_settings["fj_channels"]: return True
    if is_admin(user_id): return True
    for ch in bot_settings["fj_channels"]:
        res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})
        if res.get("ok") and res["result"]["status"] not in ["left", "kicked"]: continue
        else: return False
    return True


def send_force_join_msg(chat_id):
    kb = []
    for ch in bot_settings["fj_channels"]:
        url = f"https://t.me/{ch.replace('@', '')}" if ch.startswith("@") else ch
        kb.append([{"text": f"Join Channel", "icon_custom_emoji_id": "5789428375261023681", "url": url, "style": "primary"}])
    kb.append([{"text": "Check Joined", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Please join our channels to use the bot!</b>"), reply_markup={"inline_keyboard": kb})


def is_user_banned(user_id):
    if is_admin(user_id): return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 60:
        return user_banned_cache[user_id]['banned']
    banned = False
    row = sqlite_exec("SELECT banned FROM users WHERE user_id=?", (int(user_id),), fetch="one")
    if row is not None:
        banned = bool(row.get("banned") or 0)
    elif db:
        try:
            doc = db.collection('users').document(str(user_id)).get(timeout=5.0)
            banned = doc.exists and (doc.to_dict() or {}).get("banned", False)
        except Exception as e:
            print(f"⚠️  is_user_banned Firestore ({user_id}): {type(e).__name__}")
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned


def build_group_kb(otp_value, fw=None):
    kb = [[{"text": f"{otp_value}", "icon_custom_emoji_id": COPY_EMOJI,
            "copy_text": {"text": otp_value}, "style": "success"}]]
    row2 = [{"text": "𝐍𝐔𝐌𝐁𝐄𝐑", "icon_custom_emoji_id": NUMBER_BTN_EMOJI,
             "url": f"https://t.me/{BOT_USERNAME}?start=start", "style": "primary"}]
    ch_link = bot_settings.get("main_channel_link", "")
    if ch_link:
        row2.append({"text": "𝐂𝐇𝐀𝐍𝐍𝐄𝐋", "icon_custom_emoji_id": CHANNEL_EMOJI,
                     "url": ch_link, "style": "primary"})
    kb.append(row2)
    if fw:
        for btn in fw.get("buttons", []):
            b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
            if "icon_custom_emoji_id" in btn:
                b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
            kb.append([b_obj])
    return {"inline_keyboard": kb}


# ==========================================
# Withdrawal group message — "NEW WITHDRAW REUQUEST"
# ==========================================
def build_withdrawal_group_msg(chat_id, full_name, amount, number, method, req_id):
    frog_emoji = '<tg-emoji emoji-id="6307777408300753473">🐸</tg-emoji>'
    web_emoji = '<tg-emoji emoji-id="6206245785877616415">🕸️</tg-emoji>'
    user_emoji = '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>'
    balance_icon = f'<tg-emoji emoji-id="{WITHDRAW_BALANCE_EMOJI}">🔘</tg-emoji>'
    phone_emoji = '<tg-emoji emoji-id="5337132498965010628">🍏</tg-emoji>'
    method_icon = f'<tg-emoji emoji-id="{WITHDRAW_METHOD_ICON}">🥂</tg-emoji>'
    method_emoji = get_wmethod_emoji_html(method)
    amount_display = fmt_payout(amount)

    txt = (
        f"<blockquote>🎙 <b>NEW WITHDRAW REUQUEST</b>{web_emoji}</blockquote>\n"
        f"\n"
        f"{frog_emoji} <b>USER ID :</b> <code>{chat_id}</code>\n"
        f"{user_emoji} <b>User :</b> <a href='tg://user?id={chat_id}'>{full_name}</a>\n"
        f"{balance_icon} <b>BALANCE:</b> <code>${amount_display}</code>\n"
        f"{phone_emoji} <b>NUMBER :</b> <code>{number}</code>\n"
        f"{method_icon} <b>METHOD :</b> {method_emoji} <b>{method}</b>\n"
        f"\n"
        f"🧾 <b>WITHDRAW ID :</b> <code>{req_id}</code>"
    )
    return render_body_text(txt)


# ==========================================
# Withdrawal status message
# APPROVED → 🕸️  |  REJECTED → ❌
# ==========================================
def build_withdrawal_status_msg(action, u_id, full_name, amount, number, method, req_id):
    if action == "APPROVE" and len(number) >= 7:
        masked_num = f"{number[:4]}❖STR❖{number[-3:]}"
    else:
        masked_num = number

    status_word = "APPROVED" if action == "APPROVE" else "REJECTED"
    trailing_emoji = '<tg-emoji emoji-id="6206245785877616415">🕸️</tg-emoji>' if action == "APPROVE" \
                     else '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>'

    frog_emoji = '<tg-emoji emoji-id="6307777408300753473">🐸</tg-emoji>'
    user_emoji = '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>'
    balance_icon = f'<tg-emoji emoji-id="{WITHDRAW_BALANCE_EMOJI}">🔘</tg-emoji>'
    phone_emoji = '<tg-emoji emoji-id="5337132498965010628">🍏</tg-emoji>'
    method_icon = f'<tg-emoji emoji-id="{WITHDRAW_METHOD_ICON}">🥂</tg-emoji>'
    method_emoji = get_wmethod_emoji_html(method)
    amount_display = fmt_payout(amount)

    txt = (
        f"<blockquote>🎙 <b>WITHDRAW {status_word}</b> {trailing_emoji}</blockquote>\n"
        f"\n"
        f"{frog_emoji} <b>USER ID :</b> <code>{u_id}</code>\n"
        f"{user_emoji} <b>User :</b> <a href='tg://user?id={u_id}'>{full_name}</a>\n"
        f"{balance_icon} <b>BALANCE:</b> <code>${amount_display}</code>\n"
        f"{phone_emoji} <b>NUMBER :</b> <code>{masked_num}</code>\n"
        f"{method_icon} <b>METHOD :</b> {method_emoji} <b>{method}</b>\n"
        f"\n"
        f"🧾 <b>WITHDRAW ID :</b> <code>{req_id}</code>"
    )
    return render_body_text(txt)


# ==========================================
# Withdrawal BALANCE HOLD / REFUND helpers
# ==========================================
def hold_withdrawal_balance(user_id, amount):
    try:
        update_balance(user_id, -float(amount))
        return True
    except Exception as e:
        print(f"⚠️  hold_withdrawal_balance: {type(e).__name__}")
        return False


def refund_withdrawal_balance(user_id, amount):
    try:
        update_balance(user_id, float(amount))
        return True
    except Exception as e:
        print(f"⚠️  refund_withdrawal_balance: {type(e).__name__}")
        return False


# ==========================================
# Panel Monitor
# ==========================================
def panel_monitor_thread():
    global processed_otps, recent_traffic, panel_sessions
    while True:
        try:
            for idx, p in enumerate(bot_settings.get("panels", [])):
                if p.get("status") == "ON":
                    if p.get("type") == "Auto Captcha Panel":
                        sess = panel_sessions.get(idx)
                        if not sess:
                            now = time.time()
                            if now - p.get("last_login_attempt", 0) < 30:
                                continue
                            p["last_login_attempt"] = now
                            success = attempt_auto_login(p, idx)
                            save_db()
                            if not success:
                                continue
                            sess = panel_sessions.get(idx)
                        try:
                            parsed_data, res_text = fetch_cpt_panel_cdrs(p, sess, p["msg_link"])
                            p["login_status"] = "Active & Fetching"
                        except Exception as e:
                            p["login_status"] = "Session Expired (Retrying...)"
                            del panel_sessions[idx]
                            save_db()
                            continue

                    elif p.get("api_url") or p.get("curl_command"):
                        url = p.get("api_url", "").strip()
                        token = p.get("token", "").strip()
                        curl_cmd = p.get("curl_command", "").strip()
                        parsed_data = []
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

                        if curl_cmd:
                            try:
                                parsed_curl = parse_curl_command(curl_cmd)
                                curl_url = parsed_curl.get("url", "")
                                curl_method = parsed_curl.get("method", "GET")
                                curl_headers = parsed_curl.get("headers", {})
                                curl_headers.setdefault("User-Agent", headers["User-Agent"])
                                if curl_url:
                                    if curl_method.upper() == "POST":
                                        res = requests.post(curl_url, headers=curl_headers, timeout=15)
                                    else:
                                        res = requests.get(curl_url, headers=curl_headers, timeout=15)
                                    parsed_data = parse_panel_response(res.text, p)
                            except Exception as _ce:
                                print(f"CURL fetch error (panel {idx}): {_ce}")

                        if not parsed_data and url:
                            urls_to_try = []
                            if "{token}" in url or "{key}" in url:
                                urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                            elif "token=" in url or "key=" in url:
                                urls_to_try.append(url)
                            else:
                                sep = '&' if '?' in url else '?'
                                urls_to_try.append(f"{url}{sep}token={token}")
                                urls_to_try.append(f"{url}{sep}key={token}&start=0")
                                urls_to_try.append(f"{url}{sep}key={token}")
                            for try_url in urls_to_try:
                                try:
                                    res = requests.get(try_url, headers=headers, timeout=10)
                                    parsed_data = parse_panel_response(res.text, p)
                                    if parsed_data:
                                        if try_url != url and token:
                                            p["api_url"] = try_url.replace(token, "{token}")
                                            save_db()
                                        break
                                except: continue

                        if not parsed_data: continue
                    else:
                        continue

                    if p.get("type") != "Auto Captcha Panel":
                        limit = p.get("records", 0)
                        if limit > 0: parsed_data = parsed_data[:limit]

                    for item in parsed_data:
                        num = item["number"]
                        otp = item["otp"]
                        msg_text = item["message"]
                        panel_svc_name = item.get("service_name", "").strip()
                        unique_id = f"{num}_{otp}"

                        if unique_id not in processed_otps:
                            processed_otps.add(unique_id)
                            if len(processed_otps) > 5000: processed_otps.clear()

                            char, iso = get_flag_and_code(num)
                            app_full_name, prem_app_html = get_service_info_html(panel_svc_name or p.get("name", "Panel"), msg_text)
                            current_time = time.time()

                            recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                            recent_traffic.append({
                                "service": app_full_name, "iso": iso, "flag": char,
                                "number": num, "time": current_time
                            })
                            save_local_db()

                            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                            lang = detect_language(msg_text)

                            display_msg = render_body_text(format_otp_display(display_num, app_full_name, lang, masked=True))

                            for fw in bot_settings["fw_groups"]:
                                kb = build_group_kb(otp, fw)
                                send_message(fw["chat_id"], display_msg, reply_markup=kb)

                            owners = []
                            clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                            for uid, session_data in user_active_sessions.items():
                                for act_num in session_data.get("nums", []):
                                    act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                        owners.append(uid)
                                        break
                            if not owners:
                                for stex_n, n_owner in stex_assigned_numbers.items():
                                    clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                        owners.append(n_owner)

                            owners = list(set(owners))
                            for owner_id in owners:
                                reward = get_payout_for_number(clean_api_num, app_full_name)
                                credit_otp_to_user(owner_id, reward, app_full_name)
                                new_bal = user_cache.get(owner_id, {}).get("balance", 0.0)
                                it, ik = deliver_to_inbox(owner_id, app_full_name, display_num, msg_text, new_bal, reward, lang)
                                it = render_body_text(it)
                                send_message(owner_id, it, reply_markup=ik)
        except Exception:
            pass
        time.sleep(5)
        
# ==========================================
# UI Keyboards
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}


def main_menu(user_id):
    kb = [
        [
            {"text": "GET NUMBER", "icon_custom_emoji_id": "5262606754725771771", "style": "danger"},
            {"text": "SEARCH NUMBER", "icon_custom_emoji_id": "5463352748751753567", "style": "success"}
        ],
        [
            {"text": "TRAFFIC", "icon_custom_emoji_id": "5429651785352501917", "style": "success"},
            {"text": "2FA ONLINE", "icon_custom_emoji_id": "5267421176841398765", "style": "primary"}
        ],
        [
            {"text": "REFER", "icon_custom_emoji_id": "5332724926216428039", "style": "primary"},
            {"text": "BALANCE", "icon_custom_emoji_id": "5215420556089776398", "style": "danger"}
        ],
        [{"text": "SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "style": "success"}]
    ]
    if is_admin(user_id):
        kb.append([{"text": "Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}


def get_admin_text():
    users_count = len(all_known_users)
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())

    if bot_settings.get("maintenance"):
        maint_status = "🟢 RUNNING"
    else:
        maint_status = "🔴 OFF"

    yellow_icon = '<tg-emoji emoji-id="5339082633160703625">🟡</tg-emoji>'
    green_icon = '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>'
    if db and current_db_mode == "firebase":
        db_status = f"{green_icon} <b>FIREBASE ACTIVE</b>"
        db_line2 = f"{green_icon} <b>SQLITE ACTIVE</b>"
    else:
        db_status = f"{green_icon} <b>SQLITE ACTIVE</b>"
        db_line2 = f"{yellow_icon} <b>FIREBASE OFF</b>"

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free

{PEM['gear']} <b>MAINTENANCE:</b> {maint_status}
{PEM['file']} <b>DATABASE:</b> {db_status}
{PEM['file']} <b>FALLBACK:</b> {db_line2}
"""
    return render_body_text(txt)


def admin_panel_keyboard():
    maint_on = bot_settings.get("maintenance", False)
    if maint_on:
        maint_btn = {"text": "MAINTENENCE OFF", "icon_custom_emoji_id": "5318840353510408444", "callback_data": "toggle_maintenance", "style": "danger"}
    else:
        maint_btn = {"text": "MAINTENENCE ON", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "toggle_maintenance", "style": "success"}

    return {"inline_keyboard": [
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"},
         {"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "DATABASE", "icon_custom_emoji_id": "5352721946054268944", "callback_data": "database_menu", "style": "danger"}],
        [maint_btn],
        [{"text": "Used number", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "show_used", "style": "success"},
         {"text": "Unused number", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}


def database_menu_keyboard():
    return {"inline_keyboard": [
        [{"text": "DOWNLOAD DATA", "icon_custom_emoji_id": "6203886371363364022", "callback_data": "db_download", "style": "success"}],
        [{"text": "UPLOAD DATA", "icon_custom_emoji_id": "6206046503690048595", "callback_data": "db_upload", "style": "primary"}],
        [{"text": "DELETE DATA", "icon_custom_emoji_id": "6206108815075579644", "callback_data": "db_delete_confirm", "style": "danger"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}]
    ]}


def system_settings_keyboard(user_id=None):
    # ⭐ ADMIN MANAGEMENT row — owner sees it, others don't
    if user_id == OWNER_ID:
        row2 = [
            {"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
            {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}
        ]
    else:
        row2 = [
            {"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"}
        ]

    return {"inline_keyboard": [
        [{"text": "StexSMS Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_control", "style": "success"},
         {"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"}],
        row2,
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}],
        [{"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"},
         {"text": "CHANGE PAYOUT", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "change_payout_menu", "style": "success"}],
        [{"text": "STORM Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "dxa_control", "style": "primary"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}


def get_user_management_text():
    total = len(all_known_users)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)


def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}


def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"},
         {"text": "Edit Search Number", "icon_custom_emoji_id": "5190645917711114179", "callback_data": "md_edit_search_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit TRAFFIC", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "md_edit_traffic", "style": "primary"},
         {"text": "Edit Refer", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Edit WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "md_edit_withdrawal", "style": "danger"},
         {"text": "Edit SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "md_edit_support", "style": "danger"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}


def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}


def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}


def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        kb.append([{"text": f"Delete: {ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}


def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}


def otp_groups_list_keyboard():
    ch_link = bot_settings.get("main_channel_link", "")
    ch_display = ch_link if ch_link else "Not Set"
    if len(ch_display) > 32: ch_display = ch_display[:32] + "..."
    kb = [[{"text": f"Channel Link: {ch_display}", "icon_custom_emoji_id": "6204010762206189094", "callback_data": "edit_main_channel_link", "style": "success"}]]
    otp_display = bot_settings.get("otp_link", "")
    if len(otp_display) > 32: otp_display = otp_display[:32] + "..."
    kb.append([{"text": f"OTP Link: {otp_display}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}])
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}


def stex_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add StexSMS Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_stex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_stex_keys", "style": "danger"}],
        [{"text": "Manage StexSMS Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_stex_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}


def voltx_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}


def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}


def storm_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    sup_status = "ON" if bot_settings.get("support_link") else "OFF"
    grp_status = "ON" if bot_settings.get("w_group") else "OFF"
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "dxa_toggle_w", "style": "primary"}],
        [{"text": f"MIN WITHDRAW: {fmt_payout(bot_settings['min_withdraw'])}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "dxa_min_w", "style": "success"},
         {"text": f"OTP REWARD: {fmt_payout(bot_settings['otp_reward'])}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "dxa_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {fmt_payout(bot_settings['refer_reward'])}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "dxa_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "dxa_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "dxa_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "dxa_num_share", "style": "primary"}],
        [{"text": f"SUPPORT LINK: {sup_status}", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "dxa_sup_link", "style": "success"},
         {"text": "W. METHODS", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. GROUP: {grp_status}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "dxa_w_group", "style": "success"},
         {"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}


def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        if isinstance(m, dict):
            name = m.get("name", "")
            eid = m.get("emoji_id", "")
            icon = eid if (eid and str(eid).isdigit() and len(str(eid)) >= 10) else WITHDRAW_SELECT_EMOJI
        else:
            name = str(m)
            icon = WITHDRAW_SELECT_EMOJI
        kb.append([{"text": f"Delete: {name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "primary"}])
    return {"inline_keyboard": kb}


def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type: continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703"
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    add_cb = "add_api_panel" if p_type == "API Panel" else "add_cpt_panel"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5420323438508155202", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": f"list_del_{'api' if p_type=='API Panel' else 'cpt'}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}


def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    if p.get("type") == "Auto Captcha Panel":
        kb = []
        action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
        kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
        kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_cpt_panels", "style": "danger"}])
        return {"inline_keyboard": kb}
    kb = []
    action_text = "STOP POLLING" if p['status'] == 'ON' else "START POLLING"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    for label, field, emoji_id in API_PANEL_FIELDS:
        value = p.get(field, "")
        if field == "token":
            display_value = ('*' * min(len(str(value)), 15)) if value else "Not set"
        elif field == "curl_command":
            sv = str(value).replace("\n", " ")
            display_value = (sv[:30] + "...") if len(sv) > 30 else (sv if sv else "Not set")
        else:
            sv = str(value) if value is not None else ""
            display_value = (sv[:28] + "...") if len(sv) > 28 else (sv if sv else "Not set")
        kb.append([{"text": f"{label}: {display_value}", "icon_custom_emoji_id": emoji_id, "callback_data": f"api_pf|{idx}|{field}", "style": "primary"}])
    kb.append([{"text": "TEST CONNECTION", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
    kb.append([{"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_api_panels", "style": "danger"}])
    return {"inline_keyboard": kb}


def build_traffic_ui():
    global recent_traffic
    current_time = time.time()
    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
    stats = {}
    for t in recent_traffic:
        srv = t.get("service", "Unknown")
        iso = t.get("iso", "XX")
        flag = t.get("flag", "🌍")
        if srv not in stats: stats[srv] = {}
        if iso not in stats[srv]: stats[srv][iso] = {"count": 0, "flag": flag}
        stats[srv][iso]["count"] += 1
    txt = "╔═════════════════╗\n║  📈 <b>NETWORK TRAFFIC</b>\n╚═════════════════╝\n\n"
    kb = []
    if not stats:
        txt += "<i>No recent traffic found in the last hour...</i>\n"
    else:
        srv_totals = []
        for srv, countries in stats.items():
            total = sum(c["count"] for c in countries.values())
            srv_totals.append((srv, total, countries))
        srv_totals.sort(key=lambda x: x[1], reverse=True)
        for srv, total, countries in srv_totals:
            app_full_name, prem_app_html = get_service_info_html(srv)
            txt += f"[ {prem_app_html} <b>{app_full_name}</b> ]\n│\n"
            c_list = sorted(countries.items(), key=lambda x: x[1]["count"], reverse=True)[:7]
            for i, (iso, c_data) in enumerate(c_list):
                prem_flag_html = get_flag_info_html(iso)
                count = c_data["count"]
                c_name = iso
                for code, fdata in bot_settings.get("premium_flags", {}).items():
                    if fdata.get("iso") == iso: c_name = fdata.get("name", iso); break
                txt += f"├ {prem_flag_html} <b>{c_name} ({iso})</b>\n"
                txt += f"│ ╰ Success: {count}\n"
                if i < len(c_list) - 1: txt += "│\n"
            txt += "\n"
        for srv, _, _ in srv_totals:
            safe_srv = srv[:20]
            app_full_name, _ = get_service_info_html(safe_srv, safe_srv)
            kb.append([{"text": f"Explore {app_full_name} Range", "icon_custom_emoji_id": "5190645917711114179", "callback_data": f"exp_rng_{safe_srv}", "style": "success"}])
    txt = render_body_text(txt)
    kb.append([{"text": "Refresh", "icon_custom_emoji_id": "5465368548702446780", "callback_data": "refresh_traffic", "style": "primary"}])
    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
    return txt, {"inline_keyboard": kb}


def expire_previous_number(chat_id):
    if chat_id in user_active_sessions:
        prev_data = user_active_sessions[chat_id]
        prev_msg_id = prev_data["msg_id"]
        nums = prev_data["nums"]
        for num in nums:
            if num in stex_assigned_numbers: del stex_assigned_numbers[num]
        save_db()
        kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
        try: edit_message(chat_id, prev_msg_id, "ㅤ\n", reply_markup={"inline_keyboard": kb})
        except: pass
        del user_active_sessions[chat_id]


def purge_pending_search_prompts(chat_id, keep_msg_id=None):
    ids = pending_search_prompts.pop(chat_id, [])
    for mid in ids:
        try:
            if keep_msg_id is not None and mid == keep_msg_id:
                continue
            delete_message(chat_id, mid)
        except Exception:
            pass


# ==========================================
# Leaderboard position formatter
# ==========================================
def leaderboard_pos_emoji(rank):
    if rank == 10:
        return '<tg-emoji emoji-id="6309655288261644098">ℹ️</tg-emoji><tg-emoji emoji-id="6307374961275180239">🅾️</tg-emoji>'
    eid = LEADERBOARD_NUM_EMOJI.get(rank)
    if eid:
        char_map = {1:"1️⃣",2:"2️⃣",3:"3️⃣",4:"4️⃣",5:"5️⃣",6:"6️⃣",7:"7️⃣",8:"8️⃣",9:"9️⃣"}
        return f'<tg-emoji emoji-id="{eid}">{char_map.get(rank, "🔹")}</tg-emoji>'
    return f'<b>{rank}.</b>'


# ==========================================
# Message Handler
# ==========================================
def handle_message(msg):
    global total_uploaded_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    if chat_type != "private": return
    text = msg.get("text", "")
    register_user_local(chat_id)

    if text.startswith("/dmotp"):
        if not is_admin(chat_id): return
        parts = text.split(maxsplit=4)
        if len(parts) < 5:
            send_message(chat_id, render_body_text(
                "📝 <b>Usage:</b> <code>/dmotp SERVICE NUMBER OTP LANG</code>\n\n"
                "<b>Example:</b>\n<code>/dmotp WhatsApp +8801712345678 556677 EN</code>"
            ))
            return
        srv_test = parts[1].strip()
        num_test = parts[2].strip()
        otp_test = parts[3].strip()
        lang_test = parts[4].strip().upper()
        if not lang_test.startswith("#"): lang_test = "#" + lang_test
        fake_msg = f"Your code is {otp_test}"
        app_full_name, _ = get_service_info_html(srv_test)
        reward_test = get_payout_for_number(num_test.replace("+", ""), app_full_name)
        dm_text, dm_kb = deliver_to_inbox(chat_id, app_full_name, num_test, fake_msg, 0.0, reward_test, lang_test)
        send_message(chat_id, "🧪 <b>DM OTP Preview:</b>")
        send_message(chat_id, render_body_text(dm_text), reply_markup=dm_kb)
        return

    if text.startswith("/setservice"):
        if not is_admin(chat_id): return
        raw = text.replace("/setservice", "", 1).strip()
        if "|" not in raw:
            send_message(chat_id, render_body_text(
                "📝 <b>Usage:</b> <code>/setservice SERVICE_NAME | EMOJI_ID</code>\n\n"
                "<b>Examples:</b>\n"
                "<code>/setservice Facebook | 5334807341109908955</code>\n"
                "<code>/setservice Instagram | 5420130255174145507</code>"
            ))
            return
        svc_part, eid_part = raw.split("|", 1)
        svc_name = svc_part.strip().upper()
        eid = eid_part.strip()
        if not svc_name or not eid:
            send_message(chat_id, render_body_text("❌ <b>Both service name and emoji ID are required.</b>"))
            return
        default_char = svc_name[0] if svc_name else "📱"
        bot_settings["premium_apps"][svc_name] = {"char": default_char, "id": str(eid), "name": svc_name.title()}
        save_db()
        send_message(chat_id, render_body_text(
            f"{PEM['ok']} <b>Service emoji saved!</b>\n\n"
            f"📌 <b>Service:</b> <b>{svc_name}</b>\n"
            f"🆔 <b>Emoji ID:</b> <code>{eid}</code>"
        ))
        return

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text(
            "🚫 <b>You are banned from using this bot!</b>\n"
            "<i>If you think this is a mistake, please contact support.</i>"
        ))
        return

    if bot_settings.get("maintenance", False) and not is_admin(chat_id):
        if not text.startswith("/start") and text != "SUPPORT":
            maint_msg = (
                f'<tg-emoji emoji-id="6267262260243076354">㊙️</tg-emoji> <b>The Bot Is On Under MENTENENCE.</b>\n\n'
                f'Wait Some Time <tg-emoji emoji-id="5226560988291019577">🦕</tg-emoji> <b>Bot Will Available Soon</b> '
                f'<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>'
            )
            send_message(chat_id, render_body_text(maint_msg))
            return

    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                _sqlite_ensure_user(chat_id)
                process_referral_for_user(chat_id, inviter)

    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return

    MAIN_MENU_CMDS = ["GET NUMBER", "SEARCH NUMBER", "TRAFFIC", "REFER", "BALANCE", "SUPPORT", "Admin Panel", "2FA ONLINE"]
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True

    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]

        # ========== AUTO CAPTCHA PANEL SETUP ==========
        if state == "wait_for_cpanel_url" and text:
            temp_data[chat_id]["p_data"]["login_url"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_user"
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ <i>Panel এর Username দিন:</i>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_user" and text:
            temp_data[chat_id]["p_data"]["username"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_pass"
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ <i>Panel এর Password দিন:</i>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_pass" and text:
            temp_data[chat_id]["p_data"]["password"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_link"
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ <i>যেখান থেকে SMS/OTP ডাটা আসবে সেই Link:</i>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_msg_link" and text:
            temp_data[chat_id]["p_data"]["msg_link"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_name"
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ <i>(যেমন: number, phone):</i>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp_data[chat_id]["p_data"]["num_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_idx"
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Serial</b>\n➡️ <i>(যেমন: 3, 5):</i>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["num_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_msg_col_name"
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ <i>(যেমন: message, sms):</i>"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text("❌ <b>Please enter a valid number serial!</b>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp_data[chat_id]["p_data"]["msg_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_col_idx"
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Serial</b>\n➡️ <i>(যেমন: 5, 7):</i>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["msg_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_service_col_name"
                send_message(chat_id, render_body_text("9️⃣ <b>Service Column Name</b>\n➡️ <i>(যেমন: service, app, type):</i>"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text("❌ <b>Please enter a valid number serial!</b>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_service_col_name" and text:
            temp_data[chat_id]["p_data"]["service_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_service_col_idx"
            send_message(chat_id, render_body_text("ℹ️🅾️ <b>Service Col Serial</b>\n➡️ <i>(যেমন: 4, 6):</i>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_service_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["service_col_idx"] = int(text)
                temp_data[chat_id]["p_data"]["login_status"] = "Pending Auto-Login..."
                bot_settings["panels"].append(temp_data[chat_id]["p_data"])
                save_db()
                send_message(chat_id, render_body_text(
                    f"{PEM['ok']} <b>Auto Captcha Panel Added!</b>\n\n"
                    f"📌 <b>Name:</b> <b>{temp_data[chat_id]['p_data'].get('name', 'Panel')}</b>\n"
                    f"🔐 <b>Status:</b> <b>Pending Auto-Login</b>"
                ), reply_markup=main_menu(chat_id))
                msg_id = temp_data[chat_id]["msg_id"]
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_cpt_panels", "id": "internal"})
                del user_states[chat_id]; del temp_data[chat_id]
            else:
                send_message(chat_id, render_body_text("❌ <b>Please enter a valid number serial!</b>"), reply_markup=get_cancel_kb())
            return

        # ========== API PANEL FIELD EDIT ==========
        elif state == "wait_for_api_pf_value" and text:
            idx = temp_data[chat_id]["p_idx"]; field = temp_data[chat_id]["p_field"]
            new_value = text.strip()
            if new_value.lower() == "/cancel":
                del user_states[chat_id]; del temp_data[chat_id]
                p = bot_settings["panels"][idx]
                send_message(chat_id, render_body_text(f"⚙️ <b>Configure</b> <b>{p['name']}</b>"), reply_markup=panel_config_keyboard(idx))
                return
            if field in ["interval_sec", "records"]:
                try:
                    new_value = int(new_value)
                except ValueError:
                    send_message(chat_id, render_body_text("❌ <b>Please send a valid number.</b>"))
                    return
            bot_settings["panels"][idx][field] = new_value
            save_db()
            del user_states[chat_id]; del temp_data[chat_id]
            p = bot_settings["panels"][idx]
            send_message(chat_id, render_body_text(f"{PEM['ok']} <b>{field}</b> updated!"))
            send_message(chat_id, render_body_text(f"⚙️ <b>Configure</b> <b>{p['name']}</b>"), reply_markup=panel_config_keyboard(idx))
            return

        # ========== USER MANAGEMENT ==========
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ <b>Invalid ID!</b>"), reply_markup=get_cancel_kb()); return
            target_uid = int(target_uid_str)
            row = sqlite_exec("SELECT balance FROM users WHERE user_id=?", (target_uid,), fetch="one")
            if row is None and db:
                try:
                    doc = db.collection('users').document(str(target_uid)).get(timeout=5.0)
                    if doc.exists:
                        row = {"balance": (doc.to_dict() or {}).get('balance', 0.0)}
                except Exception as e:
                    print(f"⚠️  um_bal lookup Firestore: {type(e).__name__}")
            if row is None:
                send_message(chat_id, render_body_text("❌ <b>User not found!</b>"), reply_markup=get_cancel_kb()); return
            current_bal = row.get('balance', 0.0)
            temp_data[chat_id]["target_uid"] = target_uid
            user_states[chat_id] = "wait_for_um_bal_amt"
            send_message(chat_id, render_body_text(
                f"{PEM['ok']} <b>User found!</b>\n\n"
                f"💰 <b>Current Balance:</b> <b>${fmt_payout(current_bal)}</b>\n\n"
                f"📝 <b>Send amount to ADD/REMOVE:</b>"
            ), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip()); target_uid = temp_data[chat_id]["target_uid"]
                update_balance(target_uid, amt)
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Balance updated for</b> <b>{target_uid}</b>!"), reply_markup=main_menu(chat_id))
                send_message(target_uid, render_body_text(f"🔔 <b>Your balance adjusted by</b> <b>${fmt_payout(amt)}</b>"))
                del user_states[chat_id]; del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ <b>Invalid amount!</b>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ <b>Invalid ID!</b>"), reply_markup=get_cancel_kb()); return
            target_uid = int(target_uid_str)
            row = sqlite_exec("SELECT banned FROM users WHERE user_id=?", (target_uid,), fetch="one")
            if row is None:
                send_message(chat_id, render_body_text("❌ <b>User not found!</b>"), reply_markup=get_cancel_kb()); return
            current_status = bool(row.get("banned") or 0)
            new_status = not current_status
            try:
                with sqlite_tx() as conn:
                    if conn:
                        conn.cursor().execute("UPDATE users SET banned=?, updated_at=? WHERE user_id=?",
                                              (1 if new_status else 0, time.time(), target_uid))
            except Exception as e:
                print(f"⚠️  um ban SQLite: {type(e).__name__}")
            user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
            if target_uid in user_cache:
                user_cache[target_uid]["banned"] = new_status
            if db:
                try:
                    db.collection('users').document(str(target_uid)).set({"banned": new_status}, merge=True, timeout=5.0)
                except Exception as e:
                    print(f"⚠️  um ban Firestore: {type(e).__name__}")
            status_str = "🚫 <b>BANNED</b>" if new_status else "✅ <b>UNBANNED</b>"
            send_message(chat_id, render_body_text(f"{PEM['ok']} <b>User</b> <b>{target_uid}</b> <b>→</b> {status_str}"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]; del temp_data[chat_id]
            return
        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ <b>Invalid ID!</b>"), reply_markup=get_cancel_kb()); return
            target_uid = int(target_uid_str)
            data = None
            row = sqlite_exec(
                "SELECT user_id,balance,total_refers,total_otps,banned FROM users WHERE user_id=?",
                (target_uid,), fetch="one"
            )
            if row:
                data = {
                    "balance": float(row.get("balance") or 0.0),
                    "total_refers": int(row.get("total_refers") or 0),
                    "total_otps": int(row.get("total_otps") or 0),
                    "banned": bool(row.get("banned") or 0),
                }
            if data is None and db:
                try:
                    doc = db.collection('users').document(str(target_uid)).get(timeout=5.0)
                    if doc.exists:
                        data = doc.to_dict() or {}
                except Exception as e:
                    print(f"⚠️  um profile Firestore: {type(e).__name__}")
            if not data:
                send_message(chat_id, render_body_text("❌ <b>User not found!</b>"), reply_markup=get_cancel_kb()); return
            prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 <b>ID:</b> <code>{target_uid}</code>
💰 <b>Balance:</b> <b>${fmt_payout(data.get('balance', 0.0))}</b>
🤝 <b>Refers:</b> <b>{data.get('total_refers', 0)}</b>
🔐 <b>OTPs:</b> <b>{data.get('total_otps', 0)}</b>
🚫 <b>Banned:</b> <b>{data.get('banned', False)}</b>
➖➖➖➖➖➖➖➖"""
            kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
            send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
            del user_states[chat_id]; del temp_data[chat_id]
            return

        # ========== MENU DESIGN ==========
        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                formatted_html_text = extract_premium_html(msg)
                bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                save_db()
                delete_message(chat_id, msg["message_id"])
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Updated!</b>\n\n🎨 <b>{menu_key.upper()}</b>\n\n<b>Preview:</b>\n{preview_text}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                send_message(chat_id, f"❌ <b>Error:</b> {e}")
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip(); btn_url = parts[1].strip()
                    emoji_id = None; emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0); length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le'); break
                    if emoji_char: btn_text = btn_text.replace(emoji_char, "").strip()
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary"}
                    if emoji_id: btn_data["icon_custom_emoji_id"] = emoji_id
                    bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['gear']} <b>Edit Buttons:</b> <b>{menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} <b>Invalid format.</b>"))
            except Exception:
                pass
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        # ========== TEST MESSAGE ==========
        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 <b>Send the Number:</b>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 <b>Send the OTP:</b>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 <b>Send Language (EN, AR):</b>"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"): lang = "#" + lang
            srv = temp_data[chat_id]["service"]; num = temp_data[chat_id]["number"]; otp = temp_data[chat_id]["otp"]
            app_full_name, _ = get_service_info_html(srv)
            msg_text = render_body_text(format_otp_display(num, app_full_name, lang, masked=True))
            for fw in bot_settings["fw_groups"]:
                kb = build_group_kb(otp, fw)
                send_message(fw["chat_id"], msg_text, reply_markup=kb)
            send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Test message sent!</b>"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]; del temp_data[chat_id]
            return

        # ========== BROADCAST ==========
        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Broadcast started...</b>"))
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id)).start()
            del user_states[chat_id]
            return

        # ========== UPLOAD NUMBER FILE ==========
        elif state == "wait_for_txt" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} <b>Please upload a .txt file only.</b>")); return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"{FILE_URL}{file_path}").text
            lines = [l.strip() for l in file_content.splitlines() if l.strip()]
            clean_list = []
            for n in lines:
                nn = n if n.startswith('+') else '+' + n
                clean_list.append(nn)
            raw_filename = doc["file_name"]
            fname_clean = raw_filename.rsplit('.', 1)[0].strip()
            detected_country_from_file = fname_clean
            file_service_hint = ""
            if "_" in fname_clean:
                parts_f = fname_clean.split("_")
                detected_country_from_file = parts_f[0].strip()
                if len(parts_f) > 1:
                    file_service_hint = " ".join(parts_f[1:]).strip()
            elif "-" in fname_clean:
                parts_f = fname_clean.split("-")
                detected_country_from_file = parts_f[0].strip()
                if len(parts_f) > 1:
                    file_service_hint = " ".join(parts_f[1:]).strip()
            detected_country = ""
            detected_iso = ""
            if clean_list:
                first_num = clean_list[0].replace('+', '')
                dial_code, src = _find_dial_code(first_num)
                if src == "premium":
                    detected_country = bot_settings["premium_flags"][dial_code].get("name", "")
                    detected_iso = bot_settings["premium_flags"][dial_code].get("iso", "")
                elif src == "db":
                    detected_country = COUNTRY_DB[dial_code].get("name", "")
                    detected_iso = COUNTRY_DB[dial_code].get("iso", "")
                else:
                    for code, info in sorted(COUNTRY_DB.items(), key=lambda x: len(x[0]), reverse=True):
                        if first_num.startswith(code):
                            detected_country = info.get("name", "")
                            detected_iso = info.get("iso", "")
                            break
            temp_data[chat_id] = {
                "numbers": clean_list,
                "filename": raw_filename,
                "file_country": detected_country_from_file,
                "file_service_hint": file_service_hint,
                "detected_country": detected_country,
                "detected_iso": detected_iso
            }
            user_states[chat_id] = "wait_for_service"
            file_hint = f"📁 <b>Country from filename:</b> <b>{html.escape(detected_country_from_file)}</b>"
            svc_hint = f"\n🔧 <b>Service hint:</b> <b>{html.escape(file_service_hint)}</b>" if file_service_hint else ""
            flag_from_num = f" {get_flag_info_html(detected_iso)}" if detected_iso else ""
            send_message(chat_id, render_body_text(
                f"{PEM['ok']} <b>File received</b>\n\n"
                f"📁 <code>{raw_filename}</code>\n"
                f"📊 <b>Numbers:</b> <b>{len(clean_list)}</b>\n"
                f"{file_hint}{flag_from_num}{svc_hint}\n\n"
                f"📌 <b>Enter the service name:</b>"
            ), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_service" and text:
            temp_data[chat_id]["service"] = text.upper().strip()
            file_country = temp_data[chat_id].get("file_country", "")
            detected_iso = temp_data[chat_id].get("detected_iso", "")
            if file_country:
                temp_data[chat_id]["country_name"] = file_country
                temp_data[chat_id]["country_iso"] = detected_iso
                user_states[chat_id] = "wait_for_payout"
                svc = temp_data[chat_id]["service"]
                flag_preview = f" {get_flag_info_html(detected_iso)}" if detected_iso else ""
                send_message(chat_id, render_body_text(
                    f"{PEM['ok']} <b>Country:</b> <b>{file_country}</b>{flag_preview}\n"
                    f"🔧 <b>Service:</b> <b>{svc}</b>\n\n"
                    f"💰 <b>Enter payout per OTP in USD</b>"
                ), reply_markup=get_cancel_kb())
                return
            user_states[chat_id] = "wait_for_country"
            send_message(chat_id, render_body_text(
                f"{PEM['ok']} <b>Service:</b> <b>{temp_data[chat_id]['service']}</b>\n\n"
                f"🌍 <b>Enter the country name:</b>"
            ), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_country" and text:
            t = text.strip()
            detected_iso = temp_data[chat_id].get("detected_iso", "")
            file_country = temp_data[chat_id].get("file_country", "")
            if t.lower() == "/skip" and file_country:
                country_name = file_country
                country_iso = detected_iso
            else:
                country_name = t
                country_iso = detected_iso
                if not country_iso:
                    for cname, cinfo in COUNTRIES_DATA.items():
                        if cname.lower() == t.lower():
                            country_iso = cinfo.get("iso", ""); break
                if not country_iso:
                    for ccode, cinfo in COUNTRY_DB.items():
                        if cinfo["name"].lower() == t.lower():
                            country_iso = cinfo["iso"]; break
                if not country_iso:
                    for fcode, finfo in bot_settings.get("premium_flags", {}).items():
                        if finfo.get("name", "").lower() == t.lower() or finfo.get("iso", "").upper() == t.upper():
                            country_iso = finfo.get("iso", ""); break
            temp_data[chat_id]["country_name"] = country_name
            temp_data[chat_id]["country_iso"] = country_iso
            user_states[chat_id] = "wait_for_payout"
            svc = temp_data[chat_id]["service"]
            flag_preview = f" {get_flag_info_html(country_iso)}" if country_iso else ""
            send_message(chat_id, render_body_text(
                f"{PEM['ok']} <b>Country:</b> <b>{country_name}</b>{flag_preview}\n"
                f"🔧 <b>Service:</b> <b>{svc}</b>\n\n"
                f"💰 <b>Enter payout per OTP in USD</b>"
            ), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_payout" and text:
            try:
                payout_val = float(text.strip())
                if payout_val < 0: raise ValueError()
                if payout_val > 1000:
                    send_message(chat_id, render_body_text("❌ <b>Max $1000.</b>")); return
            except:
                send_message(chat_id, render_body_text("❌ <b>Invalid amount.</b>")); return
            country_name = temp_data[chat_id]["country_name"]
            country_iso = temp_data[chat_id]["country_iso"]
            service = temp_data[chat_id]["service"]
            raw_numbers = temp_data[chat_id]["numbers"]
            filename = temp_data[chat_id].get("filename", "upload.txt")
            bcast_key = f"{country_name}|{service}|{len(raw_numbers)}|{filename}"
            now_ts = time.time()
            if bcast_key in _last_upload_bcast and now_ts - _last_upload_bcast[bcast_key] < 30:
                send_message(chat_id, render_body_text("⚠️ <b>Duplicate upload blocked.</b>"))
                del user_states[chat_id]; del temp_data[chat_id]; return
            _last_upload_bcast[bcast_key] = now_ts
            if "otp_pair_rates" not in bot_settings: bot_settings["otp_pair_rates"] = {}
            pair_key = f"{country_name.upper()}|{service.upper()}"
            bot_settings["otp_pair_rates"][pair_key] = payout_val
            batch_id = str(uuid.uuid4())[:8]
            number_batches[batch_id] = {
                "filename": filename, "service": service.upper(),
                "country": country_name.upper(), "country_iso": country_iso,
                "payout": payout_val,
                "numbers": [{"num": n, "shares": 0, "used_by": []} for n in raw_numbers]
            }
            total_uploaded_stats += len(raw_numbers)
            save_db()
            flag_html = get_flag_info_html(country_name)
            app_full, app_emoji_html = get_service_info_html(service)
            broadcast_txt, broadcast_kb = build_stock_broadcast_new(country_name.upper(), service.upper(), len(raw_numbers), payout_val, flag_html, app_emoji_html)
            broadcast_txt = render_body_text(broadcast_txt)
            send_message(chat_id, render_body_text(
                f"{PEM['ok']} <b>Numbers added!</b>\n\n"
                f"🌍 <b>Country:</b> <b>{country_name.upper()}</b>\n"
                f"🏳️ <b>Flag:</b> {flag_html}\n"
                f"🔧 <b>Service:</b> <b>{service.upper()}</b>\n"
                f"💰 <b>Payout:</b> <b>${fmt_payout(payout_val)}/OTP</b>\n"
                f"📤 <b>Count:</b> <b>{len(raw_numbers)}</b>"
            ))
            def sb(txt, kb):
                b_session = requests.Session()
                sent_ok = 0; sent_fail = 0; last_err = ""
                sent_to = set()
                txt_no_premium = re.sub(r'<tg-emoji[^>]*>([^<]*)</tg-emoji>', r'\1', txt)
                txt_plain = re.sub(r'<[^>]+>', '', txt)
                kb_no_icons = {"inline_keyboard": [[{k: v for k, v in btn.items() if k != "icon_custom_emoji_id"} for btn in row] for row in kb.get("inline_keyboard", [])]}
                for u_id in list(all_known_users):
                    if u_id in sent_to: continue
                    sent_to.add(u_id)
                    ok = False
                    try:
                        rr = b_session.post(f"{BASE_URL}/sendMessage", json={"chat_id": u_id, "text": txt, "parse_mode": "HTML", "reply_markup": kb}, timeout=8)
                        j = rr.json()
                        if j.get("ok"): ok = True
                        else:
                            rr2 = b_session.post(f"{BASE_URL}/sendMessage", json={"chat_id": u_id, "text": txt_no_premium, "parse_mode": "HTML", "reply_markup": kb_no_icons}, timeout=8)
                            if rr2.json().get("ok"): ok = True
                            else:
                                rr3 = b_session.post(f"{BASE_URL}/sendMessage", json={"chat_id": u_id, "text": txt_plain, "reply_markup": kb_no_icons}, timeout=8)
                                if rr3.json().get("ok"): ok = True
                                else:
                                    rr4 = b_session.post(f"{BASE_URL}/sendMessage", json={"chat_id": u_id, "text": txt_plain}, timeout=8)
                                    if rr4.json().get("ok"): ok = True
                                    else: last_err = str(rr4.json().get("description", "?"))[:100]
                        if ok: sent_ok += 1
                        else: sent_fail += 1
                    except Exception as e:
                        sent_fail += 1; last_err = str(e)[:100]
                    time.sleep(0.05)
                try: send_message(chat_id, f"📢 <b>Broadcast: OK</b> {sent_ok} / <b>FAIL</b> {sent_fail}\n⚠️ <b>Last:</b> {last_err}")
                except: pass
            threading.Thread(target=sb, args=(broadcast_txt, broadcast_kb), daemon=True).start()
            del user_states[chat_id]; del temp_data[chat_id]
            return

        # ========== STEX/VOLTX KEY ADD ==========
        elif state == "wait_for_add_stex_key" and text:
            bot_settings["stex_keys"].append(text.strip()); save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['ok']} <b>StexSMS Key Added! Total:</b> <b>{len(bot_settings.get('stex_keys', []))}</b>"), reply_markup=stex_control_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]; return
        elif state == "wait_for_add_voltx_key" and text:
            bot_settings["voltx_keys"].append(text.strip()); save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['ok']} <b>Voltx Key Added! Total:</b> <b>{len(bot_settings.get('voltx_keys', []))}</b>"), reply_markup=voltx_control_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]; return

        # ========== SEARCH COUNTRY / SERVICE / ADDRESS ==========
        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
            bot_settings["search_countries"].append(code); save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "stex_search_country", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]; return
        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
            bot_settings["voltx_search_countries"].append(code); save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "voltx_search_country", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]; return
        elif state == "wait_nx_srv_name" and text:
            srv = text.strip().upper()
            if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
            if srv not in bot_settings["stex_services"]: bot_settings["stex_services"][srv] = {}
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_stex_srv", "id": "internal"})
            del user_states[chat_id]; return
        elif state == "wait_nx_cnt_name" and text:
            cnt = text.strip(); srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["stex_services"][srv]: bot_settings["stex_services"][srv][cnt] = []
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]; return
        elif state == "wait_nx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            if new_range not in bot_settings["stex_services"][srv][cnt]:
                bot_settings["stex_services"][srv][cnt].append(new_range)
                if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
                if new_range not in bot_settings["search_countries"]: bot_settings["search_countries"].append(new_range)
                save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]; return
        elif state == "wait_vx_srv_name" and text:
            srv = text.strip().upper()
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            if srv not in bot_settings["voltx_services"]: bot_settings["voltx_services"][srv] = {}
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_voltx_srv", "id": "internal"})
            del user_states[chat_id]; return
        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip(); srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["voltx_services"][srv]: bot_settings["voltx_services"][srv][cnt] = []
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]; return
        elif state == "wait_vx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            if new_range not in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].append(new_range)
                if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
                if new_range not in bot_settings["voltx_search_countries"]: bot_settings["voltx_search_countries"].append(new_range)
                save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]; return

        # ========== WITHDRAWAL METHOD ==========
        elif state == "wait_for_add_wm" and text:
            raw = text.strip()
            if "|" in raw:
                parts = raw.split("|", 1)
                m_name = parts[0].strip()
                m_eid = parts[1].strip()
                m_char = "🔘"
                method_obj = {"name": m_name, "emoji_id": m_eid, "char": m_char}
                bot_settings["w_methods"].append(method_obj)
            else:
                bot_settings["w_methods"].append(raw)
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]; return

        # ========== FORCE JOIN ==========
        elif state == "wait_for_add_fj" and text:
            bot_settings["fj_channels"].append(parse_chat_id(text)); save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🔗 <b>FORCE JOIN SYSTEM</b>"), reply_markup=fj_settings_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]; return

        # ========== ADMIN MANAGEMENT ==========
        elif state == "wait_for_add_adm" and text:
            if chat_id != OWNER_ID:
                send_message(chat_id, render_body_text(f"{PEM['no']} <b>Only OWNER can add admins!</b>"))
                del user_states[chat_id]; del temp_data[chat_id]; return
            if text.isdigit():
                bot_settings["admins"].append(int(text)); save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]; return

        # ========== FORWARD GROUP ==========
        elif state == "wait_for_add_fw_id" and text:
            bot_settings["fw_groups"].append({"chat_id": text.strip(), "buttons": []}); save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]; return
        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp_data[chat_id]["fw_idx"]
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip(); btn_url = parts[1].strip()
                emoji_id = None; emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0); length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le'); break
                if emoji_char: btn_text = btn_text.replace(emoji_char, "").strip()
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id: btn_data["icon_custom_emoji_id"] = emoji_id
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data); save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Manage Group:</b> <b>{bot_settings['fw_groups'][fw_idx]['chat_id']}</b>"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]; del temp_data[chat_id]; return
        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip(); save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]; return
        elif state == "wait_for_main_channel_link" and text:
            new_link = text.strip()
            if not new_link.startswith("http"):
                send_message(chat_id, render_body_text("❌ <b>Link must start with http://</b>"), reply_markup=get_cancel_kb()); return
            bot_settings["main_channel_link"] = new_link; save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]; return

        # ========== PANEL NAME ==========
        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp_data[chat_id].get("add_type", "api")
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            if t_key == "logc":
                user_states[chat_id] = "wait_for_cpanel_url"
                temp_data[chat_id] = {"msg_id": msg_id, "p_data": {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", "records": 0,
                    "login_status": "Pending First Login"
                }}
                edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>\n➡️ <i>Panel এর Login Link দিন:</i>"), reply_markup=get_cancel_kb())
                return
            else:
                bot_settings["panels"].append({
                    "name": p_name, "type": "API Panel", "status": "OFF",
                    "api_url": "", "curl_command": "",
                    "endpoint": "/", "token": "", "method": "GET",
                    "interval_sec": 30, "records": 0,
                    "otp_list_path": "data", "number_path": "number", "message_path": "message",
                    "service_path": "service"
                })
                save_db()
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_api_panels", "id": "internal"})
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return

        # ========== DXA CONTROL ==========
        elif state == "set_dxa":
            msg_id = temp_data[chat_id]["msg_id"]; key = temp_data[chat_id]["key"]
            try:
                if key in ["min_withdraw", "otp_reward", "refer_reward"]: bot_settings[key] = float(text)
                elif key in ["cooldown", "num_req", "num_share"]: bot_settings[key] = int(text)
                else: bot_settings[key] = text
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>STORM CONTROL PANEL</b>"), reply_markup=storm_control_keyboard())
            except:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>STORM</b>\n\n❌ <b>Invalid!</b>"), reply_markup=storm_control_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]; return

        # ========== PAYOUT VALUE ==========
        elif state == "set_payout_value" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            service = temp_data[chat_id].get("service", "?")
            country = temp_data[chat_id].get("country", "?")

            try: delete_message(chat_id, msg.get("message_id"))
            except: pass

            try:
                new_val = float(text.strip())
                if new_val < 0: raise ValueError("negative")
            except:
                fail_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"❌ <b>PAYOUT UPDATE FAILED</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📌 <b>Reason:</b> <b>Invalid number format</b>\n"
                    f"💡 <b>Example:</b> <code>0.005</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📝 <b>Send a valid number:</b>"
                )
                if msg_id_to_edit:
                    try:
                        edit_message(chat_id, msg_id_to_edit, render_body_text(fail_txt), reply_markup=get_cancel_kb())
                    except:
                        send_message(chat_id, render_body_text(fail_txt), reply_markup=get_cancel_kb())
                else:
                    send_message(chat_id, render_body_text(fail_txt), reply_markup=get_cancel_kb())
                return

            try:
                if "otp_pair_rates" not in bot_settings: bot_settings["otp_pair_rates"] = {}
                key = f"{str(country).upper()}|{str(service).upper()}"
                old_val = bot_settings["otp_pair_rates"].get(key, "None")
                bot_settings["otp_pair_rates"][key] = new_val
                save_db()

                country_flag = get_flag_info_html(country)

                ok_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"✅ <b>PAYOUT UPDATED SUCCESSFULLY</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🌍 <b>Country:</b> <code>{country}</code> {country_flag}\n"
                    f"🔧 <b>Service:</b> <code>{service}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"💵 <b>Old Payout:</b> <code>${old_val}</code>\n"
                    f"💷 <b>New Payout:</b> <code>${fmt_payout(new_val)}</code>\n"
                    f"━━━━━━━━━━━━━━━"
                )

                if msg_id_to_edit:
                    try:
                        edit_message(
                            chat_id, msg_id_to_edit,
                            render_body_text(ok_txt),
                            reply_markup={"inline_keyboard": [[
                                {"text": "◀️ Back to Payout Menu", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "change_payout_menu", "style": "primary"},
                                {"text": "🏠 Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "back_to_admin", "style": "success"}
                            ]]}
                        )
                    except:
                        send_message(chat_id, render_body_text(ok_txt), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "change_payout_menu", "style": "primary"}]]})
                else:
                    send_message(chat_id, render_body_text(ok_txt), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "change_payout_menu", "style": "primary"}]]})
            except Exception as e:
                fail_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"❌ <b>PAYOUT UPDATE FAILED</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📌 <b>Error:</b> <code>{html.escape(str(e)[:80])}</code>\n"
                    f"━━━━━━━━━━━━━━━"
                )
                if msg_id_to_edit:
                    try:
                        edit_message(chat_id, msg_id_to_edit, render_body_text(fail_txt), reply_markup=get_cancel_kb())
                    except:
                        send_message(chat_id, render_body_text(fail_txt), reply_markup=get_cancel_kb())
                else:
                    send_message(chat_id, render_body_text(fail_txt), reply_markup=get_cancel_kb())
                return

            del user_states[chat_id]
            del temp_data[chat_id]
            return

        # ========== DATA ZIP RESTORE ==========
        elif state == "wait_for_data_zip" and "document" in msg:
            doc = msg["document"]
            if doc["file_name"] != "STR_BOT_DATA.zip":
                send_message(chat_id, render_body_text(f"{PEM['no']} <b>File name must be exactly</b> <code>STR_BOT_DATA.zip</code>"))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            if not file_info.get("ok"):
                send_message(chat_id, render_body_text(f"❌ <b>Download failed.</b>"))
                if chat_id in user_states: del user_states[chat_id]
                return
            file_path = file_info["result"]["file_path"]
            raw_bytes = requests.get(f"{FILE_URL}{file_path}").content
            ok, summary = restore_data_from_zip(raw_bytes)
            if ok:
                send_message(chat_id, render_body_text(
                    f"{PEM['ok']} <b>Data restored successfully!</b>\n\n"
                    f"📊 <b>Applied:</b>\n<code>{html.escape(summary)}</code>"
                ), reply_markup=main_menu(chat_id))
            else:
                send_message(chat_id, render_body_text(
                    f"{PEM['no']} <b>Restore failed!</b>\n<code>{html.escape(str(summary))}</code>"
                ))
            if chat_id in user_states: del user_states[chat_id]
            return

        # ========== SEARCH NUMBER ==========
        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text(
                    "━━━━━━━━━━━━━━━\n"
                    "❌ <b>INVALID INPUT</b>\n"
                    "━━━━━━━━━━━━━━━\n"
                    "📌 <b>3 to 9 digits required!</b>\n"
                    "━━━━━━━━━━━━━━━"
                ), reply_markup=main_menu(chat_id))
                del user_states[chat_id]
                return

            _, iso_det, dial_code = get_country_from_num(query)
            country_name_det = ""
            country_flag_html = "🌍"
            if iso_det and iso_det != "XX":
                for _c, fdata in bot_settings.get("premium_flags", {}).items():
                    if fdata.get("iso", "").upper() == iso_det.upper():
                        country_name_det = fdata.get("name", "")
                        eid = fdata.get("id"); char = fdata.get("char")
                        if eid:
                            country_flag_html = f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                        else:
                            country_flag_html = char
                        break
                if not country_name_det:
                    for _c, cinfo in COUNTRY_DB.items():
                        if cinfo["iso"].upper() == iso_det.upper():
                            country_name_det = cinfo["name"]
                            country_flag_html = get_flag_emoji(iso_det)
                            break

            services_found = {}

            for b_id, b_data in number_batches.items():
                b_nums = b_data.get("numbers", [])
                if not b_nums: continue
                b_country = b_data.get("country", "").upper()
                b_iso = b_data.get("country_iso", "").upper()
                b_service = b_data.get("service", "").upper()
                if not b_service: continue
                matched = False
                if country_name_det and b_country == country_name_det.upper(): matched = True
                if not matched and iso_det and iso_det != "XX" and b_iso == iso_det.upper(): matched = True
                if not matched:
                    for n_obj in b_nums[:5]:
                        if n_obj["num"].replace("+", "").startswith(query):
                            matched = True; break
                if matched:
                    services_found.setdefault(b_service, []).append(("local", b_id))

            for srv_name, c_dict in bot_settings.get("stex_services", {}).items():
                srv_up = srv_name.upper()
                for c_name, r_list in c_dict.items():
                    matched = False
                    if country_name_det and c_name.upper() == country_name_det.upper(): matched = True
                    if not matched and iso_det and iso_det != "XX" and c_name.upper() == iso_det.upper(): matched = True
                    if not matched:
                        for r in r_list:
                            if query.startswith(r): matched = True; break
                    if matched:
                        services_found.setdefault(srv_up, []).append(("stex", c_name))

            for srv_name, c_dict in bot_settings.get("voltx_services", {}).items():
                srv_up = srv_name.upper()
                for c_name, r_list in c_dict.items():
                    matched = False
                    if country_name_det and c_name.upper() == country_name_det.upper(): matched = True
                    if not matched and iso_det and iso_det != "XX" and c_name.upper() == iso_det.upper(): matched = True
                    if not matched:
                        for r in r_list:
                            if query.startswith(r): matched = True; break
                    if matched:
                        services_found.setdefault(srv_up, []).append(("voltx", c_name))

            if not services_found:
                send_message(chat_id, render_body_text(
                    f"━━━━━━━━━━━━━━━\n"
                    f"❌ <b>NO SERVICES FOUND</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📌 <b>Prefix:</b> <code>{query}</code>\n"
                    f"{country_flag_html} <b>Country:</b> {country_name_det or iso_det or 'Unknown'}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"💡 <b>Try another prefix!</b>"
                ), reply_markup=main_menu(chat_id))
                del user_states[chat_id]
                return

            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            for srv_name in sorted(services_found.keys()):
                sources = services_found[srv_name]
                total_cnt = 0
                for src_type, src_id in sources:
                    if src_type == "local":
                        total_cnt += len(number_batches.get(src_id, {}).get("numbers", []))
                    else:
                        total_cnt += 1
                svc_emoji_id = "5352694861990501856"
                svc_display = srv_name.title()
                for ak, ad in apps_db.items():
                    if srv_name.upper() == ak or srv_name.upper() in ak or ak in srv_name.upper():
                        if "id" in ad: svc_emoji_id = ad["id"]
                        svc_display = ad.get("name", ak.title())
                        break
                kb.append([{
                    "text": f"{svc_display} | {total_cnt}",
                    "icon_custom_emoji_id": svc_emoji_id,
                    "callback_data": f"s_srv|{query}|{srv_name}",
                    "style": "success"
                }])
            kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])

            prev_prompt_id = temp_data.get(chat_id, {}).get("prompt_msg_id")
            prefix_msg_id = msg.get("message_id")

            temp_data[chat_id] = {
                "search_query": query,
                "search_country": country_name_det,
                "search_iso": iso_det,
                "prompt_msg_id": prev_prompt_id,
                "prefix_msg_id": prefix_msg_id,
            }
            del user_states[chat_id]

            tiger_icon = f'<tg-emoji emoji-id="{SEARCH_TIGER_EMOJI}">🐯</tg-emoji>'
            world_icon = f'<tg-emoji emoji-id="{SEARCH_WORLD_EMOJI}">🌍</tg-emoji>'
            target_icon = f'<tg-emoji emoji-id="{SEARCH_TARGET_EMOJI}">🎯</tg-emoji>'
            country_display_name = country_name_det.upper() if country_name_det else (iso_det or "UNKNOWN")
            if iso_det and iso_det != "XX":
                flag_for_country = country_flag_html
            else:
                flag_for_country = "🌍"

            txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"🔍 <b>SEARCH RESULT</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📌 <b>Prefix:</b> <code>{query}</code> {tiger_icon}\n"
                f"{world_icon} <b>Country:</b> {country_display_name} {flag_for_country}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"{target_icon} <b>Available Services:</b>\n"
            )
            sent_res = send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

            search_result_msg_id = None
            try:
                if sent_res and sent_res.get("ok"):
                    search_result_msg_id = sent_res["result"]["message_id"]
            except Exception:
                search_result_msg_id = None

            ids_to_track = []
            if prev_prompt_id:        ids_to_track.append(prev_prompt_id)
            if prefix_msg_id:         ids_to_track.append(prefix_msg_id)
            if search_result_msg_id:  ids_to_track.append(search_result_msg_id)
            pending_search_prompts[chat_id] = ids_to_track

            if search_result_msg_id:
                temp_data[chat_id]["search_result_msg_id"] = search_result_msg_id
            return

        # ========== WITHDRAW AMOUNT ==========
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = float(text.strip())
                bal = temp_data[chat_id]["balance"]; min_w = bot_settings['min_withdraw']
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ <b>Min</b> <b>${fmt_payout(min_w)}!</b>\n💰 <b>Balance:</b> <b>${fmt_payout(bal)}</b>"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ <b>Insufficient!</b>\n💰 <b>Balance:</b> <b>${fmt_payout(bal)}</b>"), reply_markup=get_cancel_kb())
                    return
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"{PEM['ok']} <b>Amount:</b> <b>${fmt_payout(amount)}</b>\n\n📱 <b>Send</b> <b>{temp_data[chat_id]['method']}</b> <b>number:</b>"), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ <b>Invalid amount!</b>"), reply_markup=get_cancel_kb())
            return

        # ========== 2FA ==========
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
            delete_message(chat_id, msg.get("message_id"))
            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ <b>Error.</b>")); del user_states[chat_id]; return
            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret); code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                success_txt = (f"━━━━━━━━━━━━━━━\n《 🔐 <b>2FA CODE</b> 》\n━━━━━━━━━━━━━━━\n"
                              f"🔐 <b>CODE:</b> <code>{code}</code>\n━━━━━━━━━━━━━━━\n"
                              f"🕓 <b>EXPIRES IN:</b> <b>{remaining_time}s</b>\n━━━━━━━━━━━━━━━")
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            except:
                error_txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n❌ <b>Invalid Secret Key!</b>\n━━━━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        # ========== WITHDRAW NUMBER ==========
        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            method = temp_data[chat_id]["method"]; amount = temp_data[chat_id]["amount"]
            number = text; req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()

            # ⭐ HOLD the balance: deduct from user immediately
            hold_withdrawal_balance(chat_id, amount)

            pending_withdrawals[req_id] = {"user_id": chat_id, "amount": amount, "method": method, "number": number, "full_name": full_name}
            try:
                with sqlite_tx() as conn:
                    if conn:
                        conn.cursor().execute(
                            "INSERT INTO withdrawals(req_id,user_id,amount,method,number,full_name,status,timestamp) "
                            "VALUES(?,?,?,?,?,?,?,?)",
                            (req_id, int(chat_id), float(amount), method, number, full_name, "pending", time.time())
                        )
            except Exception as e:
                print(f"⚠️  withdrawal SQLite insert: {type(e).__name__}")
            if db:
                try:
                    db.collection('withdrawals').document(req_id).set({
                        "user_id": str(chat_id), "amount": amount, "method": method,
                        "status": "pending", "timestamp": firestore.SERVER_TIMESTAMP
                    }, timeout=5.0)
                except Exception as e:
                    print(f"⚠️  withdrawal Firestore set: {type(e).__name__}")
            if bot_settings["w_group"]:
                admin_msg = build_withdrawal_group_msg(chat_id, full_name, amount, number, method, req_id)
                kb = {"inline_keyboard": [[{"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"}, {"text": "REJECT", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrej_{req_id}", "style": "danger"}]]}
                send_message(bot_settings["w_group"], admin_msg, reply_markup=kb)

            balance_icon = f'<tg-emoji emoji-id="{WITHDRAW_BALANCE_EMOJI}">🔘</tg-emoji>'
            method_icon = f'<tg-emoji emoji-id="{WITHDRAW_METHOD_ICON}">🥂</tg-emoji>'
            method_emoji = get_wmethod_emoji_html(method)
            amount_display = fmt_payout(amount)
            success_text = (
                f"{PEM['ok']} <b>Your Withdraw Request is Submitted!</b>\n"
                f"\n"
                f"🧾 <b>WITHDRAW ID :</b> <code>{req_id}</code>\n"
                f"{balance_icon} <b>BALANCE :</b> <code>${amount_display}</code>\n"
                f"{method_icon} <b>METHOED :</b> <b>{method}</b> {method_emoji}\n"
                f"📱 <b>YOUR NUMBER :</b> <code>{number}</code>\n"
            )
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text))
            else:
                send_message(chat_id, render_body_text(success_text))
            del user_states[chat_id]; del temp_data[chat_id]; return

    # ========== MAIN MENU COMMANDS ==========
    if text.startswith("/start"):
        get_user(chat_id)
        check_and_pay_referral_for_user(chat_id)
        c_msg = bot_settings["custom_messages"].get("start", {})
        start_text = c_msg.get("text", "").strip()
        if not start_text or "WELCOME" not in start_text.upper():
            start_text = "<blockquote>👋 <b>WELCOME TO 𝐒𝐓𝐎𝐑𝐌 𝐗 𝐎𝐍𝐄</b> 🤔</blockquote>\n\n📩 <b>RECEIVE OTP'S AND START EARNING MONEY</b> 🤑"
        txt = render_body_text(start_text)
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        if kb:
            res_welcome = send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
        else:
            res_welcome = send_message(chat_id, txt, reply_markup=main_menu(chat_id))
        if not res_welcome or not res_welcome.get("ok"):
            plain_txt = "👋 WELCOME TO 𝐒𝐓𝐎𝐑𝐌 𝐗 𝐎𝐍𝐄 🤔\n\n📩 RECEIVE OTP'S AND START EARNING MONEY 🤑"
            send_message(chat_id, plain_txt, reply_markup=main_menu(chat_id))

    elif text == "TRAFFIC":
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)
    elif text == "REFER":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        raw_txt = c_msg.get("text", "").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", fmt_payout(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
    elif text == "BALANCE":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} <b>Withdrawals disabled.</b>")); return
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        total_otp_cnt = u_data.get('total_otps', 0)
        total_ref_cnt = u_data.get('total_refers', 0)
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = (c_msg.get("text", "")
                   .replace("{user_id}", str(chat_id))
                   .replace("{bal}", fmt_payout(bal))
                   .replace("{total_otp}", str(total_otp_cnt))
                   .replace("{total_ref}", str(total_ref_cnt))
                   .replace("{min_w}", fmt_payout(bot_settings['min_withdraw'])))
        txt = render_body_text(raw_txt)
        kb = []
        for m_name, m_emoji_html, m_icon_id in get_wmethod_display_list():
            kb.append([{"text": m_name.strip(), "icon_custom_emoji_id": m_icon_id, "callback_data": f"sel_wm_{m_name.strip()}", "style": "primary"}])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
    elif text == "Admin Panel" and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())
    elif text == "GET NUMBER":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        all_services = local_srvs.union(stex_srvs).union(voltx_srvs)
        if not all_services:
            send_message(chat_id, render_body_text(f"{PEM['no']} <b>No services!</b>"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} <b>Select Service</b>"))
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            for s in all_services:
                emoji_id = "5352694861990501856"
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data: emoji_id = app_data["id"]; break
                kb.append([{"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s|{s}", "style": "primary"}])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
    elif text == "SEARCH NUMBER":
        user_states[chat_id] = "wait_for_search"
        c_msg = bot_settings["custom_messages"].get("search_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['num']} <b>Search</b>"))
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]
        sent = send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
        try:
            if sent and sent.get("ok"):
                temp_data[chat_id] = {"prompt_msg_id": sent["result"]["message_id"]}
        except Exception:
            pass
    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate 2FA code instantly.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
    elif text == "SUPPORT":
        c_msg = bot_settings["custom_messages"].get("support", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['msg']} <b>Support</b>"))
        kb = []
        sup_link = bot_settings.get("support_link", "")
        if sup_link: kb.insert(0, [{"text": "Contact Support", "icon_custom_emoji_id": "5337302974806922068", "url": sup_link, "style": "success"}])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb} if kb else None)


# ==========================================
# 📦 Database ZIP — FOLDER-STRUCTURED
# ==========================================
def build_data_zip():
    mem = io.BytesIO()
    try:
        with zipfile.ZipFile(mem, 'w', zipfile.ZIP_DEFLATED) as zf:
            user_details = {}
            try:
                for row in sqlite_exec("SELECT * FROM users", fetch="all") or []:
                    user_details[str(row.get("user_id"))] = row
            except Exception as _e:
                print(f"⚠️  ZIP users dump: {type(_e).__name__}")
            for uid, udata in user_cache.items():
                user_details[str(uid)] = udata
            zf.writestr("USER DETAILS/users.json", json.dumps(user_details, default=str, indent=4))
            zf.writestr("USER DETAILS/user_cache.json", json.dumps({str(k): v for k, v in user_cache.items()}, default=str, indent=4))
            zf.writestr("USER DETAILS/all_known_users.json", json.dumps(list(all_known_users), default=str, indent=4))
            try:
                pend = sqlite_exec("SELECT * FROM pending_referrals", fetch="all") or []
                zf.writestr("USER DETAILS/pending_referrals.json", json.dumps(pend, default=str, indent=4))
                paid = sqlite_exec("SELECT * FROM referral_paid_users", fetch="all") or []
                zf.writestr("USER DETAILS/referral_paid_users.json", json.dumps(paid, default=str, indent=4))
                wds = sqlite_exec("SELECT * FROM withdrawals ORDER BY timestamp DESC", fetch="all") or []
                zf.writestr("USER DETAILS/withdrawals.json", json.dumps(wds, default=str, indent=4))
            except Exception as _e:
                print(f"⚠️  ZIP user-details: {type(_e).__name__}")

            zf.writestr("NUMBERS/number_batches.json", json.dumps(number_batches, default=str, indent=4))
            zf.writestr("NUMBERS/used_numbers.json", json.dumps(used_numbers_list, default=str, indent=4))
            zf.writestr("NUMBERS/stex_assigned.json", json.dumps(stex_assigned_numbers, default=str, indent=4))
            zf.writestr("NUMBERS/voltx_assigned.json", json.dumps(voltx_assigned_numbers, default=str, indent=4))
            zf.writestr("NUMBERS/assigned_meta.json", json.dumps(assigned_number_meta, default=str, indent=4))
            zf.writestr("NUMBERS/stats.json", json.dumps({
                "total_uploaded_stats": total_uploaded_stats,
                "total_assigned_stats": total_assigned_stats
            }, default=str, indent=4))

            zf.writestr("COUNTRY AND SERVICE/premium_flags.json", json.dumps(bot_settings.get("premium_flags", {}), default=str, indent=4))
            zf.writestr("COUNTRY AND SERVICE/premium_apps.json", json.dumps(bot_settings.get("premium_apps", {}), default=str, indent=4))
            try:
                if os.path.exists(FLAG_TXT_FILE):
                    with open(FLAG_TXT_FILE, "r", encoding='utf-8') as f:
                        zf.writestr("COUNTRY AND SERVICE/flag.txt", f.read())
                if os.path.exists(SERVICE_TXT_FILE):
                    with open(SERVICE_TXT_FILE, "r", encoding='utf-8') as f:
                        zf.writestr("COUNTRY AND SERVICE/service.txt", f.read())
            except Exception:
                pass

            zf.writestr("SETTINGS/bot_settings.json", json.dumps(bot_settings, default=str, indent=4))
            zf.writestr("SETTINGS/custom_messages.json", json.dumps(bot_settings.get("custom_messages", {}), default=str, indent=4))
            try:
                sql_settings = sqlite_exec("SELECT * FROM settings", fetch="all") or []
                zf.writestr("SETTINGS/sqlite_settings.json", json.dumps(sql_settings, default=str, indent=4))
                sql_kv = sqlite_exec("SELECT * FROM kv_store", fetch="all") or []
                zf.writestr("SETTINGS/kv_store.json", json.dumps(sql_kv, default=str, indent=4))
            except Exception:
                pass

            fb_status = {
                "firebase_connected": db is not None,
                "firebase_status": "FIREBASE_ACTIVE" if (db and current_db_mode == "firebase") else "SQLITE_ONLY",
                "current_db_mode": current_db_mode,
                "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "bot_username": BOT_USERNAME,
                "owner_id": OWNER_ID
            }
            zf.writestr("FIREBASE/firebase_status.json", json.dumps(fb_status, default=str, indent=4))
            if db:
                try:
                    fs_users = {}
                    for doc in db.collection('users').stream():
                        fs_users[doc.id] = doc.to_dict()
                    zf.writestr("FIREBASE/firestore_users.json", json.dumps(fs_users, default=str, indent=4))
                except Exception:
                    pass
                try:
                    fs_wd = {}
                    for doc in db.collection('withdrawals').stream():
                        fs_wd[doc.id] = doc.to_dict()
                    zf.writestr("FIREBASE/firestore_withdrawals.json", json.dumps(fs_wd, default=str, indent=4))
                except Exception:
                    pass
                try:
                    stg = db.collection('settings').document('bot_config').get(timeout=8.0)
                    if stg.exists:
                        zf.writestr("FIREBASE/firestore_settings.json", json.dumps(stg.to_dict(), default=str, indent=4))
                except Exception:
                    pass

            zf.writestr("TRAFFIC/recent_traffic.json", json.dumps(recent_traffic, default=str, indent=4))

            zf.writestr("SYSTEM/export_info.json", json.dumps({
                "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "bot_username": BOT_USERNAME,
                "owner_id": OWNER_ID,
                "total_users_known": len(all_known_users),
                "total_user_cache": len(user_cache),
                "total_batches": len(number_batches),
                "total_available_numbers": sum(len(b["numbers"]) for b in number_batches.values()),
                "total_used_numbers": len(used_numbers_list)
            }, default=str, indent=4))
            try:
                if os.path.exists(DB_FILE):
                    with open(DB_FILE, "r", encoding='utf-8') as f:
                        zf.writestr("SYSTEM/local_db_backup.json", f.read())
            except Exception:
                pass

        mem.seek(0)
        return mem.getvalue()
    except Exception as e:
        print(f"⚠️  ZIP build error: {type(e).__name__}: {e}")
        return None


# ==========================================
# 📥 Restore from ZIP — actually applies data
# ==========================================
def restore_data_from_zip(raw_bytes):
    global number_batches, used_numbers_list, stex_assigned_numbers, voltx_assigned_numbers
    global total_uploaded_stats, total_assigned_stats, recent_traffic, assigned_number_meta
    global all_known_users, bot_settings, user_cache

    try:
        zf = zipfile.ZipFile(io.BytesIO(raw_bytes), 'r')
        names = set(zf.namelist())
    except Exception as e:
        return False, f"Invalid zip: {type(e).__name__}"

    def read_json(path, default=None):
        try:
            if path in names:
                return json.loads(zf.read(path).decode('utf-8'))
        except Exception as e:
            print(f"⚠️  restore read {path}: {type(e).__name__}")
        return default

    def read_text(path):
        try:
            if path in names:
                return zf.read(path).decode('utf-8')
        except Exception:
            pass
        return None

    restored = []

    try:
        new_bs = read_json("SETTINGS/bot_settings.json")
        if isinstance(new_bs, dict):
            for k, v in new_bs.items():
                bot_settings[k] = v
            restored.append("bot_settings")
    except Exception as e:
        print(f"⚠️  restore bot_settings: {type(e).__name__}")

    cm = read_json("SETTINGS/custom_messages.json")
    if isinstance(cm, dict) and cm:
        bot_settings["custom_messages"] = cm
        restored.append("custom_messages")

    users_map = read_json("USER DETAILS/users.json", {}) or {}
    if not isinstance(users_map, dict):
        users_map = {}
    uc_map = read_json("USER DETAILS/user_cache.json", {}) or {}
    if isinstance(uc_map, dict):
        for k, v in uc_map.items():
            users_map.setdefault(k, v)

    users_applied = 0
    try:
        with sqlite_tx() as conn:
            if conn:
                cur = conn.cursor()
                for uid_s, udata in users_map.items():
                    if not isinstance(udata, dict):
                        continue
                    try:
                        uid = int(uid_s)
                    except Exception:
                        continue
                    bal = float(udata.get("balance", 0.0) or 0.0)
                    refs = int(udata.get("total_refers", 0) or 0)
                    otps = int(udata.get("total_otps", 0) or 0)
                    banned = 1 if udata.get("banned") else 0
                    verified = 1 if udata.get("verified") else 0
                    rby = udata.get("referred_by")
                    try:
                        rby = int(rby) if rby else None
                    except Exception:
                        rby = None
                    paid = 1 if udata.get("ref_paid") else 0
                    cur.execute(
                        "INSERT INTO users(user_id, balance, total_refers, total_otps, banned, verified, referred_by, ref_paid, created_at, updated_at) "
                        "VALUES(?,?,?,?,?,?,?,?,?,?) "
                        "ON CONFLICT(user_id) DO UPDATE SET "
                        "balance=excluded.balance, total_refers=excluded.total_refers, "
                        "total_otps=excluded.total_otps, banned=excluded.banned, "
                        "verified=excluded.verified, referred_by=excluded.referred_by, "
                        "ref_paid=excluded.ref_paid, updated_at=excluded.updated_at",
                        (uid, bal, refs, otps, banned, verified, rby, paid, time.time(), time.time())
                    )
                    user_cache[uid] = {
                        "user_id": uid, "balance": bal, "total_refers": refs,
                        "total_otps": otps, "banned": bool(banned), "verified": bool(verified),
                    }
                    users_applied += 1
        restored.append(f"users({users_applied})")
    except Exception as e:
        print(f"⚠️  restore users: {type(e).__name__}")

    aku = read_json("USER DETAILS/all_known_users.json")
    if isinstance(aku, list):
        for u in aku:
            all_known_users.add(str(u))
        try:
            with open(USERS_LIST_FILE, "w") as f:
                json.dump(list(all_known_users), f)
            sqlite_kv_set("all_known_users", list(all_known_users))
        except Exception:
            pass
        restored.append(f"all_known_users({len(aku)})")

    pend = read_json("USER DETAILS/pending_referrals.json", []) or []
    if isinstance(pend, list) and pend:
        try:
            with sqlite_tx() as conn:
                if conn:
                    for row in pend:
                        if not isinstance(row, dict): continue
                        try:
                            conn.cursor().execute(
                                "INSERT OR IGNORE INTO pending_referrals(new_user_id, inviter_id, created_at) VALUES(?,?,?)",
                                (int(row.get("new_user_id")), int(row.get("inviter_id")), float(row.get("created_at") or time.time()))
                            )
                        except Exception: continue
            restored.append(f"pending_referrals({len(pend)})")
        except Exception:
            pass

    paid_list = read_json("USER DETAILS/referral_paid_users.json", []) or []
    if isinstance(paid_list, list) and paid_list:
        try:
            with sqlite_tx() as conn:
                if conn:
                    for row in paid_list:
                        if not isinstance(row, dict): continue
                        try:
                            conn.cursor().execute(
                                "INSERT OR IGNORE INTO referral_paid_users(user_id, paid_at) VALUES(?,?)",
                                (int(row.get("user_id")), float(row.get("paid_at") or time.time()))
                            )
                        except Exception: continue
            restored.append(f"referral_paid_users({len(paid_list)})")
        except Exception:
            pass

    wds = read_json("USER DETAILS/withdrawals.json", []) or []
    if isinstance(wds, list) and wds:
        try:
            with sqlite_tx() as conn:
                if conn:
                    for row in wds:
                        if not isinstance(row, dict): continue
                        try:
                            conn.cursor().execute(
                                "INSERT OR REPLACE INTO withdrawals(req_id, user_id, amount, method, number, full_name, status, timestamp) "
                                "VALUES(?,?,?,?,?,?,?,?)",
                                (
                                    str(row.get("req_id")),
                                    int(row.get("user_id") or 0),
                                    float(row.get("amount") or 0),
                                    str(row.get("method") or ""),
                                    str(row.get("number") or ""),
                                    str(row.get("full_name") or ""),
                                    str(row.get("status") or "pending"),
                                    float(row.get("timestamp") or time.time()),
                                )
                            )
                        except Exception: continue
            restored.append(f"withdrawals({len(wds)})")
        except Exception:
            pass

    nb = read_json("NUMBERS/number_batches.json")
    if isinstance(nb, dict):
        number_batches.clear()
        number_batches.update(nb)
        restored.append(f"number_batches({len(nb)})")

    un = read_json("NUMBERS/used_numbers.json")
    if isinstance(un, list):
        used_numbers_list.clear()
        used_numbers_list.extend(un)
        restored.append(f"used_numbers({len(un)})")

    sx = read_json("NUMBERS/stex_assigned.json")
    if isinstance(sx, dict):
        stex_assigned_numbers.clear()
        stex_assigned_numbers.update(sx)
        restored.append(f"stex_assigned({len(sx)})")

    vx = read_json("NUMBERS/voltx_assigned.json")
    if isinstance(vx, dict):
        voltx_assigned_numbers.clear()
        voltx_assigned_numbers.update(vx)
        restored.append(f"voltx_assigned({len(vx)})")

    am = read_json("NUMBERS/assigned_meta.json")
    if isinstance(am, dict):
        assigned_number_meta.clear()
        assigned_number_meta.update(am)
        restored.append(f"assigned_meta({len(am)})")

    stats = read_json("NUMBERS/stats.json", {})
    if isinstance(stats, dict):
        try:
            total_uploaded_stats = int(stats.get("total_uploaded_stats", total_uploaded_stats))
            total_assigned_stats = int(stats.get("total_assigned_stats", total_assigned_stats))
            restored.append("stats")
        except Exception:
            pass

    pf = read_json("COUNTRY AND SERVICE/premium_flags.json")
    if isinstance(pf, dict) and pf:
        bot_settings["premium_flags"] = pf
        restored.append(f"premium_flags({len(pf)})")

    pa = read_json("COUNTRY AND SERVICE/premium_apps.json")
    if isinstance(pa, dict) and pa:
        bot_settings["premium_apps"] = pa
        restored.append(f"premium_apps({len(pa)})")

    ft = read_text("COUNTRY AND SERVICE/flag.txt")
    if ft:
        try:
            with open(FLAG_TXT_FILE, "w", encoding='utf-8') as f:
                f.write(ft)
            restored.append("flag.txt")
        except Exception: pass
    st = read_text("COUNTRY AND SERVICE/service.txt")
    if st:
        try:
            with open(SERVICE_TXT_FILE, "w", encoding='utf-8') as f:
                f.write(st)
            restored.append("service.txt")
        except Exception: pass

    rt = read_json("TRAFFIC/recent_traffic.json")
    if isinstance(rt, list):
        recent_traffic.clear()
        recent_traffic.extend(rt)
        restored.append(f"recent_traffic({len(rt)})")

    try:
        sql_settings = read_json("SETTINGS/sqlite_settings.json", []) or []
        if isinstance(sql_settings, list) and sql_settings:
            with sqlite_tx() as conn:
                if conn:
                    for row in sql_settings:
                        if not isinstance(row, dict): continue
                        k = str(row.get("key") or "")
                        if not k: continue
                        try:
                            conn.cursor().execute(
                                "INSERT INTO settings(key,value,updated_at) VALUES(?,?,?) "
                                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                                (k, row.get("value"), float(row.get("updated_at") or time.time()))
                            )
                        except Exception: continue
            restored.append("sqlite_settings")
    except Exception:
        pass

    try:
        kv = read_json("SETTINGS/kv_store.json", []) or []
        if isinstance(kv, list) and kv:
            with sqlite_tx() as conn:
                if conn:
                    for row in kv:
                        if not isinstance(row, dict): continue
                        k = str(row.get("k") or "")
                        if not k: continue
                        try:
                            conn.cursor().execute(
                                "INSERT INTO kv_store(k,v,updated_at) VALUES(?,?,?) "
                                "ON CONFLICT(k) DO UPDATE SET v=excluded.v, updated_at=excluded.updated_at",
                                (k, row.get("v"), float(row.get("updated_at") or time.time()))
                            )
                        except Exception: continue
            restored.append("kv_store")
    except Exception:
        pass

    try:
        save_db()
        restored.append("persisted")
    except Exception as e:
        print(f"⚠️  restore save_db: {type(e).__name__}")

    zf.close()
    return True, ", ".join(restored)


def delete_all_data():
    global number_batches, used_numbers_list, stex_assigned_numbers, voltx_assigned_numbers
    global total_uploaded_stats, total_assigned_stats, recent_traffic, assigned_number_meta
    global all_known_users
    if db:
        try:
            for doc in db.collection('users').stream():
                try: doc.reference.delete()
                except Exception: pass
        except Exception as _e:
            print(f"⚠️  delete fs users: {type(_e).__name__}")
        try:
            for doc in db.collection('withdrawals').stream():
                try: doc.reference.delete()
                except Exception: pass
        except Exception as _e:
            print(f"⚠️  delete fs withdrawals: {type(_e).__name__}")
    try:
        with sqlite_tx() as conn:
            if conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM users")
                cur.execute("DELETE FROM pending_referrals")
                cur.execute("DELETE FROM referral_paid_users")
                cur.execute("DELETE FROM withdrawals")
    except Exception as _e:
        print(f"⚠️  delete sqlite: {type(_e).__name__}")
    number_batches = {}
    used_numbers_list = []
    stex_assigned_numbers = {}
    voltx_assigned_numbers = {}
    total_uploaded_stats = 0
    total_assigned_stats = 0
    recent_traffic = []
    assigned_number_meta = {}
    all_known_users = set()
    user_cache.clear()
    try:
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        if os.path.exists(USERS_LIST_FILE): os.remove(USERS_LIST_FILE)
    except Exception: pass
    save_local_db()


# ==========================================
# Callback Query Handler
# ==========================================
def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")

    if not data.startswith("test_p_conn_") and not data.startswith("c_n") and not data.startswith("g_c|") and not data.startswith("g_bs|") and not data.startswith("s_srv|"):
        try: threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except Exception: pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    msg_id = call["message"]["message_id"]

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 Banned!", show_alert=True)
            return

        if bot_settings.get("maintenance", False) and not is_admin(chat_id):
            allowed_cb = ["close_msg", "check_fj", "cancel_state", "ignore"]
            if data not in allowed_cb:
                maint_msg = (
                    f'<tg-emoji emoji-id="6267262260243076354">㊙️</tg-emoji> <b>The Bot Is On Under MENTENENCE.</b>\n\n'
                    f'Wait Some Time <tg-emoji emoji-id="5226560988291019577">🦕</tg-emoji> <b>Bot Will Available Soon</b> '
                    f'<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>'
                )
                send_message(chat_id, render_body_text(maint_msg))
                return

        if not check_force_join(chat_id) and data != "check_fj":
            send_force_join_msg(chat_id)
            return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Thanks for joining!</b>"), reply_markup=main_menu(chat_id))
            get_user(chat_id)
            check_and_pay_referral_for_user(chat_id)
        else:
            answer_callback(call["id"], "❌ Join all channels first!", show_alert=True)
        return

    if data == "close_msg":
        purge_pending_search_prompts(chat_id)
        delete_message(chat_id, msg_id)
    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        purge_pending_search_prompts(chat_id)
        delete_message(chat_id, msg_id)
    elif data == "cancel_2fa":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])
    elif data == "gen_2fa":
        user_states[chat_id] = "wait_for_2fa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])
    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret); code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            success_txt = (f"━━━━━━━━━━━━━━━\n《 🔐 <b>2FA CODE</b> 》\n━━━━━━━━━━━━━━━\n"
                          f"🔐 <b>CODE:</b> <code>{code}</code>\n━━━━━━━━━━━━━━━\n"
                          f"🕓 <b>EXPIRES IN:</b> <b>{remaining_time}s</b>\n━━━━━━━━━━━━━━━")
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except Exception:
            answer_callback(call["id"], "❌ Error!", show_alert=True)
    elif data == "cancel_dxa_edit":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>STORM CONTROL PANEL</b>"), reply_markup=storm_control_keyboard())
    elif data == "dummy_alert":
        answer_callback(call["id"], "Coming soon!", show_alert=True)
    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Refreshed!", show_alert=False)

    elif data.startswith("s_srv|"):
        parts = data.split("|", 2)
        query = parts[1] if len(parts) > 1 else ""
        service = parts[2] if len(parts) > 2 else ""

        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s", show_alert=True)
            return
        user_cooldowns[chat_id] = now
        expire_previous_number(chat_id)

        search_iso = temp_data.get(chat_id, {}).get("search_iso", "")
        search_country = temp_data.get(chat_id, {}).get("search_country", "")

        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing...</i>"))
        wait_msg_id = msg_id

        fetched_nums = []
        req_count = bot_settings.get("num_req", 1)

        for b_id, b_data in number_batches.items():
            if b_data.get("service", "").upper() != service.upper(): continue
            b_country = b_data.get("country", "").upper()
            b_iso = b_data.get("country_iso", "").upper()
            matched_country = False
            if search_country and b_country == search_country.upper(): matched_country = True
            if not matched_country and search_iso and search_iso != "XX" and b_iso == search_iso.upper(): matched_country = True
            if not matched_country:
                for n_obj in b_data["numbers"][:5]:
                    if n_obj["num"].replace("+", "").startswith(query):
                        matched_country = True
                        break
            if not matched_country: continue

            for idx, n_obj in enumerate(b_data["numbers"]):
                if len(fetched_nums) >= req_count: break
                if chat_id in n_obj.get("used_by", []): continue
                if not n_obj["num"].replace("+", "").startswith(query): continue

                num_str = n_obj["num"]
                fetched_nums.append(num_str)
                n_obj["shares"] += 1
                n_obj["used_by"].append(chat_id)
                total_assigned_stats += 1

                cn = num_str.replace("+", "").strip()
                _pv = float(bot_settings.get("otp_reward", 0.0))
                _pr = bot_settings.get("otp_pair_rates", {})
                _pk = f"{str(b_country).upper()}|{str(service).upper()}"
                if _pk in _pr:
                    try: _pv = float(_pr[_pk])
                    except Exception: pass
                if "payout" in b_data:
                    try: _pv = float(b_data["payout"])
                    except Exception: pass
                assigned_number_meta[cn] = {
                    "country": b_data.get("country", ""),
                    "service": b_data.get("service", ""),
                    "iso": b_data.get("country_iso", ""),
                    "payout": _pv
                }
                if n_obj["shares"] >= bot_settings.get("num_share", 1):
                    n_obj["to_remove"] = True
                    used_numbers_list.append(num_str)

            if len(fetched_nums) >= req_count: break

        for b_id in list(number_batches.keys()):
            number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]

        if len(fetched_nums) < req_count:
            stex_srv_data = bot_settings.get("stex_services", {}).get(service, {})
            stex_range = None
            for c_name, r_list in stex_srv_data.items():
                if search_country and c_name.upper() == search_country.upper():
                    for r in r_list:
                        if query.startswith(r): stex_range = r; break
                if stex_range: break
            if not stex_range:
                for c_name, r_list in stex_srv_data.items():
                    for r in r_list:
                        if query.startswith(r): stex_range = r; break
                    if stex_range: break

            if stex_range:
                for _ in range(req_count - len(fetched_nums)):
                    for api_key in bot_settings.get("stex_keys", []):
                        try:
                            res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers={"mauthapi": api_key}, timeout=10)
                            rd = res.json()
                            if rd.get("meta", {}).get("code") == 200 and rd.get("data"):
                                ns = str(rd["data"].get("no_plus_number", "")).replace("+", "")
                                if not ns: ns = str(rd["data"].get("national_number", ""))
                                fetched_nums.append(ns)
                                stex_assigned_numbers[ns] = chat_id
                                total_assigned_stats += 1
                                break
                        except Exception: continue

        if len(fetched_nums) < req_count:
            voltx_srv_data = bot_settings.get("voltx_services", {}).get(service, {})
            voltx_range = None
            for c_name, r_list in voltx_srv_data.items():
                if search_country and c_name.upper() == search_country.upper():
                    for r in r_list:
                        if query.startswith(r): voltx_range = r; break
                if voltx_range: break
            if not voltx_range:
                for c_name, r_list in voltx_srv_data.items():
                    for r in r_list:
                        if query.startswith(r): voltx_range = r; break
                    if voltx_range: break

            if voltx_range:
                for _ in range(req_count - len(fetched_nums)):
                    for api_key in bot_settings.get("voltx_keys", []):
                        try:
                            res = requests.post(f"{VOLTX_BASE_URL}/getnum", json={"rid": query}, headers={"mauthapi": api_key}, timeout=10)
                            rd = res.json()
                            if rd.get("meta", {}).get("code") == 200 and rd.get("data"):
                                ns = str(rd["data"].get("no_plus_number", "")).replace("+", "")
                                if not ns: ns = str(rd["data"].get("national_number", ""))
                                fetched_nums.append(ns)
                                voltx_assigned_numbers[ns] = chat_id
                                total_assigned_stats += 1
                                break
                        except Exception: continue

        save_db()

        purge_pending_search_prompts(chat_id, keep_msg_id=msg_id)

        if not fetched_nums:
            answer_callback(call["id"], "❌ Out of stock!", show_alert=True)
            delete_message(chat_id, wait_msg_id)
            return

        kb = []
        app_full_name, _ = get_service_info_html(service)
        emoji_id_srv = "5337302974806922068"
        for app_key, app_data in bot_settings.get("premium_apps", {}).items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data: emoji_id_srv = app_data["id"]; break
        kb.append([{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id_srv, "callback_data": "ignore", "style": "success"}])

        flags_db = bot_settings.get("premium_flags", {})
        for num in fetched_nums:
            _, iso = get_flag_and_code(num)
            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
            emoji_id = "5780471598932337683"
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data: emoji_id = flag_data["id"]
                    break
            kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])

        kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"s_srv|{query}|{service}", "style": "danger"},
                   {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])

        hdr_country = search_country or query
        text_numbers = build_numbers_header(hdr_country, service)
        edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
        user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
        return

    elif data.startswith("g_bs|"):
        user_states.pop(chat_id, None)
        temp_data.pop(chat_id, None)
        try:
            parts = data.split("|", 2)
            service = parts[1]; country = parts[2]
        except Exception:
            answer_callback(call["id"], "❌ Invalid!", show_alert=True); return
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s", show_alert=True)
            return
        user_cooldowns[chat_id] = now
        expire_previous_number(chat_id)
        available = []
        for bid, bd in number_batches.items():
            if bd["service"] == service and bd["country"] == country:
                for i, no in enumerate(bd["numbers"]):
                    if chat_id not in no.get("used_by", []):
                        available.append((bid, i))
        if not available:
            sd = bot_settings.get("stex_services", {}).get(service, {}).get(country)
            vd = bot_settings.get("voltx_services", {}).get(service, {}).get(country)
            target = None; is_vtx = False
            if sd: target = random.choice(sd)
            elif vd: target = random.choice(vd); is_vtx = True
            if target:
                user_cooldowns[chat_id] = 0
                vf = "vtx" if is_vtx else ""
                new_call = dict(call)
                new_call["data"] = f"c_n_s|{target}|{service}|{vf}"
                if "_edit_in_place" in call: new_call["_edit_in_place"] = call["_edit_in_place"]
                handle_callback(new_call); return
            else:
                answer_callback(call["id"], "❌ Out of stock!", show_alert=True); return
        random.shuffle(available)
        fetched = []
        for bid, i in available:
            if len(fetched) >= bot_settings["num_req"]: break
            no = number_batches[bid]["numbers"][i]
            fetched.append(no["num"]); no["shares"] += 1; no["used_by"].append(chat_id)
            total_assigned_stats += 1
            cn = no["num"].replace("+", "").strip()
            bd_country = number_batches[bid]["country"]; bd_service = number_batches[bid]["service"]
            bd_iso = number_batches[bid].get("country_iso", "")
            _pv = float(bot_settings.get("otp_reward", 0.0))
            _pr = bot_settings.get("otp_pair_rates", {}); _pk = f"{str(bd_country).upper()}|{str(bd_service).upper()}"
            if _pk in _pr:
                try: _pv = float(_pr[_pk])
                except Exception: pass
            if "payout" in number_batches[bid]:
                try: _pv = float(number_batches[bid]["payout"])
                except Exception: pass
            assigned_number_meta[cn] = {"country": bd_country, "service": bd_service, "iso": bd_iso, "payout": _pv}
            if no["shares"] >= bot_settings.get("num_share", 1):
                no["to_remove"] = True; used_numbers_list.append(no["num"])
        for bid in number_batches:
            number_batches[bid]["numbers"] = [n for n in number_batches[bid]["numbers"] if not n.get("to_remove")]
        save_db()
        af = get_premium_app(service)["name"]
        eid_srv = "5337302974806922068"
        for ak, ad in bot_settings.get("premium_apps", {}).items():
            if service.upper() == ak or service.upper() in ak or ak in service.upper():
                if "id" in ad: eid_srv = ad["id"]; break
        kb = [[{"text": af, "icon_custom_emoji_id": eid_srv, "callback_data": "ignore", "style": "success"}]]
        for num in fetched:
            dn = f"+{num}" if not str(num).startswith("+") else str(num)
            _, iso, _ = get_country_from_num(num)
            eid2 = "5780471598932337683"
            for fc, fd in bot_settings.get("premium_flags", {}).items():
                if iso == fd.get("iso"):
                    if "id" in fd: eid2 = fd["id"]; break
            kb.append([{"text": dn, "icon_custom_emoji_id": eid2, "copy_text": {"text": dn}, "style": "primary"}])
        kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_bs|{service}|{country}", "style": "danger"},
                   {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        text_numbers = build_numbers_header(country, service)
        edit_target = call.get("_edit_in_place")
        if edit_target:
            try:
                edit_message(chat_id, edit_target, text_numbers, reply_markup={"inline_keyboard": kb})
                user_active_sessions[chat_id] = {"msg_id": edit_target, "nums": fetched}
            except Exception:
                msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
                if msg_res and "result" in msg_res: user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched}
        else:
            msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
            if msg_res and "result" in msg_res: user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched}
        return
    elif data.startswith("c_n_bs|"):
        try:
            parts = data.split("|", 2); service = parts[1]; country = parts[2]
        except Exception:
            answer_callback(call["id"], "❌ Invalid!", show_alert=True); return
        new_call = dict(call)
        new_call["data"] = f"g_bs|{service}|{country}"
        new_call["_edit_in_place"] = msg_id
        handle_callback(new_call); return

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        country_stats = {}
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query):
                    iso = t.get("iso", "XX"); flag = t.get("flag", "🌍")
                    if iso not in country_stats: country_stats[iso] = {"count": 0, "flag": flag}
                    country_stats[iso]["count"] += 1
        if not country_stats:
            answer_callback(call["id"], "❌ No traffic!", show_alert=True); return
        kb = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]; c_name = iso
            emoji_id = "5780471598932337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    if "id" in fdata: emoji_id = fdata["id"]
                    break
            kb.append([{"text": f"{c_name} ({iso}) - {count} OTP", "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore:</b> {prem_app_html} <b>{app_full_name}</b>"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])
    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]; iso_query = parts[3]
        nums = []
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                    num = t.get("number", "").replace("+", "").strip()
                    if num: nums.append(num)
        if not nums:
            answer_callback(call["id"], "❌ No numbers!", show_alert=True); return
        known_ranges = set()
        for s_name, c_dict in bot_settings.get("stex_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list: known_ranges.add(r)
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r): r_counts[r] += 1; matched = True; break
            if not matched:
                if len(num) >= 7: r_counts[num[:7]] += 1
                else: r_counts[num] += 1
        r_list = r_counts.most_common(12)
        kb = []
        for r, count in r_list:
            kb.append([{"text": f"{r} ({count})", "icon_custom_emoji_id": "5352862640592949843", "copy_text": {"text": r}, "style": "primary"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges:</b> {prem_app_html} <b>{app_full_name}</b> - {prem_flag_html} <b>{iso_query}</b>"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())
    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Send User ID:</b>"), reply_markup=get_cancel_kb())
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Send User ID:</b>"), reply_markup=get_cancel_kb())
    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Send User ID:</b>"), reply_markup=get_cancel_kb())

    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text("🎨 <b>Menu Design Editor</b>"), reply_markup=menu_design_list_keyboard())
    elif data == "md_reset_defaults":
        bot_settings["custom_messages"] = DEFAULT_CUSTOM_MESSAGES.copy()
        save_db()
        answer_callback(call["id"], "✅ Reset!", show_alert=True)
    elif data.startswith("md_edit_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_edit_", "")
        cm_text = render_body_text(bot_settings["custom_messages"].get(key, {}).get("text", "..."))
        try:
            edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>{key.upper()}</b>\n\n{cm_text}"), reply_markup=menu_edit_options_keyboard(key))
        except Exception: pass
    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        user_states[chat_id] = "wait_for_menu_text"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Send new text for</b> <b>{key.upper()}:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})
    elif data.startswith("md_btns_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_btns_", "")
        try: edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Buttons:</b> <b>{key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except Exception: pass
    elif data.startswith("md_addbtn_"):
        key = data.replace("md_addbtn_", "")
        user_states[chat_id] = "wait_for_menu_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"➕ <b>Send:</b> <code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_btns_{key}", "style": "danger"}]]})
    elif data.startswith("md_delbtn_"):
        parts = data.split("_"); key = parts[2]; b_idx = int(parts[3])
        if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
            del bot_settings["custom_messages"][key]["buttons"][b_idx]
            save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Buttons:</b> <b>{key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        if bal < min_w:
            answer_callback(call["id"], f"❌ Min ${fmt_payout(min_w)} required!", show_alert=True); return
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>{method}</b>\n💰 <b>${fmt_payout(bal)}</b>\n\n<b>Enter amount:</b>"), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Send Service:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Send message to broadcast:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 <b>Upload a</b> <b>.txt</b> <b>file:</b>"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "delete_files":
        kb = []
        for b_id, b_data in number_batches.items():
            kb.append([{"text": f"{b_data['filename']} ({len(b_data['numbers'])})", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select:</b>" if len(kb) > 1 else "❌ <b>No files.</b>"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            del number_batches[b_id]; save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_used":
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Used:</b> <b>{len(used_numbers_list)}</b>"), reply_markup=kb)
    elif data == "show_unused":
        unused_count = sum(len(b["numbers"]) for b in number_batches.values())
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Unused:</b> <b>{unused_count}</b>"), reply_markup=kb)
    elif data == "dl_used":
        if not used_numbers_list:
            answer_callback(call["id"], "❌ None!", show_alert=True); return
        send_document(chat_id, "used_numbers.txt", "\n".join(used_numbers_list).encode('utf-8'))
        answer_callback(call["id"])
    elif data == "dl_unused":
        unused_list = [n["num"] for b in number_batches.values() for n in b["numbers"]]
        if not unused_list:
            answer_callback(call["id"], "❌ None!", show_alert=True); return
        send_document(chat_id, "unused_numbers.txt", "\n".join(unused_list).encode('utf-8'))
        answer_callback(call["id"])

    # ---------- Leaderboard ----------
    elif data == "lb_main":
        txt = "━━━━━━━━━━━━━━━\n《 📊 <b>LEADER BOARD</b> 》\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching...</i>"))
        try:
            if not db:
                all_users = []
                for uid, udata in user_cache.items():
                    u_copy = dict(udata)
                    u_copy["user_id"] = uid
                    all_users.append(u_copy)
                if not all_users:
                    try:
                        rows = sqlite_exec("SELECT * FROM users", fetch="all") or []
                        for r in rows:
                            all_users.append(r)
                    except Exception: pass

                if sub == "top_refs":
                    title = "TOP 10 REFERRERS (LOCAL)"
                    sorted_users = sorted(all_users, key=lambda u: u.get('total_refers', 0), reverse=True)[:10]
                    res_txt = ""; count = 1
                    for u in sorted_users:
                        if u.get('total_refers', 0) > 0:
                            pos_icon = leaderboard_pos_emoji(count)
                            res_txt += f"| {pos_icon} <a href='tg://user?id={u['user_id']}'>{u['user_id']}</a> → <b>{u.get('total_refers',0)}</b>\n"
                            count += 1
                    if not res_txt: res_txt = "No data available (local cache).\n"
                elif sub == "top_otps":
                    title = "TOP 10 OTP RECEIVERS (LOCAL)"
                    sorted_users = sorted(all_users, key=lambda u: u.get('total_otps', 0), reverse=True)[:10]
                    res_txt = ""; count = 1
                    for u in sorted_users:
                        if u.get('total_otps', 0) > 0:
                            pos_icon = leaderboard_pos_emoji(count)
                            res_txt += f"| {pos_icon} <a href='tg://user?id={u['user_id']}'>{u['user_id']}</a> → <b>{u.get('total_otps',0)}</b>\n"
                            count += 1
                    if not res_txt: res_txt = "No data available (local cache).\n"
                elif sub == "w_history":
                    title = "LAST 10 WITHDRAWALS (LOCAL)"
                    res_txt = ""
                    count = 1
                    try:
                        wrows = sqlite_exec("SELECT * FROM withdrawals ORDER BY timestamp DESC LIMIT 10", fetch="all") or []
                    except Exception:
                        wrows = []
                    for wd in wrows:
                        uid = wd.get('user_id', 'User')
                        amt = wd.get('amount', 0)
                        st = str(wd.get('status', 'pending')).lower()
                        stat_icon = "✅" if st == "approved" else "❌" if st == "rejected" else "⏳"
                        pos_icon = leaderboard_pos_emoji(count)
                        res_txt += f"| {pos_icon} <a href='tg://user?id={uid}'>{uid}</a> → <b>${fmt_payout(amt)}</b> {stat_icon}\n"
                        count += 1
                    if not res_txt: res_txt = "No local withdrawal data.\n"

                final_msg = f"━━━━━━━━━━━━━━━\n📊 <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━\n<i>⚠️ Firebase disabled — showing SQLite data</i>"
                kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
                edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})
                return

            if sub == "top_refs":
                title, field, limit = "TOP 10 REFERRERS", "total_refers", 10
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""; count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        pos_icon = leaderboard_pos_emoji(count)
                        res_txt += f"| {pos_icon} <a href='tg://user?id={u.id}'>{u.id}</a> → <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "No data.\n"
            elif sub == "top_otps":
                title, field, limit = "TOP 10 OTP RECEIVERS", "total_otps", 10
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""; count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        pos_icon = leaderboard_pos_emoji(count)
                        res_txt += f"| {pos_icon} <a href='tg://user?id={u.id}'>{u.id}</a> → <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "No data.\n"
            elif sub == "w_history":
                title, limit = "LAST 10 WITHDRAWALS", 10
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""; count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = "✅" if s in ["approved","success"] else "❌" if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    pos_icon = leaderboard_pos_emoji(count)
                    res_txt += f"| {pos_icon} <a href='tg://user?id={uid}'>{uid}</a> → <b>${fmt_payout(d.get('amount',0))}</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "No history.\n"
            final_msg = f"━━━━━━━━━━━━━━━\n📊 <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})
        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ {type(e).__name__}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>"), reply_markup=system_settings_keyboard(chat_id))

    elif data == "toggle_maintenance":
        current = bot_settings.get("maintenance", False)
        bot_settings["maintenance"] = not current
        save_db()
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        if bot_settings["maintenance"]:
            answer_callback(call["id"], "🔴 Maintenance Mode: ON", show_alert=True)
            maint_msg = (
                f'<tg-emoji emoji-id="6267262260243076354">㊙️</tg-emoji> <b>The Bot Is On Under MENTENENCE.</b>\n\n'
                f'Wait Some Time <tg-emoji emoji-id="5226560988291019577">🦕</tg-emoji> <b>Bot Will Available Soon</b> '
                f'<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>'
            )
            threading.Thread(target=broadcast_text_all, args=(render_body_text(maint_msg),), daemon=True).start()
        else:
            answer_callback(call["id"], "🟢 Maintenance Mode: OFF", show_alert=True)
            thanks_msg = (
                f'<tg-emoji emoji-id="6204104220694550861">🐷</tg-emoji> <b>Thanks For Qopareting With Us</b> '
                f'<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>\n'
                f'Now You Can Use The Bot Properly '
                f'<tg-emoji emoji-id="6267107057304868214">🪲</tg-emoji>'
            )
            threading.Thread(target=broadcast_text_all, args=(render_body_text(thanks_msg),), daemon=True).start()

    elif data == "database_menu":
        txt = f'{PEM["file"]} <b>DATABASE MANAGEMENT</b>\n━━━━━━━━━━━━━━━\n<i>Choose an option:</i>'
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=database_menu_keyboard())
    elif data == "db_download":
        wait = send_message(chat_id, render_body_text("⏳ <i>Preparing database zip...</i>"))
        wait_id = wait.get("result", {}).get("message_id")
        try:
            raw = build_data_zip()
            if wait_id: delete_message(chat_id, wait_id)
            if raw:
                send_document_bytes(chat_id, "STR_BOT_DATA.zip", raw)
                send_message(chat_id, render_body_text(f'{PEM["ok"]} <b>Database Downloaded!</b>'), reply_markup=database_menu_keyboard())
            else:
                send_message(chat_id, render_body_text(f'{PEM["no"]} <b>Failed to build zip!</b>'))
        except Exception as e:
            if wait_id: delete_message(chat_id, wait_id)
            send_message(chat_id, render_body_text(f'❌ Error: {html.escape(str(e))}'))
    elif data == "db_upload":
        user_states[chat_id] = "wait_for_data_zip"
        edit_message(chat_id, msg_id, render_body_text("📂 Send <code>STR_BOT_DATA.zip</code>:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "database_menu", "style": "danger"}]]})
    elif data == "db_delete_confirm":
        txt = f'<tg-emoji emoji-id="6203773684306418660">❓</tg-emoji> <b>DO YOU REALLY WANT TO REMOVE ALL DATA?</b>'
        kb = {"inline_keyboard": [
            [{"text": "YES REMOVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "db_delete_yes", "style": "success"}],
            [{"text": "NO DON'T REMOVE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "db_delete_no", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
    elif data == "db_delete_yes":
        delete_all_data()
        edit_message(chat_id, msg_id, render_body_text(f'{PEM["ok"]} <b>All data removed!</b>'), reply_markup=database_menu_keyboard())
    elif data == "db_delete_no":
        edit_message(chat_id, msg_id, render_body_text(f'{PEM["ok"]} <b>Cancelled.</b>'), reply_markup=database_menu_keyboard())

    elif data == "change_payout_menu":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        all_services = sorted(local_srvs.union(stex_srvs).union(voltx_srvs))
        if not all_services:
            edit_message(chat_id, msg_id, render_body_text(f'{PEM["no"]} <b>No services!</b>'), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]]})
            return
        apps_db = bot_settings.get("premium_apps", {})
        kb = []; row = []
        for s in all_services:
            emoji_id = "5352694861990501856"
            for ak, ad in apps_db.items():
                if s.upper() == ak or s.upper() in ak or ak in s.upper():
                    if "id" in ad: emoji_id = ad["id"]; break
            row.append({"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"cp_srv|{s}", "style": "primary"})
            if len(row) == 2: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
        txt = f'<tg-emoji emoji-id="5190899075968441286">💳</tg-emoji> <b>CHANGE PAYOUT</b>\n━━━━━━━━━━━━━━━\n📌 <b>Select Service:</b>'
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
    elif data.startswith("cp_srv|"):
        srv = data.replace("cp_srv|", "")
        local_cnts = set()
        for b in number_batches.values():
            if b["service"] == srv and b["numbers"]: local_cnts.add(b["country"])
        stex_cnts = set(bot_settings.get("stex_services", {}).get(srv, {}).keys())
        voltx_cnts = set(bot_settings.get("voltx_services", {}).get(srv, {}).keys())
        all_countries = sorted(local_cnts.union(stex_cnts).union(voltx_cnts))
        if not all_countries:
            edit_message(chat_id, msg_id, render_body_text(f'{PEM["no"]} <b>No countries!</b>'), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "change_payout_menu", "style": "primary"}]]})
            return
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in all_countries:
            emoji_id = "5780471598932337683"
            for fc, fd in flags_db.items():
                iso = fd.get("iso", "").upper(); name = fd.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in fd: emoji_id = fd["id"]; break
            kb.append([{"text": f"{c}", "icon_custom_emoji_id": emoji_id, "callback_data": f"cp_cnt|{srv}|{c}", "style": "primary"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "change_payout_menu", "style": "danger"}])
        txt = f'<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji> <b>Select Country for {srv}:</b>'
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
    elif data.startswith("cp_cnt|"):
        parts = data.split("|", 2)
        srv = parts[1]; country = parts[2]
        pr = bot_settings.get("otp_pair_rates", {})
        key = f"{country.upper()}|{srv.upper()}"
        if key in pr:
            try: current_payout = float(pr[key])
            except Exception: current_payout = float(bot_settings.get("otp_reward", 0.0))
        else:
            current_payout = None
            for k, v in pr.items():
                try:
                    if k.split("|")[0] == country.upper():
                        current_payout = float(v); break
                except Exception: pass
            if current_payout is None:
                current_payout = float(bot_settings.get("otp_reward", 0.0))
        country_flag = get_flag_info_html(country)
        user_states[chat_id] = "set_payout_value"
        temp_data[chat_id] = {"msg_id": msg_id, "service": srv, "country": country}
        txt = (
            f'<b>{country}</b>{country_flag} <b>Payout :</b> <code>${fmt_payout(current_payout)}</code>\n\n'
            f'<b>Send The New Value</b> <code>country_payout</code> :'
        )
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "stex_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control</b>\n\n<b>Keys:</b> <b>{len(bot_settings.get('stex_keys', []))}</b>"), reply_markup=stex_control_keyboard())
    elif data == "add_stex_key":
        user_states[chat_id] = "wait_for_add_stex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Send StexSMS API Key:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}]]})
    elif data == "view_stex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("stex_keys", [])):
            safe_name = key[:10] + "..." if len(key) > 10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_nxa_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select:</b>"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("del_nxa_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("stex_keys", [])):
            del bot_settings["stex_keys"][idx]; save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_stex_keys", "id": call["id"]})
    elif data == "stex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_sc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Countries:</b>"), reply_markup={"inline_keyboard": kb})
    elif data == "add_search_country":
        user_states[chat_id] = "wait_for_add_sc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Country Code:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_search_country", "style": "danger"}]]})
    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("search_countries", [])):
            del bot_settings["search_countries"][idx]; save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "stex_search_country", "id": call["id"]})
    elif data == "manage_stex_srv":
        kb = []
        srvs = bot_settings.get("stex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "nx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📦 <b>StexSMS Services</b>"), reply_markup={"inline_keyboard": kb})
    elif data == "nx_add_srv":
        user_states[chat_id] = "wait_nx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Service Name:</b>"), reply_markup=get_cancel_kb())
    elif data.startswith("nx_srv_"):
        srv = data.replace("nx_srv_", "")
        kb = []
        countries = bot_settings["stex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598932337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper(); name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])})", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_stex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>{srv}</b>"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("nx_add_cnt_"):
        srv = data.replace("nx_add_cnt_", "")
        user_states[chat_id] = "wait_nx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 <b>Country for {srv}:</b>"), reply_markup=get_cancel_kb())
    elif data.startswith("nx_cnt_"):
        parts = data.split("_"); srv, cnt = parts[2], parts[3]
        ranges = bot_settings["stex_services"][srv].get(cnt, [])
        kb = []; row = []
        for r in ranges:
            row.append({"text": f"Del {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"nx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>{srv} | {cnt}</b>\n<b>Ranges:</b> <b>{len(ranges)}</b>"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("nx_addr_"):
        parts = data.split("_"); srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_nx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>New Range for {cnt}:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_cnt_{srv}_{cnt}", "style": "danger"}]]})
    elif data.startswith("nx_dr_"):
        parts = data.split("_"); srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["stex_services"].get(srv, {}).get(cnt, []):
            bot_settings["stex_services"][srv][cnt].remove(rng); save_db()
            answer_callback(call["id"], f"✅ {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_cnt_{srv}_{cnt}", "id": call["id"]})
    elif data.startswith("nx_del_srv_"):
        srv = data.replace("nx_del_srv_", "")
        if srv in bot_settings["stex_services"]: del bot_settings["stex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_stex_srv", "id": call["id"]})
    elif data.startswith("nx_del_cnt_"):
        parts = data.split("_"); srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["stex_services"].get(srv, {}): del bot_settings["stex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_srv_{srv}", "id": call["id"]})

    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control</b>\n\n<b>Keys:</b> <b>{len(bot_settings.get('voltx_keys', []))}</b>"), reply_markup=voltx_control_keyboard())
    elif data == "add_voltx_key":
        user_states[chat_id] = "wait_for_add_voltx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Send Voltx API Key:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})
    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key) > 10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select:</b>"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_keys", [])):
            del bot_settings["voltx_keys"][idx]; save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_voltx_keys", "id": call["id"]})
    elif data == "voltx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("voltx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Voltx Ranges:</b>"), reply_markup={"inline_keyboard": kb})
    elif data == "add_voltx_search_country":
        user_states[chat_id] = "wait_for_add_vsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Range Code:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})
    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_search_countries", [])):
            del bot_settings["voltx_search_countries"][idx]; save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": call["id"]})
    elif data == "manage_voltx_srv":
        kb = []
        srvs = bot_settings.get("voltx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Voltx Services</b>"), reply_markup={"inline_keyboard": kb})
    elif data == "vx_add_srv":
        user_states[chat_id] = "wait_vx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Service Name:</b>"), reply_markup=get_cancel_kb())
    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598932337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper(); name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])})", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_voltx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>{srv}</b>"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("vx_add_cnt_"):
        srv = data.replace("vx_add_cnt_", "")
        user_states[chat_id] = "wait_vx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 <b>Country for {srv}:</b>"), reply_markup=get_cancel_kb())
    elif data.startswith("vx_cnt_"):
        parts = data.split("_"); srv, cnt = parts[2], parts[3]
        ranges = bot_settings["voltx_services"][srv].get(cnt, [])
        kb = []; row = []
        for r in ranges:
            row.append({"text": f"Del {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>{srv} | {cnt}</b>\n<b>Ranges:</b> <b>{len(ranges)}</b>"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("vx_addr_"):
        parts = data.split("_"); srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>New Range for {cnt}:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})
    elif data.startswith("vx_dr_"):
        parts = data.split("_"); srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["voltx_services"].get(srv, {}).get(cnt, []):
            bot_settings["voltx_services"][srv][cnt].remove(rng); save_db()
            answer_callback(call["id"], f"✅ {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": call["id"]})
    elif data.startswith("vx_del_srv_"):
        srv = data.replace("vx_del_srv_", "")
        if srv in bot_settings["voltx_services"]: del bot_settings["voltx_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": call["id"]})
    elif data.startswith("vx_del_cnt_"):
        parts = data.split("_"); srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["voltx_services"].get(srv, {}): del bot_settings["voltx_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": call["id"]})

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN</b>"), reply_markup=fj_settings_keyboard())
    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]; save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN</b>"), reply_markup=fj_settings_keyboard())
    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Channel @ or ID:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})
    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            del bot_settings["fj_channels"][idx]; save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN</b>"), reply_markup=fj_settings_keyboard())

    # ---------- ADMIN MANAGEMENT (owner-only guard) ----------
    elif data == "manage_admins":
        if chat_id != OWNER_ID:
            answer_callback(call["id"], "🚫 Only OWNER can manage admins!", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>"), reply_markup=admin_settings_keyboard())
    elif data == "add_adm":
        if chat_id != OWNER_ID:
            answer_callback(call["id"], "🚫 Only OWNER can add admins!", show_alert=True)
            return
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>User ID:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})
    elif data.startswith("del_adm_"):
        if chat_id != OWNER_ID:
            answer_callback(call["id"], "🚫 Only OWNER can delete admins!", show_alert=True)
            return
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]; save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>"), reply_markup=otp_groups_list_keyboard())
    elif data == "edit_main_channel_link":
        user_states[chat_id] = "wait_for_main_channel_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        cur = bot_settings.get("main_channel_link", "") or "Not Set"
        edit_message(chat_id, msg_id, render_body_text(f"📢 <b>Channel Link</b>\n\n<b>Current:</b> <code>{html.escape(cur)}</code>\n\n<b>Send new URL:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})
    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Group ID/Username:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})
    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Group:</b> <b>{grp_id}</b>"), reply_markup=specific_fw_group_keyboard(idx))
    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 <code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})
    elif data.startswith("del_fwbtn_"):
        parts = data.split("_"); idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]; save_db()
                answer_callback(call["id"], "✅ Deleted!", show_alert=True)
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Group:</b> <b>{bot_settings['fw_groups'][idx]['chat_id']}</b>"), reply_markup=specific_fw_group_keyboard(idx))
    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]; save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>"), reply_markup=otp_groups_list_keyboard())
    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>OTP Group Link:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        api_count = len([p for p in bot_settings["panels"] if p.get("type") == "API Panel"])
        cpt_count = len([p for p in bot_settings["panels"] if p.get("type", "API Panel") == "Auto Captcha Panel"])
        text = f"{PEM['gear']} <b>Panel Management</b>"
        kb = {"inline_keyboard": [
            [{"text": f"API Panels ({api_count})", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "manage_api_panels", "style": "primary"}],
            [{"text": f"Auto Captcha ({cpt_count})", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "manage_cpt_panels", "style": "success"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=kb)
    elif data in ["manage_api_panels", "manage_cpt_panels"]:
        p_type = "API Panel" if data == "manage_api_panels" else "Auto Captcha Panel"
        p_list = [p for p in bot_settings["panels"] if p.get("type", "API Panel") == p_type]
        icon = f"{PEM['world']} <b>API</b>" if p_type == 'API Panel' else f"{PEM['lock']} <b>Auto Captcha</b>"
        text = f"{icon} <b>{p_type}s</b>\n\n"
        text += f"👀 <b>Active Monitors:</b> <b>{len(p_list)}</b>\n\n"
        text += f"🟢 <b>Available Providers:</b>\n"
        for p in p_list:
            status_icon = "🟢" if p['status'] == 'ON' else "🔴"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                if "Active" in login_state:
                    conf = f"✅ <b>{login_state}</b>"
                elif login_state:
                    conf = f"⏳ <b>{login_state}</b>"
                else:
                    conf = f"⚙️ <b>Configured</b>"
            else:
                conf = f"✅ <b>Configured</b>" if (p.get('api_url') or p.get('curl_command')) else f"❌ <b>Not Configured</b>"
            text += f"• <b>{p['name']}</b>: {status_icon} {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))
    elif data in ["add_api_panel", "add_cpt_panel"]:
        user_states[chat_id] = "wait_for_panel_name"
        p_type = "api" if data == "add_api_panel" else "logc"
        temp_data[chat_id] = {"msg_id": msg_id, "add_type": p_type}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Provider name:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='api' else 'cpt'}_panels", "style": "danger"}]]})
    elif data in ["list_del_api", "list_del_cpt"]:
        p_type = "API Panel" if data == "list_del_api" else "Auto Captcha Panel"
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            if p.get("type", "API Panel") == p_type:
                kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Delete Provider</b>"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(bot_settings["panels"]):
            p_type = bot_settings["panels"][idx].get("type", "API Panel")
            del bot_settings["panels"][idx]; save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "id": "internal"})
    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            p["status"] = "ON" if p["status"] == "OFF" else "OFF"
            save_db()
            if p["type"] == "Auto Captcha Panel":
                status_icon = "🟢" if p['status'] == 'ON' else "🔴"
                login_icon = "✅" if "Active" in str(p.get('login_status', '')) else "⏳"
                text = (f"{PEM['gear']} <b>Configure {p['name']}</b>\n\n"
                        f"📌 <b>Type:</b> <b>{p['type']}</b>\n"
                        f"{status_icon} <b>Status:</b> <b>{p['status']}</b>\n"
                        f"{login_icon} <b>Login:</b> <b>{p.get('login_status', '?')}</b>\n"
                        f"🔗 <b>URL:</b> <code>{p.get('login_url', 'None')}</code>")
            else:
                status_icon = "🟢" if p['status'] == 'ON' else "🔴"
                text = (f"{PEM['gear']} <b>Configure {p['name']}</b>\n\n"
                        f"📌 <b>Type:</b> <b>{p['type']}</b>\n"
                        f"{status_icon} <b>Status:</b> <b>{p['status']}</b>\n"
                        f"🌐 <b>API:</b> <code>{p.get('api_url', 'None')}</code>\n"
                        f"🔐 <b>Token:</b> <code>{p.get('token', 'None')}</code>")
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))
    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            if p["type"] == "Auto Captcha Panel":
                status_icon = "🟢" if p['status'] == 'ON' else "🔴"
                login_icon = "✅" if "Active" in str(p.get('login_status', '')) else "⏳"
                text = (f"{PEM['gear']} <b>Configure {p['name']}</b>\n\n"
                        f"📌 <b>Type:</b> <b>{p['type']}</b>\n"
                        f"{status_icon} <b>Status:</b> <b>{p['status']}</b>\n"
                        f"{login_icon} <b>Login:</b> <b>{p.get('login_status', '?')}</b>\n"
                        f"🔗 <b>URL:</b> <code>{p.get('login_url', 'None')}</code>\n"
                        f"👤 <b>User:</b> <code>{p.get('username', 'None')}</code>\n"
                        f"🔢 <b>Num Col:</b> <b>{p.get('num_col_name')}</b> (Idx: <code>{p.get('num_col_idx')}</code>)\n"
                        f"✉️ <b>Msg Col:</b> <b>{p.get('msg_col_name')}</b> (Idx: <code>{p.get('msg_col_idx')}</code>)\n"
                        f"🔧 <b>Svc Col:</b> <b>{p.get('service_col_name', 'None')}</b> (Idx: <code>{p.get('service_col_idx', 'None')}</code>)")
            else:
                status_icon = "🟢" if p['status'] == 'ON' else "🔴"
                text = (f"{PEM['gear']} <b>Configure {p['name']}</b>\n\n"
                        f"📌 <b>Type:</b> <b>{p['type']}</b>\n"
                        f"{status_icon} <b>Status:</b> <b>{p['status']}</b>\n"
                        f"🌐 <b>API:</b> <code>{p.get('api_url', 'None')}</code>\n"
                        f"🔐 <b>Token:</b> <code>{p.get('token', 'None')}</code>")
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))
    elif data.startswith("api_pf|"):
        parts = data.split("|")
        idx = int(parts[1]); field = parts[2]
        p = bot_settings["panels"][idx]
        if field == "token":
            val = p.get(field, ""); display = ('*' * len(str(val))) if val else "Not set"
        else:
            display = str(p.get(field, "")) or "Not set"
        label = field
        for lbl, fld, _ in API_PANEL_FIELDS:
            if fld == field: label = lbl; break
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx, "p_field": field}
        user_states[chat_id] = "wait_for_api_pf_value"
        edit_message(chat_id, msg_id, render_body_text(f"✏️ <b>Edit {label}</b>\n\n<b>Current:</b>\n<code>{html.escape(display)}</code>\n\n<b>Send new value:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})
    elif data.startswith("set_p_rec_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_rec"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Records count (0=Unlimited):</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⌛ <i>Testing connection...</i>"))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])
        try:
            parsed = []; raw_text = ""
            if p["type"] == "Auto Captcha Panel":
                sess = panel_sessions.get(idx)
                if not sess:
                    success = attempt_auto_login(p, idx)
                    if not success:
                        if wait_msg_id: delete_message(chat_id, wait_msg_id)
                        send_message(chat_id, render_body_text(f"❌ <b>Login Failed!</b>\n{html.escape(str(p.get('login_status', 'Unknown')))}"))
                        return
                    sess = panel_sessions.get(idx)
                login_url = p.get("login_url", "").strip()
                if not login_url.startswith("http"): login_url = "http://" + login_url
                msg_link = p.get("msg_link", "").strip()
                if not msg_link.startswith("http") and msg_link != "": msg_link = "http://" + msg_link
                check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
                parsed, raw_text = fetch_cpt_panel_cdrs(p, sess, check_url)
            else:
                url = p.get("api_url", "").strip()
                token = p.get("token", "").strip()
                curl_cmd = p.get("curl_command", "").strip()
                if not url and not curl_cmd:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Set API URL or CURL first!")); return
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                if curl_cmd:
                    try:
                        parsed_curl = parse_curl_command(curl_cmd)
                        curl_url = parsed_curl.get("url", "")
                        curl_method = parsed_curl.get("method", "GET")
                        curl_headers = parsed_curl.get("headers", {})
                        curl_headers.setdefault("User-Agent", headers["User-Agent"])
                        if curl_url:
                            if curl_method.upper() == "POST":
                                res = requests.post(curl_url, headers=curl_headers, timeout=15)
                            else:
                                res = requests.get(curl_url, headers=curl_headers, timeout=15)
                            raw_text = res.text
                            parsed = parse_panel_response(raw_text, p)
                    except Exception: pass
                if not parsed and url:
                    urls_to_try = []
                    if "{token}" in url or "{key}" in url:
                        urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                    elif "token=" in url or "key=" in url:
                        urls_to_try.append(url)
                    else:
                        sep = '&' if '?' in url else '?'
                        urls_to_try.append(f"{url}{sep}token={token}")
                        urls_to_try.append(f"{url}{sep}key={token}&start=0")
                        urls_to_try.append(f"{url}{sep}key={token}")
                    for try_url in urls_to_try:
                        try:
                            res = requests.get(try_url, headers=headers, timeout=10)
                            raw_text = res.text
                            parsed = parse_panel_response(raw_text, p)
                            if parsed:
                                if try_url != url and token:
                                    p["api_url"] = try_url.replace(token, "{token}")
                                    save_db()
                                break
                        except Exception: pass
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            if parsed:
                txt = f"{PEM['ok']} <b>Connection Successful!</b>\n\n<b>Sample (Max 3):</b>\n\n"
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']; msg = sample['message']; otp = sample['otp']
                    svc_name = sample.get('service_name', '').strip()
                    detected_app = detect_service(msg)
                    app_name = detected_app if detected_app else (svc_name or p.get("name", "Unknown"))
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg)
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 <code>{num}</code>\n📝 <code>{html.escape(msg[:120])}</code>\n🔐 <code>{otp}</code>\n"
                    if svc_name: txt += f"🔧 <b>Raw Svc:</b> <code>{html.escape(svc_name)}</code>\n"
                    txt += "➖" * 12 + "\n"
                send_message(chat_id, render_body_text(txt))
            else:
                if p["type"] == "Auto Captcha Panel":
                    try:
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            full_table_data = "FULL TABLE DATA\n" + "="*50 + "\n\n"
                            for t_idx, table in enumerate(tables):
                                full_table_data += f"--- Table {t_idx+1} ---\n"
                                rows = table.find_all('tr')
                                for r_idx, row in enumerate(rows):
                                    cols = row.find_all(['th', 'td'])
                                    col_texts = [f"[{c_idx+1}] {c.get_text(separator=' ', strip=True)}" for c_idx, c in enumerate(cols)]
                                    full_table_data += f"Row {r_idx+1}: {' | '.join(col_texts)}\n"
                                full_table_data += "\n" + "="*50 + "\n"
                            send_document(chat_id, f"Full_Panel_Data_{idx}.txt", full_table_data.encode('utf-8'))
                            send_message(chat_id, render_body_text("⚠️ <b>Connected, but couldn't parse OTP!</b>"))
                        else:
                            send_message(chat_id, render_body_text("⚠️ <b>Connected, no HTML Table!</b>"))
                    except Exception as e:
                        send_message(chat_id, render_body_text(f"❌ <b>HTML error:</b> {html.escape(str(e))}"))
                else:
                    safe_html = html.escape(str(raw_text)[:300])
                    send_message(chat_id, render_body_text(f"⚠️ <b>Connected, no OTP parsed.</b>\n\n<b>Raw:</b>\n<code>{safe_html}...</code>"))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Failed!</b>\n{html.escape(str(e))}"))

    elif data == "dxa_control":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>STORM CONTROL PANEL</b>"), reply_markup=storm_control_keyboard())
    elif data == "dxa_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]; save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>STORM CONTROL PANEL</b>"), reply_markup=storm_control_keyboard())
    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>"), reply_markup=w_methods_keyboard())
    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send in format:\n<code>{method_name} | {emoji_id}</code>\n\nExample:\n<code>Nagad | 5190899075968441286</code>\n\nOr just name for default emoji."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})
    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]; save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>"), reply_markup=w_methods_keyboard())
    elif data.startswith("dxa_"):
        key = data.replace("dxa_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link", "w_group": "w_group"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_dxa"
            edit_message(chat_id, msg_id, render_body_text(f"📝 <b>New value for</b> <code>{key_map[key]}</code><b>:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_dxa_edit", "style": "danger"}]]})
            answer_callback(call["id"])

    elif data.startswith("g_s|"):
        user_states.pop(chat_id, None); temp_data.pop(chat_id, None)
        service = data.split("g_s|", 1)[1]
        local_cnts = set([b["country"] for b in number_batches.values() if b["service"] == service and b["numbers"]])
        stex_cnts = set(bot_settings.get("stex_services", {}).get(service, {}).keys())
        voltx_cnts = set(bot_settings.get("voltx_services", {}).get(service, {}).keys())
        all_countries = local_cnts.union(stex_cnts).union(voltx_cnts)
        svc_app = get_premium_app(service)
        svc_full_name = svc_app.get("name", service).upper()
        svc_id = svc_app.get("id", ""); svc_char = svc_app.get("emoji", "📱")
        if re.match(r'^[A-Za-z0-9#]{1,4}$', str(svc_char)):
            svc_char = "📱"
        if svc_id and str(svc_id).isdigit() and len(str(svc_id)) >= 10:
            svc_html = f'<tg-emoji emoji-id="{svc_id}">{svc_char}</tg-emoji>'
        else:
            svc_html = svc_char
        header_txt = f'📌 <b>Select a country for</b> {svc_html} <b>{html.escape(svc_full_name)}:</b>'
        txt = render_body_text(header_txt)
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in sorted(all_countries):
            c_iso = ""
            for b in number_batches.values():
                if b.get("service") == service and b.get("country") == c:
                    c_iso = b.get("country_iso", "")
                    if c_iso: break
            emoji_id = None
            country_display_name = c
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper(); name = flag_data.get("name", "").upper()
                if (c_iso and c_iso.upper() == iso) or c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data and flag_data["id"]: emoji_id = flag_data["id"]
                    if not c_iso: country_display_name = flag_data.get("name", c)
                    break
            live_count = 0
            for b in number_batches.values():
                if b["service"] == service and b["country"] == c: live_count += len(b["numbers"])
            live_count += len(bot_settings.get("stex_services", {}).get(service, {}).get(c, []))
            live_count += len(bot_settings.get("voltx_services", {}).get(service, {}).get(c, []))
            payout_val = float(bot_settings.get("otp_reward", 0.0))
            pr = bot_settings.get("otp_pair_rates", {}); key = f"{c.upper()}|{service.upper()}"
            if key in pr:
                try: payout_val = float(pr[key])
                except Exception: pass
            payout_str = f"${fmt_payout(payout_val)}"
            btn_label = f"{country_display_name} | {live_count} | {payout_str}/OTP"
            btn_obj = {"text": btn_label, "callback_data": f"g_c|{service}|{c}", "style": "success"}
            if emoji_id: btn_obj["icon_custom_emoji_id"] = emoji_id
            kb.append([btn_obj])
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "close_msg", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_c|") or data.startswith("c_n"):
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s", show_alert=True); return
        user_cooldowns[chat_id] = now
        expire_previous_number(chat_id)

        if data.startswith("c_n_s|"):
            parts_s = data.split("|")
            query = parts_s[1] if len(parts_s) > 1 else ""
            service_from_cb = parts_s[2] if len(parts_s) > 2 and parts_s[2] else None
            is_voltx_req = len(parts_s) > 3 and parts_s[3] == "vtx"
            allowed_countries = bot_settings.get("search_countries", [])
            voltx_allowed = bot_settings.get("voltx_search_countries", [])
            is_stex_allowed = any(query.startswith(c) for c in allowed_countries) if allowed_countries else False
            is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
            if not is_voltx_req and not is_stex_allowed and not is_voltx_allowed:
                answer_callback(call["id"], "❌ Country not allowed!", show_alert=True); return
            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing...</i>"))
            wait_msg_id = msg_id
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            fetched_nums = []
            if not found_indices:
                api_found = False
                if is_voltx_req:
                    for _ in range(bot_settings.get("num_req", 1)):
                        for api_key in bot_settings.get("voltx_keys", []):
                            try:
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json={"rid": query}, headers={"mauthapi": api_key}, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str); voltx_assigned_numbers[num_str] = chat_id
                                    api_found = True; total_assigned_stats += 1; break
                            except Exception: continue
                else:
                    for _ in range(bot_settings.get("num_req", 1)):
                        for api_key in bot_settings.get("stex_keys", []):
                            try:
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers={"mauthapi": api_key}, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str); stex_assigned_numbers[num_str] = chat_id
                                    api_found = True; total_assigned_stats += 1; break
                            except Exception: continue
                if not api_found:
                    answer_callback(call["id"], "❌ Out of stock!", show_alert=True)
                    delete_message(chat_id, wait_msg_id); return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]; fetched_nums.append(num_str)
                    n_obj["shares"] += 1; n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    cn = num_str.replace("+", "").strip()
                    bd_country = number_batches[b_id]["country"]; bd_service = number_batches[b_id]["service"]
                    bd_iso = number_batches[b_id].get("country_iso", "")
                    _pv = float(bot_settings.get("otp_reward", 0.0))
                    if "payout" in number_batches[b_id]:
                        try: _pv = float(number_batches[b_id]["payout"])
                        except Exception: pass
                    assigned_number_meta[cn] = {"country": bd_country, "service": bd_service, "iso": bd_iso, "payout": _pv}
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True; used_numbers_list.append(num_str)
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
            purge_pending_search_prompts(chat_id)
            kb = []
            if service_from_cb:
                app_full_name, _ = get_service_info_html(service_from_cb)
                emoji_id_srv = "5337302974806922068"
                for app_key, app_data in bot_settings.get("premium_apps", {}).items():
                    if service_from_cb.upper() == app_key or service_from_cb.upper() in app_key or app_key in service_from_cb.upper():
                        if "id" in app_data: emoji_id_srv = app_data["id"]; break
                kb.append([{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id_srv, "callback_data": "ignore", "style": "success"}])
            flags_db = bot_settings.get("premium_flags", {})
            for num in fetched_nums:
                _, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                emoji_id = "5780471598932337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: emoji_id = flag_data["id"]; break
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
            vtx_field = "vtx" if is_voltx_req else ""
            srv_field = service_from_cb or ""
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s|{query}|{srv_field}|{vtx_field}", "style": "danger"},
                       {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            hdr_country = ""
            if fetched_nums:
                try:
                    _, iso_x, _ = get_country_from_num(fetched_nums[0])
                    if iso_x and iso_x != "XX":
                        for cn2, ci2 in COUNTRY_DB.items():
                            if ci2["iso"] == iso_x: hdr_country = ci2["name"]; break
                    else: hdr_country = query
                except Exception: hdr_country = query
            else: hdr_country = query
            text_numbers = build_numbers_header(hdr_country, service_from_cb)
            edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            return

        parts = data.split("|")
        service = parts[1]; country = parts[2]
        available_indices = []
        for b_id, b_data in number_batches.items():
            if b_data["service"] == service and b_data["country"] == country:
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if chat_id not in n_obj.get("used_by", []):
                        available_indices.append((b_id, idx))
        if not available_indices:
            stex_srv_data = bot_settings.get("stex_services", {}).get(service, {}).get(country)
            voltx_srv_data = bot_settings.get("voltx_services", {}).get(service, {}).get(country)
            target_range = None; is_voltx = False
            if stex_srv_data and len(stex_srv_data) > 0: target_range = random.choice(stex_srv_data)
            elif voltx_srv_data and len(voltx_srv_data) > 0: target_range = random.choice(voltx_srv_data); is_voltx = True
            if target_range:
                user_cooldowns[chat_id] = 0
                vtx_flag = "vtx" if is_voltx else ""
                handle_callback({"message": call["message"], "data": f"c_n_s|{target_range}|{service}|{vtx_flag}", "id": call["id"]})
                return
            else:
                answer_callback(call["id"], "❌ Out of stock!", show_alert=True)
                if data.startswith("c_n"): delete_message(chat_id, msg_id)
                return
        random.shuffle(available_indices)
        fetched_nums = []
        for b_id, idx in available_indices:
            if len(fetched_nums) >= bot_settings["num_req"]: break
            n_obj = number_batches[b_id]["numbers"][idx]
            fetched_nums.append(n_obj["num"]); n_obj["shares"] += 1; n_obj["used_by"].append(chat_id)
            total_assigned_stats += 1
            cn = n_obj["num"].replace("+", "").strip()
            bd_country = number_batches[b_id]["country"]; bd_service = number_batches[b_id]["service"]
            bd_iso = number_batches[b_id].get("country_iso", "")
            _pv = float(bot_settings.get("otp_reward", 0.0))
            if "payout" in number_batches[b_id]:
                try: _pv = float(number_batches[b_id]["payout"])
                except Exception: pass
            assigned_number_meta[cn] = {"country": bd_country, "service": bd_service, "iso": bd_iso, "payout": _pv}
            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                n_obj["to_remove"] = True; used_numbers_list.append(n_obj["num"])
        for b_id in number_batches:
            number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
        save_db()
        if not fetched_nums:
            answer_callback(call["id"], "❌ All taken!", show_alert=True)
            if data.startswith("c_n"): delete_message(chat_id, msg_id)
            return
        app_full_name, _ = get_service_info_html(service)
        emoji_id = "5337302974806922068"
        apps_db = bot_settings.get("premium_apps", {})
        for app_key, app_data in apps_db.items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data: emoji_id = app_data["id"]; break
        kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id, "callback_data": "ignore", "style": "success"}]]
        flags_db = bot_settings.get("premium_flags", {})
        for num in fetched_nums:
            _, iso = get_flag_and_code(num)
            display_num = f"+{num}" if not num.startswith("+") else num
            emoji_id = "5780471598932337683"
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
        kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n|{service}|{country}", "style": "danger"},
                   {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        text_numbers = build_numbers_header(country, service)
        try:
            edit_message(chat_id, msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums}
        except Exception:
            msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
            if msg_res and "result" in msg_res: user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}

    elif data.startswith("wapp_") or data.startswith("wrej_"):
        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Admin only!", show_alert=True); return
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        if req_id in pending_withdrawals:
            req_data = pending_withdrawals[req_id]
            u_id, amt = req_data["user_id"], req_data["amount"]
            num = req_data["number"]; full_name = req_data.get("full_name", u_id)

            new_text = build_withdrawal_status_msg(action, u_id, full_name, amt, num, req_data['method'], req_id)
            status_text = "APPROVED" if action == "APPROVE" else "REJECTED"
            emoji_icon_id = "5352694861990501856" if action == "APPROVE" else "5420130255174145507"
            kb = {"inline_keyboard": [[{"text": status_text, "icon_custom_emoji_id": emoji_icon_id, "callback_data": "ignore", "style": "success" if action == "APPROVE" else "danger"}]]}
            edit_message(chat_id, msg_id, new_text, reply_markup=kb)

            if action == "APPROVE":
                # Balance already held → just notify
                approve_msg = (
                    f"{PEM['ok']} <b><i>Your Withdrawal Has Been Paid Successfully!</i></b>\n"
                    f"\n"
                    f"💰 <b>Amount:</b> <code>${fmt_payout(amt)}</code>\n"
                    f"🧾 <b>Withdraw ID:</b> <code>{req_id}</code>"
                )
                send_message(u_id, render_body_text(approve_msg))
            else:
                # REFUND the held amount
                refund_withdrawal_balance(u_id, amt)
                reject_msg = (
                    f"{PEM['no']} <b><i>Your Withdrawal Request Was Rejected!</i></b>\n"
                    f"\n"
                    f"💰 <b>Amount:</b> <code>${fmt_payout(amt)}</code>\n"
                    f"💵 <b>Refunded to your balance</b>\n"
                    f"🧾 <b>Withdraw ID:</b> <code>{req_id}</code>"
                )
                send_message(u_id, render_body_text(reject_msg))

            try:
                with sqlite_tx() as conn:
                    if conn:
                        conn.cursor().execute("UPDATE withdrawals SET status=? WHERE req_id=?",
                                              ("approved" if action == "APPROVE" else "rejected", req_id))
            except Exception as e:
                print(f"⚠️  withdrawal status update: {type(e).__name__}")
            if db:
                try: db.collection('withdrawals').document(req_id).update({"status": "approved" if action == "APPROVE" else "rejected"}, timeout=5.0)
                except Exception as e:
                    print(f"⚠️  withdrawal status Firestore: {type(e).__name__}")
            del pending_withdrawals[req_id]
        else:
            answer_callback(call["id"], "❌ Already processed!", show_alert=True)


# ==========================================
# Voltx SMS Listener
# ==========================================
def voltx_sms_listener():
    global processed_otps, recent_traffic, voltx_assigned_numbers
    while True:
        try:
            for api_key in bot_settings.get("voltx_keys", []):
                try:
                    res = requests.get(f"{VOLTX_BASE_URL}/success-otp", headers={"mauthapi": api_key}, timeout=10)
                    resp_data = res.json()
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text)
                            if not otp: otp = "N/A"
                            otp_id = str(item.get("otp_id", otp))
                            app_name = "Voltx Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                            unique_id = f"VOLTX_{num}_{otp_id}"
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                char, iso = get_flag_and_code(num)
                                app_full_name, _ = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                lang = detect_language(msg_text)
                                display_msg = render_body_text(format_otp_display(display_num, app_full_name, lang, masked=True))
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = build_group_kb(otp, fw)
                                    send_message(fw["chat_id"], display_msg, reply_markup=kb)
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid; break
                                    if owner_id: break
                                if not owner_id:
                                    for vtx_n, n_owner in voltx_assigned_numbers.items():
                                        clean_vtx = str(vtx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_vtx == clean_api_num or (len(clean_vtx) >= 8 and clean_vtx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_vtx[-8:])):
                                            owner_id = n_owner; break
                                if owner_id:
                                    reward = get_payout_for_number(clean_api_num, app_full_name)
                                    credit_otp_to_user(owner_id, reward, app_full_name)
                                    new_bal = user_cache.get(owner_id, {}).get("balance", 0.0)
                                    it, ik = deliver_to_inbox(owner_id, app_full_name, display_num, msg_text, new_bal, reward, lang)
                                    it = render_body_text(it)
                                    send_message(owner_id, it, reply_markup=ik)
                except Exception: pass
        except Exception: pass
        time.sleep(5)


# ==========================================
# Global (StexSMS) SMS Listener
# ==========================================
def global_sms_listener():
    global processed_otps, recent_traffic, stex_assigned_numbers
    while True:
        try:
            for api_key in bot_settings.get("stex_keys", []):
                try:
                    res = requests.get(f"{STEX_BASE_URL}/success-otp", headers={"mauthapi": api_key}, timeout=10)
                    resp_data = res.json()
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text)
                            if not otp: otp = "N/A"
                            otp_id = str(item.get("otp_id", otp))
                            app_name = "Stex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                            unique_id = f"STEX_{num}_{otp_id}"
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                char, iso = get_flag_and_code(num)
                                app_full_name, _ = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                lang = detect_language(msg_text)
                                display_msg = render_body_text(format_otp_display(display_num, app_full_name, lang, masked=True))
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = build_group_kb(otp, fw)
                                    send_message(fw["chat_id"], display_msg, reply_markup=kb)
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid; break
                                    if owner_id: break
                                if not owner_id:
                                    for stex_n, n_owner in stex_assigned_numbers.items():
                                        clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                            owner_id = n_owner; break
                                if owner_id:
                                    reward = get_payout_for_number(clean_api_num, app_full_name)
                                    credit_otp_to_user(owner_id, reward, app_full_name)
                                    new_bal = user_cache.get(owner_id, {}).get("balance", 0.0)
                                    it, ik = deliver_to_inbox(owner_id, app_full_name, display_num, msg_text, new_bal, reward, lang)
                                    it = render_body_text(it)
                                    send_message(owner_id, it, reply_markup=ik)
                except Exception: pass
        except Exception: pass
        time.sleep(5)


# ==========================================
# Main
# ==========================================
def main():
    global BOT_USERNAME
    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")
    api_call("deleteWebhook", {"drop_pending_updates": True})
    print("🔗 Webhook cleared")
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    print("📡 Background APIs & Global SMS Listener Started!")
    executor = ThreadPoolExecutor(max_workers=500)
    offset = None
    while True:
        try:
            updates = api_call(f"getUpdates?timeout=50&offset={offset}")
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update:
                        executor.submit(handle_message, update["message"])
                    elif "callback_query" in update:
                        executor.submit(handle_callback, update["callback_query"])
        except Exception:
            time.sleep(2)


if __name__ == "__main__":
    main()
