"""
Generate a formatted executive summary report for the Global Energy Market.
Run with: python -m src.report
"""

from src.data_loader import load_market_data, clean_data
from src.analysis import (
    market_size_by_sector,
    regional_benchmark,
    growth_leaders,
    sustainability_score,
)


def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_section(title):
    print(f"\n--- {title} ---\n")


def generate_report():
    df = load_market_data()
    df_clean = clean_data(df)

    print_header("GLOBAL ENERGY MARKET REPORT 2023")
    print(f"  Companies analyzed: {len(df)}")
    print(f"  Regions covered:    {df['region'].nunique()}")
    print(f"  Sectors covered:    {df['sector'].nunique()}")
    total_rev = df["revenue_2023_bn"].sum()
    print(f"  Total market size:  ${total_rev:,.1f}B")

    # --- Market Size by Sector ---
    print_section("MARKET SIZE BY SECTOR")
    sector = market_size_by_sector(df)
    for name, row in sector.iterrows():
        bar = "#" * int(row["total_revenue_2023"] / 15)
        print(f"  {name:<16} ${row['total_revenue_2023']:>7.1f}B  {bar}")

    # --- Top 5 Growth Leaders ---
    print_section("TOP 5 GROWTH LEADERS")
    leaders = growth_leaders(df, top_n=5)
    for _, row in leaders.iterrows():
        arrow = "+" if row["revenue_growth_pct"] > 0 else ""
        print(
            f"  {row['company']:<22} {row['sector']:<16} "
            f"{arrow}{row['revenue_growth_pct']:.1f}%"
        )

    # --- Sustainability Scorecard ---
    print_section("SUSTAINABILITY SCORECARD (Top 10)")
    scores = sustainability_score(df).head(10)
    for _, row in scores.iterrows():
        bar = "*" * int(row["sustainability_score"] / 5)
        print(
            f"  {row['company']:<22} {row['sustainability_score']:>5.1f}  {bar}"
        )

    # --- Regional Benchmark ---
    print_section("REGIONAL BENCHMARK")
    bench = regional_benchmark(df)
    print(f"  {'Region':<16} {'Revenue':>10} {'Avg Carbon':>12} {'Renewable%':>12}")
    print(f"  {'-'*52}")
    for region, row in bench.iterrows():
        print(
            f"  {region:<16} ${row['total_revenue']:>8.1f}B "
            f"{row['avg_carbon_intensity']:>10.1f} "
            f"{row['avg_renewable_pct']:>10.1f}%"
        )

    # --- Key Insights ---
    print_section("KEY INSIGHTS")

    # Fastest grower
    top = leaders.iloc[0]
    print(f"  1. {top['company']} leads growth at +{top['revenue_growth_pct']:.1f}% YoY")

    # Most sustainable
    top_sus = scores.iloc[0]
    print(f"  2. {top_sus['company']} tops sustainability (score: {top_sus['sustainability_score']})")

    # Largest sector
    print(f"  3. {sector.index[0]} dominates with ${sector.iloc[0]['total_revenue_2023']:.1f}B revenue")

    # Renewables growth
    renewables = df[df["sector"] == "Renewables"]
    ren_growth = (
        (renewables["revenue_2023_bn"].sum() - renewables["revenue_2022_bn"].sum())
        / renewables["revenue_2022_bn"].sum()
        * 100
    )
    print(f"  4. Renewables sector grew {ren_growth:.1f}% overall, outpacing Oil & Gas")

    print(f"\n{'='*60}")
    print(f"  Report generated from {len(df)} companies across {df['region'].nunique()} regions")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    generate_report()
