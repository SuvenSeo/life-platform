from datetime import datetime

from app.adapters.base import utc_now
from app.schemas import SourceReference

DISTRICTS = ["Sri Lanka", "Colombo", "Gampaha", "Kandy", "Galle", "Jaffna", "Matara", "Kurunegala"]

SOURCE_DEFINITIONS = [
    {
        "key": "dcs-ccpi",
        "label": "DCS Colombo Consumer Price Index",
        "source_type": "official",
        "domain_key": "indices",
        "url": "https://www.statistics.gov.lk/InflationAndPrices/StaticalInformation/MonthlyCCPI",
        "confidence": "high",
        "freshness_note": "Official monthly inflation release from the Department of Census and Statistics.",
        "labels": {"si": "DCS කොළඹ පාරිභෝගික මිල දර්ශකය", "ta": "DCS கொழும்பு நுகர்வோர் விலைச் சுட்டெண்"},
    },
    {
        "key": "dcs-hies",
        "label": "DCS Household Income and Expenditure Survey",
        "source_type": "official",
        "domain_key": "areas",
        "url": "https://www.statistics.gov.lk/IncomeAndExpenditure/StaticalInformation/HouseholdIncomeandExpenditureSurvey",
        "confidence": "high",
        "freshness_note": "Official household expenditure structure used for basket weighting.",
        "labels": {"si": "DCS ගෘහ ආදායම් හා වියදම් සමීක්ෂණය", "ta": "DCS குடும்ப வருமான மற்றும் செலவுச் சர்வே"},
    },
    {
        "key": "cbsl-price-report",
        "label": "CBSL Daily Price Report",
        "source_type": "official",
        "domain_key": "food",
        "url": "https://www.cbsl.gov.lk/statistics/economic-indicators/price-report",
        "confidence": "high",
        "freshness_note": "Official food and essential price reference for market context.",
        "labels": {"si": "CBSL දෛනික මිල වාර්තාව", "ta": "CBSL தினசரி விலை அறிக்கை"},
    },
    {
        "key": "harti-daily",
        "label": "HARTI Daily Food Price Bulletin",
        "source_type": "official",
        "domain_key": "food",
        "url": "https://www.harti.gov.lk/daily-price.php",
        "confidence": "high",
        "freshness_note": "Official agricultural market bulletin for daily food prices.",
        "labels": {"si": "HARTI දෛනික ආහාර මිල පුවත්පත", "ta": "HARTI தினசரி உணவு விலை அறிவிப்பு"},
    },
    {
        "key": "pucsl-electricity",
        "label": "PUCSL Electricity Tariffs",
        "source_type": "official",
        "domain_key": "utilities",
        "url": "https://www.pucsl.gov.lk/end-user-tariff-decisions/",
        "confidence": "high",
        "freshness_note": "Official electricity tariff decisions for household cost modelling.",
        "labels": {"si": "PUCSL විදුලි ගාස්තු", "ta": "PUCSL மின்சார கட்டணங்கள்"},
    },
    {
        "key": "nwsdb-water",
        "label": "NWSDB Water Tariffs",
        "source_type": "official",
        "domain_key": "utilities",
        "url": "https://www.waterboard.lk/",
        "confidence": "medium",
        "freshness_note": "Official water board tariff reference; normalized snapshots are staged.",
        "labels": {"si": "NWSDB ජල ගාස්තු", "ta": "NWSDB நீர் கட்டணங்கள்"},
    },
    {
        "key": "litro-lpg",
        "label": "Litro LPG Prices",
        "source_type": "official",
        "domain_key": "gas",
        "url": "https://www.litrogas.com/",
        "confidence": "medium",
        "freshness_note": "Public LPG price reference; availability can vary by publication format.",
        "labels": {"si": "ලිට්රෝ ගෑස් මිල", "ta": "லிட்ரோ எரிவாயு விலை"},
    },
    {
        "key": "laugfs-lpg",
        "label": "LAUGFS LPG Prices",
        "source_type": "official",
        "domain_key": "gas",
        "url": "https://laugfsgas.lk/",
        "confidence": "medium",
        "freshness_note": "Public LPG price reference; normalized extraction is staged.",
        "labels": {"si": "LAUGFS ගෑස් මිල", "ta": "LAUGFS எரிவாயு விலை"},
    },
    {
        "key": "ntc-bus-fares",
        "label": "NTC Bus Fares",
        "source_type": "official",
        "domain_key": "transport",
        "url": "https://www.ntc.gov.lk/Bus_info/bus_fares.php",
        "confidence": "high",
        "freshness_note": "Official bus fare tables for route and distance-based public transport costs.",
        "labels": {"si": "NTC බස් ගාස්තු", "ta": "NTC பேருந்து கட்டணங்கள்"},
    },
    {
        "key": "cpc-fuel",
        "label": "CPC Fuel Pricing",
        "source_type": "official",
        "domain_key": "fuel",
        "url": "https://ceypetco.gov.lk/marketing-sales/",
        "confidence": "high",
        "freshness_note": "Official fuel price reference checked by Octane and Ariva.",
        "labels": {"si": "CPC ඉන්ධන මිල", "ta": "CPC எரிபொருள் விலை"},
    },
    {
        "key": "retail-public-pages",
        "label": "Public Retail Offer Pages",
        "source_type": "retail",
        "domain_key": "retail",
        "url": "https://www.keellssuper.com/",
        "confidence": "medium",
        "freshness_note": "Public retailer quotes are labelled as retail offers, not official prices.",
        "labels": {"si": "පොදු රීටේල් දීමනා පිටු", "ta": "பொது சில்லறை சலுகைப் பக்கங்கள்"},
    },
    {
        "key": "foodlk-platform",
        "label": "FoodLK Platform API",
        "source_type": "platform",
        "domain_key": "food",
        "url": "https://food-platform-backend.fly.dev/api/v1",
        "confidence": "medium",
        "freshness_note": "Existing Ardeno Studio food platform remains the food source of truth.",
        "labels": {"si": "FoodLK වේදිකා API", "ta": "FoodLK தள API"},
    },
]

