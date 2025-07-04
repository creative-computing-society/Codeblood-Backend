import datetime

class ChallengeStatus:
    AVAILABLE = "available"
    NOT_AVAILABLE = "not available"
    CAPTURED = "captured"
    FAILED = "failed"
    LOCKED = "locked"

class ChallengeCategory:
    REVERSE_ENGINEERING = "Reverse Engineering"
    CRYPTOGRAPHY = "Cryptography"
    WEB = "Web"
    FORENSICS = "Forensics"
    MISC = "misc"

class ChallengeType:
    FLAG = "flag"

class COUNTRIES:
    USA = "United States"
    CHINA = "China"
    JAPAN = "Japan"
    GERMANY = "Germany"
    INDIA = "India"
    UNITED_KINGDOM = "United Kingdom"
    FRANCE = "France"
    ITALY = "Italy"
    BRAZIL = "Brazil"
    CANADA = "Canada"
    RUSSIA = "Russia"
    SOUTH_KOREA = "South Korea"
    SPAIN = "Spain"
    AUSTRALIA = "Australia"
    MEXICO = "Mexico"
    INDONESIA = "Indonesia"
    NETHERLANDS = "Netherlands"
    SAUDI_ARABIA = "Saudi Arabia"
    TURKEY = "Turkey"
    SWITZERLAND = "Switzerland"
    ARGENTINA = "Argentina"
    SOUTH_AFRICA = "South Africa"
    NIGERIA = "Nigeria"
    EGYPT = "Egypt"
    ANGOLA = "Angola"

# Challenge
# {
# id: string;
# country: string;
# title: string;
# category: ChallengeCategory;
# type: ChallengeType;
# points: number;
# status: ChallengeStatus;
# description: string;
# hasAttachment: boolean;
# correctFlag: string;
# attemptsLeft: number;
# author?: string;
# }

# Team
# {
# id: string;
# name: string;
# score: number;
# rank: number;
# }

# ActivityEvent
# {
#     id: string;
# timestamp: Date;
# team: string;
# action: string;
# country: string;
# }

