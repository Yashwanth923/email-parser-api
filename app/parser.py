import json
import re
from html import unescape
from bs4 import BeautifulSoup


def html_to_text(html_content: str) -> str:
    """
    Convert HTML email body into plain text.
    """

    if not html_content:
        return ""

    decoded_html = unescape(html_content)

    soup = BeautifulSoup(
        decoded_html,
        "html.parser"
    )

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return re.sub(r"\s+", " ", text)


def extract_records(text: str):
    """
    Extract MISA records from email body.

    Supported formats:

    68421676-1 2750 Mon 21:13
    55369482-4 660 Monday
    55277454/5-2 1000 Fri 14:25
    55277454/5-1 1500/1000 Mon 15:24
    """

    records = []

    pattern = re.compile(
        r'(?P<part_number>\d+(?:[/-]\d+)+)\s+'
        r'(?P<qty>\d+(?:/\d+)?)\s+'
        r'(?P<day>'
        r'Mon|Monday|'
        r'Tue|Tues|Tuesday|'
        r'Wed|Wednesday|'
        r'Thu|Thur|Thursday|'
        r'Fri|Friday|'
        r'Sat|Saturday|'
        r'Sun|Sunday'
        r')'
        r'(?:\s+(?P<time>\d{1,2}:\d{2}))?',
        re.IGNORECASE
    )

    for match in pattern.finditer(text):

        records.append({
            "part_number": match.group("part_number"),
            "Qty": match.group("qty"),
            "day": match.group("day"),
            "time": match.group("time")
        })

    return records


def parse_payload(payload):

    result = {
        "from_email": None,
        "to_email": None,
        "subject": None,
        "body": None,
        "mail_metadata": None
    }

    for item in payload:

        disposition = (
            item.get("headers", {})
            .get("Content-Disposition", "")
        )

        field_match = re.search(
            r'name="([^"]+)"',
            disposition
        )

        if not field_match:
            continue

        field_name = field_match.group(1)

        if field_name in result:
            result[field_name] = item.get("body")

    metadata = None

    if result["mail_metadata"]:

        try:
            metadata = json.loads(
                result["mail_metadata"]
            )
        except Exception:
            metadata = None

    body_text = html_to_text(
        result["body"] or ""
    )

    records = extract_records(
        body_text
    )

    return {
        "from_email": result["from_email"],
        "to_email": result["to_email"],
        "subject": result["subject"],
        "mail_metadata": metadata,
        "body_text": body_text,
        "records": records
    }