UTILITY_TARIFFS = [
    {"key": "electricity-low", "label": "Electricity low-use block", "amount_lkr": 7200, "unit": "monthly planning estimate", "source_key": "pucsl-electricity", "confidence": "medium", "note": "Planning estimate until block-level PUCSL extraction is automated."},
    {"key": "electricity-family", "label": "Electricity family block", "amount_lkr": 18500, "unit": "monthly planning estimate", "source_key": "pucsl-electricity", "confidence": "medium", "note": "Uses a family-consumption proxy for the Cost Desk."},
    {"key": "water-domestic", "label": "Domestic water", "amount_lkr": 2600, "unit": "monthly planning estimate", "source_key": "nwsdb-water", "confidence": "low", "note": "Static v2 assumption until tariff slabs are normalized."},
]

GAS_TARIFFS = [
    {"key": "litro-12-5kg", "label": "LPG 12.5kg cylinder", "amount_lkr": 3790, "unit": "per cylinder", "source_key": "litro-lpg", "confidence": "medium", "note": "Public LPG price reference; verify against latest vendor publication."},
    {"key": "laugfs-12-5kg", "label": "LPG 12.5kg alternate quote", "amount_lkr": 3800, "unit": "per cylinder", "source_key": "laugfs-lpg", "confidence": "medium", "note": "Retail/vendor quote placeholder until automated extraction is live."},
]

TRANSPORT_OPTIONS = [
    {"mode": "bus", "from_area": "Colombo", "to_area": "Kandy", "fare_lkr": 650, "confidence": "medium", "source_key": "ntc-bus-fares", "note": "Distance-table estimate for public bus travel."},
    {"mode": "bus", "from_area": "Colombo", "to_area": "Galle", "fare_lkr": 520, "confidence": "medium", "source_key": "ntc-bus-fares", "note": "Distance-table estimate for public bus travel."},
    {"mode": "bus", "from_area": "Gampaha", "to_area": "Colombo", "fare_lkr": 220, "confidence": "medium", "source_key": "ntc-bus-fares", "note": "Commuter corridor planning estimate."},
    {"mode": "fuel", "from_area": "Colombo", "to_area": "Kandy", "fare_lkr": 6200, "confidence": "low", "source_key": "cpc-fuel", "note": "Private vehicle fuel-only estimate; excludes parking, maintenance, and tolls."},
]

RETAIL_OFFERS = [
    {"item_name": "Rice Nadu", "retailer": "Public retail blend", "district": "Sri Lanka", "price_lkr": 320, "unit": "1kg", "source_key": "retail-public-pages", "confidence": "medium", "note": "Retail quote sample; compare against FoodLK market quotes."},
    {"item_name": "Dhal", "retailer": "Public retail blend", "district": "Sri Lanka", "price_lkr": 420, "unit": "1kg", "source_key": "retail-public-pages", "confidence": "medium", "note": "Retail quote sample; official market validation pending."},
    {"item_name": "Milk powder", "retailer": "Public retail blend", "district": "Sri Lanka", "price_lkr": 1190, "unit": "400g", "source_key": "retail-public-pages", "confidence": "medium", "note": "Retail offer signal, not an official controlled price."},
    {"item_name": "Coconut", "retailer": "Public retail blend", "district": "Sri Lanka", "price_lkr": 145, "unit": "each", "source_key": "retail-public-pages", "confidence": "low", "note": "Highly local item; district quote ingestion should replace this."},
    {"item_name": "Chicken", "retailer": "Public retail blend", "district": "Colombo", "price_lkr": 1280, "unit": "1kg", "source_key": "retail-public-pages", "confidence": "medium", "note": "Retail quote sample for protein basket."},
]