mockChallenges = [
{
    "id": "1",
    "country": COUNTRIES.USA,
    "title": "Stars & Stripes Cipher",
    "category": ChallengeCategory.CRYPTOGRAPHY,
    "type": ChallengeType.FLAG,
    "points": 75,
    "status": ChallengeStatus.AVAILABLE,
    "description": "Decrypt the classified communication intercepted from a government facility. The flag is hidden in the stars and stripes pattern.",
    "hasAttachment": True,
    "correctFlag": "CTF{st4rs_4nd_str1p3s}",
    "attemptsLeft": 3,
    "author": "PatriotHacker",
},
{
    "id": "2",
    "country": COUNTRIES.CHINA,
    "title": "Dragon's Firewall",
    "category": ChallengeCategory.WEB,
    "type": ChallengeType.FLAG,
    "points": 85,
    "status": ChallengeStatus.CAPTURED,
    "description": "Bypass the Great Firewall simulation to access the hidden server. Ancient wisdom meets modern security.",
    "hasAttachment": False,
    "correctFlag": "CTF{gr34t_w4ll_byp4ss}",
    "attemptsLeft": 0,
    "author": "DragonMaster",
},
{
    "id": "3",
    "country": COUNTRIES.JAPAN,
    "title": "Sakura Steganography",
    "category": ChallengeCategory.FORENSICS,
    "type": ChallengeType.FLAG,
    "points": 60,
    "status": ChallengeStatus.AVAILABLE,
    "description": "Hidden messages in cherry blossom images reveal ancient secrets. Can you find the digital hanami treasure?",
    "hasAttachment": True,
    "correctFlag": "CTF{s4kur4_s3cr3ts}",
    "attemptsLeft": 2,
    "author": "SamuraiCoder",
},
{
    "id": "4",
    "country": COUNTRIES.GERMANY,
    "title": "Enigma Reborn",
    "category": ChallengeCategory.CRYPTOGRAPHY,
    "type": ChallengeType.FLAG,
    "points": 90,
    "status": ChallengeStatus.FAILED,
    "description": "A modern implementation of the famous Enigma machine. Crack the code using historical techniques and modern tools.",
    "hasAttachment": True,
    "correctFlag": "CTF{3n1gm4_r3b0rn}",
    "attemptsLeft": 0,
    "author": "CryptoKaiser",
},
{
    "id": "5",
    "country": COUNTRIES.INDIA,
    "title": "Bollywood Buffer Overflow",
    "category": ChallengeCategory.REVERSE_ENGINEERING,
    "type": ChallengeType.FLAG,
    "points": 70,
    "status": ChallengeStatus.AVAILABLE,
    "description": "A Bollywood-themed application has a hidden vulnerability. Dance through the code to find the overflow.",
    "hasAttachment": True,
    "correctFlag": "CTF{b0llyw00d_buff3r}",
    "attemptsLeft": 3,
    "author": "TechMaharaj",
},
{
    "id": "6",
    "country": COUNTRIES.UNITED_KINGDOM,
    "title": "Tea Time Injection",
    "category": ChallengeCategory.WEB,
    "type": ChallengeType.FLAG,
    "points": 55,
    "status": ChallengeStatus.LOCKED,
    "description": "A proper British web application serves more than just tea. Find the SQL injection vulnerability before teatime.",
    "hasAttachment": False,
    "correctFlag": "CTF{t34_t1m3_1nj3ct}",
    "attemptsLeft": 3,
    "author": "DigitalLord",
},
{
    "id": "7",
    "country": COUNTRIES.FRANCE,
    "title": "Eiffel Tower Encoder",
    "category": ChallengeCategory.CRYPTOGRAPHY,
    "type": ChallengeType.FLAG,
    "points": 65,
    "status": ChallengeStatus.AVAILABLE,
    "description": "Climb the digital Eiffel Tower by decoding messages hidden in its iron lattice structure. Très magnifique!",
    "hasAttachment": True,
    "correctFlag": "CTF{31ff3l_3nc0d3r}",
    "attemptsLeft": 2,
    "author": "MonsieurHacker",
},
{
    "id": "8",
    "country": COUNTRIES.ITALY,
    "title": "Pasta Protocol Hack",
    "category": ChallengeCategory.WEB,
    "type": ChallengeType.FLAG,
    "points": 50,
    "status": ChallengeStatus.NOT_AVAILABLE,
    "description": "Mamma mia! This Italian restaurant's ordering system has a spicy vulnerability. Can you hack the pasta protocol?",
    "hasAttachment": False,
    "correctFlag": "CTF{p4st4_pr0t0c0l}",
    "attemptsLeft": 0,
    "author": "PastaHacker",
},
{
    "id": "9",
    "country": COUNTRIES.BRAZIL,
    "title": "Carnival Chaos",
    "category": ChallengeCategory.MISC,
    "type": ChallengeType.FLAG,
    "points": 80,
    "status": ChallengeStatus.CAPTURED,
    "description": "Navigate through the chaotic carnival network to find the hidden samba rhythm that unlocks the treasure.",
    "hasAttachment": True,
    "correctFlag": "CTF{c4rn1v4l_ch40s}",
    "attemptsLeft": 0,
    "author": "SambaSecuritys",
},
{
    "id": "10",
    "country": COUNTRIES.CANADA,
    "title": "Maple Leaf Memory",
    "category": ChallengeCategory.REVERSE_ENGINEERING,
    "type": ChallengeType.FLAG,
    "points": 45,
    "status": ChallengeStatus.AVAILABLE,
    "description": "Eh, buddy! This Canadian application has memory leaks like a broken hockey stick. Find the flag, sorry!",
    "hasAttachment": True,
    "correctFlag": "CTF{m4pl3_l34f_m3m}",
    "attemptsLeft": 3,
    "author": "CanuckCoder",
},
{
    "id": "11",
    "country": COUNTRIES.RUSSIA,
    "title": "Kremlin Keylogger",
    "category": ChallengeCategory.FORENSICS,
    "type": ChallengeType.FLAG,
    "points": 95,
    "status": ChallengeStatus.LOCKED,
    "description": "Analyze the sophisticated keylogger used in the Kremlin. Vodka-level difficulty requires advanced forensic skills.",
    "hasAttachment": True,
    "correctFlag": "CTF{kr3ml1n_k3yl0gg3r}",
    "attemptsLeft": 3,
    "author": "BearHacker",
},
{
    "id": "12",
    "country": COUNTRIES.SOUTH_KOREA,
    "title": "K-Pop Cryptography",
    "category": ChallengeCategory.CRYPTOGRAPHY,
    "type": ChallengeType.FLAG,
    "points": 40,
    "status": ChallengeStatus.AVAILABLE,
    "description": "BTS meets cryptography! Decode the hidden messages in K-Pop lyrics to find the gangnam-style flag.",
    "hasAttachment": False,
    "correctFlag": "CTF{k_p0p_cry3t0}",
    "attemptsLeft": 3,
    "author": "SeoulHacker",
},
{
    "id": "13",
    "country": COUNTRIES.SPAIN,
    "title": "Flamenco File System",
    "category": ChallengeCategory.FORENSICS,
    "type": ChallengeType.FLAG,
    "points": 55,
    "status": ChallengeStatus.NOT_AVAILABLE,
    "description": "¡Olé! Dance through this corrupted file system like a flamenco dancer to recover the hidden flag.",
    "hasAttachment": True,
    "correctFlag": "CTF{fl4m3nc0_f1l3s}",
    "attemptsLeft": 0,
    "author": "ToreroTech",
},
{
    "id": "14",
    "country": COUNTRIES.AUSTRALIA,
    "title": "Outback Overflow",
    "category": ChallengeCategory.REVERSE_ENGINEERING,
    "type": ChallengeType.FLAG,
    "points": 70,
    "status": ChallengeStatus.AVAILABLE,
    "description": "G'day mate! This Aussie application has a buffer overflow bigger than Uluru. No worries, you can handle it!",
    "hasAttachment": True,
    "correctFlag": "CTF{0utb4ck_0v3rfl0w}",
    "attemptsLeft": 2,
    "author": "KangarooHacker",
},
{
    "id": "15",
    "country": COUNTRIES.MEXICO,
    "title": "Tequila SQL Injection",
    "category": ChallengeCategory.WEB,
    "type": ChallengeType.FLAG,
    "points": 35,
    "status": ChallengeStatus.CAPTURED,
    "description": "¡Vamos! This Mexican cantina's database is more vulnerable than a piñata. Inject some tequila-strength SQL!",
    "hasAttachment": False,
    "correctFlag": "CTF{t3qu1l4_sql}",
    "attemptsLeft": 0,
    "author": "MariachiHacker",
},
{
    "id": "16",
    "country": COUNTRIES.INDONESIA,
    "title": "Bali Binary Beach",
    "category": ChallengeCategory.REVERSE_ENGINEERING,
    "type": ChallengeType.FLAG,
    "points": 60,
    "status": ChallengeStatus.FAILED,
    "description": "Surf through the binary waves of this Indonesian application. Find the flag hidden in the digital archipelago.",
    "hasAttachment": True,
    "correctFlag": "CTF{b4l1_b1n4ry}",
    "attemptsLeft": 0,
    "author": "GarudaGeek",
},
{
    "id": "17",
    "country": COUNTRIES.NETHERLANDS,
    "title": "Dutch Windmill Worm",
    "category": ChallengeCategory.FORENSICS,
    "type": ChallengeType.FLAG,
    "points": 50,
    "status": ChallengeStatus.AVAILABLE,
    "description": "Investigate this malware that spreads like Dutch tulips in spring. The windmills hold the key to detection.",
    "hasAttachment": True,
    "correctFlag": "CTF{w1ndm1ll_w0rm}",
    "attemptsLeft": 3,
    "author": "TulipHacker",
},
{
    "id": "18",
    "country": COUNTRIES.SAUDI_ARABIA,
    "title": "Desert DDoS",
    "category": ChallengeCategory.WEB,
    "type": ChallengeType.FLAG,
    "points": 75,
    "status": ChallengeStatus.LOCKED,
    "description": "Mitigate this massive DDoS attack that's hotter than the Arabian desert. Water your servers well!",
    "hasAttachment": False,
    "correctFlag": "CTF{d3s3rt_dd0s}",
    "attemptsLeft": 3,
    "author": "BedouinHacker",
},
{
    "id": "19",
    "country": COUNTRIES.TURKEY,
    "title": "Istanbul Intrusion",
    "category": ChallengeCategory.WEB,
    "type": ChallengeType.FLAG,
    "points": 65,
    "status": ChallengeStatus.NOT_AVAILABLE,
    "description": "Navigate between Europe and Asia through this Turkish web application. The Bosphorus bridge hides secrets.",
    "hasAttachment": True,
    "correctFlag": "CTF{1st4nbul_1ntr}",
    "attemptsLeft": 0,
    "author": "OttomanHacker",
},
{
    "id": "20",
    "country": COUNTRIES.SWITZERLAND,
    "title": "Alpine Cryptography",
    "category": ChallengeCategory.CRYPTOGRAPHY,
    "type": ChallengeType.FLAG,
    "points": 85,
    "status": ChallengeStatus.AVAILABLE,
    "description": "Precision-engineered like Swiss clockwork, this cryptographic challenge requires mountain-peak accuracy.",
    "hasAttachment": True,
    "correctFlag": "CTF{4lp1n3_cry3t0}",
    "attemptsLeft": 1,
    "author": "SwissGenius",
},
{
    "id": "21",
    "country": COUNTRIES.ARGENTINA,
    "title": "Tango Trojan",
    "category": ChallengeCategory.FORENSICS,
    "type": ChallengeType.FLAG,
    "points": 55,
    "status": ChallengeStatus.CAPTURED,
    "description": "This sophisticated trojan dances through systems like an Argentine tango. Follow its passionate moves.",
    "hasAttachment": True,
    "correctFlag": "CTF{t4ng0_tr0j4n}",
    "attemptsLeft": 0,
    "author": "BuenosHacker",
},
{
    "id": "22",
    "country": COUNTRIES.SOUTH_AFRICA,
    "title": "Diamond Mine Data",
    "category": ChallengeCategory.FORENSICS,
    "type": ChallengeType.FLAG,
    "points": 70,
    "status": ChallengeStatus.AVAILABLE,
    "description": "Dig deep into this corrupted mining database to uncover diamonds hidden in the digital rough.",
    "hasAttachment": True,
    "correctFlag": "CTF{d14m0nd_m1n3}",
    "attemptsLeft": 3,
    "author": "DiamondDigger",
},
{
    "id": "23",
    "country": COUNTRIES.NIGERIA,
    "title": "Nollywood Network",
    "category": ChallengeCategory.WEB,
    "type": ChallengeType.FLAG,
    "points": 45,
    "status": ChallengeStatus.AVAILABLE,
    "description": "Navigate through this Nollywood streaming platform to find the blockbuster vulnerability hidden in the code.",
    "hasAttachment": False,
    "correctFlag": "CTF{n0llyw00d_n3t}",
    "attemptsLeft": 2,
    "author": "LagosLegend",
},
{
    "id": "24",
    "country": COUNTRIES.EGYPT,
    "title": "Pyramid Protocol",
    "category": ChallengeCategory.CRYPTOGRAPHY,
    "type": ChallengeType.FLAG,
    "points": 80,
    "status": ChallengeStatus.LOCKED,
    "description": "Decode the ancient hieroglyphic encryption used to protect the digital pharaoh's treasure chamber.",
    "hasAttachment": True,
    "correctFlag": "CTF{pyr4m1d_pr0t0c0l}",
    "attemptsLeft": 3,
    "author": "PharaohHacker",
},
{
    "id": "25",
    "country": COUNTRIES.ANGOLA,
    "title": "Luanda Logic Bomb",
    "category": ChallengeCategory.REVERSE_ENGINEERING,
    "type": ChallengeType.FLAG,
    "points": 65,
    "status": ChallengeStatus.NOT_AVAILABLE,
    "description": "Defuse this logic bomb before it explodes like Angolan oil reserves. Time is running out!",
    "hasAttachment": True,
    "correctFlag": "CTF{lu4nd4_l0g1c}",
    "attemptsLeft": 0,
    "author": "OilRigHacker",
},
]

