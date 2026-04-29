import re

# ── Regex patterns ────────────────────────────────────────────────────────────
PHONE_RE = re.compile(r'(\(?\+?\d[\d\s\-\(\)\.]{7,}\d)')
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
WEBSITE_RE = re.compile(
    r'('
    # Branch 1: explicit www. or http:// prefix → accept any TLD
    r'(?:https?://|www\.)[\w\-]+(?:\.[\w\-]+)+(?:/[\w\-\./?=%&]*)?'
    # Branch 2: bare domain with unambiguous long TLDs (.com / .net / .org etc.)
    r'|[\w\-]{3,}\.(?:com|net|org|biz|info|agency|site|online)(?:/[\w\-\./?=%&]*)?'
    # Branch 3: compound ccTLDs — word.co.in / word.co.uk / word.com.au (unambiguous)
    r'|[\w\-]{3,}\.co\.(?:in|uk|nz|au|za)(?:/[\w\-\./?=%&]*)?'
    r')',
    re.IGNORECASE,
)
COMPANY_RE = re.compile(
    r'\b(inc\.?|llc\.?|ltd\.?|corp\.?|co\.|group|solutions|services|technologies|'
    r'associates|partners|enterprises|institute|university|hospital|clinic|'
    r'medicine|medical|center|foundation|cardiovascular|pvt\.?|private)\b',
    re.IGNORECASE,
)
CREDENTIALS_RE = re.compile(
    r'\b(MD|PhD|Dr\.?|MBA|JD|DDS|RN|DO|MPH|MS|MA|FACS|FACC|FAHA|Prof\.?)\b',
    re.IGNORECASE,
)
PINCODE_RE = re.compile(
    r'\b\d{6}\b'                       # Indian 6-digit PIN
    r'|\b[A-Z]{2}\s*\d{5}(?:-\d{4})?\b'  # US ZIP with state prefix
    r'|\b\d{5}(?:-\d{4})?\b'           # US ZIP 5-digit
)

# Layer 1 — Explicit field labels (e.g. "Email:", "Ph:", "Website:")
LABEL_MAP = {
    'email':       re.compile(r'^(?:e[-\s]?mail|email)\s*:?\s*', re.IGNORECASE),
    'phone':       re.compile(r'^(?:phone|ph|tel|mob|mobile|cell|call|hotline|direct|contact|cont)\s*:?\s*', re.IGNORECASE),
    'fax':         re.compile(r'^(?:fax|fx)\s*:?\s*', re.IGNORECASE),
    'website':     re.compile(r'^(?:website|web|url|visit us)\s*:?\s*', re.IGNORECASE),
    'address':     re.compile(r'^(?:address|addr|add|location|office)\s*:?\s*', re.IGNORECASE),
    'company':     re.compile(r'^(?:company|co|org|organization|firm)\s*:?\s*', re.IGNORECASE),
    'designation': re.compile(r'^(?:designation|position|title|role)\s*:?\s*', re.IGNORECASE),
    'social':      re.compile(r'^(?:instagram|twitter|facebook|linkedin|fb|ig|tiktok|snapchat|youtube|x)\s*:?\s*@?\s*', re.IGNORECASE),
}

# Marketing slogans / taglines — filter from all fields
SLOGAN_PATTERNS = [
    re.compile(r'^(be|buy|make|use|try|go)\s+\w+$', re.IGNORECASE),
    re.compile(r'^(manufacturer|supplier|dealer|distributor|exporter|importer|trader|provider)\s+(of|in|for)\b', re.IGNORECASE),
    re.compile(r'^(best|always|quality|trust|excellence|pride|leader|pioneer|largest|widest|biggest)\b', re.IGNORECASE),
    re.compile(r'^(we\s+are|est\.|established|since\s+\d{4}|iso\s*\d+)', re.IGNORECASE),
]

# Layer 2 — Strip icon/symbol prefixes before parsing
ICON_PREFIX_RE = re.compile(
    r'^[\s]*[☎📞📱✆✉📧🌐🔗📍🏢©®™•·|\-]+[\s]*'
)

DESIGNATION_KEYWORDS = [
    'manager', 'director', 'ceo', 'cto', 'coo', 'cfo', 'president', 'vice president',
    'engineer', 'developer', 'designer', 'consultant', 'analyst', 'executive',
    'officer', 'agent', 'associate', 'coordinator', 'specialist', 'advisor',
    'head', 'lead', 'senior', 'junior', 'intern', 'founder', 'co-founder',
    'partner', 'architect', 'administrator', 'supervisor', 'representative',
    'sales', 'marketing', 'accountant', 'attorney', 'lawyer', 'doctor',
    'professor', 'instructor', 'real estate', 'editor', 'publisher', 'writer',
    'reporter', 'journalist', 'moderator', 'host', 'technician', 'operator',
    'sr.', 'jr.', 'proprietor', 'chairman', 'vice', 'deputy', 'general',
]

