from note import ScratchPad, Note, parse_args
from datetime import datetime, timedelta
import sys
import re
import base64
from credentials import token
import requests
from pprint import pprint

def jira_header(email, token):
    cred_string = f"{email}:{token}"
    encodedBytes = base64.b64encode(cred_string.encode("utf-8"))
    encodedStr = str(encodedBytes, "utf-8")
    header = {"Authorization": f"Basic {encodedStr}"}
    return header


class Report:
    def __init__(self, from_date, ticket_list=[], to_date=None, date_fmt="%m-%d-%y"):
        self.tickets = ticket_list
        self.date_fmt = date_fmt
        self.from_datetime = datetime.strptime(from_date, self.date_fmt)
        if to_date:
            self.to_datetime = datetime.strptime(to_date, self.date_fmt)
        else:
            self.to_datetime = datetime.now()

        self.tickets = self.filter_tickets()

        for ticket in self.tickets:
            ticket.get_status()

    def filter_tickets(self):
        filtered_list = []
        for ticket in self.tickets:
            # if ticket datetime is after from_date and before to_date, add to list
            if self.from_datetime < ticket.datetime < self.to_datetime:
                filtered_list.append(ticket)
        return filtered_list

    def compile(self):
        report_dict = {}
        for ticket in self.tickets:
            if ticket.status not in report_dict.keys():
                report_dict[ticket.status] = [ticket]
            else:
                report_dict[ticket.status].append(ticket)
        return report_dict

    def to_html(self):
        report_dict = self.compile()
        # GENERATE HTML FILE FROM REPORT DATA

    def show(self):
        print(str(self))

    def __str__(self):
        out = f"\nReport for {self.from_datetime.strftime(self.date_fmt)} => {self.to_datetime.strftime(self.date_fmt)}:\n\n"
        for ticket in self.tickets:
            out +=  f"{ticket.id} == {ticket.status} == {ticket.description}\n"
        out += "\n"
        return out


class Ticket:
    def __new__(cls, note=None):
        if note:
            # Create ticket from note
            content = note.content
            regex = r"(.*)(CC-\d+)( - )?(.*)"
            match = re.search(regex, content)
            if match:
                instance = super(Ticket, cls).__new__(cls)
                instance.id = match.group(2)
                instance.description = (match.group(1) + match.group(4)).strip()

                return instance
            else:
                return None
        else:
            # Create empty ticket
            instance = super(Ticket, cls).__new__(cls)
            instance.id = ""
            instance.description = ""
            return instance

    def __init__(self, base_url="https://forrtrak.atlassian.net/browse/", *args, **kwargs):
        if "note" in kwargs.keys():
            self.parent_note = kwargs["note"]
            self.timestamp = self.parent_note.timestamp
            self.datetime = datetime.strptime(self.parent_note.timestamp, "%m-%d-%y %H:%M:%S")
        else:
            self.parent_note = None
            self.datetime = datetime.now()
            self.timestamp = self.datetime.strftime("%m-%d-%y %H:%M:%S")

        self.base_url = base_url
        self.url = self.base_url + self.id
        self.status = None
        self.data = None

    def get_status(self):
        self.data = get_jira_issue(self.id)
        self.status = self.data['fields']['status']['name']

    def show(self):
        print(str(self))

    def __str__(self):
        out = f"Ticket: {self.id}\n"
        for attr in [a for a in dir(self) if not a.startswith("_")]:
            value = getattr(self, attr)
            out += f"{attr:<12}: {value}\n"
        out += "\n"
        return out


def get_jira_issue(key, email="sstuver@forrester.com", token=token):
    headers = jira_header(email, token)
    r = requests.get(f'https://forrtrak.atlassian.net/rest/agile/1.0/issue/{key}', headers=headers)
    assert r.ok
    issue = r.json()
    print(f"Found issue: {issue['key']}")
    return issue

if __name__ == "__main__":
    args = parse_args()
    db_file = r"C:\sqlite\db\notes.db"
    scratchpad = ScratchPad(db_file, args)
    notes = scratchpad.fetch()
    tickets = []
    for note in notes:
        t = Ticket(note=note)
        if t:
            tickets.append(t)

    yesterday = datetime.today() - timedelta(hours=24)
    yesterday = yesterday.strftime("%m-%d-%y")
    report = Report(yesterday, ticket_list=tickets)
    report.show()

    pprint(report.compile())
    # scratchpad.run()
    # scratchpad.add_note()
