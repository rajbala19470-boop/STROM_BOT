import requests
import time
import json
import os
import zipfile
import io
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import threading
import random
import re
import html
import pyotp
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

# ==========================================
# Configuration (Token & Owner ID)
# ==========================================
TOKEN = "7940813464:AAHSDQmgNw-S2LuDDtVacPCHYixLbkYd2tc"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = 6704775322
BOT_USERNAME = ""
DB_FILE = "bot_data.json"

# ==========================================
# Premium Emoji Database
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
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>'
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
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
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
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607",
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
    "❓": "6203773684306418660"
}

# ==========================================
# API PANEL FIELDS (Reduced set)
# ==========================================
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
# 🌍 World Country Database
# ==========================================
COUNTRY_DB = {
    "1":   {"iso": "US", "name": "United States"},
    "7":   {"iso": "RU", "name": "Russia"},
    "20":  {"iso": "EG", "name": "Egypt"},
    "27":  {"iso": "ZA", "name": "South Africa"},
    "30":  {"iso": "GR", "name": "Greece"},
    "31":  {"iso": "NL", "name": "Netherlands"},
    "32":  {"iso": "BE", "name": "Belgium"},
    "33":  {"iso": "FR", "name": "France"},
    "34":  {"iso": "ES", "name": "Spain"},
    "36":  {"iso": "HU", "name": "Hungary"},
    "39":  {"iso": "IT", "name": "Italy"},
    "40":  {"iso": "RO", "name": "Romania"},
    "41":  {"iso": "CH", "name": "Switzerland"},
    "43":  {"iso": "AT", "name": "Austria"},
    "44":  {"iso": "GB", "name": "United Kingdom"},
    "45":  {"iso": "DK", "name": "Denmark"},
    "46":  {"iso": "SE", "name": "Sweden"},
    "47":  {"iso": "NO", "name": "Norway"},
    "48":  {"iso": "PL", "name": "Poland"},
    "49":  {"iso": "DE", "name": "Germany"},
    "51":  {"iso": "PE", "name": "Peru"},
    "52":  {"iso": "MX", "name": "Mexico"},
    "53":  {"iso": "CU", "name": "Cuba"},
    "54":  {"iso": "AR", "name": "Argentina"},
    "55":  {"iso": "BR", "name": "Brazil"},
    "56":  {"iso": "CL", "name": "Chile"},
    "57":  {"iso": "CO", "name": "Colombia"},
    "58":  {"iso": "VE", "name": "Venezuela"},
    "60":  {"iso": "MY", "name": "Malaysia"},
    "61":  {"iso": "AU", "name": "Australia"},
    "62":  {"iso": "ID", "name": "Indonesia"},
    "63":  {"iso": "PH", "name": "Philippines"},
    "64":  {"iso": "NZ", "name": "New Zealand"},
    "65":  {"iso": "SG", "name": "Singapore"},
    "66":  {"iso": "TH", "name": "Thailand"},
    "81":  {"iso": "JP", "name": "Japan"},
    "82":  {"iso": "KR", "name": "South Korea"},
    "84":  {"iso": "VN", "name": "Vietnam"},
    "86":  {"iso": "CN", "name": "China"},
    "90":  {"iso": "TR", "name": "Turkey"},
    "91":  {"iso": "IN", "name": "India"},
    "92":  {"iso": "PK", "name": "Pakistan"},
    "93":  {"iso": "AF", "name": "Afghanistan"},
    "94":  {"iso": "LK", "name": "Sri Lanka"},
    "95":  {"iso": "MM", "name": "Myanmar"},
    "98":  {"iso": "IR", "name": "Iran"},
    "212": {"iso": "MA", "name": "Morocco"},
    "213": {"iso": "DZ", "name": "Algeria"},
    "216": {"iso": "TN", "name": "Tunisia"},
    "218": {"iso": "LY", "name": "Libya"},
    "220": {"iso": "GM", "name": "Gambia"},
    "221": {"iso": "SN", "name": "Senegal"},
    "222": {"iso": "MR", "name": "Mauritania"},
    "223": {"iso": "ML", "name": "Mali"},
    "224": {"iso": "GN", "name": "Guinea"},
    "225": {"iso": "CI", "name": "Ivory Coast"},
    "226": {"iso": "BF", "name": "Burkina Faso"},
    "227": {"iso": "NE", "name": "Niger"},
    "228": {"iso": "TG", "name": "Togo"},
    "229": {"iso": "BJ", "name": "Benin"},
    "230": {"iso": "MU", "name": "Mauritius"},
    "231": {"iso": "LR", "name": "Liberia"},
    "232": {"iso": "SL", "name": "Sierra Leone"},
    "233": {"iso": "GH", "name": "Ghana"},
    "234": {"iso": "NG", "name": "Nigeria"},
    "235": {"iso": "TD", "name": "Chad"},
    "236": {"iso": "CF", "name": "Central African Republic"},
    "237": {"iso": "CM", "name": "Cameroon"},
    "238": {"iso": "CV", "name": "Cape Verde"},
    "239": {"iso": "ST", "name": "Sao Tome and Principe"},
    "240": {"iso": "GQ", "name": "Equatorial Guinea"},
    "241": {"iso": "GA", "name": "Gabon"},
    "242": {"iso": "CG", "name": "Congo"},
    "243": {"iso": "CD", "name": "DR Congo"},
    "244": {"iso": "AO", "name": "Angola"},
    "245": {"iso": "GW", "name": "Guinea-Bissau"},
    "248": {"iso": "SC", "name": "Seychelles"},
    "249": {"iso": "SD", "name": "Sudan"},
    "250": {"iso": "RW", "name": "Rwanda"},
    "251": {"iso": "ET", "name": "Ethiopia"},
    "252": {"iso": "SO", "name": "Somalia"},
    "253": {"iso": "DJ", "name": "Djibouti"},
    "254": {"iso": "KE", "name": "Kenya"},
    "255": {"iso": "TZ", "name": "Tanzania"},
    "256": {"iso": "UG", "name": "Uganda"},
    "257": {"iso": "BI", "name": "Burundi"},
    "258": {"iso": "MZ", "name": "Mozambique"},
    "260": {"iso": "ZM", "name": "Zambia"},
    "261": {"iso": "MG", "name": "Madagascar"},
    "263": {"iso": "ZW", "name": "Zimbabwe"},
    "264": {"iso": "NA", "name": "Namibia"},
    "265": {"iso": "MW", "name": "Malawi"},
    "266": {"iso": "LS", "name": "Lesotho"},
    "267": {"iso": "BW", "name": "Botswana"},
    "268": {"iso": "SZ", "name": "Eswatini"},
    "269": {"iso": "KM", "name": "Comoros"},
    "290": {"iso": "SH", "name": "Saint Helena"},
    "291": {"iso": "ER", "name": "Eritrea"},
    "297": {"iso": "AW", "name": "Aruba"},
    "298": {"iso": "FO", "name": "Faroe Islands"},
    "299": {"iso": "GL", "name": "Greenland"},
    "350": {"iso": "GI", "name": "Gibraltar"},
    "351": {"iso": "PT", "name": "Portugal"},
    "352": {"iso": "LU", "name": "Luxembourg"},
    "353": {"iso": "IE", "name": "Ireland"},
    "354": {"iso": "IS", "name": "Iceland"},
    "355": {"iso": "AL", "name": "Albania"},
    "356": {"iso": "MT", "name": "Malta"},
    "357": {"iso": "CY", "name": "Cyprus"},
    "358": {"iso": "FI", "name": "Finland"},
    "359": {"iso": "BG", "name": "Bulgaria"},
    "370": {"iso": "LT", "name": "Lithuania"},
    "371": {"iso": "LV", "name": "Latvia"},
    "372": {"iso": "EE", "name": "Estonia"},
    "373": {"iso": "MD", "name": "Moldova"},
    "374": {"iso": "AM", "name": "Armenia"},
    "375": {"iso": "BY", "name": "Belarus"},
    "376": {"iso": "AD", "name": "Andorra"},
    "377": {"iso": "MC", "name": "Monaco"},
    "378": {"iso": "SM", "name": "San Marino"},
    "380": {"iso": "UA", "name": "Ukraine"},
    "381": {"iso": "RS", "name": "Serbia"},
    "382": {"iso": "ME", "name": "Montenegro"},
    "385": {"iso": "HR", "name": "Croatia"},
    "386": {"iso": "SI", "name": "Slovenia"},
    "387": {"iso": "BA", "name": "Bosnia and Herzegovina"},
    "389": {"iso": "MK", "name": "North Macedonia"},
    "420": {"iso": "CZ", "name": "Czech Republic"},
    "421": {"iso": "SK", "name": "Slovakia"},
    "423": {"iso": "LI", "name": "Liechtenstein"},
    "500": {"iso": "FK", "name": "Falkland Islands"},
    "501": {"iso": "BZ", "name": "Belize"},
    "502": {"iso": "GT", "name": "Guatemala"},
    "503": {"iso": "SV", "name": "El Salvador"},
    "504": {"iso": "HN", "name": "Honduras"},
    "505": {"iso": "NI", "name": "Nicaragua"},
    "506": {"iso": "CR", "name": "Costa Rica"},
    "507": {"iso": "PA", "name": "Panama"},
    "509": {"iso": "HT", "name": "Haiti"},
    "591": {"iso": "BO", "name": "Bolivia"},
    "592": {"iso": "GY", "name": "Guyana"},
    "593": {"iso": "EC", "name": "Ecuador"},
    "595": {"iso": "PY", "name": "Paraguay"},
    "597": {"iso": "SR", "name": "Suriname"},
    "598": {"iso": "UY", "name": "Uruguay"},
    "670": {"iso": "TL", "name": "East Timor"},
    "673": {"iso": "BN", "name": "Brunei"},
    "675": {"iso": "PG", "name": "Papua New Guinea"},
    "676": {"iso": "TO", "name": "Tonga"},
    "677": {"iso": "SB", "name": "Solomon Islands"},
    "678": {"iso": "VU", "name": "Vanuatu"},
    "679": {"iso": "FJ", "name": "Fiji"},
    "680": {"iso": "PW", "name": "Palau"},
    "682": {"iso": "CK", "name": "Cook Islands"},
    "685": {"iso": "WS", "name": "Samoa"},
    "686": {"iso": "KI", "name": "Kiribati"},
    "688": {"iso": "TV", "name": "Tuvalu"},
    "689": {"iso": "PF", "name": "French Polynesia"},
    "691": {"iso": "FM", "name": "Micronesia"},
    "692": {"iso": "MH", "name": "Marshall Islands"},
    "850": {"iso": "KP", "name": "North Korea"},
    "852": {"iso": "HK", "name": "Hong Kong"},
    "853": {"iso": "MO", "name": "Macau"},
    "855": {"iso": "KH", "name": "Cambodia"},
    "856": {"iso": "LA", "name": "Laos"},
    "880": {"iso": "BD", "name": "Bangladesh"},
    "886": {"iso": "TW", "name": "Taiwan"},
    "960": {"iso": "MV", "name": "Maldives"},
    "961": {"iso": "LB", "name": "Lebanon"},
    "962": {"iso": "JO", "name": "Jordan"},
    "963": {"iso": "SY", "name": "Syria"},
    "964": {"iso": "IQ", "name": "Iraq"},
    "965": {"iso": "KW", "name": "Kuwait"},
    "966": {"iso": "SA", "name": "Saudi Arabia"},
    "967": {"iso": "YE", "name": "Yemen"},
    "968": {"iso": "OM", "name": "Oman"},
    "970": {"iso": "PS", "name": "Palestine"},
    "971": {"iso": "AE", "name": "United Arab Emirates"},
    "972": {"iso": "IL", "name": "Israel"},
    "973": {"iso": "BH", "name": "Bahrain"},
    "974": {"iso": "QA", "name": "Qatar"},
    "975": {"iso": "BT", "name": "Bhutan"},
    "976": {"iso": "MN", "name": "Mongolia"},
    "977": {"iso": "NP", "name": "Nepal"},
    "992": {"iso": "TJ", "name": "Tajikistan"},
    "993": {"iso": "TM", "name": "Turkmenistan"},
    "994": {"iso": "AZ", "name": "Azerbaijan"},
    "995": {"iso": "GE", "name": "Georgia"},
    "996": {"iso": "KG", "name": "Kyrgyzstan"},
    "998": {"iso": "UZ", "name": "Uzbekistan"},
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "╔═══════════╗\n       📊 NUMBER BOT\n╚═══════════╝\n🚀 Welcome to Number & OTP Service\n━━━━━━━━━━━━\n✅ Choose an option below\nto continue using the bot.\n━━━━━━━━━━━━\n💎 Premium OTP Service", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []},
    "search_number": {"text": "╔═══════════╗\n     🔍 <b>SEARCH NUMBER</b>\n╚═══════════╝\n✅ Enter 3 to 9 digits  \nto search for a number.\n━━━━━━━━━━━━━\n📝 Example:\n➥ 880\n➥ 9227373\n━━━━━━━━━━━━━\n🔍 Fast Number Lookup System", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>{{ref_reward}} TK</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖\n《 🙈 <b>USER ID</b> : <code>{user_id}</code>  》\n➖➖➖➖➖➖➖\n☁️ <b>Total Otp:</b> <code>{total_otp}</code>\n➖➖➖➖➖➖➖\n🫂 <b>Reffer :</b><code>{total_ref}</code>\n➖➖➖➖➖➖➖\n📅 <b>BALANCE:</b> <code>{bal}</code>\n➖➖➖➖➖➖➖\n🔐 <b>MINIMUM:</b> <code>{min_w}</code>\n➖➖➖➖➖➖➖\n<b>SELECT METHOD</b> 📱", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []}
}