ADDRESS_PATTERNS = [
    re.compile(r'\d+\s+\w+\s+(st|street|ave|avenue|rd|road|blvd|boulevard|ln|lane|dr|drive|ct|court|pl|place|way|pkwy|hwy|highway|nagar|marg|chowk|sector|block)', re.IGNORECASE),
    re.compile(r'\b(suite|ste|apt|floor|fl|unit|#|flat|shop|office)\s*[\-\d]+', re.IGNORECASE),
    re.compile(r'\b[A-Z]{2}\s+\d{5}(-\d{4})?\b'),        # US ZIP
    re.compile(r'\b\d{6}\b'),                               # Indian PIN code
    re.compile(r'\b\d{5}(-\d{4})?\b'),                     # US ZIP (5-digit)
    re.compile(r'\b(po box|p\.o\.\s*box)\b', re.IGNORECASE),
    re.compile(r'\b(gujarat|maharashtra|rajasthan|punjab|karnataka|kerala|'
               r'delhi|tamilnadu|telangana|andhra|uttar pradesh|madhya pradesh|'
               r'west bengal|bihar|odisha|haryana|goa)\b', re.IGNORECASE),
]

NAME_STOPLIST = {
    'members', 'member', 'customer', 'service', 'provider', 'providers',
    'health', 'medical', 'care', 'insurance', 'contact', 'phone', 'fax',
    'tel', 'address', 'email', 'website', 'office', 'mobile', 'cell',
    'claims', 'billing', 'support', 'helpdesk', 'hello', 'info', 'dear',
    'greetings', 'team', 'staff', 'department', 'division', 'group',
    'authorized', 'dealer', 'distributor', 'reseller', 'branch',
}

LOW_CONFIDENCE_THRESHOLD = 0.6
MIN_LINE_CONFIDENCE = 0.15

# H. Rule-based confidence per detection method — blended with OCR confidence
_RULE_CONF = {
    'phone_intl':               0.95,   # international format (+91, +1 ...)
    'phone_local':              0.85,   # local digits only
    'email_exact':              0.95,   # clean regex match
    'email_fixed':              0.80,   # OCR artifact corrected (missing dot etc.)
    'website_www':              0.95,   # explicit www. prefix
    'website_domain':           0.85,   # bare domain pattern
    'name_credential':          0.95,   # MD / PhD / Dr suffix present
    'name_top_zone':            0.85,   # top 35 % of card
    'name_fallback':            0.70,   # position heuristic only
    'company_label':            0.98,   # explicit "Company:" label
    'company_at_logo':          0.85,   # @brand detection
    'company_keyword':          0.88,   # COMPANY_RE keyword (Pvt, Ltd ...)
    'company_prominence':       0.75,   # large-font heuristic
    'company_email_domain':     0.65,   # inferred from email domain
    'company_website_domain':   0.60,   # inferred from website domain
    'designation_keyword':      0.82,   # DESIGNATION_KEYWORDS match
    'address_pattern':          0.88,   # ADDRESS_PATTERNS match
    'address_label':            0.95,   # explicit "Address:" label
    'address_fallback':         0.65,   # catch-all remaining lines
}


# ── Text helpers ──────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\b[wW]{3}\.', 'www.', text)
    text = text.strip('.,;:')
    return text


def _strip_icon(text: str) -> str:
    return ICON_PREFIX_RE.sub('', text).strip()


def _fix_url(text: str) -> str:
    text = re.sub(r'https?\s*:\s*/\s*/', 'http://', text, flags=re.IGNORECASE)
    text = re.sub(r'(\w),(\w{2,6})\b', r'\1.\2', text)
    # Fix OCR space after "www. ": "www. domain.com" → "www.domain.com"
    text = re.sub(r'\bwww\.\s+', 'www.', text, flags=re.IGNORECASE)
    # OCR sometimes drops dots: "wwwdomaincom" → "www.domain.com"
    text = re.sub(
        r'^(www)([a-zA-Z0-9\-]+?)(com|net|org|in|co|io|biz|info|edu|gov)$',
        r'\1.\2.\3', text, flags=re.IGNORECASE
    )
    return text


def _fix_email(text: str) -> str:
    # Fix OCR space after dot in local part: "name. surname@" → "name.surname@"
    text = re.sub(r'(\w)\.\s+(\w)', r'\1.\2', text)
    # Fix OCR space replacing dot before @: "harmish trivedi@" → "harmish.trivedi@"
    # Only when both sides are ≥2 chars — avoids matching random "word label@" phrases
    text = re.sub(r'(\w{2,})\s+(\w{2,}@)', r'\1.\2', text)
    text = re.sub(r'\s*@\s*', '@', text)
    text = re.sub(
        r'(@[a-zA-Z0-9\-]+)(com|net|org|io|co|in|biz|info|edu|gov)$',
        r'\1.\2', text, flags=re.IGNORECASE
    )
    return text


