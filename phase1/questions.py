from typing import List

sets = {
    "1": ["10", "7", "21", "22", "8", "13", "14", "9", "13", "6"],
    "2": ["13", "17", "11", "18", "3", "8", "2", "11", "24", "25"],
    "3": ["15", "1", "20", "8", "16", "20", "7", "25", "3", "24"],
    "4": ["23", "25", "17", "4", "7", "6", "23", "19", "14", "20"],
}

def sets_without_question(question_id: str) -> List[str]:
    return list(filter(
        lambda question_set: question_id not in question_set,
        sets
    ))

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

questions = [
    {
        "id": "1",
        "country": COUNTRIES.USA,
        "title": "Stars & Stripes Cipher",
        "points": "medium",
        "description": "Decrypt the classified communication intercepted from a government facility. The flag is hidden in the stars and stripes pattern.",
        "hasAttachment": True,
        "answer": "CTF{st4rs_4nd_str1p3s}",
    },
    {
        "id": "2",
        "country": COUNTRIES.CHINA,
        "title": "Dragon's Firewall",
        "points": "medium",
        "description": "Bypass the Great Firewall simulation to access the hidden server. Ancient wisdom meets modern security.",
        "hasAttachment": False,
        "answer": "CTF{gr34t_w4ll_byp4ss}",
    },
    {
        "id": "3",
        "country": COUNTRIES.JAPAN,
        "title": "Sakura Steganography",
        "points": "medium",
        "description": "Hidden messages in cherry blossom images reveal ancient secrets. Can you find the digital hanami treasure?",
        "hasAttachment": True,
        "answer": "CTF{s4kur4_s3cr3ts}",
    },
    {
        "id": "4",
        "country": COUNTRIES.GERMANY,
        "title": "Enigma Reborn",
        "points": "medium",
        "description": "A modern implementation of the famous Enigma machine. Crack the code using historical techniques and modern tools.",
        "hasAttachment": True,
        "answer": "CTF{3n1gm4_r3b0rn}",
    },
    {
        "id": "5",
        "country": COUNTRIES.INDIA,
        "title": "Bollywood Buffer Overflow",
        "points": "medium",
        "description": "A Bollywood-themed application has a hidden vulnerability. Dance through the code to find the overflow.",
        "hasAttachment": True,
        "answer": "CTF{b0llyw00d_buff3r}",
    },
    {
        "id": "6",
        "country": COUNTRIES.UNITED_KINGDOM,
        "title": "Tea Time Injection",
        "points": "medium",
        "description": "A proper British web application serves more than just tea. Find the SQL injection vulnerability before teatime.",
        "hasAttachment": False,
        "answer": "CTF{t34_t1m3_1nj3ct}",
    },
    {
        "id": "7",
        "country": COUNTRIES.FRANCE,
        "title": "Eiffel Tower Encoder",
        "points": "medium",
        "description": "Climb the digital Eiffel Tower by decoding messages hidden in its iron lattice structure. Très magnifique!",
        "hasAttachment": True,
        "answer": "CTF{31ff3l_3nc0d3r}",
    },
    {
        "id": "8",
        "country": COUNTRIES.ITALY,
        "title": "Pasta Protocol Hack",
        "points": "medium",
        "description": "Mamma mia! This Italian restaurant's ordering system has a spicy vulnerability. Can you hack the pasta protocol?",
        "hasAttachment": False,
        "answer": "CTF{p4st4_pr0t0c0l}",
    },
    {
        "id": "9",
        "country": COUNTRIES.BRAZIL,
        "title": "Carnival Chaos",
        "points": "medium",
        "description": "Navigate through the chaotic carnival network to find the hidden samba rhythm that unlocks the treasure.",
        "hasAttachment": True,
        "answer": "CTF{c4rn1v4l_ch40s}",
    },
    {
        "id": "10",
        "country": COUNTRIES.CANADA,
        "title": "Maple Leaf Memory",
        "points": "medium",
        "description": "Eh, buddy! This Canadian application has memory leaks like a broken hockey stick. Find the flag, sorry!",
        "hasAttachment": True,
        "answer": "CTF{m4pl3_l34f_m3m}",
    },
    {
        "id": "11",
        "country": COUNTRIES.RUSSIA,
        "title": "Kremlin Keylogger",
        "points": "medium",
        "description": "Analyze the sophisticated keylogger used in the Kremlin. Vodka-level difficulty requires advanced forensic skills.",
        "hasAttachment": True,
        "answer": "CTF{kr3ml1n_k3yl0gg3r}",
    },
    {
        "id": "12",
        "country": COUNTRIES.SOUTH_KOREA,
        "title": "K-Pop Cryptography",
        "points": "medium",
        "description": "BTS meets cryptography! Decode the hidden messages in K-Pop lyrics to find the gangnam-style flag.",
        "hasAttachment": False,
        "answer": "CTF{k_p0p_cry3t0}",
    },
    {
        "id": "13",
        "country": COUNTRIES.SPAIN,
        "title": "Flamenco File System",
        "points": "medium",
        "description": "¡Olé! Dance through this corrupted file system like a flamenco dancer to recover the hidden flag.",
        "hasAttachment": True,
        "answer": "CTF{fl4m3nc0_f1l3s}",
    },
    {
        "id": "14",
        "country": COUNTRIES.AUSTRALIA,
        "title": "Outback Overflow",
        "points": "medium",
        "description": "G'day mate! This Aussie application has a buffer overflow bigger than Uluru. No worries, you can handle it!",
        "hasAttachment": True,
        "answer": "CTF{0utb4ck_0v3rfl0w}",
    },
    {
        "id": "15",
        "country": COUNTRIES.MEXICO,
        "title": "Tequila SQL Injection",
        "points": "medium",
        "description": "¡Vamos! This Mexican cantina's database is more vulnerable than a piñata. Inject some tequila-strength SQL!",
        "hasAttachment": False,
        "answer": "CTF{t3qu1l4_sql}",
    },
    {
        "id": "16",
        "country": COUNTRIES.INDONESIA,
        "title": "Bali Binary Beach",
        "points": "medium",
        "description": "Surf through the binary waves of this Indonesian application. Find the flag hidden in the digital archipelago.",
        "hasAttachment": True,
        "answer": "CTF{b4l1_b1n4ry}",
    },
    {
        "id": "17",
        "country": COUNTRIES.NETHERLANDS,
        "title": "Dutch Windmill Worm",
        "points": "medium",
        "description": "Investigate this malware that spreads like Dutch tulips in spring. The windmills hold the key to detection.",
        "hasAttachment": True,
        "answer": "CTF{w1ndm1ll_w0rm}",
    },
    {
        "id": "18",
        "country": COUNTRIES.SAUDI_ARABIA,
        "title": "Desert DDoS",
        "points": "medium",
        "description": "Mitigate this massive DDoS attack that's hotter than the Arabian desert. Water your servers well!",
        "hasAttachment": False,
        "answer": "CTF{d3s3rt_dd0s}",
    },
    {
        "id": "19",
        "country": COUNTRIES.TURKEY,
        "title": "Istanbul Intrusion",
        "points": "medium",
        "description": "Navigate between Europe and Asia through this Turkish web application. The Bosphorus bridge hides secrets.",
        "hasAttachment": True,
        "answer": "CTF{1st4nbul_1ntr}",
    },
    {
        "id": "20",
        "country": COUNTRIES.SWITZERLAND,
        "title": "Alpine Cryptography",
        "points": "medium",
        "description": "Precision-engineered like Swiss clockwork, this cryptographic challenge requires mountain-peak accuracy.",
        "hasAttachment": True,
        "answer": "CTF{4lp1n3_cry3t0}",
    },
    {
        "id": "21",
        "country": COUNTRIES.ARGENTINA,
        "title": "Tango Trojan",
        "points": "medium",
        "description": "This sophisticated trojan dances through systems like an Argentine tango. Follow its passionate moves.",
        "hasAttachment": True,
        "answer": "CTF{t4ng0_tr0j4n}",
    },
    {
        "id": "22",
        "country": COUNTRIES.SOUTH_AFRICA,
        "title": "Diamond Mine Data",
        "points": "medium",
        "description": "Dig deep into this corrupted mining database to uncover diamonds hidden in the digital rough.",
        "hasAttachment": True,
        "answer": "CTF{d14m0nd_m1n3}",
    },
    {
        "id": "23",
        "country": COUNTRIES.NIGERIA,
        "title": "Nollywood Network",
        "points": "medium",
        "description": "Navigate through this Nollywood streaming platform to find the blockbuster vulnerability hidden in the code.",
        "hasAttachment": False,
        "answer": "CTF{n0llyw00d_n3t}",
    },
    {
        "id": "24",
        "country": COUNTRIES.EGYPT,
        "title": "Pyramid Protocol",
        "points": "medium",
        "description": "Decode the ancient hieroglyphic encryption used to protect the digital pharaoh's treasure chamber.",
        "hasAttachment": True,
        "answer": "CTF{pyr4m1d_pr0t0c0l}",
    },
    {
        "id": "25",
        "country": COUNTRIES.ANGOLA,
        "title": "Luanda Logic Bomb",
        "points": "medium",
        "description": "Defuse this logic bomb before it explodes like Angolan oil reserves. Time is running out!",
        "hasAttachment": True,
        "answer": "CTF{lu4nd4_l0g1c}",
    },
]
