"""
Generate 100 messy, inconsistent CSV files simulating sales & marketing data
from different companies with varied schemas, formats, and data quality issues.
"""

import csv
import random
import os
import string
from datetime import datetime, timedelta

random.seed(42)

OUTPUT_DIR = "raw_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Company pool
# ---------------------------------------------------------------------------
COMPANIES = [
    "Acme Corp", "Globex Industries", "Initech Solutions", "Umbrella Ltd",
    "Soylent Corp", "Wonka Enterprises", "Stark Industries", "Wayne Corp",
    "Cyberdyne Systems", "Tyrell Corporation", "Oscorp Technologies",
    "Massive Dynamic", "Hooli Inc", "Pied Piper", "Bluth Company",
    "Dunder Mifflin", "Sterling Cooper", "Prestige Worldwide", "Vandelay Ind",
    "Stratton Oakmont", "Genco Pura", "Nakatomi Trading", "Rekall Inc",
    "Weyland Corp", "Dharma Initiative", "Oceanic Airlines", "Buy N Large",
    "Spacely Sprockets", "Cogswell Cogs", "Brawndo Corp", "Virtucon",
    "Krusty Burger LLC", "Planet Express", "MomCorp", "Omni Consumer Products",
    "Cybertruck Co", "NovaTech Solutions", "Pinnacle Analytics", "FreshCart",
    "DataWave Inc", "BrightPath Media", "CloudNine SaaS", "QuickShip Logistics",
    "HealthPlus Pharma", "GreenLeaf Energy", "TrueNorth Financial",
    "PixelForge Studios", "AgriGrow Corp", "BlueOcean Retail", "SummitView Hotels",
]

PRODUCTS = [
    "Widget A", "Widget B", "Widget Pro", "Gadget X", "Gadget Mini",
    "Service Plan Basic", "Service Plan Pro", "Service Plan Enterprise",
    "Software License", "Software Subscription", "Consulting Hours",
    "Training Package", "Support Tier 1", "Support Tier 2", "Hardware Unit",
    "Cloud Storage 1TB", "Cloud Storage 5TB", "Analytics Dashboard",
    "Marketing Suite", "CRM Module", "ERP Add-on", "Security Bundle",
    "Data Pipeline", "API Access", "Premium Onboarding",
]

REGIONS = [
    "North America", "NA", "N. America", "US", "USA", "United States",
    "EMEA", "Europe", "EU", "UK", "United Kingdom", "Britain",
    "APAC", "Asia Pacific", "Asia", "ASIAPAC",
    "LATAM", "Latin America", "South America", "SA",
    "MEA", "Middle East", "Africa", "ANZ", "Australia",
]

CHANNELS = [
    "Online", "online", "ONLINE", "Web", "web", "Website", "E-Commerce",
    "ecommerce", "e-comm",
    "Retail", "retail", "RETAIL", "In-Store", "in-store", "Store", "Brick & Mortar",
    "Direct Sales", "direct", "Direct", "DIRECT", "Field Sales", "field",
    "Partner", "partner", "PARTNER", "Reseller", "reseller", "Channel Partner",
    "Referral", "referral", "Affiliate", "affiliate",
    "Phone", "phone", "Telesales", "Call Center", "call center",
    "Email", "email", "Email Campaign", "email campaign",
    "Social Media", "social", "Social", "social media",
]

STATUSES = [
    "Closed Won", "closed won", "CLOSED WON", "Won", "WON", "Closed-Won", "CW",
    "Closed Lost", "closed lost", "CLOSED LOST", "Lost", "LOST", "Closed-Lost", "CL",
    "Pending", "pending", "PENDING", "Open", "open", "In Progress", "in progress",
    "Negotiation", "negotiation", "Proposal", "proposal",
    "Qualified", "qualified", "Lead", "lead",
]

CURRENCIES = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", ""]

SALES_REPS = [
    "John Smith", "J. Smith", "john smith", "JOHN SMITH",
    "Jane Doe", "J. Doe", "jane doe", "JANE DOE",
    "Alice Johnson", "A. Johnson", "alice johnson",
    "Bob Williams", "B. Williams", "bob williams",
    "Carol Davis", "C. Davis", "carol davis",
    "David Brown", "D. Brown", "david brown",
    "Eva Martinez", "E. Martinez", "eva martinez",
    "Frank Wilson", "F. Wilson", "frank wilson",
    "Grace Lee", "G. Lee", "grace lee",
    "Henry Taylor", "H. Taylor", "henry taylor",
    "Iris Anderson", "I. Anderson", "iris anderson",
    "Jake Thomas", "J. Thomas", "jake thomas",
    "Karen White", "K. White", "karen white",
    "Leo Harris", "L. Harris", "leo harris",
    "Mia Clark", "M. Clark", "mia clark",
]

