from dataclasses import dataclass

STATCAN = "https://www150.statcan.gc.ca"
METADATA_URL = f"{STATCAN}/t1/wds/rest/getCubeMetadata"
PROVINCES = (
    "Newfoundland and Labrador", "Prince Edward Island", "Nova Scotia",
    "New Brunswick", "Quebec", "Ontario", "Manitoba", "Saskatchewan",
    "Alberta", "British Columbia",
)
TERRITORIES = ("Yukon", "Northwest Territories", "Nunavut")
JURISDICTIONS = PROVINCES + TERRITORIES
ALL_GEOS = ("Canada",) + JURISDICTIONS
NAPCS = "North American Product Classification System (NAPCS)"
NAICS = "North American Industry Classification System (NAICS)"


@dataclass(frozen=True)
class Source:
    pid: str
    table: str
    frequency: str
    title_en: str
    title_fr: str
    classification: str
    geos: tuple[str, ...]

    @property
    def url(self) -> str:
        return f"{STATCAN}/n1/tbl/csv/{self.pid}-eng.zip"

    @property
    def table_url(self) -> str:
        return f"{STATCAN}/t1/tbl1/en/tv.action?pid={self.pid}01"

    @property
    def data_member(self) -> str:
        return f"{self.pid}.csv"

    @property
    def metadata_member(self) -> str:
        return f"{self.pid}_MetaData.csv"


SOURCES = (
    Source("12100173", "12-10-0173-01", "annual", "Annual merchandise trade",
           "Commerce annuel de marchandises", "NAPCS/SCPAN 2022", ALL_GEOS),
    Source("12100175", "12-10-0175-01", "monthly", "Monthly merchandise trade",
           "Commerce mensuel de marchandises", "NAPCS/SCPAN 2022", ALL_GEOS),
    Source("12100129", "12-10-0129-01", "annual", "Domestic export concentration",
           "Concentration des exportations nationales", "HS/SH chapters and destinations", ALL_GEOS),
    Source("12100100", "12-10-0100-01", "annual", "Value added in exports",
           "Valeur ajoutée dans les exportations", "Supply and use industries / Industries des TRE", ALL_GEOS),
    Source("36100711", "36-10-0711-01", "annual", "GDP by industry",
           "PIB par industrie", "NAICS/SCIAN 2022", JURISDICTIONS),
    Source("14100022", "14-10-0022-01", "monthly", "Labour force by industry",
           "Population active par industrie", "NAICS/SCIAN 2022", ("Canada",) + PROVINCES),
)