mockTeams = [
    {"id": "1", "name": "CyberSamurai", "score": 1250, "rank": 1},
    {"id": "2", "name": "RedDragon", "score": 1180, "rank": 2},
    {"id": "3", "name": "PhoenixTeam", "score": 1050, "rank": 3},
    {"id": "4", "name": "DigitalKnights", "score": 920, "rank": 4},
    {"id": "5", "name": "EagleEye", "score": 850, "rank": 5},
    {"id": "6", "name": "NordicHackers", "score": 780, "rank": 6},
    {"id": "7", "name": "TechNinjas", "score": 720, "rank": 7},
    {"id": "8", "name": "CyberBears", "score": 650, "rank": 8},
    {"id": "9", "name": "MapleHackers", "score": 580, "rank": 9},
    {"id": "10", "name": "GarudaGuards", "score": 520, "rank": 10},
    {"id": "11", "name": "AlpinePrecision", "score": 460, "rank": 11},
    {"id": "12", "name": "DesertStorm", "score": 400, "rank": 12},
]

mockActivity = [
{
    "id": "1",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=27),
    "team": "Invictus",
    "action": "available",
    "country": COUNTRIES.BRAZIL,
},
{
    "id": "2",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=45),
    "team": "CyberSamurai",
    "action": "failed attempt",
    "country": COUNTRIES.JAPAN,
},
{
    "id": "3",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=60),
    "team": "Mh0c473",
    "action": "captured",
    "country": COUNTRIES.INDIA,
},
{
    "id": "4",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=90),
    "team": "RedDragon",
    "action": "captured",
    "country": COUNTRIES.CHINA,
},
{
    "id": "5",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=120),
    "team": "Punina",
    "action": "captured",
    "country": COUNTRIES.BRAZIL,
},
{
    "id": "6",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1150),
    "team": "ByteForBait",
    "action": "available",
    "country": COUNTRIES.GERMANY,
},
{
    "id": "7",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=11180),
    "team": "AyamKunyit",
    "action": "captured",
    "country": COUNTRIES.ANGOLA,
},
{
    "id": "8",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=111210),
    "team": "DigitalKnights",
    "action": "failed attempt",
    "country": COUNTRIES.UNITED_KINGDOM,
},
{
    "id": "9",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1112240),
    "team": "PhoenixTeam",
    "action": "captured",
    "country": COUNTRIES.SOUTH_AFRICA,
},
{
    "id": "10",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=11122300),
    "team": "NordicHackers",
    "action": "available",
    "country": COUNTRIES.FRANCE,
},