def _scan_remainder(text: str, conf: float, emails: list, websites: list, phones: list) -> None:
    """Extract any additional fields hiding in leftover text on the same OCR line."""
    if not text.strip():
        return
    # Website
    url_t = _fix_url(text)
    ws_m = WEBSITE_RE.search(url_t)
    if ws_m and '@' not in url_t:
        w_method = 'website_www' if 'www.' in url_t.lower() else 'website_domain'
        websites.append({'text': ws_m.group().lower(), 'confidence': conf, 'method': w_method})
        text = text[:url_t.find(ws_m.group())] + text[url_t.find(ws_m.group()) + len(ws_m.group()):]
    # Email
    em_t = _fix_email(text)
    em_m = EMAIL_RE.search(em_t)
    if em_m:
        emails.append({'text': em_m.group().lower(), 'confidence': conf, 'method': 'email_exact'})
        text = text[:em_t.find(em_m.group())] + text[em_t.find(em_m.group()) + len(em_m.group()):]
    # Phone
    for ph in _extract_phones(text):
        method = 'phone_intl' if re.search(r'\+?\d{1,3}[\s\-]', text) else 'phone_local'
        phones.append({'text': ph, 'confidence': conf, 'method': method})


def _extract_phones(text: str) -> list[str]:
    matches = PHONE_RE.findall(text)
    cleaned = []
    for m in matches:
        phone = re.sub(r'[^\d\-\+\(\)\.\s].*$', '', m).strip()
        if len(re.sub(r'\D', '', phone)) >= 7:
            cleaned.append(phone)
    return cleaned


def _extract_name_from_credentials(text: str) -> str | None:
    if not CREDENTIALS_RE.search(text):
        return None
    # Validate that removing credentials leaves a real person name
    name_only = CREDENTIALS_RE.sub('', text)
    name_only = re.sub(r'[,\s]+', ' ', name_only).strip().strip(',').strip()
    if len(name_only) < 3 or not re.match(r'^[A-Za-z\s\.\-]+$', name_only):
        return None
    # Return the full name WITH credentials, comma-spacing normalised
    # "Joseph C. Wu,MD,PhD" → "Joseph C. Wu, MD, PhD"
    full = re.sub(r'\s*,\s*', ', ', text.strip())
    full = re.sub(r'\s+', ' ', full).strip().strip(',').strip()
    return full


def is_noise(text: str, confidence: float = 1.0) -> bool:
    if confidence < MIN_LINE_CONFIDENCE:
        return True
    if len(text) < 2:
        return True
    # Require at least 2 alphanumeric chars — filters "E'" but allows phone-only lines
    if len(re.sub(r'[^a-zA-Z0-9]', '', text)) < 2:
        return True
    if re.match(r'^[\W_]+$', text):
        return True
    if len(set(text.replace(' ', ''))) <= 1:
        return True
    if text.isupper() and len(text) <= 10 and not re.search(r'[AEIOU]', text):
        return True
    return False


# Words that must not appear inside a person name
_NAME_WORD_STOP = frozenset({
    # prepositions / articles — particles like "de"/"van" are allowed but these are not
    'in', 'of', 'the', 'and', 'for', 'from', 'to', 'with', 'by', 'at', 'a', 'an',
    # product / industry / place nouns that look Title-Cased on cards
    'filter', 'filters', 'housing', 'water', 'india', 'products', 'industries',
    'manufacturing', 'solution', 'systems', 'technology', 'traders', 'agencies',
    'enterprises', 'traders', 'supplier', 'supplies', 'distributor',
})


def _is_proper_name(text: str) -> bool:
    """True when text looks like a person name: no digits/symbols, Title Case, ≤4 words, no filler words."""
    if re.search(r'[\d@#$%^&*()_+=\[\]{}|<>!]', text):
        return False
    words = [w for w in text.split() if w]
    # Person names are 1–4 words; longer phrases are descriptions
    if not words or len(words) > 4:
        return False
    # Reject if any word is a known non-name filler (preposition, product noun)
    if any(w.lower() in _NAME_WORD_STOP for w in words):
        return False
    # Single ALL-CAPS word longer than 3 chars is a brand/logo name, not a person name
    # (e.g. "VOLUME", "ANDOVER" — person names appear as "Rahi", not "RAHI")
    if len(words) == 1 and words[0].isupper() and len(words[0]) > 3:
        return False
    # Multi-word all-caps phrases are slogans/taglines (e.g. "WHAT YOU CARRY MATTERS")
    # Person names in all-caps have at most 2 words (e.g. "RAHI PAREKH")
    if len(words) > 2 and all(w.isupper() for w in words if w.isalpha()):
        return False
    cap_count = sum(1 for w in words if w[0].isupper())
    # Allow at most one non-capitalised word (particles: "de", "van", "al")
    return cap_count >= max(1, len(words) - 1)


