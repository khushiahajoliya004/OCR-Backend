import re

# Allow leading ( for formats like (650) 736-2246
PHONE_RE = re.compile(r'(\(?\+?\d[\d\s\-\(\)\.]{7,}\d)')
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
WEBSITE_RE = re.compile(
    r'((?:https?://)?(?:www\.)?[\w\-]+\.(?:com|net|org|io|co|in|biz|info|us|uk|edu|gov|mil|agency|site|online)(?:/[\w\-\./?=%&]*)?)',
    re.IGNORECASE,
)
COMPANY_RE = re.compile(
    r'\b(inc\.?|llc\.?|ltd\.?|corp\.?|co\.|group|solutions|services|technologies|associates|partners|enterprises|institute|university|hospital|clinic|medicine|medical|center|foundation|cardiovascular)\b',
    re.IGNORECASE,
)
CREDENTIALS_RE = re.compile(
    r'\b(MD|PhD|Dr\.?|MBA|JD|DDS|RN|DO|MPH|MS|MA|FACS|FACC|FAHA|Prof\.?)\b'
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
]

ADDRESS_PATTERNS = [
    re.compile(r'\d+\s+\w+\s+(st|street|ave|avenue|rd|road|blvd|boulevard|ln|lane|dr|drive|ct|court|pl|place|way|pkwy)', re.IGNORECASE),
    re.compile(r'\b(suite|ste|apt|floor|fl|unit|#)\s*\d+', re.IGNORECASE),
    re.compile(r'\b[A-Z]{2}\s+\d{5}(-\d{4})?\b'),
    re.compile(r'\b\d{5}(-\d{4})?\b'),
    re.compile(r'\b(po box|p\.o\.\s*box)\b', re.IGNORECASE),
]

# Common heading/label words that are never a person's name
NAME_STOPLIST = {
    'members', 'member', 'customer', 'service', 'provider', 'providers',
    'health', 'medical', 'care', 'insurance', 'contact', 'phone', 'fax',
    'tel', 'address', 'email', 'website', 'office', 'mobile', 'cell',
    'claims', 'billing', 'support', 'helpdesk', 'hello', 'info', 'dear',
    'greetings', 'team', 'staff', 'department', 'division', 'group',
}

LOW_CONFIDENCE_THRESHOLD = 0.6
MIN_LINE_CONFIDENCE = 0.15


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\b[wW]{3}\.', 'www.', text)
    text = text.strip('.,;:')
    return text


def _fix_url(text: str) -> str:
    text = re.sub(r'https?\s*:\s*/\s*/', 'http://', text, flags=re.IGNORECASE)
    # Fix OCR comma-as-dot in URLs: "mysite,com" → "mysite.com"
    text = re.sub(r'(\w),(\w{2,6})\b', r'\1.\2', text)
    return text


def _fix_email(text: str) -> str:
    # Fix spaces around @
    text = re.sub(r'\s*@\s*', '@', text)
    # Fix missing dot before TLD: "user@domaincom" → "user@domain.com"
    text = re.sub(
        r'(@[a-zA-Z0-9\-]+)(com|net|org|io|co|in|biz|info|edu|gov)$',
        r'\1.\2', text, flags=re.IGNORECASE
    )
    return text


def _extract_phones(text: str) -> list[str]:
    """Extract all phone numbers from a line and strip trailing garbage."""
    matches = PHONE_RE.findall(text)
    cleaned = []
    for m in matches:
        phone = re.sub(r'[^\d\-\+\(\)\.\s].*$', '', m).strip()
        if len(re.sub(r'\D', '', phone)) >= 7:
            cleaned.append(phone)
    return cleaned


def _extract_name_from_credentials(text: str) -> str | None:
    """
    If a line contains academic/medical credentials (MD, PhD, etc.)
    strip them out and return the name portion.
    e.g. "Joseph C. Wu, MD, PhD" → "Joseph C. Wu"
    """
    if not CREDENTIALS_RE.search(text):
        return None
    name = CREDENTIALS_RE.sub('', text)
    name = re.sub(r'[,\s]+', ' ', name).strip().strip(',').strip()
    if len(name) >= 3 and re.match(r'^[A-Za-z\s\.\-]+$', name):
        return name
    return None


def is_noise(text: str, confidence: float = 1.0) -> bool:
    if confidence < MIN_LINE_CONFIDENCE:
        return True
    if len(text) < 2:
        return True
    if re.match(r'^[\W_]+$', text):
        return True
    if len(set(text.replace(' ', ''))) <= 1:
        return True
    # All-caps short tokens with no vowels → likely logo misread
    if text.isupper() and len(text) <= 10 and not re.search(r'[AEIOU]', text):
        return True
    return False


def _avg(lines: list) -> float | None:
    if not lines:
        return None
    return round(sum(l['confidence'] for l in lines) / len(lines), 4)


def _same_row(bbox1: list, bbox2: list) -> bool:
    y1_top, y1_bot = bbox1[0][1], bbox1[2][1]
    y2_top, y2_bot = bbox2[0][1], bbox2[2][1]
    overlap = min(y1_bot, y2_bot) - max(y1_top, y2_top)
    height = min(y1_bot - y1_top, y2_bot - y2_top)
    return overlap > height * 0.5


def _merge_address(address_lines: list) -> str | None:
    if not address_lines:
        return None
    sorted_lines = sorted(address_lines, key=lambda x: x['bbox'][0][1])

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