{
    "id": "11",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=360),
    "team": "TechNinjas",
    "action": "captured",
    "country": COUNTRIES.SOUTH_KOREA,
},
{
    "id": "12",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=420),
    "team": "CyberBears",
    "action": "failed attempt",
    "country": COUNTRIES.RUSSIA,
},
{
    "id": "13",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=480),
    "team": "EagleEye",
    "action": "captured",
    "country": COUNTRIES.USA,
},
{
    "id": "14",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=540),
    "team": "MapleHackers",
    "action": "available",
    "country": COUNTRIES.CANADA,
},
{
    "id": "15",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=600),
    "team": "PastaSquad",
    "action": "failed attempt",
    "country": COUNTRIES.ITALY,
},
{
    "id": "16",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=660),
    "team": "TequilaTeam",
    "action": "captured",
    "country": COUNTRIES.MEXICO,
},
{
    "id": "17",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=720),
    "team": "FlamencoForce",
    "action": "available",
    "country": COUNTRIES.SPAIN,
},
{
    "id": "18",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=780),
    "team": "KangarooKrew",
    "action": "captured",
    "country": COUNTRIES.AUSTRALIA,
},
{
    "id": "19",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=840),
    "team": "GarudaGuards",
    "action": "failed attempt",
    "country": COUNTRIES.INDONESIA,
},
{
    "id": "20",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=900),
    "team": "TulipTactics",
    "action": "captured",
    "country": COUNTRIES.NETHERLANDS,
},
{
    "id": "21",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=960),
    "team": "DesertStorm",
    "action": "available",
    "country": COUNTRIES.SAUDI_ARABIA,
},
{
    "id": "22",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1020),
    "team": "BosphorusBridge",
    "action": "failed attempt",
    "country": COUNTRIES.TURKEY,
},
{
    "id": "23",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1080),
    "team": "AlpinePrecision",
    "action": "captured",
    "country": COUNTRIES.SWITZERLAND,
},
{
    "id": "24",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1140),
    "team": "TangoMasters",
    "action": "available",
    "country": COUNTRIES.ARGENTINA,
},
{
    "id": "25",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1200),
    "team": "NollywoodNet",
    "action": "captured",
    "country": COUNTRIES.NIGERIA,
},
{
    "id": "26",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1260),
    "team": "PharaohProtocol",
    "action": "failed attempt",
    "country": COUNTRIES.EGYPT,
},
{
    "id": "27",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1320),
    "team": "CyberSamurai",
    "action": "captured",
    "country": COUNTRIES.JAPAN,
},
{
    "id": "28",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1380),
    "team": "RedDragon",
    "action": "available",
    "country": COUNTRIES.CHINA,
},
{
    "id": "29",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1440),
    "team": "DiamondDiggers",
    "action": "captured",
    "country": COUNTRIES.SOUTH_AFRICA,
},
{
    "id": "30",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1500),
    "team": "BollywoodBytes",
    "action": "failed attempt",
    "country": COUNTRIES.INDIA,
},
{
    "id": "31",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1560),
    "team": "EiffelEncrypters",
    "action": "captured",
    "country": COUNTRIES.FRANCE,
},
{
    "id": "32",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1620),
    "team": "EnigmaExperts",
    "action": "available",
    "country": COUNTRIES.GERMANY,
},
{
    "id": "33",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1680),
    "team": "TeaTimeHackers",
    "action": "failed attempt",
    "country": COUNTRIES.UNITED_KINGDOM,
},
{
    "id": "34",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1740),
    "team": "OilRigRaiders",
    "action": "captured",
    "country": COUNTRIES.ANGOLA,
},
{
    "id": "35",
    "timestamp": datetime.datetime.now() - datetime.timedelta(seconds=1800),
    "team": "StarSpangled",
    "action": "available",
    "country": COUNTRIES.USA,
},
]