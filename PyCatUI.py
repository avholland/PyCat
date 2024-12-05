import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from marcIO import MARCIO
from pdb import set_trace

class DText(tk.Text):
    def __init__(self, master, *args, **kwargs):
        tk.Text.__init__(self, master, *args, **kwargs)
        self.updateSize()
        bindtags = list(self.bindtags())
        bindtags.insert(2, "custom")
        self.bindtags(tuple(bindtags))
        self.bind_class("custom", "<Key>", self.updateSize)

    def updateSize(self, event=None):
        lines = 0
        for line in self.get('1.0', 'end-1c').split('\n'):
            # width=max(width,self.font.measure(line))
            lines += 1
        self.config(height=lines)

class MARCViewer:
    def __init__(self, root):
        self.root = root
        self.root.title('MARC Viewer')
        self.root.geometry('640x480')

        self.settings = dict()
        self.settings['highlightFields'] = ['100', '110', '245']

        self.marcIO = MARCIO()
        self.loadedRecords = list()
        self.activeRecord = None
        self.activeRecordVar = tk.StringVar()
        self.highlightFields = list()

        self.recordFields = list()

        self.filetypes = (
            ('marc files', '*.mrc'),
            ('marc text files', '*.mrk'),
            ('all files', '*.*'),
        )

        self.HIGHLIGHT = 'yellow'
        self.BACKGROUND = 'white'

        self.createMenu()
        self.createWidgets()
        self.setBindings()

    def createMenu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        fileMenu = tk.Menu(menubar, tearoff=False)
        fileMenu.add_command(
            label='Open...',
            command=self.loadFile,
            underline=0,
        )
        fileMenu.add_command(
            label='Exit', 
            command=self.exit, 
            underline=1,
        )

        menubar.add_cascade(label='File', menu=fileMenu, underline=0)

    def createWidgets(self):
        self.window = tk.Frame(self.root)
        self.window.pack(pady=10)

        recordSummary = tk.Frame(self.window)
        recordSummary.pack(side=tk.TOP)
        self.prevBtn = tk.Button(recordSummary, text='<<<', command=self.showPrevRecord)
        self.prevBtn.pack(side=tk.LEFT)
        self.activeRecordNumber = tk.Label(recordSummary, textvariable=self.activeRecordVar)
        self.activeRecordNumber.pack(side=tk.LEFT)
        self.nextBtn = tk.Button(recordSummary, text='>>>', command=self.showNextRecord)
        self.nextBtn.pack(side=tk.LEFT)

        self.textarea = tk.Frame(self.window)
        self.textarea.pack(expand=True, fill='both')
        
        self.updateState()

    def updateButtonStates(self):
        if self.activeRecord:
            # if there are previous records, enable button
            if self.activeRecord > 1:
                self.prevBtn.config(state=tk.NORMAL)
            else:
                self.prevBtn.config(state=tk.DISABLED)
            # if there are next records, enable button
            if self.activeRecord < len(self.loadedRecords):
                self.nextBtn.config(state=tk.NORMAL)
            else:
                self.nextBtn.config(state=tk.DISABLED)
        else:
            # there are no active records, disable buttons
            self.prevBtn.config(state=tk.DISABLED)
            self.nextBtn.config(state=tk.DISABLED)

    def updateRecordState(self):
        if self.activeRecord:
            self.activeRecordVar.set(str(self.activeRecord) + ' of ' + str(len(self.loadedRecords)))
        else:
            self.activeRecordVar.set('load records')

    def updateState(self):
        self.updateButtonStates()
        self.updateRecordState()

    def clearTextArea(self):
        for row in self.recordFields:
            for field in row.winfo_children():
                field.delete('1.0', tk.END)

            

    def parseRecord(self, record):
        row = 0
        for field in record:
            self.buildRow(field, row)
            row += 1

    def buildRow(self, field, row):
        if row >= len(self.recordFields):
            rowFrame = tk.Frame(self.textarea, padx=5, pady=1)
            rowFrame.pack(expand=True, fill='x')
            self.recordFields.append(rowFrame)
            tag = tk.Text(rowFrame, width=3)
            tag.pack(side=tk.LEFT)
            indicator1 = tk.Text(rowFrame, width=1)
            indicator1.pack(side=tk.LEFT)
            indicator2 = tk.Text(rowFrame, width=1)
            indicator2.pack(side=tk.LEFT)
            contents = tk.Text(rowFrame, wrap='word')
            contents.pack(side=tk.TOP)

        if field.tag in self.settings.get('highlightFields'):
            COLOR = self.HIGHLIGHT
        else:
            COLOR = self.BACKGROUND

        lines = len(field.value())//70 + 1

        fields = self.recordFields[row].winfo_children()
        #rowFrame = tk.Frame(self.textarea, padx=5, pady=1)
        #rowFrame.pack(expand=True, fill='x')
        #tag = tk.Text(rowFrame, width=3, background=COLOR)
        fields[0].insert('1.0', field.tag)
        fields[0].config(height=lines, background=COLOR)
        #tag.pack(side=tk.LEFT)
        #indicator1 = tk.Text(rowFrame, width=1, background=COLOR)
        fields[1].insert('1.0', field.indicator1)
        fields[1].config(height=lines, background=COLOR)
        #indicator1.pack(side=tk.LEFT)
        #indicator2 = tk.Text(rowFrame, width=1, background=COLOR)
        fields[2].insert('1.0', field.indicator2)
        fields[2].config(height=lines, background=COLOR)
        #indicator2.pack(side=tk.LEFT)
        
        #contents = tk.Text(rowFrame, wrap='word', background=COLOR)
        fields[3].insert('1.0', field.value())
        fields[3].config(height=lines, background=COLOR)
        #contents.pack(side=tk.TOP)

    def showNextRecord(self, event=None):
        if self.activeRecord and self.activeRecord < len(self.loadedRecords):
            self.activeRecord += 1
            self.clearTextArea()
            self.parseRecord(self.loadedRecords[self.activeRecord-1])
        self.updateState()

    def showPrevRecord(self, event=None):
        if self.activeRecord and self.activeRecord > 1:
            self.activeRecord -= 1
            self.clearTextArea()
            self.parseRecord(self.loadedRecords[self.activeRecord-1])
        self.updateState()

    def clearRecords(self):
        self.loadedRecords = list()

    def exit(self, event=None):
        self.root.destroy

    def loadFile(self, event=None):
        filename = filedialog.askopenfilename(
            title='open marc records file',
            initialdir='/',
            filetypes=self.filetypes
        )
        self.loadedRecords = self.marcIO.loadRecordsFromFile(filename)
        self.activeRecord = 1
        self.parseRecord(self.loadedRecords[0])
        self.updateState()

    def setBindings(self):
        self.root.bind('<Left>', self.showPrevRecord)
        self.root.bind('<Right>', self.showNextRecord)
        self.root.bind('<Control-o>', self.loadFile)
        self.root.bind('<Control-q>', self.exit)

root = tk.Tk()
app = MARCViewer(root)
root.mainloop()