AREA_BASE = {
    "Sri Lanka": {"rent": 58, "food": 66, "transport": 61, "utilities": 58, "source": 70},
    "Colombo": {"rent": 41, "food": 62, "transport": 74, "utilities": 62, "source": 82},
    "Gampaha": {"rent": 57, "food": 65, "transport": 70, "utilities": 60, "source": 76},
    "Kandy": {"rent": 63, "food": 67, "transport": 66, "utilities": 58, "source": 70},
    "Galle": {"rent": 65, "food": 68, "transport": 61, "utilities": 57, "source": 68},
    "Jaffna": {"rent": 69, "food": 60, "transport": 56, "utilities": 54, "source": 62},
    "Matara": {"rent": 71, "food": 69, "transport": 57, "utilities": 56, "source": 63},
    "Kurunegala": {"rent": 72, "food": 70, "transport": 62, "utilities": 56, "source": 65},
}

I18N_LABELS = {
    "en": {
        "today": "Today",
        "cost_os": "Cost Desk",
        "atlas": "Atlas",
        "intelligence": "Signals",
        "sources": "Sources",
        "national_cost_pulse": "National cost pulse",
        "daily_living_total": "Daily living total",
        "source_health": "Source health",
        "public_only": "Public only",
        "no_accounts": "Optional account. Public view works without sign-in.",
        "degraded": "Degraded source",
        "search": "Search food, fuel, rent, transport",
    },
    "si": {
        "today": "අද",
        "cost_os": "වියදම් මධ්‍යස්ථානය",
        "atlas": "සිතියම",
        "intelligence": "සංඥා",
        "sources": "මූලාශ්‍ර",
        "national_cost_pulse": "ජාතික වියදම් තත්ත්වය",
        "daily_living_total": "දෛනික ජීවන වියදම",
        "source_health": "මූලාශ්‍ර සෞඛ්‍යය",
        "public_only": "පොදු පමණි",
        "no_accounts": "ගිණුමක් අවශ්‍ය නැත. පොදු දසුන සැමට විවෘතයි.",
        "degraded": "අඩු තත්ත්වයේ මූලාශ්‍රය",
        "search": "ආහාර, ඉන්ධන, කුලිය, ගමනාගමනය සොයන්න",
    },
    "ta": {
        "today": "இன்று",
        "cost_os": "செலவு மேசை",
        "atlas": "வரைபடம்",
        "intelligence": "சிக்னல்கள்",
        "sources": "மூலங்கள்",
        "national_cost_pulse": "தேசிய செலவு நிலை",
        "daily_living_total": "தினசரி வாழ்வு செலவு",
        "source_health": "மூல நலம்",
        "public_only": "பொது பயன்பாடு மட்டும்",
        "no_accounts": "கணக்கு விருப்பம். பொது காட்சி உள்நுழைவு இல்லாமலும் செயல்படும்.",
        "degraded": "குறைந்த நம்பகத் தரம்",
        "search": "உணவு, எரிபொருள், வாடகை, போக்குவரத்து தேடுங்கள்",
    },
}

DOMAIN_TRANSLATIONS = {
    "en": {
        "food": "Food and grocery",
        "fuel": "Fuel",
        "property": "Property and rent",
        "vehicle": "Vehicle market",
        "utilities": "Utilities",
        "gas": "LPG gas",
        "transport": "Public transport",
        "retail": "Retail offers",
        "indices": "Official indices",
        "areas": "District life scores",
    },
    "si": {
        "food": "ආහාර හා සිල්ලර",
        "fuel": "ඉන්ධන",
        "property": "දේපළ හා කුලී",
        "vehicle": "වාහන වෙළඳපොළ",
        "utilities": "උපයෝගිතා",
        "gas": "LPG ගෑස්",
        "transport": "පොදු ප්‍රවාහනය",
        "retail": "රීටේල් දීමනා",
        "indices": "නිල දර්ශක",
        "areas": "ප්‍රදේශ ජීවන ලකුණු",
    },
    "ta": {
        "food": "உணவு மற்றும் மளிகை",
        "fuel": "எரிபொருள்",
        "property": "சொத்து மற்றும் வாடகை",
        "vehicle": "வாகன சந்தை",
        "utilities": "பயன்பாட்டு சேவைகள்",
        "gas": "LPG எரிவாயு",
        "transport": "பொது போக்குவரத்து",
        "retail": "சில்லறை சலுகைகள்",
        "indices": "அதிகாரப்பூர்வ சுட்டெண்கள்",
        "areas": "பகுதி வாழ்வு மதிப்பெண்கள்",
    },
}


def source_refs(domain: str | None = None) -> list[SourceReference]:
    now = utc_now()
    rows = [row for row in SOURCE_DEFINITIONS if domain is None or row["domain_key"] == domain]
    return [
        SourceReference(
            key=row["key"],
            label=row["label"],
            source_type=row["source_type"],
            url=row["url"],
            confidence=row["confidence"],
            freshness_note=row["freshness_note"],
            last_checked_at=now,
            labels=row.get("labels", {}),
        )
        for row in rows
    ]


def grade_for(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "E"


def iso_now() -> datetime:
    return utc_now()