def is_slogan(text: str) -> bool:
    return any(p.search(text) for p in SLOGAN_PATTERNS)


def _line_height(line: dict) -> float:
    bbox = line['bbox']
    return max(bbox[2][1] - bbox[0][1], 1)


def _is_vertically_adjacent(line1: dict, line2: dict) -> bool:
    h1 = _line_height(line1)
    h2 = _line_height(line2)
    gap = line2['bbox'][0][1] - line1['bbox'][2][1]
    return gap < (h1 + h2) / 2


def _has_pincode(text: str) -> bool:
    return bool(PINCODE_RE.search(text))


_GENERIC_EMAIL_DOMAINS = frozenset({
    'gmail', 'yahoo', 'hotmail', 'outlook', 'icloud', 'rediffmail',
    'ymail', 'protonmail', 'live', 'msn', 'aol', 'mail',
})

_GENERIC_WEBSITE_DOMAINS = frozenset({
    'gmail', 'yahoo', 'google', 'facebook', 'instagram', 'twitter',
    'linkedin', 'whatsapp', 'youtube', 'amazon', 'flipkart',
})


def _dedupe_emails(entries: list) -> list:
    """Remove duplicate email entries, keeping the first occurrence (case-insensitive)."""
    seen: set[str] = set()
    result = []
    for e in entries:
        key = e['text'].lower()
        if key not in seen:
            seen.add(key)
            result.append(e)
    return result


def _dedupe_websites(entries: list) -> list:
    """Remove duplicate website entries.

    Deduplication key is the bare domain (strip www., http://, trailing slash).
    When two entries map to the same domain, keep the one with the www. prefix
    (more complete), or the first one if neither has it.
    """
    def _domain_key(url: str) -> str:
        url = url.lower()
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        return url.rstrip('/')

    seen: dict[str, int] = {}   # domain_key → index in result
    result = []
    for e in entries:
        key = _domain_key(e['text'])
        if key in seen:
            existing = result[seen[key]]
            # Prefer the entry that starts with www.
            if e['text'].startswith('www.') and not existing['text'].startswith('www.'):
                result[seen[key]] = e
        else:
            seen[key] = len(result)
            result.append(e)
    return result


def _company_from_email(email: str) -> str | None:
    """Infer company name from the email domain (skips generic providers)."""
    m = re.search(r'@([\w\-]+)\.', email)
    if not m:
        return None
    domain = m.group(1).lower()
    if domain in _GENERIC_EMAIL_DOMAINS:
        return None
    # CamelCase domains like "lumoslogic" → "Lumoslogic" (best we can do without spaces)
    return domain.title()


def _company_from_website(url: str) -> str | None:
    """Infer company name from the website URL (skips generic sites)."""
    # strip protocol and www.
    domain = re.sub(r'^https?://', '', url, flags=re.IGNORECASE)
    domain = re.sub(r'^www\.', '', domain, flags=re.IGNORECASE)
    # remove path and query string
    domain = domain.split('/')[0].split('?')[0]
    # remove TLD(s): .co.in, .com, .net, .org, .in, .biz, .info ...
    domain = re.sub(
        r'\.(com|net|org|in|co\.in|co\.uk|biz|info|edu|gov|io|agency|site|online).*$',
        '', domain, flags=re.IGNORECASE
    )
    if len(domain) < 2:
        return None
    if domain.lower() in _GENERIC_WEBSITE_DOMAINS:
        return None
    return domain.title()


def _field_confidence(entries: list) -> float | None:
    """Blend OCR confidence with rule-based confidence for a field."""
    if not entries:
        return None
    ocr_avg = sum(e['confidence'] for e in entries) / len(entries)
    rule_avg = sum(_RULE_CONF.get(e.get('method', ''), 0.80) for e in entries) / len(entries)
    return round((ocr_avg + rule_avg) / 2, 4)


def _same_row(bbox1: list, bbox2: list) -> bool:
    y1_top, y1_bot = bbox1[0][1], bbox1[2][1]
    y2_top, y2_bot = bbox2[0][1], bbox2[2][1]
    overlap = min(y1_bot, y2_bot) - max(y1_top, y2_top)
    height = min(y1_bot - y1_top, y2_bot - y2_top)
    return overlap > height * 0.5


def _card_top_zone(lines: list) -> float:
    if not lines:
        return float('inf')
    all_y = [l['bbox'][0][1] for l in lines] + [l['bbox'][2][1] for l in lines]
    card_top, card_bot = min(all_y), max(all_y)
    return card_top + (card_bot - card_top) * 0.35


