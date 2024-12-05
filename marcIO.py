from pymarc import MARCReader

class MARCIO:
    def __init__(self):
        self.records = None

    def loadRecordsFromFile(self, filename):
        records = list()
        with open(filename, 'rb') as fh:
            reader = MARCReader(fh)
            for record in reader:
                records.append(record)
        return records
