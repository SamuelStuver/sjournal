from note import ScratchPad, Note, parse_args
from datetime import datetime
import re


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

    def filter_tickets(self):
        filtered_list = []
        for ticket in self.tickets:
            # if ticket datetime is after from_date and before to_date, add to list
            if self.from_datetime < ticket.datetime < self.to_datetime:
                filtered_list.append(ticket)
        return filtered_list

    def show(self):
        print(str(self))

    def __str__(self):
        out = f"Report for {self.from_datetime} - {self.to_datetime}:\n"
        for ticket in self.tickets:
            out +=  f"{ticket.id}: {ticket.description}\n"
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

    def show(self):
        print(str(self))

    def __str__(self):
        out = f"Ticket: {self.id}\n"
        for attr in [a for a in dir(self) if not a.startswith("_")]:
            value = getattr(self, attr)
            out += f"{attr:<12}: {value}\n"
        out += "\n"
        return out


def get_ticket_status(id):
    pass


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

    report = Report("06-20-21", ticket_list=tickets)
    report.show()

    # scratchpad.run()
    # scratchpad.add_note()