def _merge_address(address_lines: list) -> str | None:
    if not address_lines:
        return None
    sorted_lines = sorted(address_lines, key=lambda x: x['bbox'][0][1])

    # G. Stop collecting once a PIN / ZIP code line is reached
    pincode_idx = None
    for idx, line in enumerate(sorted_lines):
        if _has_pincode(line['text']):
            pincode_idx = idx
            break
    if pincode_idx is not None:
        sorted_lines = sorted_lines[:pincode_idx + 1]

    groups: list[list] = []
    current_group = [sorted_lines[0]]
    for i in range(1, len(sorted_lines)):
        if _same_row(sorted_lines[i - 1]['bbox'], sorted_lines[i]['bbox']):
            current_group.append(sorted_lines[i])
        else:
            groups.append(current_group)
            current_group = [sorted_lines[i]]
    groups.append(current_group)

    row_texts = []
    for group in groups:
        group_sorted = sorted(group, key=lambda x: x['bbox'][0][0])
        row = ' '.join(l['text'].strip().strip(',') for l in group_sorted if l['text'].strip())
        if row:
            row_texts.append(row)

    merged = ', '.join(row_texts)
    merged = re.sub(r',\s*,', ',', merged)
    return merged


# ── Main extractor ────────────────────────────────────────────────────────────

