cf_float32 = 1

def local_clock():
    return 1234.5678

class XMLElement:
    def append_child(self, name):
        return XMLElement()
    def append_child_value(self, name, value):
        pass

class StreamInfo:
    def __init__(self, name, type, channel_count, nominal_srate, channel_format, source_id=""):
        self.name = name
        self.type = type
        self.channel_count = channel_count
        self.nominal_srate = nominal_srate
        self.channel_format = channel_format
        self.source_id = source_id

    def desc(self):
        return XMLElement()

def resolve_streams(timeout=1.0):
    return []

class StreamOutlet:
    def __init__(self, info):
        self.info = info
    def push_sample(self, sample):
        pass