# ---------------------------------------------------------------------------
# Schema variations – different companies use different column names
# ---------------------------------------------------------------------------
SCHEMA_VARIANTS = [
    # variant 0 – clean-ish
    {"date": "Date", "company": "Company", "product": "Product",
     "quantity": "Quantity", "unit_price": "Unit Price", "revenue": "Revenue",
     "region": "Region", "channel": "Channel", "status": "Status",
     "sales_rep": "Sales Rep", "leads": "Leads", "conversions": "Conversions",
     "ad_spend": "Ad Spend", "campaign": "Campaign"},
    # variant 1 – snake_case
    {"date": "sale_date", "company": "company_name", "product": "product_name",
     "quantity": "qty", "unit_price": "unit_price", "revenue": "total_revenue",
     "region": "sales_region", "channel": "sales_channel", "status": "deal_status",
     "sales_rep": "rep_name", "leads": "num_leads", "conversions": "num_conversions",
     "ad_spend": "ad_spend_usd", "campaign": "campaign_name"},
    # variant 2 – camelCase
    {"date": "saleDate", "company": "companyName", "product": "productName",
     "quantity": "quantity", "unit_price": "unitPrice", "revenue": "totalRevenue",
     "region": "salesRegion", "channel": "salesChannel", "status": "dealStatus",
     "sales_rep": "salesRep", "leads": "leadCount", "conversions": "conversionCount",
     "ad_spend": "adSpend", "campaign": "campaignName"},
    # variant 3 – abbreviated
    {"date": "dt", "company": "co", "product": "prod", "quantity": "qty",
     "unit_price": "price", "revenue": "rev", "region": "rgn",
     "channel": "ch", "status": "stat", "sales_rep": "rep",
     "leads": "lds", "conversions": "conv", "ad_spend": "spend",
     "campaign": "cmpgn"},
    # variant 4 – ALL CAPS
    {"date": "DATE", "company": "COMPANY", "product": "PRODUCT",
     "quantity": "QTY", "unit_price": "UNIT_PRICE", "revenue": "REVENUE",
     "region": "REGION", "channel": "CHANNEL", "status": "STATUS",
     "sales_rep": "SALES_REP", "leads": "LEADS", "conversions": "CONVERSIONS",
     "ad_spend": "AD_SPEND", "campaign": "CAMPAIGN"},
    # variant 5 – spaces and mixed
    {"date": "Transaction Date", "company": "Company Name", "product": "Product / Service",
     "quantity": "Units Sold", "unit_price": "Price Per Unit", "revenue": "Total Amount",
     "region": "Geographic Region", "channel": "Sales Channel", "status": "Deal Status",
     "sales_rep": "Account Executive", "leads": "Marketing Leads",
     "conversions": "Closed Deals", "ad_spend": "Marketing Spend", "campaign": "Campaign ID"},
    # variant 6 – German-ish labels
    {"date": "Datum", "company": "Firma", "product": "Produkt",
     "quantity": "Menge", "unit_price": "Stueckpreis", "revenue": "Umsatz",
     "region": "Region", "channel": "Kanal", "status": "Status",
     "sales_rep": "Vertreter", "leads": "Leads", "conversions": "Abschluesse",
     "ad_spend": "Werbeausgaben", "campaign": "Kampagne"},
    # variant 7 – with typos
    {"date": "Dte", "company": "Comapny", "product": "Prodcut",
     "quantity": "Quatity", "unit_price": "Untit Price", "revenue": "Revnue",
     "region": "Reigon", "channel": "Chanell", "status": "Stauts",
     "sales_rep": "Saels Rep", "leads": "Laeds", "conversions": "Converison",
     "ad_spend": "Ad Spned", "campaign": "Campagn"},
]

# ---------------------------------------------------------------------------
# Date format variations
# ---------------------------------------------------------------------------
DATE_FORMATS = [
    "%Y-%m-%d",           # 2024-01-15
    "%m/%d/%Y",           # 01/15/2024
    "%d/%m/%Y",           # 15/01/2024
    "%m-%d-%Y",           # 01-15-2024
    "%d-%b-%Y",           # 15-Jan-2024
    "%B %d, %Y",          # January 15, 2024
    "%Y/%m/%d",           # 2024/01/15
    "%d.%m.%Y",           # 15.01.2024
    "%m.%d.%Y",           # 01.15.2024
    "%Y%m%d",             # 20240115
]