def extract_fields(lines: list) -> dict:
    phones, emails, websites, designations, companies, address_lines = [], [], [], [], [], []
    name_candidate = None
    used: set[int] = set()
    top_zone_y = _card_top_zone(lines)

    for i, line in enumerate(lines):
        raw_text = clean_text(line['text'])
        conf = line['confidence']

        # ── Layer 1: Explicit label detection ─────────────────────────────────
        matched_label = None
        label_value = raw_text
        for field, pattern in LABEL_MAP.items():
            if pattern.match(raw_text):
                matched_label = field
                label_value = pattern.sub('', raw_text).strip()
                break

        if matched_label and label_value:
            if matched_label == 'social':
                # Instagram/Twitter/LinkedIn handles are not business contact fields
                used.add(i); continue
            if matched_label == 'email':
                fixed = _fix_email(label_value)
                em_m = EMAIL_RE.search(fixed)
                if em_m:
                    method = 'email_fixed' if fixed != label_value else 'email_exact'
                    emails.append({'text': em_m.group().lower(), 'confidence': conf, 'method': method})
                    # Scan the rest of this line — OCR sometimes merges multiple labels into one block
                    remainder = fixed[fixed.find(em_m.group()) + len(em_m.group()):]
                    _scan_remainder(remainder, conf, emails, websites, phones)
                    used.add(i); continue
            if matched_label in ('phone', 'fax'):
                method = 'phone_intl' if re.search(r'^\+?\d{1,3}[\s\-]', label_value) else 'phone_local'
                for ph in _extract_phones(label_value):
                    phones.append({'text': ph, 'confidence': conf, 'method': method})
                # Scan remainder for email/website merged on the same OCR line
                _scan_remainder(PHONE_RE.sub('', label_value), conf, emails, websites, phones)
                used.add(i); continue
            if matched_label == 'website':
                fixed = _fix_url(label_value)
                m = WEBSITE_RE.search(fixed)
                if m:
                    method = 'website_www' if 'www.' in fixed.lower() else 'website_domain'
                    websites.append({'text': m.group().lower(), 'confidence': conf, 'method': method})
                    used.add(i); continue
            if matched_label == 'address':
                address_lines.append({'text': label_value, 'bbox': line['bbox'], 'confidence': conf, 'method': 'address_label'})
                used.add(i); continue
            if matched_label == 'designation':
                designations.append({'text': label_value, 'confidence': conf, 'method': 'designation_keyword'})
                used.add(i); continue
            if matched_label == 'company':
                companies.append({'text': label_value, 'confidence': conf, 'method': 'company_label'})
                used.add(i); continue

        # ── Layer 2: Strip icons then re-parse ────────────────────────────────
        text = _strip_icon(raw_text)
        if not text:
            used.add(i); continue

        # @word → company (logo/brand handle), but skip if the previous OCR line was a social label
        if re.match(r'^@\w+$', text) and conf >= MIN_LINE_CONFIDENCE:
            prev_raw = clean_text(lines[i - 1]['text']) if i > 0 else ''
            is_social_handle = bool(
                LABEL_MAP['social'].search(prev_raw)          # previous line had "Instagram:" etc.
                or LABEL_MAP['social'].match(text.lstrip('@'))  # the handle word itself is a platform name
            )
            if not is_social_handle:
                companies.append({'text': text.lstrip('@'), 'confidence': conf, 'method': 'company_at_logo'})
            used.add(i); continue

        if is_noise(text, conf):
            used.add(i); continue

        if is_slogan(text):
            used.add(i); continue

        # ── Layer 3: Pattern matching ──────────────────────────────────────────

        # B. Email
        email_text = _fix_email(text)
        em_match = EMAIL_RE.search(email_text)
        if em_match:
            detected_email = em_match.group().lower()

            # Recover orphaned local-part prefix that OCR split into a separate box.
            # EasyOCR sometimes cuts "harmish.trivedi@..." into:
            #   box(i-1) = "harmish."  →  clean_text strips the dot → "harmish"
            #   box(i)   = "trivedi@lumoslogic.com"
            # We look one box back: if it's on the same row, purely word-like,
            # and not already claimed, prepend it with a dot.
            curr_bbox   = line['bbox']
            curr_left_x = curr_bbox[0][0]
            curr_height = max(curr_bbox[2][1] - curr_bbox[0][1], 1)
            # Spatial search for orphaned local-part prefix — do NOT rely on sequential
            # index order (OCR box ordering is unpredictable when columns interleave).
            # Find the unused box that:
            #   1. is on the same row
            #   2. ends closest to where the email box starts (horizontally adjacent)
            #   3. gap < 3× line height  (adjacent, not across the card)
            best_gap    = float('inf')
            best_idx    = None
            best_prefix = None
            for j, candidate_line in enumerate(lines):
                if j == i or j in used:
                    continue
                cb = candidate_line['bbox']
                right_x = cb[1][0]
                gap     = abs(curr_left_x - right_x)
                if (gap < curr_height * 3
                        and right_x <= curr_left_x + curr_height   # must be to the left
                        and _same_row(cb, curr_bbox)
                        and gap < best_gap):
                    pc = clean_text(_strip_icon(candidate_line['text']))
                    if (re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._+%-]*$', pc)
                            and not EMAIL_RE.search(pc)):
                        candidate_email = (pc.rstrip('.') + '.' + detected_email)
                        if EMAIL_RE.fullmatch(candidate_email):
                            best_gap    = gap
                            best_idx    = j
                            best_prefix = candidate_email
            if best_prefix:
                detected_email = best_prefix
                used.add(best_idx)

            method = 'email_fixed' if email_text != text else 'email_exact'
            emails.append({'text': detected_email, 'confidence': conf, 'method': method})
            remainder = email_text[email_text.find(em_match.group()) + len(em_match.group()):]
            _scan_remainder(remainder, conf, emails, websites, phones)
            used.add(i); continue

        # C. Website
        url_text = _fix_url(text)
        ws_match = WEBSITE_RE.search(url_text)
        if ws_match and '@' not in url_text:
            matched_url = ws_match.group().lower()
            # If OCR split "www." into a previous line and this line is just the bare domain,
            # check if the previous OCR line was exactly "www." and prepend it.
            if not matched_url.startswith(('www.', 'http://', 'https://')):
                prev_text = clean_text(lines[i - 1]['text']).lower().strip() if i > 0 else ''
                if re.fullmatch(r'www\.?', prev_text):
                    matched_url = 'www.' + matched_url
            method = 'website_www' if matched_url.startswith('www.') or 'http' in matched_url else 'website_domain'
            websites.append({'text': matched_url, 'confidence': conf, 'method': method})
            used.add(i); continue

        # A. Phone
        extracted_phones = _extract_phones(text)
        if extracted_phones:
            method = 'phone_intl' if re.search(r'^\+?\d{1,3}[\s\-]', text) else 'phone_local'
            for ph in extracted_phones:
                phones.append({'text': ph, 'confidence': conf, 'method': method})
            used.add(i); continue

        # G. Address patterns
        if any(p.search(text) for p in ADDRESS_PATTERNS):
            address_lines.append({'text': text, 'bbox': line['bbox'], 'confidence': conf, 'method': 'address_pattern'})
            used.add(i); continue

        # F. Designation — predefined keyword list
        if any(kw in text.lower() for kw in DESIGNATION_KEYWORDS):
            designations.append({'text': text, 'confidence': conf, 'method': 'designation_keyword'})
            used.add(i); continue

        # E. Company — keyword match; skip if text looks like a domain (co. inside URL)
        domain_like = bool(re.search(r'[\w\-]+\.[\w\-]+\.\w{2,}', text) and ' ' not in text)
        if COMPANY_RE.search(text) and not domain_like:
            companies.append({'text': re.sub(r'[;]', ',', text), 'confidence': conf, 'method': 'company_keyword'})
            used.add(i); continue

    NAME_RE = re.compile(r'^[A-Za-z\s\.\-]{3,40}$')

    # ── Prominent-line company detection (logo/brand text) ────────────────────
    if not companies:
        eligible_heights = [_line_height(l) for i, l in enumerate(lines) if i not in used]
        if eligible_heights:
            avg_h = sum(eligible_heights) / len(eligible_heights)
            prominent = [
                (i, l) for i, l in enumerate(lines)
                if i not in used
                and _line_height(l) > avg_h * 1.5
                and len(re.sub(r'[^\w]', '', clean_text(_strip_icon(l['text'])))) >= 3
                and not is_noise(clean_text(_strip_icon(l['text'])), l['confidence'])
                and not is_slogan(clean_text(_strip_icon(l['text'])))
                # person names are often in large font too — don't mistake them for company
                and not (NAME_RE.match(clean_text(_strip_icon(l['text'])))
                         and _is_proper_name(clean_text(_strip_icon(l['text']))))
            ]
            if prominent:
                prominent.sort(key=lambda x: (x[1]['bbox'][0][1], x[1]['bbox'][0][0]))
                cluster = [prominent[0]]
                for j in range(1, len(prominent)):
                    prev_line = cluster[-1][1]
                    curr_line = prominent[j][1]
                    if (_same_row(prev_line['bbox'], curr_line['bbox'])
                            or _is_vertically_adjacent(prev_line, curr_line)):
                        cluster.append(prominent[j])
                    else:
                        break
                cluster.sort(key=lambda x: x[1]['bbox'][0][0])
                comp_text = ' '.join(
                    clean_text(_strip_icon(l['text'])) for _, l in cluster
                )
                # Strip leading logo-artifact fragments: short tokens with non-alpha chars
                # e.g. "E' Aishwaryam" → "Aishwaryam"  |  "F2 BrandName" → "BrandName"
                comp_words = comp_text.split()
                while comp_words and (
                    len(comp_words[0]) <= 2
                    or re.search(r"['\"`~^]", comp_words[0])
                    or (len(comp_words[0]) <= 3 and not comp_words[0].isalpha())
                ):
                    comp_words.pop(0)
                comp_text = ' '.join(comp_words) if comp_words else comp_text
                comp_conf = sum(l['confidence'] for _, l in cluster) / len(cluster)
                if comp_text and len(comp_text) >= 2:
                    companies.append({'text': comp_text, 'confidence': round(comp_conf, 4), 'method': 'company_prominence'})
                    for idx, _ in cluster:
                        used.add(idx)

    # Fallback: infer company from email domain when OCR found nothing
    if not companies:
        for e in emails:
            inferred = _company_from_email(e['text'])
            if inferred:
                companies.append({
                    'text': inferred,
                    'confidence': e['confidence'],
                    'method': 'company_email_domain',
                })
                break

    # Fallback: infer company from website domain when still nothing
    if not companies:
        for w in websites:
            inferred = _company_from_website(w['text'])
            if inferred:
                companies.append({
                    'text': inferred,
                    'confidence': w['confidence'],
                    'method': 'company_website_domain',
                })
                break

    # E. Company heuristic: longest matching line wins
    if len(companies) > 1:
        companies.sort(key=lambda c: len(c['text']), reverse=True)

    # ── Layer 4: Position-aware name detection ─────────────────────────────────

    # D. Priority 1: credential lines (MD, PhD) anywhere on card
    for i, line in enumerate(lines):
        if i in used:
            continue
        text = clean_text(_strip_icon(line['text']))
        extracted = _extract_name_from_credentials(text)

        # If credentials are present but name_only is too short (e.g. "Wu" from "Wu, MD, PhD"),
        # OCR likely split the full name across two boxes — look for an adjacent proper-name
        # prefix line ("Joseph C.") and combine before retrying extraction.
        if extracted is None and CREDENTIALS_RE.search(text):
            for j, prefix_line in enumerate(lines):
                if j == i or j in used:
                    continue
                prefix_text = clean_text(_strip_icon(prefix_line['text']))
                if not (NAME_RE.match(prefix_text)
                        and _is_proper_name(prefix_text)
                        and prefix_text.lower() not in NAME_STOPLIST):
                    continue
                prefix_above = prefix_line['bbox'][2][1] <= line['bbox'][0][1] + _line_height(line) * 0.5
                spatially_close = (
                    _same_row(prefix_line['bbox'], line['bbox'])
                    or (prefix_above and _is_vertically_adjacent(prefix_line, line))
                )
                if not spatially_close:
                    continue
                combined = prefix_text + ' ' + text
                extracted = _extract_name_from_credentials(combined)
                if extracted:
                    used.add(j)
                    break

        if extracted and extracted.lower() not in NAME_STOPLIST:
            name_candidate = {'text': extracted, 'confidence': line['confidence'], 'bbox': line['bbox'], 'method': 'name_credential'}
            used.add(i)
            break

    # D. Priority 2: topmost line with no digits/symbols and Title Case (first-line rule)
    if not name_candidate:
        by_y = sorted(
            [(i, l) for i, l in enumerate(lines) if i not in used],
            key=lambda x: x[1]['bbox'][0][1]
        )
        for i, line in by_y:
            text = clean_text(_strip_icon(line['text']))
            if (not is_noise(text, line['confidence'])
                    and NAME_RE.match(text)
                    and _is_proper_name(text)
                    and text.lower() not in NAME_STOPLIST
                    and not COMPANY_RE.search(text)):
                name_candidate = {'text': text, 'confidence': line['confidence'], 'bbox': line['bbox'], 'method': 'name_top_zone'}
                used.add(i)
                break

    # D. Priority 3: fallback — still require proper capitalization;
    # relaxed only in that it searches anywhere on the card (not just top zone)
    if not name_candidate:
        for i, line in enumerate(lines):
            if i in used:
                continue
            text = clean_text(_strip_icon(line['text']))
            if (not is_noise(text, line['confidence'])
                    and NAME_RE.match(text)
                    and _is_proper_name(text)
                    and text.lower() not in NAME_STOPLIST
                    and not COMPANY_RE.search(text)):
                name_candidate = {'text': text, 'confidence': line['confidence'], 'bbox': line['bbox'], 'method': 'name_fallback'}
                used.add(i)
                break

    # Merge same-row name fragments (e.g. "Jeff" + "Covey" split by OCR)
    if name_candidate:
        same_row_parts = [{'text': name_candidate['text'], 'x': name_candidate['bbox'][0][0]}]
        for i, line in enumerate(lines):
            if i in used:
                continue
            text = clean_text(_strip_icon(line['text']))
            conf = line['confidence']
            if (not is_noise(text, conf)
                    and NAME_RE.match(text)
                    and _same_row(name_candidate['bbox'], line['bbox'])):
                same_row_parts.append({'text': text, 'x': line['bbox'][0][0], 'idx': i})
                used.add(i)
        if len(same_row_parts) > 1:
            same_row_parts.sort(key=lambda p: p['x'])
            name_candidate['text'] = ' '.join(p['text'] for p in same_row_parts)

    # G. Address fallback — only lines spatially adjacent to an already-detected address block.
    # Random leftover lines (e.g. taglines, product names) must NOT fall into address.
    if address_lines:
        addr_ys = [pt for l in address_lines for pt in (l['bbox'][0][1], l['bbox'][2][1])]
        addr_y_min, addr_y_max = min(addr_ys), max(addr_ys)
        # Allow ±1 block-height tolerance around the detected address block
        block_height = max(addr_y_max - addr_y_min, 30)

        for i, line in enumerate(lines):
            if i in used:
                continue
            text = clean_text(_strip_icon(line['text']))
            conf = line['confidence']
            if is_noise(text, conf) or is_slogan(text):
                continue
            y_top = line['bbox'][0][1]
            y_bot = line['bbox'][2][1]
            if y_top <= addr_y_max + block_height and y_bot >= addr_y_min - block_height:
                address_lines.append({'text': text, 'bbox': line['bbox'], 'confidence': conf, 'method': 'address_fallback'})

    # ── H. Build output with blended rule + OCR confidence ────────────────────
    field_confidence: dict[str, float] = {}
    low_confidence_fields: list[dict] = []

    def record(field: str, conf):
        if conf is not None:
            field_confidence[field] = conf
            if conf < LOW_CONFIDENCE_THRESHOLD:
                low_confidence_fields.append({'field': field, 'confidence': conf})

    if name_candidate:
        nc_rule = _RULE_CONF.get(name_candidate.get('method', ''), 0.80)
        nc_conf = round((name_candidate['confidence'] + nc_rule) / 2, 4)
        record('name', nc_conf)
    if designations:
        record('designation', _field_confidence(designations))
    if companies:
        record('company', _field_confidence(companies[:1]))  # primary (longest) company
    if phones:
        record('phone', _field_confidence(phones))
    if emails:
        record('email', _field_confidence(emails))
    if websites:
        record('website', _field_confidence(websites))
    if address_lines:
        record('address', _field_confidence(address_lines))

    emails   = _dedupe_emails(emails)
    websites = _dedupe_websites(websites)

    merged_address = _merge_address(address_lines)
    designation_text = ' | '.join(d['text'] for d in designations) if designations else None

    raw_data = {
        'name':        name_candidate['text'] if name_candidate else None,
        'designation': designation_text,
        'company':     companies[0]['text'] if companies else None,
        'phone':       [p['text'] for p in phones] or None,
        'email':       [e['text'] for e in emails] or None,
        'website':     [w['text'] for w in websites] or None,
        'address':     merged_address if merged_address else None,
    }

    # Only include fields that were actually detected.
    # null is reserved for fields flagged in low_confidence_fields
    # (detected but below confidence threshold).
    data = {k: v for k, v in raw_data.items() if v is not None}

    return {
        'data': data,
        'confidence': field_confidence,
        'low_confidence_fields': low_confidence_fields,
    }
