#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
summarize_ics.py

Summarizes .ics calendar files via CLI or a Qt GUI with drag-and-drop support.
Includes HTML-formatted descriptions with live links, attendees, and timezone support.

Setting up the environment:

    pip install icalendar python-dateutil pytz PyQt5
"""

import os
import argparse
import html
import re
from typing import Optional
from datetime import datetime
from icalendar import Calendar, Event, vCalAddress
from dateutil.rrule import rrulestr
import pytz

# Qt imports
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit,
    QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextBrowser


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize an ICS file")
    parser.add_argument("--ics", "-i", required=False, help="Path to the .ics file")
    parser.add_argument("--local-time", "-l", required=False, help="Convert to this time zone")
    return parser.parse_args()


def decode_bytes(value) -> str:
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


def format_datetime(dt: datetime, local_tz: Optional[pytz.timezone]) -> str:
    if local_tz:
        if dt.tzinfo is None:
            dt = local_tz.localize(dt)
        else:
            dt = dt.astimezone(local_tz)
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")


def extract_attendees(event: Event) -> list[str]:
    attendees = []
    attendees_field = event.get("ATTENDEE")
    if not attendees_field:
        return attendees
    if not isinstance(attendees_field, list):
        attendees_field = [attendees_field]
    for attendee in attendees_field:
        if not isinstance(attendee, vCalAddress):
            continue
        email = str(attendee)
        cn = decode_bytes(attendee.params.get("CN", ""))
        attendees.append(f"{cn} <{email}>" if cn else email)
    return attendees


def format_description(description_raw: str) -> str:
    """Convert DESCRIPTION field to readable HTML with links and line breaks."""
    # Handle literal \n sequences as real line breaks
    text = description_raw.replace("\\n", "\n").replace("\\r", "")

    # Convert angle-bracketed links like: Join now<https://link>
    def angle_replacer(match):
        label = match.group(1).strip()
        url = match.group(2).strip()
        return f'{html.escape(label)}: <a href="{html.escape(url)}">{html.escape(url)}</a>'

    text = re.sub(r"([^\n<]{1,100})<((https?|ftp)://[^>]+)>", angle_replacer, text)

    # Convert standalone links into clickable HTML links
    text = re.sub(r"(?<!href=\")(?<!\">)(https?://[^\s<>\"]+)",
                  lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>',
                  text)

    # Convert remaining plain text to safe HTML (preserving links)
    lines = text.splitlines()
    html_lines = []
    for line in lines:
        html_lines.append(line)

    return "<br>".join(html_lines)



def summarize_event(event: Event, local_tz: Optional[pytz.timezone], html_output: bool = False) -> str:
    uid = decode_bytes(event.get("UID"))
    summary = decode_bytes(event.get("SUMMARY", "No Summary"))
    dtstart = event.get("DTSTART")
    dtend = event.get("DTEND")
    rrule = decode_bytes(event.get("RRULE", ""))
    recurrence_id = event.get("RECURRENCE-ID")
    status = decode_bytes(event.get("STATUS", ""))
    description_raw = decode_bytes(event.get("DESCRIPTION", ""))
    attendees = extract_attendees(event)

    event_type = "NEW"
    if recurrence_id:
        event_type = "RESCHEDULE"
    elif status.upper() == "CANCELLED":
        event_type = "CANCELLATION"

    lines = []

    if html_output:
        lines.append(f"<h3>{html.escape(summary)}</h3>")
        lines.append(f"<b>Type:</b> {event_type}<br>")
        lines.append(f"<b>UID:</b> {html.escape(uid)}<br>")
        if recurrence_id:
            lines.append(f"<b>Change to occurrence:</b> {format_datetime(recurrence_id.dt, local_tz)}<br>")
        if dtstart:
            lines.append(f"<b>Starts:</b> {format_datetime(dtstart.dt, local_tz)}<br>")
        if dtend:
            lines.append(f"<b>Ends:</b> {format_datetime(dtend.dt, local_tz)}<br>")
        if rrule:
            lines.append(f"<b>Recurs:</b> {html.escape(rrule)}<br>")
            try:
                rule = rrulestr(rrule, dtstart=dtstart.dt)
                next_occ = rule.after(datetime.now(pytz.utc))
                lines.append(f"<b>Next Occurrence:</b> {format_datetime(next_occ, local_tz)}<br>")
            except Exception as e:
                lines.append(f"<b>Recurrence Error:</b> {html.escape(str(e))}<br>")
        if attendees:
            lines.append("<b>Attendees:</b><ul>")
            lines.extend([f"<li>{html.escape(a)}</li>" for a in attendees])
            lines.append("</ul>")
        if description_raw.strip():
            lines.append("<b>Description:</b><br>")
            lines.append(format_description(description_raw))
        lines.append("<hr>")
        return "\n".join(lines)

    else:
        lines.append(f"\n🔹 UID: {uid}")
        lines.append(f"   ➤ Type: {event_type}")
        lines.append(f"   ➤ Summary: {summary}")
        if recurrence_id:
            lines.append(f"   ➤ Change to occurrence on: {format_datetime(recurrence_id.dt, local_tz)}")
        if dtstart:
            lines.append(f"   ➤ Starts: {format_datetime(dtstart.dt, local_tz)}")
        if dtend:
            lines.append(f"   ➤ Ends:   {format_datetime(dtend.dt, local_tz)}")
        if rrule:
            lines.append(f"   ➤ Recurs: {rrule}")
            try:
                rule = rrulestr(rrule, dtstart=dtstart.dt)
                next_occ = rule.after(datetime.now(pytz.utc))
                lines.append(f"   ➤ Next Occurrence: {format_datetime(next_occ, local_tz)}")
            except Exception as e:
                lines.append(f"   ➤ Recurrence parse error: {e}")
        if attendees:
            lines.append("   ➤ Attendees:")
            lines.extend([f"     - {a}" for a in attendees])
        if description_raw:
            lines.append("   ➤ Description:")
            lines.append("     " + description_raw)
        return "\n".join(lines)


def summarize_ics_file(path: str, tz_name: Optional[str], html_output: bool = False) -> str:
    if not os.path.exists(path):
        return f"<b>❌ File not found:</b> {path}" if html_output else f"❌ File not found: {path}"

    local_tz = None
    if tz_name:
        try:
            local_tz = pytz.timezone(tz_name)
        except Exception:
            return f"<b>❌ Invalid time zone:</b> {tz_name}" if html_output else f"❌ Invalid time zone: {tz_name}"

    with open(path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    output = []
    output.append(f"<h2>📅 {html.escape(os.path.basename(path))}</h2>") if html_output else output.append(f"\n📅 Parsing ICS file: {path}")
    if local_tz:
        output.append(f"<p><b>Time zone:</b> {local_tz.zone}</p>") if html_output else output.append(f"🕑 Converting times to: {local_tz.zone}")

    for component in cal.walk():
        if component.name == "VEVENT":
            output.append(summarize_event(component, local_tz, html_output=html_output))

    return "\n".join(output)


# ───────────────────────────────────────────── GUI Mode ───────────────────────────────────────────── #

class ICSDropper(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle("ICS Summarizer")
        self.setMinimumSize(800, 600)

        self.layout = QVBoxLayout()
        self.last_path = None  # NEW: store the last file path

        self.label = QLabel("📂 Drop an .ics file here")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; padding: 12px;")
        self.layout.addWidget(self.label)

        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems(sorted(pytz.all_timezones))
        self.timezone_combo.setCurrentText("UTC")
        self.timezone_combo.currentTextChanged.connect(self.reapply_timezone)  # NEW: connect to update
        self.layout.addWidget(self.timezone_combo)

        self.output_box = QTextBrowser()
        self.output_box.setReadOnly(True)
        self.output_box.setAcceptRichText(True)
        self.output_box.setOpenExternalLinks(True)
        self.layout.addWidget(self.output_box)

        self.setLayout(self.layout)

    def reapply_timezone(self, new_tz: str):
        """Re-render the current ICS file with the newly selected time zone."""
        if self.last_path:
            result = summarize_ics_file(self.last_path, tz_name=new_tz, html_output=True)
            self.output_box.setHtml(result)


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().endswith(".ics") for url in urls):
                event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".ics"):
                self.last_path = path  # NEW: store path
                tz = self.timezone_combo.currentText()
                result = summarize_ics_file(path, tz_name=tz, html_output=True)
                self.output_box.setHtml(result)

# ───────────────────────────────────────────── Entry Point ───────────────────────────────────────────── #

if __name__ == "__main__":
    args = parse_arguments()

    if args.ics:
        print(summarize_ics_file(args.ics, args.local_time, html_output=False))
    else:
        import sys
        app = QApplication(sys.argv)
        dropper = ICSDropper()
        dropper.show()
        sys.exit(app.exec_())