def extract_fields(lines: list) -> dict:
    phones, emails, websites, designations, companies, address_lines = [], [], [], [], [], []
    name_candidate = None
    used: set[int] = set()

    for i, line in enumerate(lines):
        text = clean_text(line['text'])
        conf = line['confidence']

        # Logo text like "@ekads" → company name "aekads"
        if re.match(r'^@\w+$', text) and conf >= MIN_LINE_CONFIDENCE:
            companies.append({'text': text.lstrip('@'), 'confidence': conf})
            used.add(i)
            continue

        if is_noise(text, conf):
            used.add(i)
            continue

        # Email
        email_text = _fix_email(text)
        if EMAIL_RE.search(email_text):
            emails.append({'text': EMAIL_RE.search(email_text).group().lower(), 'confidence': conf})
            used.add(i)
            continue

        # Website — fix OCR artifacts before matching
        url_text = _fix_url(text)
        ws_match = WEBSITE_RE.search(url_text)
        if ws_match and '@' not in url_text:
            websites.append({'text': ws_match.group().lower(), 'confidence': conf})
            used.add(i)
            continue

        # Phone — extract all numbers from line
        extracted_phones = _extract_phones(text)
        if extracted_phones:
            for ph in extracted_phones:
                phones.append({'text': ph, 'confidence': conf})
            used.add(i)
            continue

        # Address patterns
        if any(p.search(text) for p in ADDRESS_PATTERNS):
            address_lines.append({'text': text, 'bbox': line['bbox'], 'confidence': conf})
            used.add(i)
            continue

        # Designation — collect ALL matching lines
        if any(kw in text.lower() for kw in DESIGNATION_KEYWORDS):
            designations.append({'text': text, 'confidence': conf})
            used.add(i)
            continue

        # Company
        if COMPANY_RE.search(text):
            company_text = re.sub(r'[;]', ',', text)
            companies.append({'text': company_text, 'confidence': conf})
            used.add(i)
            continue

    NAME_RE = re.compile(r'^[A-Za-z\s\.\-]{3,40}$')

    # Priority pass: detect name from lines with credentials (MD, PhD, etc.)
    for i, line in enumerate(lines):
        if i in used:
            continue
        text = clean_text(line['text'])
        extracted = _extract_name_from_credentials(text)
        if extracted and extracted.lower() not in NAME_STOPLIST:
            name_candidate = {'text': extracted, 'confidence': line['confidence'], 'bbox': line['bbox']}
            used.add(i)
            break

    # Fallback: first clean line that looks like a name (2+ words preferred)
    if not name_candidate:
        for i, line in enumerate(lines):
            if i in used:
                continue
            text = clean_text(line['text'])
            if (not is_noise(text, line['confidence'])
                    and NAME_RE.match(text)
                    and text.lower() not in NAME_STOPLIST):
                name_candidate = {'text': text, 'confidence': line['confidence'], 'bbox': line['bbox']}
                used.add(i)
                break

    # Merge same-row name fragments (e.g. "Jeff" and "Covey" split by OCR)
    if name_candidate:
        same_row_parts = [{'text': name_candidate['text'], 'x': name_candidate['bbox'][0][0]}]
        for i, line in enumerate(lines):
            if i in used:
                continue
            text = clean_text(line['text'])
            conf = line['confidence']
            if (not is_noise(text, conf)
                    and NAME_RE.match(text)
                    and _same_row(name_candidate['bbox'], line['bbox'])):
                same_row_parts.append({'text': text, 'x': line['bbox'][0][0], 'idx': i})
                used.add(i)
        if len(same_row_parts) > 1:
            same_row_parts.sort(key=lambda p: p['x'])
            name_candidate['text'] = ' '.join(p['text'] for p in same_row_parts)

    # Remaining unused non-noise lines → address
    for i, line in enumerate(lines):
        if i in used:
            continue
        text = clean_text(line['text'])
        conf = line['confidence']
        if not is_noise(text, conf):
            address_lines.append({'text': text, 'bbox': line['bbox'], 'confidence': conf})

    field_confidence: dict[str, float] = {}
    low_confidence_fields: list[dict] = []

    def record(field: str, conf):
        if conf is not None:
            field_confidence[field] = conf
            if conf < LOW_CONFIDENCE_THRESHOLD:
                low_confidence_fields.append({'field': field, 'confidence': conf})

    if name_candidate:
        record('name', name_candidate['confidence'])
    if designations:
        record('designation', _avg(designations))
    if companies:
        record('company', _avg(companies))
    if phones:
        record('phone', _avg(phones))
    if emails:
        record('email', _avg(emails))
    if websites:
        record('website', _avg(websites))
    if address_lines:
        record('address', _avg(address_lines))

    merged_address = _merge_address(address_lines)

    designation_text = ' | '.join(d['text'] for d in designations) if designations else None
    website_list = [w['text'] for w in websites] if websites else None

    raw_data = {
        'name': name_candidate['text'] if name_candidate else None,
        'designation': designation_text,
        'company': companies[0]['text'] if companies else None,
        'phone': [p['text'] for p in phones] or None,
        'email': [e['text'] for e in emails] or None,
        'website': website_list,
        'address': merged_address if merged_address else None,
    }

    # Drop fields that have no value — don't show null in response
    data = {k: v for k, v in raw_data.items() if v is not None}

    return {
        'data': data,
        'confidence': field_confidence,
        'low_confidence_fields': low_confidence_fields,
    }