# ==========================================
# Firebase Setup (with 20s timeout + graceful fallback)
# ==========================================
firebase_credentials_json = r"""
{
  "type": "service_account",
  "project_id": "sadikul-b2b8a",
  "private_key_id": "61818af700e11e61fe83475a189b4aa6d0573f39",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDCECvcx+DNBgdf\nVbS11ws1k8nYhFyRyLx6R9YUyxi1gXpAsixQFvCvtnEPfC0Znt3GYzOzLnZnhvSu\nPw5oMePnZAOn0bF1v3lQK/rnpsh1vlKCP4QSRCorJxhtIfWKFv7p10hZmaktoMZP\n6cfXyn95+It5/vsw1IsK3P7keLtSDn3dwbvWcm8LKQcDCh+1ra9zMf7+vw/ClAgF\nL8eaMb8J+f5MuLWVfZad8X1CvekVLESbUgZ6nkFVfcSXPW/5FpWq9uJvQ+V9dTBY\nTNnlpuSSf+kfTd0janymvMKo23KeG2bDgl2kfvPCmOhly2gd5adaIuUC2MdjBzt4\nt/MAQyKRAgMBAAECggEAQOkp0rpkng9TLfc778rTLAOX8z0qvXSYXopiuCfKxwNd\nAgDWw584uH1cyeIuL7Cs26vY4ik7X5uLgjEDP6TYZ1BTzLFeG1WFXWSokw19ZazY\nakqWgYmdVTvJds9yEtNoRo1E3PuB1Ao/6wD2YF6STxjshkzcdlPRgjuzYnZjqakq\n8LU+dbTpVELbEbO8oaji+oBhDuMzaGOgvbxPNCX4AdFTLWpXw3kII85w2RirLKA9\n4li4LqAqp4dgyPMITn3Xsf4+m9wLBgn6jUTCbAmOHvyC5YI7IMqdYuxSnjaECOfv\n63DKW0xpg1OHqTLfL5c0COWXe/r8jBH8/JBeTNJqZQKBgQD89ycOVUMS/Cpcc6je\nNOQqghCwi2yL7jksshlGQzWA/YJe5qw5ASHykYcix5HhBrOjL1FimyVYxezkKe2I\nUjlQ+pmBUT+20m5hpHuslqd0WE2tt8Dfaq6t7JvPymyMRkFWO+qtQ89QWT/CheQA\nMYlJ+bdyRyjW8gIEw3/IRPPn5wKBgQDEZCHRK7UKad+HLhQd5yovT+U0EOr+vJnQ\nG/FAjg7kC+od46qJ5Rqn1YtEVTMm7jX8/AwaH5UDzFPmjeWPLr1WcR2k06on2NQv\n0PZmOyIe/5lLXlXHxIIjVH7w5pJIOcrNldHxVNLZwPJYEjUzyTRe9rZNNzz4zW+p\nJhYFatNyxwKBgHO4LCmmX1Sj/kzkq+9airXXYgMhBLrOc2E658z4mdU0Ixt+snIx\nTnJEmGkUmmsyQaL41mYhSuhdQoztkTe3RXkB6o75uAfOI6iPMfQ1xsy2SHKbiKOr\njdUKVAyuMRHKYcEtD6HLT18WNNCrpy1fe8pXbc/dNZV+h+Xd+OqIgHspAoGAHt8W\nqcjTFqX560gFBYZXDUTj5MFcD1saWqppzBoIoTR2QuiM4ExRWlypHb6+4bnEZtZA\nGMMqK4StE6rukQlp3fK+FDDpqIXfJP0WHo/hFzpaoIxds59iTad0pO25xPzAsnyA\nmg0Zb/1ymwGRt2hDgUIK+ixau0mf6dkA0S0vu/UCgYEAkKleZE662o/JtBUEbOJT\nr/fNAZfSJkgGtOsfIlSE14mPRCO34SripRJ1X72j+1NslPdqKKZyzxpov6lj4V/Z\ntsfnnKZKJNl3xyWVPdBlP30XQ4xZRHN2aeteYIeAHMzAVm8TI4Xk6Ru0DLffi503\niKs4FV2iBPYKwCOJn5+S2zk=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@sadikul-b2b8a.iam.gserviceaccount.com",
  "client_id": "115361300368288169762",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40sadikul-b2b8a.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""

db = None
_firebase_ready = False

def _init_firebase_with_timeout():
    """Firebase init with 20-second timeout. Falls back to local-only mode if failed."""
    global db, _firebase_ready
    try:
        cred_dict = json.loads(firebase_credentials_json)
        cred = credentials.Certificate(cred_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
        # Quick ping test with 6s timeout to verify real connection
        try:
            _db.collection('_startup_ping_').document('x').get(timeout=6.0)
            db = _db
            _firebase_ready = True
            print("✅ Firebase Connected & VERIFIED!")
        except Exception as _te:
            print(f"⚠️ Firebase auth FAILED: {type(_te).__name__}: {str(_te)[:120]}")
            print("⚠️ Firebase DISABLED - running in LOCAL-ONLY mode.")
            db = None
            _firebase_ready = False
    except Exception as e:
        print(f"❌ Firebase Init Error: {e}")
        print("⚠️ Running in LOCAL-ONLY mode.")
        db = None
        _firebase_ready = False

_fb_t = threading.Thread(target=_init_firebase_with_timeout, daemon=True)
_fb_t.start()
_fb_t.join(timeout=20.0)
if _fb_t.is_alive():
    print("⏱ Firebase init TIMEOUT (20s) - switching to LOCAL-ONLY mode.")
    db = None
    _firebase_ready = False
else:
    print("🔍 Firebase init completed.")

bot_settings = {
    "admins": [OWNER_ID],
    "panels": [],
    "fw_groups": [],
    "otp_link": "https://t.me/your_otp_group",
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    "refer_reward": 0.2,
    "cooldown": 10,
    "num_req": 3,
    "num_share": 1,
    "support_link": "https://t.me/your_support",
    "w_methods": ["bKash", "Nagad"],
    "w_group": "",
    "fj_on": False,
    "fj_channels": [],
    "stex_keys": [],
    "voltx_keys": [],
    "search_countries": [],
    "stex_services": {},
    "voltx_services": {},
    "otp_pair_rates": {},
    "maintenance": False,
    "premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5913463998522592692"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"}
    },
    "premium_apps": {
        "FACEBOOK": {"char": "🚫", "id": "5334807341109908955", "name": "Facebook"},
        "WHATSAPP": {"char": "🚫", "id": "5334759662677957452", "name": "WhatsApp"}
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
}

FS_KEYS = [
    "admins", "panels", "fw_groups", "otp_link", "withdraw_on",
    "min_withdraw", "otp_reward", "refer_reward", "cooldown",
    "num_req", "num_share", "support_link", "w_methods", "w_group",
    "stex_keys", "voltx_keys", "search_countries", "stex_services", "voltx_services",
    "fj_on", "fj_channels", "otp_pair_rates", "maintenance"
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
assigned_number_meta = {}
panel_sessions = {}

# ==========================================
# Per-country/service Payout Resolver
# ==========================================
def get_payout_for_number(clean_api_num, service_hint=""):
    meta = assigned_number_meta.get(clean_api_num, {})
    if "payout" in meta:
        try: return float(meta["payout"])
        except: pass
    oc = str(meta.get("country", "") or "").strip()
    osvc = str(meta.get("service", "") or service_hint or "").strip()
    if not oc:
        try:
            _, iso_det, _ = get_country_from_num(clean_api_num)
            if iso_det and iso_det != "XX":
                for _c, fdata in bot_settings.get("premium_flags", {}).items():
                    if fdata.get("iso", "").upper() == iso_det.upper():
                        oc = fdata.get("name", ""); break
                if not oc:
                    for _c, cinfo in COUNTRY_DB.items():
                        if cinfo["iso"] == iso_det:
                            oc = cinfo["name"]; break
        except: pass
    pr = bot_settings.get("otp_pair_rates", {})
    if oc and osvc:
        key = f"{oc.upper()}|{osvc.upper()}"
        if key in pr:
            try: return float(pr[key])
            except: pass
        for k, v in pr.items():
            try:
                if k.split("|")[0] == oc.upper():
                    return float(v)
            except: pass
    return float(bot_settings.get("otp_reward", 0.0))


def get_wmethod_emoji_html(method_name):
    for m in bot_settings.get("w_methods", []):
        if isinstance(m, dict):
            if m.get("name", "").lower() == method_name.lower():
                eid = m.get("emoji_id", "")
                if eid:
                    return f'<tg-emoji emoji-id="{eid}">{m.get("char", "💳")}</tg-emoji>'
    return '<tg-emoji emoji-id="5190899075968441286">💳</tg-emoji>'


def get_wmethod_display_list():
    out = []
    for m in bot_settings.get("w_methods", []):
        if isinstance(m, dict):
            name = m.get("name", "")
            eid = m.get("emoji_id", "")
            char = m.get("char", "💳")
            if eid:
                emoji_html = f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            else:
                emoji_html = "💳"
            out.append((name, emoji_html))
        else:
            out.append((str(m), "💳"))
    return out


# ==========================================
# Captcha Panel CDRs Fetcher
# ==========================================
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
    n_idx = int(p.get("num_col_idx", 1)) - 1 if p.get("num_col_idx") else 1
    m_idx = int(p.get("msg_col_idx", 2)) - 1 if p.get("msg_col_idx") else 2
    if s_ajax_source:
        baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
        if not baseUrl.startswith("http"):
            baseUrl = "http://" + baseUrl
        full_ajax_url = ""
        if s_ajax_source.startswith("http"):
            full_ajax_url = s_ajax_source
        elif s_ajax_source.startswith("/"):
            full_ajax_url = f"{baseUrl}{s_ajax_source}"
        else:
            last_slash_idx = check_url.rfind("/")
            current_dir = check_url[:last_slash_idx]
            full_ajax_url = f"{current_dir}/{s_ajax_source}"
        if "iDisplayLength" not in full_ajax_url:
            query_params = "sEcho=1&iColumns=7&iDisplayStart=0&iDisplayLength=250&sSearch=&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc"
            divider = "&" if "?" in full_ajax_url else "?"
            full_ajax_url += f"{divider}{query_params}"
        ajax_headers = {"Referer": check_url, "X-Requested-With": "XMLHttpRequest"}
        ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
        data_dict = ajax_res.json()
        rows = data_dict.get("aaData", [])
        for row_val in rows:
            if not isinstance(row_val, list): continue
            if len(row_val) < max(n_idx, m_idx) + 1: continue
            num_val = row_val[n_idx] if (0 <= n_idx < len(row_val)) else row_val[2]
            msg_val = row_val[m_idx] if (0 <= m_idx < len(row_val)) else row_val[4]
            clean_num = re.sub(r'\D', '', str(num_val))
            if clean_num and 5 <= len(clean_num) <= 18:
                otp = extract_otp_code(msg_val)
                if otp and len(msg_val) > 4:
                    results.append({"number": clean_num, "message": msg_val, "otp": otp})
    else:
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue
            final_n_idx = n_idx
            final_m_idx = m_idx
            header_cells = rows[0].find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                c_text = cell.get_text(strip=True).lower()
                if n_col_name in c_text: final_n_idx = i
                if m_col_name in c_text: final_m_idx = i
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if all(c.name == 'th' for c in cols): continue
                if len(cols) > max(final_n_idx, final_m_idx):
                    num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                    msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                    clean_num = re.sub(r'\D', '', num_text)
                    if clean_num and 5 <= len(clean_num) <= 18:
                        otp = extract_otp_code(msg_text)
                        if otp and len(msg_text) > 4:
                            results.append({"number": clean_num, "message": msg_text, "otp": otp})
    return results, html_text

user_active_sessions = {}

def load_db():
    """Load settings — Firestore first (if available), else local file. Timeout-safe."""
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic
    global stex_assigned_numbers, voltx_assigned_numbers, assigned_number_meta

    # ---- Load from Firestore (only if db is available) ----
    if db:
        try:
            doc = db.collection('settings').document('bot_config').get(timeout=8.0)
            if doc.exists:
                fs_data = doc.to_dict()
                for k in FS_KEYS:
                    if k in fs_data:
                        bot_settings[k] = fs_data[k]
                print("✅ Config Loaded from Firestore!")
            else:
                fs_data = {k: bot_settings[k] for k in FS_KEYS}
                db.collection('settings').document('bot_config').set(fs_data, timeout=8.0)
                print("✅ Firestore Config Initialized!")
        except Exception as e:
            print(f"⚠️ Firestore load skipped ({type(e).__name__}): {str(e)[:100]}")

    # ---- Load from local file (always — to get stock/UI data) ----
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
                number_batches = data.get("number_batches", {})
                used_numbers_list = data.get("used_numbers_list", [])
                total_uploaded_stats = data.get("total_uploaded_stats", 0)
                total_assigned_stats = data.get("total_assigned_stats", 0)
                recent_traffic = data.get("recent_traffic", [])
                stex_assigned_numbers = data.get("stex_assigned_numbers", {})
                voltx_assigned_numbers = data.get("voltx_assigned_numbers", {})
                assigned_number_meta.update(data.get("assigned_number_meta", {}))
            print("✅ Local Stock/UI DB Loaded Successfully!")
        except Exception as e:
            print(f"⚠️ Error loading local DB: {e}")

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
            json.dump(local_data, f, indent=4)
    except: pass

def _sync_fs():
    """Sync bot_settings to Firestore in background (if db available)."""
    if not db: return
    fs_data = {k: bot_settings[k] for k in FS_KEYS if k in bot_settings}
    try:
        db.collection('settings').document('bot_config').set(fs_data, timeout=8.0)
    except Exception as e:
        print(f"⚠️ Firestore sync failed: {e}")

def save_db():
    save_local_db()
    if db:
        threading.Thread(target=_sync_fs, daemon=True).start()

# ==========================================
# BACKGROUND LOAD — Bot starts immediately, DB loads in background
# ==========================================
def _bg_load_db():
    try:
        load_db()
        print("✅ load_db() completed in background.")
    except Exception as e:
        print(f"❌ load_db() crashed: {e}")

threading.Thread(target=_bg_load_db, daemon=True).start()
print("🚀 load_db() started in background - bot starting now.")

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}

# ==========================================
# Telegram API & Helpers
# ==========================================
tg_session = requests.Session()

def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    try:
        res = tg_session.post(url, json=payload, timeout=15)
        return res.json()
    except Exception as e:
        return {}

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "photo": photo_url_or_file_id, "caption": caption, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendPhoto", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("editMessageText", payload)

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
_users_lock = threading.Lock()

def sync_users_list():
    global all_known_users
    try:
        if os.path.exists("users_list.json"):
            with open("users_list.json", "r") as f:
                with _users_lock:
                    all_known_users = set(json.load(f))
        if not all_known_users and db:
            try:
                for doc in db.collection('users').select([]).stream():
                    with _users_lock:
                        all_known_users.add(doc.id)
                with open("users_list.json", "w") as f:
                    json.dump(list(all_known_users), f)
            except Exception as e:
                print(f"⚠️ Firestore user list sync skipped: {e}")
    except: pass

threading.Thread(target=sync_users_list, daemon=True).start()

def _save_users_list():
    try:
        with _users_lock:
            data_to_save = list(all_known_users)
        with open("users_list.json", "w") as f:
            json.dump(data_to_save, f)
    except: pass

def register_user_local(uid):
    uid_str = str(uid)
    with _users_lock:
        if uid_str in all_known_users:
            return
        all_known_users.add(uid_str)
    threading.Thread(target=_save_users_list, daemon=True).start()

def broadcast_copymessage(from_chat_id, msg_id):
    success = 0
    failed = 0
    with _users_lock:
        users = list(all_known_users)
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): success += 1
            else: failed += 1
        except: failed += 1
        time.sleep(0.035)
    send_message(from_chat_id, render_body_text(f"📢 <b>Broadcast Completed!</b>\n✅ Success: {success}\n❌ Failed: {failed}\n👥 Total Sent: {len(users)}"))

def broadcast_text_all(txt, kb=None):
    with _users_lock:
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
    except Exception as e:
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
    if len(num_or_iso) == 2:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso") == num_or_iso:
                eid = data.get("id")
                char = data.get("char")
                if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        return "🌍"
    char, _, eid = get_flag_info_from_num(num_or_iso)
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char

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
    # ==========================================
# Language Full Name Lookup
# ==========================================
def lang_full(code):
    if not code: return "English"
    c = str(code).replace("#","").strip().upper()
    names = {
        "EN":"English","AR":"Arabic","BN":"Bangla","HI":"Hindi","PA":"Punjabi","GU":"Gujarati",
        "OR":"Odia","TA":"Tamil","TE":"Telugu","KN":"Kannada","ML":"Malayalam","SI":"Sinhala",
        "TH":"Thai","LO":"Lao","BO":"Tibetan","MY":"Burmese","AM":"Amharic","KM":"Khmer",
        "KA":"Georgian","HY":"Armenian","HE":"Hebrew","EL":"Greek","RU":"Russian","ZH":"Chinese",
        "JA":"Japanese","KO":"Korean","ID":"Indonesian","MS":"Malay","VN":"Vietnamese","TL":"Tagalog",
        "ES":"Spanish","PT":"Portuguese","FR":"French","DE":"German","IT":"Italian","PL":"Polish",
        "TR":"Turkish","NL":"Dutch","SV":"Swedish","DA":"Danish","NO":"Norwegian","FI":"Finnish",
        "CS":"Czech","SK":"Slovak","HU":"Hungarian","RO":"Romanian","HR":"Croatian","BG":"Bulgarian",
        "UK":"Ukrainian","SW":"Swahili","AF":"Afrikaans","FA":"Persian"
    }
    return names.get(c, c.title() if c else "English")


# ==========================================
# OTP Display Format
# 🇳🇬 NG | 📱 | +2348🔹372 |✉️ English
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
    elif svc_char and svc_char != "📱":
        svc_html = svc_char
    else:
        svc_html = f"#{app_full_name.replace(' ', '')}"

    if masked:
        first4 = clean[:4] if len(clean) >= 4 else clean
        last3 = clean[-3:] if len(clean) >= 3 else clean
        num_part = f'+<b>{first4}</b><tg-emoji emoji-id="5352638632278660622">🔹</tg-emoji><b>{last3}</b>'
    else:
        num_part = f'+<b>{clean}</b>'

    lang_display = lang_full(lang)

    return (
        f"{flag_html} <b>{iso}</b> | "
        f"{svc_html} | "
        f"{num_part} |"
        f'<tg-emoji emoji-id="5337302974806922068">✉️</tg-emoji> {lang_display}'
    )


# ==========================================
# SERVICE & LANGUAGE DETECTION
# ==========================================
SERVICE_SMS_KEYWORDS = {
    "whatsapp": ["whatsapp", "wa", "wap", "w/a", "whatsapp business", "wa.me", "wa code", "wh", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "वाट्सएप", "वॉट्सऐप", "व्हाट्सप्प", "হোয়াটসঅ্যাপ", "হোটসঅ্যাপ", "ватсап", "уотсап", "вотсап", "ватс апп", "వాట్సాప్", "വാട്‌സ്ആപ്പ്", "வாட்ஸ்அப்", "ವಾಟ್ಸಾಪ್", "વોટ્સએપ", "ਵਟਸਐਪ", "ହ୍ଵାଟସ୍ ଆପ୍", "වට්ස්ඇප්", "วอตส์แอปป์", "วอทส์แอพ", "ဝက်စ်အက်ပ်", "វ៉តសាប់", "ວອດແອັບ", "ワッツアップ", "왓츠앱", "whatsapp的", "whatsapp验证码", "וואטסאפ", "γουάτσαπ", "ዋትስአፕ", "ვოთსაფი", "վոթսափ"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code", "فيسبوك", "فيس بوك"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code", "انستغرام", "انستقرام"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code", "تيك توك"],
    "snapchat": ["snapchat", "snap", "snap code", "سناب شات"],
    "twitter": ["twitter", "x.com", "x code", "twitter code", "تويتر"],
    "discord": ["discord", "discord code", "ديسكورد"],
    "viber": ["viber", "viber code", "فايبر"],
    "line": ["line", "line code", "line verification", "لاين"],
    "wechat": ["wechat", "we chat", "wechat code", "وي تشات"],
    "signal": ["signal", "signal code", "سيجنال"],
    "linkedin": ["linkedin", "linked in", "لينكد إن"],
    "imo": ["imo", "imo code", "imo verification", "ايمو"],
    "kakaotalk": ["kakao", "kakaotalk", "كاكاو"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],
    "google": ["google", "gmail", "youtube", "g-", "google voice", "جوجل", "غوغل"],
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
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]): return "#VN"
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]): return "#TL"
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]): return "#ES"
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]): return "#PT"
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR"
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE"
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]): return "#IT"
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]): return "#PL"
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]): return "#TR"
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]): return "#NL"
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]): return "#SV"
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]): return "#DA"
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]): return "#NO"
    if any(w in text_lower for w in ["vahvistuskoodi", "älä jaa"]): return "#FI"
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]): return "#CS"
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]): return "#SK"
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]): return "#HU"
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]): return "#RO"
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]): return "#HR"
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]): return "#BG"
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]): return "#UK"
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]): return "#SW"
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]): return "#AF"
    return "#EN"

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"): return text
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
    if db:
        try:
            doc = db.collection('users').document(str(user_id)).get(timeout=5.0)
            banned = doc.exists and doc.to_dict().get("banned", False)
        except: pass
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned


# ==========================================
# OTP Extraction
# ==========================================
def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))
    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:
        return multi_part.group(0).replace(" ", "")
    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit():
        return keyword_match.group(1)
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|কোড)', clean_text, re.I)
    if keyword_match_rev and keyword_match_rev.group(1).isdigit():
        return keyword_match_rev.group(1)
    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match: return g_match.group(1)
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches: return digit_matches[0]
    return None


# ==========================================
# Panel Response Parser
# ==========================================
def parse_panel_response(response_text, p_config=None):
    results = []
    p_type = p_config.get("type", "API Panel") if p_config else "API Panel"
    n_col_name = p_config.get("num_col_name", "number").lower() if p_config else "number"
    m_col_name = p_config.get("msg_col_name", "message").lower() if p_config else "message"
    n_idx = int(p_config.get("num_col_idx", 1)) - 1 if p_config and p_config.get("num_col_idx") else 1
    m_idx = int(p_config.get("msg_col_idx", 2)) - 1 if p_config and p_config.get("msg_col_idx") else 2

    if p_type == "Auto Captcha Panel":
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                if not rows: continue
                final_n_idx = n_idx
                final_m_idx = m_idx
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(strip=True).lower()
                    if n_col_name in c_text: final_n_idx = i
                    if m_col_name in c_text: final_m_idx = i
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if all(c.name == 'th' for c in cols): continue
                    if len(cols) > max(final_n_idx, final_m_idx):
                        num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                        msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                        clean_num = re.sub(r'\D', '', num_text)
                        if clean_num and 5 <= len(clean_num) <= 18:
                            otp = extract_otp_code(msg_text)
                            if otp and len(msg_text) > 4:
                                results.append({"number": clean_num, "message": msg_text, "otp": otp})
        except: pass
    else:
        try:
            data = json.loads(response_text)
            temp_results = []

            def process_item(item):
                pot_nums_list = []
                pot_msg = None
                values = []
                if isinstance(item, dict):
                    lower_keys = {str(k).lower(): v for k, v in item.items()}
                    for k in ["number", "num", "phone", "msisdn", "sender"]:
                        if k in lower_keys:
                            clean_val = re.sub(r'\D', '', str(lower_keys[k]))
                            if 5 <= len(clean_val) <= 18:
                                if clean_val not in pot_nums_list: pot_nums_list.append(clean_val)
                    for k in ["message", "msg", "sms", "content", "text"]:
                        if k in lower_keys:
                            val = str(lower_keys[k])
                            if len(val) > 4:
                                pot_msg = val
                                break
                    values = list(item.values())
                elif isinstance(item, list):
                    values = item
                for v in values:
                    if isinstance(v, (dict, list)) or v is None: continue
                    v_str = str(v).strip()
                    clean_v = re.sub(r'\D', '', v_str)
                    if 7 <= len(clean_v) <= 18 and not re.search(r'[a-zA-Z]', v_str):
                        if not re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', v_str) and not re.search(r'\d{2}:\d{2}:\d{2}', v_str) and "." not in v_str:
                            if clean_v not in pot_nums_list:
                                pot_nums_list.append(clean_v)
                    if len(v_str) > 4 and not v_str.isdigit():
                        if extract_otp_code(v_str):
                            if pot_msg is None or len(v_str) > len(pot_msg):
                                pot_msg = v_str
                pot_num = None
                if pot_nums_list:
                    matched_user_num = None
                    for n in pot_nums_list:
                        if n in stex_assigned_numbers or any(n in str(key) for key in stex_assigned_numbers.keys()):
                            matched_user_num = n
                            break
                    if matched_user_num:
                        pot_num = matched_user_num
                    elif len(pot_nums_list) >= 2:
                        pot_num = pot_nums_list[1]
                    else:
                        pot_num = pot_nums_list[0]
                if pot_num and pot_msg:
                    otp = extract_otp_code(pot_msg)
                    if otp:
                        temp_results.append({"number": pot_num, "message": pot_msg, "otp": otp})

            def traverse_json(node):
                if isinstance(node, list):
                    if len(node) > 0 and not isinstance(node[0], (dict, list)):
                        process_item(node)
                    for child in node:
                        if isinstance(child, (dict, list)):
                            traverse_json(child)
                elif isinstance(node, dict):
                    process_item(node)
                    for val in node.values():
                        if isinstance(val, (dict, list)):
                            traverse_json(val)

            traverse_json(data)
            seen = set()
            for r in temp_results:
                uid = f"{r['number']}_{r['otp']}"
                if uid not in seen:
                    seen.add(uid)
                    results.append(r)
        except: pass
    return results


# ==========================================
# Auto Login for Captcha Panel
# ==========================================
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
                        captcha_match = m
                        break
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
        from urllib.parse import urljoin
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
# Panel Monitor Thread
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
                            p["login_status"] = "✅ Active & Fetching"
                        except:
                            p["login_status"] = "❌ Session Expired (Retrying...)"
                            del panel_sessions[idx]
                            save_db()
                            continue
                    elif p.get("api_url") or p.get("curl_command"):
                        url = p.get("api_url", "").strip()
                        token = p.get("token", "").strip()
                        curl_cmd = p.get("curl_command", "").strip()
                        parsed_data = []
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

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
                        unique_id = f"{num}_{otp}"
                        if unique_id not in processed_otps:
                            processed_otps.add(unique_id)
                            if len(processed_otps) > 5000: processed_otps.clear()
                            char, iso = get_flag_and_code(num)
                            app_full_name, prem_app_html = get_service_info_html(p.get("name", "Panel"), msg_text)
                            current_time = time.time()
                            recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": num,
                                "time": current_time
                            })
                            save_local_db()
                            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                            lang = detect_language(msg_text)
                            display_msg = render_body_text(format_otp_display(display_num, app_full_name, lang, masked=True))
                            for fw in bot_settings["fw_groups"]:
                                kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                for btn in fw.get("buttons", []):
                                    b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
                                    if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                    kb.append([b_obj])
                                send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
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
                                if reward > 0:
                                    update_balance(owner_id, reward)
                                    if db:
                                        try: db.collection('users').document(str(owner_id)).update({"total_otps": firestore.Increment(1)}, timeout=5.0)
                                        except: pass
                                new_bal = user_cache.get(owner_id, {}).get("balance", 0.0)
                                inbox_msg = render_body_text(format_otp_display(display_num, app_full_name, lang, masked=False))
                                inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                if reward > 0:
                                    inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
        except: pass
        time.sleep(5)


# ==========================================
# Firebase User Management (Local Cache + Firestore)
# ==========================================
user_cache = {}

def get_user(user_id):
    if user_id in user_cache: return user_cache[user_id]
    if not db:
        new_user = {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0, "banned": False, "verified": False}
        user_cache[user_id] = new_user
        return new_user
    try:
        doc_ref = db.collection('users').document(str(user_id))
        doc = doc_ref.get(timeout=5.0)
        if doc.exists:
            data = doc.to_dict()
            if "total_otps" not in data: data["total_otps"] = 0
            if "banned" not in data: data["banned"] = False
            if "verified" not in data: data["verified"] = False
            user_cache[user_id] = data
            return data
        else:
            new_user = {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0, "banned": False, "verified": False}
            doc_ref.set(new_user, timeout=5.0)
            user_cache[user_id] = new_user
            return new_user
    except Exception as e:
        new_user = {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0, "banned": False, "verified": False}
        user_cache[user_id] = new_user
        return new_user

def update_balance(user_id, amount):
    if user_id in user_cache:
        user_cache[user_id]["balance"] = user_cache[user_id].get("balance", 0.0) + float(amount)
    if not db: return
    try:
        doc_ref = db.collection('users').document(str(user_id))
        doc_ref.set({"user_id": user_id, "balance": firestore.Increment(float(amount))}, merge=True, timeout=5.0)
    except: pass

def add_referral(inviter_id, new_user_id):
    if not db:
        reward = bot_settings.get("refer_reward", 0.2)
        update_balance(inviter_id, reward)
        ref_msg = (f"{PEM['gift']} <b>New Referral !</b>\n------------------\n🔥 <b>You Received {reward} TK</b>\n------------------\n{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>")
        send_message(inviter_id, render_body_text(ref_msg))
        return
    try:
        doc = db.collection('users').document(str(new_user_id)).get(timeout=5.0)
        if not doc.exists:
            get_user(new_user_id)
            reward = bot_settings.get("refer_reward", 0.2)
            update_balance(inviter_id, reward)
            db.collection('users').document(str(inviter_id)).update({"total_refers": firestore.Increment(1)}, timeout=5.0)
            ref_msg = (f"{PEM['gift']} <b>New Referral !</b>\n------------------\n🔥 <b>You Received {reward} TK</b>\n------------------\n{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>")
            send_message(inviter_id, render_body_text(ref_msg))
    except: pass
    # ==========================================
# UI Keyboards & Menu Builders
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    kb = [
        [
            {"text": "GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "style": "primary"},
            {"text": "Search Number", "icon_custom_emoji_id": "5463352748751753567", "style": "primary"}
        ],
        [
            {"text": "TRAFFIC", "icon_custom_emoji_id": "5352877703043258544", "style": "success"},
            {"text": "2FA ONLINE", "icon_custom_emoji_id": "5267421176841398765", "style": "primary"}
        ],
        [
            {"text": "Refer", "icon_custom_emoji_id": "5420396762189831222", "style": "success"},
            {"text": "WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "style": "danger"}
        ],
        [
            {"text": "SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "style": "primary"}
        ]
    ]
    if is_admin(user_id):
        kb.append([{"text": "Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}

def get_admin_text():
    with _users_lock:
        users_count = len(all_known_users)
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())
    maint_status = "🟢 OFF" if not bot_settings.get("maintenance") else "🔴 ON"

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
        [{"text": "📁DATABASE", "icon_custom_emoji_id": "5352721946054268944", "callback_data": "database_menu", "style": "danger"}],
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

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "StexSMS Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_control", "style": "success"},
         {"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"}],
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}],
        [{"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"},
         {"text": "CHANGE PAYOUT", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "change_payout_menu", "style": "success"}],
        [{"text": "STRM Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "STRM_control", "style": "primary"},
         {"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def get_user_management_text():
    with _users_lock:
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

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

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
    kb = [[{"text": "Edit OTP Button Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}]]
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

def STRM_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    sup_status = "ON" if bot_settings.get("support_link") else "OFF"
    grp_status = "ON" if bot_settings.get("w_group") else "OFF"
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "STRM_toggle_w", "style": "primary"}],
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "STRM_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "STRM_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "STRM_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "STRM_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "STRM_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "STRM_num_share", "style": "primary"}],
        [{"text": f"SUPPORT LINK: {sup_status}", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "STRM_sup_link", "style": "success"},
         {"text": "W. METHODS", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. GROUP: {grp_status}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "STRM_w_group", "style": "success"},
         {"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        if isinstance(m, dict):
            name = m.get("name", "")
            eid = m.get("emoji_id", "")
            icon = eid if eid else "5190899075968441286"
        else:
            name = str(m)
            icon = "5190899075968441286"
        kb.append([{"text": f"Delete: {name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "STRM_control", "style": "primary"}])
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
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])

    if p["type"] != "Auto Captcha Panel":
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

    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
    back_data = "manage_api_panels" if p.get("type", "API Panel") == "API Panel" else "manage_cpt_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
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
        if srv not in stats:
            stats[srv] = {}
        if iso not in stats[srv]:
            stats[srv][iso] = {"count": 0, "flag": flag}
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
            c_list = sorted(countries.items(), key=lambda x: x[1]["count"], reverse=True)
            c_list = c_list[:7]
            for i, (iso, c_data) in enumerate(c_list):
                prem_flag_html = get_flag_info_html(iso)
                count = c_data["count"]
                c_name = iso
                for code, fdata in bot_settings.get("premium_flags", {}).items():
                    if fdata.get("iso") == iso:
                        c_name = fdata.get("name", iso)
                        break
                txt += f"├ {prem_flag_html} <b>{c_name} ({iso})</b>\n"
                txt += f"│ ╰ Success: {count}\n"
                if i < len(c_list) - 1:
                    txt += "│\n"
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
            if num in stex_assigned_numbers:
                del stex_assigned_numbers[num]
            if num in voltx_assigned_numbers:
                del voltx_assigned_numbers[num]
        save_db()
        kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
        try: edit_message(chat_id, prev_msg_id, "ㅤ\n", reply_markup={"inline_keyboard": kb})
        except: pass
        del user_active_sessions[chat_id]


# ==========================================
# Withdrawal Group Message Builder
# ==========================================
def build_withdrawal_group_msg(chat_id, full_name, amount, number, method, req_id):
    frog_emoji = '<tg-emoji emoji-id="6307777408300753473">🐸</tg-emoji>'
    web_emoji = '<tg-emoji emoji-id="6206245785877616415">🕸️</tg-emoji>'
    user_emoji = '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>'
    money_emoji = '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>'
    phone_emoji = '<tg-emoji emoji-id="5337132498965010628">🍏</tg-emoji>'
    bank_emoji = '<tg-emoji emoji-id="5348469219761626211">🏦</tg-emoji>'
    tkt_emoji = '<tg-emoji emoji-id="5192739271886282680">🧾</tg-emoji>'

    method_icon = get_wmethod_emoji_html(method)

    txt = (
        f"🎙 <b>NEW WITHDRAWAL</b> {web_emoji}\n"
        f"{frog_emoji} <b>USER ID :</b><code>{chat_id}</code>\n"
        f"{user_emoji} <b>User :</b> <a href='tg://user?id={chat_id}'>{full_name}</a>\n"
        f"{money_emoji} <b>BALANCE:</b> <code>{amount}</code>\n"
        f"{phone_emoji} <b>NUMBER :</b> <code>{number}</code>\n"
        f"{bank_emoji} <b>METHOD :</b> {method_icon} <b>{method}</b>\n\n"
        f"{tkt_emoji} <b>WITHDRAW ID :</b> <code>{req_id}</code>"
    )
    return render_body_text(txt)


# ==========================================
# Numbers Header Builder
# ==========================================
def build_numbers_header(country, service=None, payout=None):
    HEADER_EMOJI_1 = "6282641460093260838"
    HEADER_EMOJI_2 = "6267315814190290529"
    PHONE_ICON     = "5197474438970363734"
    NOPHONE_ICON   = "6266787022111773140"
    flag_html = get_flag_info_html(country)

    if payout is None:
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
    else:
        payout_val = float(payout)

    try:
        payout_str = f"{float(payout_val):.10f}".rstrip('0').rstrip('.')
        if '.' not in payout_str: payout_str += ".00"
    except:
        payout_str = "0.00"

    header = (
        f'<tg-emoji emoji-id="{HEADER_EMOJI_1}">⚙️</tg-emoji> <b>THIS IS YOUR</b>'
        f'<tg-emoji emoji-id="{HEADER_EMOJI_2}">📱</tg-emoji>'
        f'<b>{html.escape(str(country).upper())}</b>{flag_html} <b>NUMBERS</b>'
        f'<tg-emoji emoji-id="{PHONE_ICON}">📱</tg-emoji>\n'
        f'<b>💰{payout_str}/OTP</b> <tg-emoji emoji-id="{NOPHONE_ICON}">📵</tg-emoji>\n'
    )
    return render_body_text(header)


# ==========================================
# Message Handler
# ==========================================
def handle_message(msg):
    global total_uploaded_stats, total_assigned_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    if chat_type != "private":
        return
    text = msg.get("text", "")
    register_user_local(chat_id)

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return

    # ================== MAINTENANCE CHECK ==================
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
                if db:
                    try:
                        doc = db.collection('users').document(str(chat_id)).get(timeout=5.0)
                        if not doc.exists:
                            get_user(chat_id)
                            db.collection('users').document(str(chat_id)).update({"referred_by": inviter, "ref_paid": False}, timeout=5.0)
                    except: pass

    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return

    MAIN_MENU_CMDS = ["GET NUMBER", "Search Number", "TRAFFIC", "Refer", "WITHDRAWAL", "SUPPORT", "Admin Panel", "2FA ONLINE"]
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True

    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]

        # ================== AUTO CAPTCHA PANEL SETUP ==================
        if state == "wait_for_cpanel_url" and text:
            temp_data[chat_id]["p_data"]["login_url"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_user"
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ Panel এর Username দিন:"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_user" and text:
            temp_data[chat_id]["p_data"]["username"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_pass"
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ Panel এর Password দিন:"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_pass" and text:
            temp_data[chat_id]["p_data"]["password"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_link"
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ যেখান থেকে SMS/OTP ডাটা আসবে সেই Link দিন:"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_msg_link" and text:
            temp_data[chat_id]["p_data"]["msg_link"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_name"
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ Data তে Number column এর নাম কী? (যেমন: number, phone):"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp_data[chat_id]["p_data"]["num_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_idx"
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Serial</b>\n➡️ Number Column এর Serial Number কত? (যেমন: 3, 5):"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["num_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_msg_col_name"
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ Message/OTP column এর নাম কী?"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp_data[chat_id]["p_data"]["msg_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_col_idx"
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Serial</b>\n➡️ Message Column এর Serial Number কত?"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["msg_col_idx"] = int(text)
                temp_data[chat_id]["p_data"]["login_status"] = "⏳ Pending Auto-Login..."
                bot_settings["panels"].append(temp_data[chat_id]["p_data"])
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Auto Captcha Panel Added Successfully!</b>"), reply_markup=main_menu(chat_id))
                msg_id = temp_data[chat_id]["msg_id"]
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_cpt_panels", "id": "internal"})
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return

        # ================== USER MANAGEMENT ==================
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb()); return
            target_uid = int(target_uid_str)
            if db:
                try:
                    doc = db.collection('users').document(str(target_uid)).get(timeout=5.0)
                    if not doc.exists:
                        send_message(chat_id, render_body_text("❌ User not found!"), reply_markup=get_cancel_kb()); return
                    current_bal = doc.to_dict().get('balance', 0.0)
                    temp_data[chat_id]["target_uid"] = target_uid
                    user_states[chat_id] = "wait_for_um_bal_amt"
                    send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {current_bal} ৳\n\n📝 Send amount (+/-):"), reply_markup=get_cancel_kb())
                except Exception as e:
                    send_message(chat_id, render_body_text(f"❌ DB error: {e}"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip())
                target_uid = temp_data[chat_id]["target_uid"]
                update_balance(target_uid, amt)
                send_message(chat_id, render_body_text(f"{PEM['ok']} Balance updated for {target_uid}!"), reply_markup=main_menu(chat_id))
                send_message(target_uid, render_body_text(f"🔔 Balance adjusted by <b>{amt} ৳</b> by Admin."))
                del user_states[chat_id]; del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount!"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb()); return
            target_uid = int(target_uid_str)
            if db:
                try:
                    doc_ref = db.collection('users').document(str(target_uid))
                    doc = doc_ref.get(timeout=5.0)
                    if not doc.exists:
                        send_message(chat_id, render_body_text("❌ User not found!"), reply_markup=get_cancel_kb()); return
                    current_status = doc.to_dict().get("banned", False)
                    new_status = not current_status
                    doc_ref.update({"banned": new_status}, timeout=5.0)
                    user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
                    status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
                    send_message(chat_id, render_body_text(f"✅ User {target_uid} → {status_text}!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]; del temp_data[chat_id]
                except Exception as e:
                    send_message(chat_id, render_body_text(f"❌ DB error: {e}"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb()); return
            target_uid = int(target_uid_str)
            if db:
                try:
                    doc = db.collection('users').document(str(target_uid)).get(timeout=5.0)
                    if not doc.exists:
                        send_message(chat_id, render_body_text("❌ User not found!"), reply_markup=get_cancel_kb()); return
                    data = doc.to_dict()
                    prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {data.get('balance', 0.0)} ৳
🤝 Refers: {data.get('total_refers', 0)}
🔐 OTPs: {data.get('total_otps', 0)}
🚫 Banned: {data.get('banned', False)}
➖➖➖➖➖➖➖➖"""
                    kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
                    send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
                    del user_states[chat_id]; del temp_data[chat_id]
                except Exception as e:
                    send_message(chat_id, render_body_text(f"❌ DB error: {e}"), reply_markup=get_cancel_kb())
            return

        # ================== MENU DESIGN ==================
        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                formatted_html_text = extract_premium_html(msg)
                bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                save_db()
                delete_message(chat_id, msg["message_id"])
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Updated!</b>\n\n🎨 <b>{menu_key.upper()}</b>\n\n{preview_text}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                send_message(chat_id, f"❌ Error: {e}")
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    emoji_id = None
                    emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0); length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                            break
                    if emoji_char: btn_text = btn_text.replace(emoji_char, "").strip()
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary"}
                    if emoji_id: btn_data["icon_custom_emoji_id"] = emoji_id
                    bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['gear']} <b>Edit Buttons: {menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format."))
            except: pass
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        # ================== TEST FLOW ==================
        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 Send the Number:"), reply_markup=get_cancel_kb()); return
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 Send the OTP:"), reply_markup=get_cancel_kb()); return
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 Send the Language (EN, AR):"), reply_markup=get_cancel_kb()); return
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"): lang = "#" + lang
            srv = temp_data[chat_id]["service"]; num = temp_data[chat_id]["number"]; otp = temp_data[chat_id]["otp"]
            app_full_name, _ = get_service_info_html(srv)
            msg_text = render_body_text(format_otp_display(num, app_full_name, lang, masked=True))
            for fw in bot_settings["fw_groups"]:
                kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                for btn in fw.get("buttons", []):
                    b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
                    if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                    kb.append([b_obj])
                send_message(fw["chat_id"], msg_text, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test sent!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]; del temp_data[chat_id]
            return

        # ================== EMOJI MANAGEMENT ==================
        elif state == "wait_for_emoji_extract":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0); length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode('utf-16-le')
                    emoji_text = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                    break
            if custom_emoji_id:
                temp_data[chat_id] = {"id": custom_emoji_id, "char": emoji_text}
                user_states[chat_id] = "wait_for_emoji_details"
                send_message(chat_id, render_body_text(f"{PEM['ok']} Emoji ID: <code>{custom_emoji_id}</code>\n\n<b>ফরমেট:</b>\n`FLAG | 880 | BD | Bangladesh`\nঅথবা\n`APP | WhatsApp`"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} Premium Emoji পাওয়া যায়নি!"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_emoji_details" and text:
            parts = [p.strip() for p in text.split("|")]
            mode = parts[0].upper()
            eid = temp_data[chat_id]["id"]; char = temp_data[chat_id]["char"]
            if mode == "FLAG" and len(parts) == 4:
                code, iso, name = parts[1], parts[2], parts[3]
                bot_settings["premium_flags"][code] = {"char": char, "iso": iso.upper(), "name": name, "id": eid}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Flag saved!"), reply_markup=emoji_settings_keyboard())
            elif mode == "APP" and len(parts) == 2:
                name = parts[1]
                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name.title()}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} App Emoji saved!"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} ফরম্যাট ভুল!"))
            del user_states[chat_id]; del temp_data[chat_id]
            return
        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} .txt only.")); return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            content = requests.get(f"{FILE_URL}{file_path}").text
            mode = "flags" if state == "wait_for_flag_txt" else "apps"
            count = 0
            if mode == "flags":
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji"); eid = data.get("id")
                            prefix_str = line[:json_match.start()].strip()
                            code_match = re.search(r'\((\d+)\)', prefix_str)
                            iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                            if code_match and iso_match and char and eid:
                                code = code_match.group(1); iso = iso_match.group(1).upper()
                                name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                count += 1
                        except: pass
            else:
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji"); eid = data.get("id")
                            name_part = line[:json_match.start()].strip()
                            name = name_part.replace(char, '').strip() if char else name_part
                            if char and eid and name:
                                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                count += 1
                        except: pass
            save_db()
            send_message(chat_id, render_body_text(f"{PEM['ok']} Loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            del user_states[chat_id]
            return

        # ================== BROADCAST ==================
        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id)).start()
            del user_states[chat_id]
            return

        # ================== UPLOAD NUMBER ==================
        elif state == "wait_for_txt" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"{FILE_URL}{file_path}").text
            temp_data[chat_id] = {"numbers": file_content.splitlines(), "filename": doc["file_name"]}
            user_states[chat_id] = "wait_for_service"
            send_message(chat_id, render_body_text(f"{PEM['ok']} File received.\n\n📌 Enter the service name:"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_service" and text:
            temp_data[chat_id]["service"] = text.upper()
            user_states[chat_id] = "wait_for_country"
            send_message(chat_id, render_body_text(f"{PEM['ok']} Service set.\n\n🌍 Enter the country name:"), reply_markup=get_cancel_kb())
            return
        elif state == "wait_for_country" and text:
            country = text.upper()
            service = temp_data[chat_id]["service"]
            raw_numbers = temp_data[chat_id]["numbers"]
            clean_nums = []
            for num in raw_numbers:
                num = num.strip()
                if num:
                    if not num.startswith('+'): num = '+' + num
                    clean_nums.append(num)
            country_iso = ""
            if clean_nums:
                _, iso_x, _ = get_country_from_num(clean_nums[0])
                if iso_x and iso_x != "XX": country_iso = iso_x
            batch_id = str(uuid.uuid4())[:8]
            number_batches[batch_id] = {
                "filename": temp_data[chat_id]["filename"],
                "service": service,
                "country": country,
                "country_iso": country_iso,
                "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]
            }
            total_uploaded_stats += len(clean_nums)
            save_db()
            app_full_name, prem_app_html = get_service_info_html(service)
            prem_flag_html = get_flag_info_html(clean_nums[0]) if clean_nums else f"{PEM['world']}"
            broadcast_txt = f"➖➖➖➖➖➖➖➖\n《 NEW NUMBERS 》\n➖➖➖➖➖➖➖➖\n{prem_flag_html} {country} {prem_app_html} {service}\n➖➖➖➖➖➖➖➖\n📤 Total Added: <b>{len(clean_nums)}</b>\n➖➖➖➖➖➖➖➖\nUse /start to get your numbers!"
            broadcast_txt = render_body_text(broadcast_txt)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Numbers added! Starting broadcast..."))
            def simple_broadcast(txt):
                b_session = requests.Session()
                url = f"{BASE_URL}/sendMessage"
                with _users_lock:
                    users_copy = list(all_known_users)
                for u_id in users_copy:
                    try:
                        b_session.post(url, json={"chat_id": u_id, "text": txt, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=5)
                    except: pass
                    time.sleep(0.035)
            threading.Thread(target=simple_broadcast, args=(broadcast_txt,)).start()
            del user_states[chat_id]; del temp_data[chat_id]
            return

        # ================== STEX/VOLTX KEYS ==================
        elif state == "wait_for_add_stex_key" and text:
            bot_settings["stex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ StexSMS Key Added!"), reply_markup=stex_control_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]
            return
        elif state == "wait_for_add_voltx_key" and text:
            bot_settings["voltx_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Voltx Key Added!"), reply_markup=voltx_control_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]
            return
        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
            bot_settings["search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "stex_search_country", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]
            return
        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
            bot_settings["voltx_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "voltx_search_country", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]
            return
        elif state == "wait_nx_srv_name" and text:
            srv = text.strip().upper()
            if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
            if srv not in bot_settings["stex_services"]: bot_settings["stex_services"][srv] = {}
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_stex_srv", "id": "internal"})
            del user_states[chat_id]
            return
        elif state == "wait_nx_cnt_name" and text:
            cnt = text.strip(); srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["stex_services"][srv]: bot_settings["stex_services"][srv][cnt] = []
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return
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
            del user_states[chat_id]
            return
        elif state == "wait_vx_srv_name" and text:
            srv = text.strip().upper()
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            if srv not in bot_settings["voltx_services"]: bot_settings["voltx_services"][srv] = {}
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_voltx_srv", "id": "internal"})
            del user_states[chat_id]
            return
        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip(); srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["voltx_services"][srv]: bot_settings["voltx_services"][srv][cnt] = []
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return
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
            del user_states[chat_id]
            return

        # ================== WITHDRAW METHOD / FJ / ADMIN / OTP GROUP ==================
        elif state == "wait_for_add_wm" and text:
            raw = text.strip()
            if "|" in raw:
                parts = raw.split("|", 1)
                m_name = parts[0].strip()
                m_eid = parts[1].strip()
                m_char = "💳"
                method_obj = {"name": m_name, "emoji_id": m_eid, "char": m_char}
                bot_settings["w_methods"].append(method_obj)
            else:
                bot_settings["w_methods"].append(raw)
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]
            return
        elif state == "wait_for_add_fj" and text:
            bot_settings["fj_channels"].append(parse_chat_id(text))
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🔗 <b>FORCE JOIN</b>"), reply_markup=fj_settings_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]
            return
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                bot_settings["admins"].append(int(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]
            return
        elif state == "wait_for_add_fw_id" and text:
            bot_settings["fw_groups"].append({"chat_id": text.strip(), "buttons": []})
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP</b>"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]
            return
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
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                if emoji_char: btn_text = btn_text.replace(emoji_char, "").strip()
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id: btn_data["icon_custom_emoji_id"] = emoji_id
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Group:</b> {bot_settings['fw_groups'][fw_idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]; del temp_data[chat_id]
            return
        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP</b>"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]
            return

        # ================== PANEL ADD ==================
        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp_data[chat_id].get("add_type", "api")
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            if t_key == "logc":
                user_states[chat_id] = "wait_for_cpanel_url"
                temp_data[chat_id] = {"msg_id": msg_id, "p_data": {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", "records": 0, "login_status": "⏳ Pending First Login"
                }}
                edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>"), reply_markup=get_cancel_kb())
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
        elif state == "wait_for_api_pf_value" and text:
            idx = temp_data[chat_id]["p_idx"]; field = temp_data[chat_id]["p_field"]
            new_value = text.strip()
            if new_value.lower() == "/cancel":
                del user_states[chat_id]; del temp_data[chat_id]
                p = bot_settings["panels"][idx]
                send_message(chat_id, render_body_text(f"⚙️ <b>Configure</b> <b>{p['name']}</b>"), reply_markup=panel_config_keyboard(idx))
                return
            if field in ["interval_sec", "records"]:
                try: new_value = int(new_value)
                except ValueError: send_message(chat_id, render_body_text("❌ <b>Please send a valid number.</b>")); return
            bot_settings["panels"][idx][field] = new_value
            save_db()
            del user_states[chat_id]; del temp_data[chat_id]
            p = bot_settings["panels"][idx]
            send_message(chat_id, render_body_text(f"{PEM['ok']} <b>{field}</b> updated!"))
            send_message(chat_id, render_body_text(f"⚙️ <b>Configure</b> <b>{p['name']}</b>"), reply_markup=panel_config_keyboard(idx))
            return
        elif state == "wait_for_p_rec" and text:
            if text.isdigit():
                idx = temp_data[chat_id]["p_idx"]
                bot_settings["panels"][idx]["records"] = int(text)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Records:</b> {p.get('records')}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            else:
                send_message(chat_id, render_body_text("❌ Invalid number!"), reply_markup=get_cancel_kb())
            del user_states[chat_id]; del temp_data[chat_id]
            return

        # ================== STRM EDIT ==================
        elif state == "set_STRM":
            msg_id = temp_data[chat_id]["msg_id"]; key = temp_data[chat_id]["key"]
            try:
                if key in ["min_withdraw", "otp_reward", "refer_reward"]: bot_settings[key] = float(text)
                elif key in ["cooldown", "num_req", "num_share"]: bot_settings[key] = int(text)
                else: bot_settings[key] = text
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>STRM CONTROL PANEL</b>"), reply_markup=STRM_control_keyboard())
            except:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>STRM</b>\n\n❌ Invalid!"), reply_markup=STRM_control_keyboard())
            del user_states[chat_id]; del temp_data[chat_id]
            return

        # ================== CHANGE PAYOUT - Country new value ==================
        elif state == "set_payout_value" and text:
            msg_id = temp_data[chat_id]["msg_id"]
            service = temp_data[chat_id]["service"]
            country = temp_data[chat_id]["country"]
            try:
                new_val = float(text.strip())
                if new_val < 0: raise ValueError()
                if "otp_pair_rates" not in bot_settings: bot_settings["otp_pair_rates"] = {}
                key = f"{str(country).upper()}|{str(service).upper()}"
                bot_settings["otp_pair_rates"][key] = new_val
                save_db()
                country_flag = get_flag_info_html(country)
                delete_message(chat_id, msg["message_id"])
                ok_txt = (
                    f"{PEM['ok']} <b>Payout Updated Successfully!</b>\n\n"
                    f"🌍 <b>Country:</b> <code>{country}</code> {country_flag}\n"
                    f"🔧 <b>Service:</b> <code>{service}</code>\n"
                    f"💰 <b>New Payout:</b> <code>${new_val}</code>"
                )
                edit_message(chat_id, msg_id, render_body_text(ok_txt), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "change_payout_menu", "style": "primary"}]]})
            except ValueError:
                send_message(chat_id, render_body_text("❌ <b>Invalid value!</b> Please send a number."), reply_markup=get_cancel_kb())
            del user_states[chat_id]; del temp_data[chat_id]
            return

        # ================== DATABASE RESTORE ==================
        elif state == "wait_for_data_zip" and "document" in msg:
            doc = msg["document"]
            if doc["file_name"] != "STRM_BOT_DATA.zip":
                send_message(chat_id, render_body_text(f"{PEM['no']} <b>File name must be exactly</b> <code>STRM_BOT_DATA.zip</code>"))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            raw_bytes = requests.get(f"{FILE_URL}{file_path}").content
            try:
                with zipfile.ZipFile(io.BytesIO(raw_bytes), 'r') as zf:
                    zf.extractall(".")
                load_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Data restored successfully!</b>"), reply_markup=main_menu(chat_id))
            except Exception as e:
                send_message(chat_id, render_body_text(f"❌ <b>Restore failed:</b> {html.escape(str(e))}"))
            if chat_id in user_states: del user_states[chat_id]
            return

        # ================== SEARCH NUMBER ==================
        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text("❌ 3-9 digit number required!")); return
            wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing...</i>"))
            wait_msg_id = wait_msg.get("result", {}).get("message_id")
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            fetched_nums = []
            if not found_indices:
                stex_allowed = bot_settings.get("search_countries", [])
                voltx_allowed = bot_settings.get("voltx_search_countries", [])
                is_stex_allowed = any(query.startswith(c) for c in stex_allowed) if stex_allowed else False
                is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
                if not is_stex_allowed and not is_voltx_allowed:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Country not allowed!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]; return
                if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Fetching via API...</i>"))
                is_voltx_used = False
                req_count = bot_settings.get("num_req", 1)
                if is_voltx_allowed:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json={"rid": query}, headers={"mauthapi": api_key}, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id
                                    is_voltx_used = True
                                    total_assigned_stats += 1
                                    break
                            except: continue
                if len(fetched_nums) < req_count and is_stex_allowed:
                    stex_keys = bot_settings.get("stex_keys", [])
                    for _ in range(req_count - len(fetched_nums)):
                        for api_key in stex_keys:
                            try:
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers={"mauthapi": api_key}, timeout=10)
                                data = res.json()
                                if data.get("meta", {}).get("code") == 200 and data.get("data"):
                                    num_str = str(data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id
                                    total_assigned_stats += 1
                                    break
                            except: continue
                if not fetched_nums:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Out of stock!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]; return
                for n in fetched_nums:
                    cn_x = str(n).replace("+", "").strip()
                    _, iso_x, _ = get_country_from_num(n)
                    country_name_x = ""
                    for _c, fdata in bot_settings.get("premium_flags", {}).items():
                        if fdata.get("iso") == iso_x: country_name_x = fdata.get("name", ""); break
                    if not country_name_x and iso_x and iso_x != "XX":
                        for _c, cinfo in COUNTRY_DB.items():
                            if cinfo["iso"] == iso_x: country_name_x = cinfo["name"]; break
                    assigned_number_meta[cn_x] = {"country": country_name_x, "service": "", "iso": iso_x}
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    fetched_nums.append(num_str)
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    cn = num_str.replace("+", "").strip()
                    bd_country = number_batches[b_id]["country"]
                    bd_service = number_batches[b_id]["service"]
                    bd_iso = number_batches[b_id].get("country_iso", "")
                    _pv = float(bot_settings.get("otp_reward", 0.0))
                    _pr = bot_settings.get("otp_pair_rates", {})
                    _pk = f"{str(bd_country).upper()}|{str(bd_service).upper()}"
                    if _pk in _pr:
                        try: _pv = float(_pr[_pk])
                        except: pass
                    assigned_number_meta[cn] = {"country": bd_country, "service": bd_service, "iso": bd_iso, "payout": _pv}
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
            if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text(f"{PEM['ok']} <b>Number Found!</b>"))
            kb = []
            flags_db = bot_settings.get("premium_flags", {})
            for num in fetched_nums:
                _, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not num.startswith("+") else num
                emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: emoji_id = flag_data["id"]
                        break
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
            vtx_ext = "_vtx" if 'is_voltx_used' in locals() and is_voltx_used else ""
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{vtx_ext}", "style": "danger"},
                       {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns:
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            hdr_country = query
            if fetched_nums:
                try:
                    _, iso_x, _ = get_country_from_num(fetched_nums[0])
                    if iso_x and iso_x != "XX":
                        for cn2, ci2 in COUNTRY_DB.items():
                            if ci2["iso"] == iso_x: hdr_country = ci2["name"]; break
                except: pass
            header_txt = build_numbers_header(hdr_country)
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, header_txt, reply_markup={"inline_keyboard": kb})
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            else:
                msg_res = send_message(chat_id, header_txt, reply_markup={"inline_keyboard": kb})
                if msg_res and "result" in msg_res:
                    user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}
            return

        # ================== WITHDRAW AMOUNT ==================
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = float(text.strip())
                bal = temp_data[chat_id]["balance"]
                min_w = bot_settings['min_withdraw']
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Min {min_w} ৳!\n💰 Balance: {bal} ৳"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Insufficient balance!\n💰 {bal} ৳"), reply_markup=get_cancel_kb())
                    return
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"✅ Amount: {amount} ৳\n\n📱 Send your <b>{temp_data[chat_id]['method']}</b> number:"), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount!"), reply_markup=get_cancel_kb())
            return

        # ================== 2FA ==================
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
            delete_message(chat_id, msg.get("message_id"))
            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error.")); del user_states[chat_id]; return
            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret); code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                success_txt = (f"━━━━━━━━━━━━━━━\n《 🔐 <b>2FA CODE</b> 》\n━━━━━━━━━━━━━━━\n"
                              f"🔐 <b>CODE:</b> <code>{code}</code>\n━━━━━━━━━━━━━━━\n"
                              f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n━━━━━━━━━━━━━━━")
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

        # ================== WITHDRAW NUMBER ==================
        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            method = temp_data[chat_id]["method"]
            amount = temp_data[chat_id]["amount"]
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            pending_withdrawals[req_id] = {
                "user_id": chat_id, "amount": amount, "method": method,
                "number": number, "full_name": full_name
            }
            if db:
                try:
                    db.collection('withdrawals').document(req_id).set({
                        "user_id": str(chat_id), "amount": amount, "method": method,
                        "status": "pending", "timestamp": firestore.SERVER_TIMESTAMP
                    }, timeout=5.0)
                except: pass
            if bot_settings["w_group"]:
                admin_msg = build_withdrawal_group_msg(chat_id, full_name, amount, number, method, req_id)
                kb = {"inline_keyboard": [[
                    {"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"},
                    {"text": "REJECT", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrej_{req_id}", "style": "danger"}
                ]]}
                send_message(bot_settings["w_group"], admin_msg, reply_markup=kb)
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            success_text = f"{PEM['ok']} Withdrawal submitted!\n\n🧾 <b>Req ID:</b> {req_id}\n💰 <b>Amount:</b> {amount} ৳\n🏦 <b>Method:</b> {method}\n📱 <b>Number:</b> <code>{number}</code>"
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
            del user_states[chat_id]
            del temp_data[chat_id]
            return

    # ==========================================
    # Regular Commands
    # ==========================================
    if text.startswith("/start"):
        get_user(chat_id)
        if db:
            try:
                doc = db.collection('users').document(str(chat_id)).get(timeout=5.0)
                if doc.exists:
                    u_data = doc.to_dict()
                    if u_data.get("referred_by") and not u_data.get("ref_paid"):
                        inviter = u_data["referred_by"]
                        db.collection('users').document(str(chat_id)).update({"ref_paid": True}, timeout=5.0)
                        reward = bot_settings.get("refer_reward", 0.2)
                        update_balance(inviter, reward)
                        db.collection('users').document(str(inviter)).update({"total_refers": firestore.Increment(1)}, timeout=5.0)
                        ref_msg = (f"{PEM['gift']} <b>New Referral !</b>\n------------------\n🔥 <b>You Received {reward} TK</b>\n------------------\n{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>")
                        send_message(inviter, render_body_text(ref_msg))
            except: pass
        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))

    elif text == "TRAFFIC":
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)

    elif text == "Refer":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        raw_txt = c_msg.get("text", f"{PEM['gift']} Refer").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", str(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "WITHDRAWAL":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} Withdrawals disabled."))
            return
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = (c_msg.get("text", "Withdrawal")
                   .replace("{user_id}", str(chat_id))
                   .replace("{bal}", f"{float(bal):.2f}")
                   .replace("{total_otp}", str(u_data.get('total_otps', 0)))
                   .replace("{total_ref}", str(u_data.get('total_refers', 0)))
                   .replace("{min_w}", f"{float(bot_settings['min_withdraw']):.2f}"))
        txt = render_body_text(raw_txt)
        kb = []
        for m_name, m_emoji in get_wmethod_display_list():
            kb.append([{"text": m_name.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m_name.strip()}", "style": "primary"}])
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
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
            send_message(chat_id, render_body_text(f"{PEM['no']} No services!"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            for s in all_services:
                emoji_id = "5352694861990501856"
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                kb.append([{"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"}])
            for b in c_msg.get("buttons", []):
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Search Number":
        user_states[chat_id] = "wait_for_search"
        c_msg = bot_settings["custom_messages"].get("search_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['num']} Search Number"))
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate 2FA code.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif text == "SUPPORT":
        c_msg = bot_settings["custom_messages"].get("support", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['msg']} Support"))
        if not txt.strip(): txt = render_body_text(f"{PEM['msg']} Support")
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        sup_link = bot_settings.get("support_link", "")
        if sup_link:
            kb.insert(0, [{"text": "Contact Support", "icon_custom_emoji_id": "5337302974806922068", "url": sup_link, "style": "success"}])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb} if kb else None)
        # ==========================================
# Database Helpers
# ==========================================
def build_data_zip():
    """সব ডেটা (Firestore + Local) একটি zip এ প্যাক করে bytes রিটার্ন করবে"""
    mem = io.BytesIO()
    try:
        with zipfile.ZipFile(mem, 'w', zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists(DB_FILE):
                zf.write(DB_FILE, DB_FILE)
            if os.path.exists("users_list.json"):
                zf.write("users_list.json", "users_list.json")
            if db:
                try:
                    all_users_data = {}
                    for doc in db.collection('users').stream():
                        all_users_data[doc.id] = doc.to_dict()
                    zf.writestr("firestore_users.json", json.dumps(all_users_data, default=str, indent=2))
                except: pass
                try:
                    all_wd = {}
                    for doc in db.collection('withdrawals').stream():
                        all_wd[doc.id] = doc.to_dict()
                    zf.writestr("firestore_withdrawals.json", json.dumps(all_wd, default=str, indent=2))
                except: pass
                try:
                    stg = db.collection('settings').document('bot_config').get(timeout=8.0)
                    if stg.exists:
                        zf.writestr("firestore_settings.json", json.dumps(stg.to_dict(), default=str, indent=2))
                except: pass
        mem.seek(0)
        return mem.getvalue()
    except Exception as e:
        print(f"ZIP build error: {e}")
        return None


def delete_all_data():
    """সব ডেটা ডিলিট করে দেবে — Firestore users/withdrawals + Local DB"""
    global number_batches, used_numbers_list, stex_assigned_numbers, voltx_assigned_numbers
    global total_uploaded_stats, total_assigned_stats, recent_traffic, assigned_number_meta
    global all_known_users
    if db:
        try:
            for doc in db.collection('users').stream():
                try: doc.reference.delete()
                except: pass
        except: pass
        try:
            for doc in db.collection('withdrawals').stream():
                try: doc.reference.delete()
                except: pass
        except: pass
    number_batches = {}
    used_numbers_list = []
    stex_assigned_numbers = {}
    voltx_assigned_numbers = {}
    total_uploaded_stats = 0
    total_assigned_stats = 0
    recent_traffic = []
    assigned_number_meta = {}
    with _users_lock:
        all_known_users = set()
    try:
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        if os.path.exists("users_list.json"): os.remove("users_list.json")
    except: pass
    save_local_db()


# ==========================================
# Callback Query Handler
# ==========================================
def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")

    if not data.startswith("test_p_conn_") and not data.startswith("c_n_") and not data.startswith("g_c_"):
        try: threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except: pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    msg_id = call["message"]["message_id"]

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned!", show_alert=True)
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
            send_message(chat_id, render_body_text(f"{PEM['ok']} Thanks for joining!"), reply_markup=main_menu(chat_id))
            if db:
                try:
                    doc = db.collection('users').document(str(chat_id)).get(timeout=5.0)
                    if doc.exists:
                        u_data = doc.to_dict()
                        if u_data.get("referred_by") and not u_data.get("ref_paid"):
                            inviter = u_data["referred_by"]
                            db.collection('users').document(str(chat_id)).update({"ref_paid": True}, timeout=5.0)
                            reward = bot_settings.get("refer_reward", 0.2)
                            update_balance(inviter, reward)
                            db.collection('users').document(str(inviter)).update({"total_refers": firestore.Increment(1)}, timeout=5.0)
                            ref_msg = (f"{PEM['gift']} <b>New Referral !</b>\n------------------\n🔥 <b>You Received {reward} TK</b>\n------------------\n{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>")
                            send_message(inviter, render_body_text(ref_msg))
                except: pass
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels!", show_alert=True)
        return

    if data == "close_msg":
        delete_message(chat_id, msg_id)

    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
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
                          f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n━━━━━━━━━━━━━━━")
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except:
            answer_callback(call["id"], "❌ Error!", show_alert=True)

    elif data == "cancel_STRM_edit":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>STRM CONTROL PANEL</b>"), reply_markup=STRM_control_keyboard())

    elif data == "dummy_alert":
        answer_callback(call["id"], "Coming soon!", show_alert=True)

    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Refreshed!", show_alert=False)

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
            emoji_id = "5780471598922337683"
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

    # ==========================================
    # User Management
    # ==========================================
    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())
    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send User ID:"), reply_markup=get_cancel_kb())
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send User ID:"), reply_markup=get_cancel_kb())
    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send User ID:"), reply_markup=get_cancel_kb())

    # ==========================================
    # Menu Design
    # ==========================================
    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Menu Design Editor</b>"), reply_markup=menu_design_list_keyboard())
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
        except: pass
    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        user_states[chat_id] = "wait_for_menu_text"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Edit Body: {key.upper()}</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})
    elif data.startswith("md_btns_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_btns_", "")
        try: edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Buttons:</b> <b>{key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except: pass
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

    # ==========================================
    # Withdraw method selection
    # ==========================================
    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        if bal < min_w:
            answer_callback(call["id"], f"❌ Min {min_w} ৳ required!", show_alert=True); return
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>{method}</b>\n💰 <b>{bal}</b> ৳\n\nEnter amount:"), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    # ==========================================
    # Emoji Management
    # ==========================================
    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>"), reply_markup=emoji_settings_keyboard())
    elif data == "up_flags_txt":
        user_states[chat_id] = "wait_for_flag_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Upload Flag Emojis <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})
    elif data == "up_apps_txt":
        user_states[chat_id] = "wait_for_app_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Upload Service Apps <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})
    elif data == "add_single_emoji":
        user_states[chat_id] = "wait_for_emoji_extract"
        edit_message(chat_id, msg_id, render_body_text("📝 Send any Premium Emoji (e.g., 🇧🇩 or 🚫):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})
    elif data == "dl_flags_txt":
        content = generate_emoji_txt("flags")
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ Empty!", show_alert=True)
    elif data == "dl_apps_txt":
        content = generate_emoji_txt("apps")
        if content:
            send_document(chat_id, "Service_Apps.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ Empty!", show_alert=True)
    elif data == "del_all_flags":
        bot_settings["premium_flags"] = {}
        save_db()
        answer_callback(call["id"], "✅ All Flags Deleted!", show_alert=True)

    # ==========================================
    # Broadcast / Upload / Delete
    # ==========================================
    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message to broadcast."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})
    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Upload numbers in <b>.txt</b> file."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})
    elif data == "delete_files":
        kb = []
        for b_id, b_data in number_batches.items():
            kb.append([{"text": f"{b_data['filename']} ({len(b_data['numbers'])})", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a file to delete:" if len(kb) > 1 else f"{PEM['no']} No files."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            del number_batches[b_id]
            save_db()
            answer_callback(call["id"], "✅ File deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_used":
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Used:</b> {len(used_numbers_list)}"), reply_markup=kb)
    elif data == "show_unused":
        unused_count = sum(len(b["numbers"]) for b in number_batches.values())
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Unused:</b> {unused_count}"), reply_markup=kb)
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

    # ==========================================
    # Leaderboard
    # ==========================================
    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━"
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
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        try:
            if not db:
                edit_message(chat_id, msg_id, render_body_text("❌ Firebase disabled!"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})
                return
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""; count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data.</i>\n"
            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""; count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data.</i>\n"
            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""; count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history.</i>\n"
            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})
        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>"), reply_markup=system_settings_keyboard())

    # ==========================================
    # MAINTENANCE TOGGLE
    # ==========================================
    elif data == "toggle_maintenance":
        current = bot_settings.get("maintenance", False)
        bot_settings["maintenance"] = not current
        save_db()
        if bot_settings["maintenance"]:
            edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
            answer_callback(call["id"], "🔴 Maintenance Mode: ON", show_alert=True)
        else:
            edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
            answer_callback(call["id"], "🟢 Maintenance Mode: OFF", show_alert=True)
            thanks_msg = (
                f'<tg-emoji emoji-id="6204104220694550861">🐷</tg-emoji> <b>Thanks For Qopareting With Us</b> '
                f'<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>\n'
                f'Now You Can Use The Bot Properly '
                f'<tg-emoji emoji-id="6267107057304868214">🪲</tg-emoji>'
            )
            threading.Thread(target=broadcast_text_all, args=(render_body_text(thanks_msg),), daemon=True).start()

    # ==========================================
    # DATABASE MENU
    # ==========================================
    elif data == "database_menu":
        txt = (
            f'{PEM["file"]} <b>DATABASE MANAGEMENT</b>\n'
            f'━━━━━━━━━━━━━━━\n'
            f'<i>Choose an option below:</i>'
        )
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=database_menu_keyboard())

    elif data == "db_download":
        wait = send_message(chat_id, render_body_text("⏳ <i>Preparing database zip...</i>"))
        wait_id = wait.get("result", {}).get("message_id")
        try:
            raw = build_data_zip()
            if wait_id: delete_message(chat_id, wait_id)
            if raw:
                send_document_bytes(chat_id, "STRM_BOT_DATA.zip", raw)
                send_message(chat_id, render_body_text(f'{PEM["ok"]} <b>Database Downloaded!</b>'), reply_markup=database_menu_keyboard())
            else:
                send_message(chat_id, render_body_text(f'{PEM["no"]} <b>Failed to build zip!</b>'))
        except Exception as e:
            if wait_id: delete_message(chat_id, wait_id)
            send_message(chat_id, render_body_text(f'❌ Error: {html.escape(str(e))}'))

    elif data == "db_upload":
        user_states[chat_id] = "wait_for_data_zip"
        edit_message(chat_id, msg_id, render_body_text("📂 Send the <code>STRM_BOT_DATA.zip</code> file to restore:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "database_menu", "style": "danger"}]]})

    elif data == "db_delete_confirm":
        txt = (
            f'<tg-emoji emoji-id="6203773684306418660">❓</tg-emoji> '
            f'<b>DO YOU REALY WANT TO REMOVE ALL THE DATA\'S ?</b>'
        )
        kb = {"inline_keyboard": [
            [{"text": "✅YES REMOVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "db_delete_yes", "style": "success"}],
            [{"text": "❌NO DON'T REMOVE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "db_delete_no", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)

    elif data == "db_delete_yes":
        delete_all_data()
        edit_message(chat_id, msg_id, render_body_text(f'{PEM["ok"]} <b>All data has been removed successfully!</b>'), reply_markup=database_menu_keyboard())

    elif data == "db_delete_no":
        edit_message(chat_id, msg_id, render_body_text(f'{PEM["ok"]} <b>Cancelled.</b>'), reply_markup=database_menu_keyboard())

    # ==========================================
    # CHANGE PAYOUT Flow
    # ==========================================
    elif data == "change_payout_menu":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        all_services = sorted(local_srvs.union(stex_srvs).union(voltx_srvs))
        if not all_services:
            edit_message(chat_id, msg_id, render_body_text(f'{PEM["no"]} <b>No services available!</b>'), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]]})
            return
        apps_db = bot_settings.get("premium_apps", {})
        kb = []; row = []
        for s in all_services:
            emoji_id = "5352694861990501856"
            for ak, ad in apps_db.items():
                if s.upper() == ak or s.upper() in ak or ak in s.upper():
                    if "id" in ad: emoji_id = ad["id"]; break
            row.append({"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"cp_srv|{s}", "style": "primary"})
            if len(row) == 2:
                kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
        txt = (
            f'<tg-emoji emoji-id="5190899075968441286">💳</tg-emoji> '
            f'<b>CHANGE PAYOUT</b>\n'
            f'━━━━━━━━━━━━━━━\n'
            f'📌 <b>Select a Service</b> to change its payout:'
        )
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("cp_srv|"):
        srv = data.replace("cp_srv|", "")
        local_cnts = set()
        for b in number_batches.values():
            if b["service"] == srv and b["numbers"]:
                local_cnts.add(b["country"])
        stex_cnts = set(bot_settings.get("stex_services", {}).get(srv, {}).keys())
        voltx_cnts = set(bot_settings.get("voltx_services", {}).get(srv, {}).keys())
        all_countries = sorted(local_cnts.union(stex_cnts).union(voltx_cnts))
        if not all_countries:
            edit_message(chat_id, msg_id, render_body_text(f'{PEM["no"]} <b>No countries found for {srv}!</b>'), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "change_payout_menu", "style": "primary"}]]})
            return
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in all_countries:
            emoji_id = "5780471598922337683"
            for fc, fd in flags_db.items():
                iso = fd.get("iso", "").upper(); name = fd.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in fd: emoji_id = fd["id"]; break
            kb.append([{"text": f"{c}", "icon_custom_emoji_id": emoji_id, "callback_data": f"cp_cnt|{srv}|{c}", "style": "primary"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "change_payout_menu", "style": "danger"}])
        txt = (
            f'<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji> '
            f'<b>Select a Country for {srv}:</b>'
        )
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("cp_cnt|"):
        parts = data.split("|", 2)
        srv = parts[1]; country = parts[2]
        pr = bot_settings.get("otp_pair_rates", {})
        key = f"{country.upper()}|{srv.upper()}"
        if key in pr:
            try: current_payout = float(pr[key])
            except: current_payout = float(bot_settings.get("otp_reward", 0.0))
        else:
            current_payout = None
            for k, v in pr.items():
                try:
                    if k.split("|")[0] == country.upper():
                        current_payout = float(v); break
                except: pass
            if current_payout is None:
                current_payout = float(bot_settings.get("otp_reward", 0.0))

        country_flag = get_flag_info_html(country)

        user_states[chat_id] = "set_payout_value"
        temp_data[chat_id] = {"msg_id": msg_id, "service": srv, "country": country}

        txt = (
            f'<b>{country}</b>{country_flag} <b>Payout :</b> <code>{current_payout}</code>\n\n'
            f'<b>Send The New Value</b> <code>country_payout</code> :'
        )
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    # ==========================================
    # Stex Control
    # ==========================================
    elif data == "stex_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control</b>\n\nKeys: {len(bot_settings.get('stex_keys', []))}"), reply_markup=stex_control_keyboard())
    elif data == "add_stex_key":
        user_states[chat_id] = "wait_for_add_stex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send StexSMS API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}]]})
    elif data == "view_stex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("stex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_nxa_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Key:</b>"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("del_nxa_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("stex_keys", [])):
            del bot_settings["stex_keys"][idx]
            save_db()
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
        edit_message(chat_id, msg_id, render_body_text("📝 Country Code:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_search_country", "style": "danger"}]]})
    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("search_countries", [])):
            del bot_settings["search_countries"][idx]
            save_db()
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
        edit_message(chat_id, msg_id, render_body_text("📝 Service Name:"), reply_markup=get_cancel_kb())
    elif data.startswith("nx_srv_"):
        srv = data.replace("nx_srv_", "")
        kb = []
        countries = bot_settings["stex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
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
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Country for <b>{srv}</b>:"), reply_markup=get_cancel_kb())
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
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>{srv} | {cnt}</b>\nRanges: {len(ranges)}"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("nx_addr_"):
        parts = data.split("_"); srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_nx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 New Range for <b>{cnt}</b>:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_cnt_{srv}_{cnt}", "style": "danger"}]]})
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

    # ==========================================
    # Voltx Control
    # ==========================================
    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control</b>\n\nKeys: {len(bot_settings.get('voltx_keys', []))}"), reply_markup=voltx_control_keyboard())
    elif data == "add_voltx_key":
        user_states[chat_id] = "wait_for_add_voltx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Voltx API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})
    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Key:</b>"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_keys", [])):
            del bot_settings["voltx_keys"][idx]
            save_db()
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
        edit_message(chat_id, msg_id, render_body_text("📝 Range Code:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})
    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_search_countries", [])):
            del bot_settings["voltx_search_countries"][idx]
            save_db()
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
        edit_message(chat_id, msg_id, render_body_text("📝 Service Name:"), reply_markup=get_cancel_kb())
    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
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
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Country for <b>{srv}</b>:"), reply_markup=get_cancel_kb())
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
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>{srv} | {cnt}</b>\nRanges: {len(ranges)}"), reply_markup={"inline_keyboard": kb})
    elif data.startswith("vx_addr_"):
        parts = data.split("_"); srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 New Range for <b>{cnt}</b>:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})
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

    # ==========================================
    # Force Join
    # ==========================================
    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN</b>"), reply_markup=fj_settings_keyboard())
    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN</b>"), reply_markup=fj_settings_keyboard())
    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Channel @ or ID:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})
    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            del bot_settings["fj_channels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN</b>"), reply_markup=fj_settings_keyboard())

    # ==========================================
    # Admin Management
    # ==========================================
    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>"), reply_markup=admin_settings_keyboard())
    elif data == "add_adm":
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 User ID:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})
    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]
            save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>"), reply_markup=admin_settings_keyboard())

    # ==========================================
    # OTP Group
    # ==========================================
    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP</b>"), reply_markup=otp_groups_list_keyboard())
    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Group ID/Username:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})
    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Group:</b> {grp_id}"), reply_markup=specific_fw_group_keyboard(idx))
    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 <code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})
    elif data.startswith("del_fwbtn_"):
        parts = data.split("_"); idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                save_db()
                answer_callback(call["id"], "✅ Deleted!", show_alert=True)
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Group:</b> {bot_settings['fw_groups'][idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(idx))
    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]
            save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP</b>"), reply_markup=otp_groups_list_keyboard())
    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    # ==========================================
    # Panel Management
    # ==========================================
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
        icon = f"{PEM['world']} API" if p_type == 'API Panel' else f"{PEM['lock']} Auto Captcha"
        text = f"{icon} <b>{p_type}s</b>\n\n👀 Active: {len(p_list)}\n\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                conf = f" {login_state}" if login_state else f"{PEM['ok']} Configured"
            else:
                conf = f"{PEM['ok']} Configured" if p.get('api_url') else f"{PEM['no']} Not Configured"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))
    elif data in ["add_api_panel", "add_cpt_panel"]:
        user_states[chat_id] = "wait_for_panel_name"
        p_type = "api" if data == "add_api_panel" else "logc"
        temp_data[chat_id] = {"msg_id": msg_id, "add_type": p_type}
        edit_message(chat_id, msg_id, render_body_text("📝 New Provider Name:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='api' else 'cpt'}_panels", "style": "danger"}]]})
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
            del bot_settings["panels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "id": "internal"})
    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            p["status"] = "ON" if p["status"] == "OFF" else "OFF"
            save_db()
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\nStatus: {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\nLogin: {p.get('login_status', 'Unknown')}\nURL: <code>{p.get('login_url', 'None')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\nStatus: {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\nAPI: <code>{p.get('api_url', 'None')}</code>\nToken: <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))
    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\nStatus: {'🟢' if p['status'] == 'ON' else '🔴'}\nLogin: {p.get('login_status', 'Unknown')}\nURL: <code>{p.get('login_url', 'None')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\nStatus: {'🟢' if p['status'] == 'ON' else '🔴'}\nAPI: <code>{p.get('api_url', 'None')}</code>\nToken: <code>{p.get('token', 'None')}</code>"
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
        edit_message(chat_id, msg_id, render_body_text("📝 Records count (0=Unlimited):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})
    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection..."))
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
                        send_message(chat_id, render_body_text(f"❌ Login Failed!\n{p.get('login_status', 'Unknown')}"))
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
                    except Exception as _ce: pass
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
                        except: pass
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n<b>Sample (Max 3):</b>\n\n"
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']; msg = sample['message']; otp = sample['otp']
                    detected_app = detect_service(msg)
                    app_name = detected_app if detected_app else p.get("name", "Unknown")
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg)
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 <code>{num}</code>\n📝 <code>{html.escape(msg[:120])}</code>\n🔐 <code>{otp}</code>\n"
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
                            send_message(chat_id, render_body_text("⚠️ Connected but couldn't parse OTP!"))
                        else:
                            send_message(chat_id, render_body_text("⚠️ Connected, no HTML Table!"))
                    except Exception as e:
                        send_message(chat_id, render_body_text(f"❌ HTML error: {html.escape(str(e))}"))
                else:
                    safe_html = html.escape(str(raw_text)[:300])
                    send_message(chat_id, render_body_text(f"⚠️ Connected, no OTP.\n\nRaw:\n<code>{safe_html}...</code>"))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ Failed!\n{html.escape(str(e))}"))

    # ==========================================
    # STRM Control
    # ==========================================
    elif data == "STRM_control":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>STRM CONTROL PANEL</b>"), reply_markup=STRM_control_keyboard())
    elif data == "STRM_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>STRM CONTROL PANEL</b>"), reply_markup=STRM_control_keyboard())
    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>"), reply_markup=w_methods_keyboard())
    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send in format:\n<code>{method_name} | {emoji_id}</code>\n\nExample:\n<code>Nagad | 5190899075968441286</code>\n\nOr just name for default emoji."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})
    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]
            save_db()
            answer_callback(call["id"], "✅ Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>"), reply_markup=w_methods_keyboard())
    elif data.startswith("STRM_"):
        key = data.replace("STRM_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link", "w_group": "w_group"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_STRM"
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_STRM_edit", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"📝 New value for <code>{key_map[key]}</code>:"), reply_markup=cancel_kb)
            answer_callback(call["id"])

    # ==========================================
    # Service -> Country selection
    # ==========================================
    elif data.startswith("g_s_"):
        service = data.split("g_s_")[1]
        local_cnts = set([b["country"] for b in number_batches.values() if b["service"] == service and b["numbers"]])
        stex_cnts = set(bot_settings.get("stex_services", {}).get(service, {}).keys())
        voltx_cnts = set(bot_settings.get("voltx_services", {}).get(service, {}).keys())
        all_countries = local_cnts.union(stex_cnts).union(voltx_cnts)
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        raw_txt = c_msg.get("text", "📌 Select country for {service}:").replace("{service}", service)
        txt = render_body_text(raw_txt)
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in all_countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper(); name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_c_{service}_{c}", "style": "success"}])
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "close_msg", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_c_") or data.startswith("c_n_"):
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s", show_alert=True); return
        user_cooldowns[chat_id] = now
        expire_previous_number(chat_id)

        if data.startswith("c_n_s_"):
            is_voltx_req = data.endswith("_vtx")
            clean_data = data[:-4] if is_voltx_req else data
            parts_s = clean_data.split("_", 4)
            query = parts_s[3] if len(parts_s) > 3 else ""
            service_from_cb = parts_s[4] if len(parts_s) > 4 else None
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
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id
                                    api_found = True; total_assigned_stats += 1; break
                            except: continue
                else:
                    for _ in range(bot_settings.get("num_req", 1)):
                        for api_key in bot_settings.get("stex_keys", []):
                            try:
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers={"mauthapi": api_key}, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id
                                    api_found = True; total_assigned_stats += 1; break
                            except: continue
                if not api_found:
                    answer_callback(call["id"], "❌ Out of stock!", show_alert=True)
                    delete_message(chat_id, wait_msg_id); return
                for n in fetched_nums:
                    cn_x = str(n).replace("+", "").strip()
                    _, iso_x, _ = get_country_from_num(n)
                    country_name_x = ""
                    for _c, fdata in bot_settings.get("premium_flags", {}).items():
                        if fdata.get("iso") == iso_x: country_name_x = fdata.get("name", ""); break
                    if not country_name_x and iso_x and iso_x != "XX":
                        for _c, cinfo in COUNTRY_DB.items():
                            if cinfo["iso"] == iso_x: country_name_x = cinfo["name"]; break
                    _pv = None
                    if country_name_x and service_from_cb:
                        _pr = bot_settings.get("otp_pair_rates", {})
                        _pk = f"{country_name_x.upper()}|{str(service_from_cb).upper()}"
                        if _pk in _pr:
                            try: _pv = float(_pr[_pk])
                            except: pass
                    meta_entry = {"country": country_name_x, "service": service_from_cb or "", "iso": iso_x}
                    if _pv is not None: meta_entry["payout"] = _pv
                    assigned_number_meta[cn_x] = meta_entry
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
                    _pr = bot_settings.get("otp_pair_rates", {}); _pk = f"{str(bd_country).upper()}|{str(bd_service).upper()}"
                    if _pk in _pr:
                        try: _pv = float(_pr[_pk])
                        except: pass
                    assigned_number_meta[cn] = {"country": bd_country, "service": bd_service, "iso": bd_iso, "payout": _pv}
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True; used_numbers_list.append(num_str)
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
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
                emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: emoji_id = flag_data["id"]; break
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
            vtx_ext = "_vtx" if is_voltx_req else ""
            srv_ext = f"_{service_from_cb}" if service_from_cb else ""
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{srv_ext}{vtx_ext}", "style": "danger"},
                       {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns:
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            hdr_country = query
            try:
                if fetched_nums:
                    _, iso_x, _ = get_country_from_num(fetched_nums[0])
                    if iso_x and iso_x != "XX":
                        for cn2, ci2 in COUNTRY_DB.items():
                            if ci2["iso"] == iso_x: hdr_country = ci2["name"]; break
            except: pass
            header_txt = build_numbers_header(hdr_country, service_from_cb)
            edit_message(chat_id, wait_msg_id, header_txt, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            return

        parts = data.split("_")
        service = parts[2]; country = parts[3]
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
                vtx_flag = "_vtx" if is_voltx else ""
                handle_callback({"message": call["message"], "data": f"c_n_s_{target_range}_{service}{vtx_flag}", "id": call["id"]})
                return
            else:
                answer_callback(call["id"], "❌ Out of stock!", show_alert=True)
                if data.startswith("c_n_"): delete_message(chat_id, msg_id)
                return
        random.shuffle(available_indices)
        fetched_nums = []
        for b_id, idx in available_indices:
            if len(fetched_nums) >= bot_settings["num_req"]: break
            n_obj = number_batches[b_id]["numbers"][idx]
            fetched_nums.append(n_obj["num"])
            n_obj["shares"] += 1; n_obj["used_by"].append(chat_id)
            total_assigned_stats += 1
            cn = n_obj["num"].replace("+", "").strip()
            bd_country = number_batches[b_id]["country"]; bd_service = number_batches[b_id]["service"]
            bd_iso = number_batches[b_id].get("country_iso", "")
            _pv = float(bot_settings.get("otp_reward", 0.0))
            if "payout" in number_batches[b_id]:
                try: _pv = float(number_batches[b_id]["payout"])
                except: pass
            assigned_number_meta[cn] = {"country": bd_country, "service": bd_service, "iso": bd_iso, "payout": _pv}
            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                n_obj["to_remove"] = True; used_numbers_list.append(n_obj["num"])
        for b_id in number_batches:
            number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
        save_db()
        if not fetched_nums:
            answer_callback(call["id"], "❌ All taken!", show_alert=True)
            if data.startswith("c_n_"): delete_message(chat_id, msg_id)
            return
        app_full_name, _ = get_service_info_html(service)
        emoji_id = "5337302974806922068"
        for app_key, app_data in bot_settings.get("premium_apps", {}).items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data: emoji_id = app_data["id"]; break
        kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id, "callback_data": "ignore", "style": "success"}]]
        flags_db = bot_settings.get("premium_flags", {})
        for num in fetched_nums:
            _, iso = get_flag_and_code(num)
            display_num = f"+{num}" if not num.startswith("+") else num
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
        kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_{service}_{country}", "style": "danger"},
                   {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
        c_btns = bot_settings["custom_messages"].get("get_number", {}).get("buttons", [])
        for c_b in c_btns:
            b_copy = c_b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        header_txt = build_numbers_header(country, service)
        try:
            edit_message(chat_id, msg_id, header_txt, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums}
        except:
            msg_res = send_message(chat_id, header_txt, reply_markup={"inline_keyboard": kb})
            if msg_res and "result" in msg_res:
                user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}

    # ==========================================
    # WITHDRAWAL APPROVE/REJECT
    # ==========================================
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
            if action == "APPROVE" and len(num) >= 7:
                masked_num = f"{num[:4]}❖STRM❖{num[-3:]}"
            else:
                masked_num = num
            status_text = "APPROVED" if action == "APPROVE" else "REJECTED"
            emoji_icon_id = "5352694861990501856" if action == "APPROVE" else "5420130255174145507"
            frog_emoji = '<tg-emoji emoji-id="6307777408300753473">🐸</tg-emoji>'
            web_emoji = '<tg-emoji emoji-id="6206245785877616415">🕸️</tg-emoji>'
            method_icon = get_wmethod_emoji_html(req_data['method'])
            new_text = (
                f"🎙 <b>WITHDRAWAL {status_text}</b> {web_emoji}\n"
                f"{frog_emoji} <b>USER ID :</b><code>{u_id}</code>\n"
                f"👤 <b>User :</b> <a href='tg://user?id={u_id}'>{full_name}</a>\n"
                f"💸 <b>BALANCE:</b> <code>{amt}</code>\n"
                f"🍏 <b>NUMBER :</b> <code>{masked_num}</code>\n"
                f"🏦 <b>METHOD :</b> {method_icon} <b>{req_data['method']}</b>\n\n"
                f"🧾 <b>WITHDRAW ID :</b> <code>{req_id}</code>"
            )
            kb = {"inline_keyboard": [[{"text": status_text, "icon_custom_emoji_id": emoji_icon_id, "callback_data": "ignore", "style": "success" if action == "APPROVE" else "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(new_text), reply_markup=kb)
            if action == "APPROVE":
                update_balance(u_id, -amt)
                send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} ৳ withdrawal has been paid successfully!"))
            else:
                send_message(u_id, render_body_text(f"❌ Your {amt} ৳ withdrawal request was rejected."))
            if db:
                try: db.collection('withdrawals').document(req_id).update({"status": "approved" if action == "APPROVE" else "rejected"}, timeout=5.0)
                except: pass
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
            voltx_keys = bot_settings.get("voltx_keys", [])
            for api_key in voltx_keys:
                try:
                    res = requests.get(f"{VOLTX_BASE_URL}/success-otp", headers={"mauthapi": api_key}, timeout=10)
                    resp_data = res.json()
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            app_name = "Voltx Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                            unique_id = f"VOLTX_{num}_{otp_id}"
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                lang = detect_language(msg_text)
                                display_msg = render_body_text(format_otp_display(display_num, app_full_name, lang, masked=True))
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    for btn in fw.get("buttons", []):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        kb.append([b_obj])
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
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
                                    if reward > 0: update_balance(owner_id, reward)
                                    new_bal = user_cache.get(owner_id, {}).get("balance", 0.0)
                                    inbox_msg = render_body_text(format_otp_display(display_num, app_full_name, lang, masked=False))
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    if reward > 0:
                                        inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    if db:
                                        try: db.collection('users').document(str(owner_id)).update({"total_otps": firestore.Increment(1)}, timeout=5.0)
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)


# ==========================================
# Global (StexSMS) SMS Listener
# ==========================================
def global_sms_listener():
    global processed_otps, recent_traffic, stex_assigned_numbers
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            for api_key in stex_keys:
                try:
                    res = requests.get(f"{STEX_BASE_URL}/success-otp", headers={"mauthapi": api_key}, timeout=10)
                    resp_data = res.json()
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            app_name = "Stex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                            unique_id = f"STEX_{num}_{otp_id}"
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                lang = detect_language(msg_text)
                                display_msg = render_body_text(format_otp_display(display_num, app_full_name, lang, masked=True))
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    for btn in fw.get("buttons", []):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        kb.append([b_obj])
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
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
                                    if reward > 0: update_balance(owner_id, reward)
                                    new_bal = user_cache.get(owner_id, {}).get("balance", 0.0)
                                    inbox_msg = render_body_text(format_otp_display(display_num, app_full_name, lang, masked=False))
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    if reward > 0:
                                        inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    if db:
                                        try: db.collection('users').document(str(owner_id)).update({"total_otps": firestore.Increment(1)}, timeout=5.0)
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)


# ==========================================
# Helper: Emoji TXT Generator
# ==========================================
def generate_emoji_txt(mode="flags"):
    lines = []
    if mode == "flags":
        lines.append("# flag.txt - Format: CountryName (calling_code) (ISO) { \"emoji\": \"🇧🇩\", \"id\": \"5911365056594973179\" }")
        for code, data in bot_settings.get("premium_flags", {}).items():
            char = data.get("char", "")
            iso = data.get("iso", "")
            name = data.get("name", "")
            eid = data.get("id", "")
            if char and eid:
                lines.append(f'{name} ({code}) ({iso}) {{ "emoji": "{char}", "id": "{eid}" }}')
    else:
        lines.append("# service.txt - Format: ServiceName { \"emoji\": \"📱\", \"id\": \"5334807341109908955\" }")
        for name, data in bot_settings.get("premium_apps", {}).items():
            char = data.get("char", "")
            eid = data.get("id", "")
            if char and eid:
                lines.append(f'{name} {{ "emoji": "{char}", "id": "{eid}" }}')
    if len(lines) <= 1:
        return None
    return "\n".join(lines).encode('utf-8')


# ==========================================
# Polling Loop / Main
# ==========================================
def main():
    global BOT_USERNAME
    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")

    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    print("📡 Background APIs & SMS Listeners Started!")

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
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
