from datetime import date, datetime
from typing import Optional


class Sample:
    def __init__(self, data) -> None:
        self.sample_id = data['sample_id']
        self.participant = data['participant']
        self.start = self.convert_to_datetime(data['collection_start'])
        self.end = self.convert_to_datetime(data['collection_end'])
        self.latitude = data['latitude']
        self.longitude = data['longitude']
        self.melanogaster = int(data['melanogaster'])
        self.simulans = int(data['simulans'])
        self.suzukii = int(data['suzukii'])
        self.busckii = int(data['busckii'])
        self.testacea = int(data['testacea'])
        self.hydei = int(data['hydei'])
        self.mercatorum = int(data['mercatorum'])
        self.repleta = int(data['repleta'])
        self.funebris = int(data['funebris'])
        self.immigrans = int(data['immigrans'])
        self.phalerata = int(data['phalerata'])
        self.subobscura = int(data['subobscura'])
        self.virilis = int(data['virilis'])

    def sample_to_dict(self) -> dict:
        return {
            "sample_id": self.sample_id,
            "participant": self.participant,
            "collection_start": self.start,
            "collection_end": self.end,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "melanogaster": self.melanogaster,
            "simulans": self.simulans,
            "suzukii": self.suzukii,
            "busckii": self.busckii,
            "testacea": self.testacea,
            "hydei": self.hydei,
            "mercatorum": self.mercatorum,
            "repleta": self.repleta,
            "funebris": self.funebris,
            "immigrans": self.immigrans,
            "phalerata": self.phalerata,
            "subobscura": self.subobscura,
            "virilis": self.virilis}

    @staticmethod
    def convert_to_datetime(date_) -> Optional[date]:
        if date_ == '?':
            return None
        return datetime.strptime(date_, '%d-%m-%Y').date()



@app.before_request
def before_request() -> None:
    import pandas as pd
    data = pd.read_csv(FILE_PATH, delimiter=',', encoding='utf-8', dtype=str)
    data = data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    data = data[data["participant"] != "?"]
    data = data.fillna(0)
    g.samples = [Sample(row) for _, row in data.iterrows()]
    sample_dicts = [sample.sample_to_dict() for sample in g.samples]

    # Convert to DataFrame
    df_samples = pd.DataFrame(sample_dicts)
    g.data = df_samples
    g.species = ['melanogaster', 'simulans', 'suzukii', 'busckii', 'testacea',
               'hydei', 'mercatorum', 'repleta', 'funebris', 'immigrans',
               'phalerata', 'subobscura', 'virilis']