# ---------------------------------------------------------------------------
# Revenue formatting helpers
# ---------------------------------------------------------------------------
def fmt_revenue(val, style):
    if val is None:
        return random.choice(["", "N/A", "NA", "-", "null", "NULL", "#N/A", "missing"])
    if style == 0:
        return f"{val:.2f}"
    elif style == 1:
        return f"${val:,.2f}"
    elif style == 2:
        return f"${val:.0f}"
    elif style == 3:
        return str(int(val))
    elif style == 4:
        return f"{val:,.2f} USD"
    elif style == 5:
        return f"USD {val:,.2f}"
    elif style == 6:
        return f"{val:.2f}".replace(".", ",")  # European style
    else:
        return f"{val:.2f}"

def fmt_quantity(val):
    if val is None:
        return random.choice(["", "N/A", "-", "null", "0", "#REF!"])
    style = random.randint(0, 3)
    if style == 0:
        return str(val)
    elif style == 1:
        return f"{val}.0"
    elif style == 2:
        return f"{val}.00"
    else:
        return str(val)

# ---------------------------------------------------------------------------
# Generate one file
# ---------------------------------------------------------------------------
def generate_file(file_index):
    company = random.choice(COMPANIES)
    schema = random.choice(SCHEMA_VARIANTS)
    date_fmt = random.choice(DATE_FORMATS)
    rev_style = random.randint(0, 6)
    num_rows = random.randint(15, 200)

    # Decide which columns to include (always include date/revenue, drop others randomly)
    all_keys = list(schema.keys())
    must_have = ["date", "revenue"]
    optional = [k for k in all_keys if k not in must_have]
    # Keep 60-100% of optional columns
    keep_count = random.randint(max(1, int(len(optional) * 0.6)), len(optional))
    kept_optional = random.sample(optional, keep_count)
    final_keys = must_have + kept_optional
    random.shuffle(final_keys)  # randomize column order

    headers = [schema[k] for k in final_keys]

    # Decide on some file-level quirks
    has_extra_blank_rows = random.random() < 0.3
    has_duplicate_rows = random.random() < 0.25
    has_trailing_spaces = random.random() < 0.2
    delimiter = random.choice([",", ",", ",", ",", ";", "\t", "|"])  # mostly comma
    has_currency_col = random.random() < 0.3
    has_notes_col = random.random() < 0.2

    if has_currency_col:
        headers.append(random.choice(["Currency", "currency", "CUR", "ccy", "Waehrung"]))
        final_keys.append("_currency")
    if has_notes_col:
        headers.append(random.choice(["Notes", "notes", "Comments", "Remarks"]))
        final_keys.append("_notes")

    rows = []
    base_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))

    for i in range(num_rows):
        row = {}
        sale_date = base_date + timedelta(days=random.randint(0, 730))
        qty = random.randint(1, 500) if random.random() > 0.08 else None
        price = round(random.uniform(5, 5000), 2) if random.random() > 0.05 else None
        if qty and price:
            rev = round(qty * price, 2)
        elif random.random() > 0.3:
            rev = round(random.uniform(100, 250000), 2)
        else:
            rev = None

        for key in final_keys:
            if key == "date":
                if random.random() < 0.05:
                    row[key] = random.choice(["", "N/A", "TBD", "null", "pending"])
                else:
                    row[key] = sale_date.strftime(date_fmt)
            elif key == "company":
                if random.random() < 0.03:
                    row[key] = ""
                else:
                    row[key] = company if random.random() < 0.7 else random.choice(COMPANIES)
            elif key == "product":
                if random.random() < 0.06:
                    row[key] = random.choice(["", "N/A", "Other", "MISC", "-"])
                else:
                    row[key] = random.choice(PRODUCTS)
            elif key == "quantity":
                row[key] = fmt_quantity(qty)
            elif key == "unit_price":
                row[key] = fmt_revenue(price, rev_style)
            elif key == "revenue":
                row[key] = fmt_revenue(rev, rev_style)
            elif key == "region":
                if random.random() < 0.07:
                    row[key] = random.choice(["", "N/A", "Unknown", "??", "-"])
                else:
                    row[key] = random.choice(REGIONS)
            elif key == "channel":
                if random.random() < 0.06:
                    row[key] = ""
                else:
                    row[key] = random.choice(CHANNELS)
            elif key == "status":
                row[key] = random.choice(STATUSES)
            elif key == "sales_rep":
                if random.random() < 0.08:
                    row[key] = random.choice(["", "N/A", "TBD", "Unassigned"])
                else:
                    row[key] = random.choice(SALES_REPS)
            elif key == "leads":
                if random.random() < 0.1:
                    row[key] = random.choice(["", "N/A", "-", "null"])
                else:
                    row[key] = str(random.randint(0, 5000))
            elif key == "conversions":
                if random.random() < 0.1:
                    row[key] = random.choice(["", "N/A", "-"])
                else:
                    row[key] = str(random.randint(0, 500))
            elif key == "ad_spend":
                if random.random() < 0.12:
                    row[key] = random.choice(["", "N/A", "0", "-", "null"])
                else:
                    row[key] = fmt_revenue(round(random.uniform(100, 50000), 2), rev_style)
            elif key == "campaign":
                if random.random() < 0.1:
                    row[key] = ""
                else:
                    prefix = random.choice(["Q1", "Q2", "Q3", "Q4", "H1", "H2", "FY"])
                    year = random.choice(["2023", "2024", "24", "23"])
                    name = random.choice(["Spring Push", "Summer Blitz", "Fall Campaign",
                                          "Holiday Sale", "New Year Promo", "Black Friday",
                                          "Product Launch", "Brand Awareness", "Retention",
                                          "Upsell", "Cross-sell", "Webinar Series",
                                          "Trade Show", "Email Blast", "Social Push"])
                    row[key] = f"{prefix}-{year}-{name}"
            elif key == "_currency":
                row[key] = random.choice(CURRENCIES)
            elif key == "_notes":
                if random.random() < 0.7:
                    row[key] = ""
                else:
                    row[key] = random.choice([
                        "follow up needed", "VIP client", "discount applied",
                        "bulk order", "returned", "partial payment",
                        "NET30 terms", "renewal", "new customer",
                        "escalated", "pending approval", "CEO referral",
                    ])

        if has_trailing_spaces and random.random() < 0.3:
            k = random.choice(list(row.keys()))
            row[k] = row[k] + "  "

        rows.append(row)

    # Insert duplicate rows
    if has_duplicate_rows:
        num_dupes = random.randint(1, max(1, num_rows // 10))
        for _ in range(num_dupes):
            rows.append(random.choice(rows).copy())

    # Shuffle to mix duplicates in
    random.shuffle(rows)

    # Build filename with variety
    safe_company = company.lower().replace(" ", "_").replace(".", "").replace(",", "")
    name_styles = [
        f"{safe_company}_sales_{file_index:03d}.csv",
        f"sales_data_{safe_company}_{random.randint(2023,2025)}.csv",
        f"{safe_company}_marketing_export.csv",
        f"export_{file_index:03d}_{safe_company}.csv",
        f"{safe_company.upper()}_Q{random.randint(1,4)}_{random.randint(2023,2025)}.csv",
        f"data_dump_{safe_company}_{file_index}.csv",
        f"{safe_company}-sales-{random.choice(['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'])}{random.randint(23,25)}.csv",
    ]
    filename = random.choice(name_styles)

    filepath = os.path.join(OUTPUT_DIR, filename)
    # Handle potential filename collisions
    while os.path.exists(filepath):
        filename = f"{file_index}_{filename}"
        filepath = os.path.join(OUTPUT_DIR, filename)

    # Write file
    ext = filepath.split(".")[-1]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=delimiter)

        # Some files have a junk header row or blank line before the real headers
        if random.random() < 0.15:
            writer.writerow([f"Exported from {company} CRM on {datetime.now().strftime('%Y-%m-%d')}"]
                            + [""] * (len(headers) - 1))
        if random.random() < 0.1:
            writer.writerow([""] * len(headers))

        writer.writerow(headers)

        for row in rows:
            writer.writerow([row.get(k, "") for k in final_keys])

        # Some files have blank rows at the end
        if has_extra_blank_rows:
            for _ in range(random.randint(1, 5)):
                writer.writerow([""] * len(headers))

    return filepath


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Generating 100 dummy sales/marketing data files...\n")
    files = []
    for i in range(100):
        fp = generate_file(i)
        files.append(fp)

    # Print summary
    print(f"Created {len(files)} files in '{OUTPUT_DIR}/':\n")

    # Show some stats
    total_size = 0
    for fp in sorted(files):
        size = os.path.getsize(fp)
        total_size += size
        print(f"  {fp:60s}  {size:>8,} bytes")

    print(f"\nTotal: {total_size:,} bytes across {len(files)} files")
    print("\nData quality issues baked in:")
    print("  - 8 different schema/column-naming conventions (incl. typos & German)")
    print("  - 10 different date formats")
    print("  - 7 different revenue/price formatting styles")
    print("  - Random missing values (empty, N/A, null, #N/A, #REF!, etc.)")
    print("  - Inconsistent region, channel, and status labels")
    print("  - Duplicate rows in ~25% of files")
    print("  - Trailing whitespace in ~20% of files")
    print("  - Junk header rows in ~15% of files")
    print("  - Blank rows at end of ~30% of files")
    print("  - Mixed delimiters (comma, semicolon, tab, pipe)")
    print("  - Random column subsets and orderings per file")
    print("  - Inconsistent sales rep name casing/abbreviation")
