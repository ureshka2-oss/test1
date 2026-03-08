"""
Tests for the analysis module.
"""

import pytest
import pandas as pd
from src.data_loader import load_market_data, validate_data, clean_data
from src.analysis import (
    market_size_by_sector,
    regional_benchmark,
    growth_leaders,
    sustainability_score,
    competitive_positioning,
)


@pytest.fixture
def sample_data():
    return load_market_data()


@pytest.fixture
def cleaned_data(sample_data):
    return clean_data(sample_data)


# --- Data Loading Tests ---

class TestDataLoader:
    def test_load_market_data(self, sample_data):
        assert not sample_data.empty
        assert len(sample_data) == 20

    def test_required_columns_exist(self, sample_data):
        required = [
            "company", "region", "sector", "revenue_2022_bn",
            "revenue_2023_bn", "market_cap_bn", "employees",
        ]
        for col in required:
            assert col in sample_data.columns

    def test_no_missing_values(self, sample_data):
        assert sample_data.isnull().sum().sum() == 0

    def test_validate_data_returns_no_critical_issues(self, sample_data):
        """All data should pass validation without issues."""
        issues = validate_data(sample_data)
        assert len(issues) == 0, f"Unexpected issues: {issues}"


# --- Data Cleaning Tests ---

class TestDataCleaning:
    def test_region_codes_added(self, cleaned_data):
        assert "region_code" in cleaned_data.columns
        assert cleaned_data["region_code"].isnull().sum() == 0

    def test_revenue_growth_calculation(self, cleaned_data):
        """Revenue growth should be calculated as (new - old) / old * 100."""
        row = cleaned_data[cleaned_data["company"] == "SolarWave"].iloc[0]
        expected_growth = (18.9 - 12.8) / 12.8 * 100
        assert abs(row["revenue_growth_pct"] - expected_growth) < 0.1, (
            f"Expected growth ~{expected_growth:.1f}%, got {row['revenue_growth_pct']:.1f}%"
        )


# --- Analysis Tests ---

class TestMarketAnalysis:
    def test_market_size_by_sector(self, sample_data):
        result = market_size_by_sector(sample_data)
        assert "total_revenue_2023" in result.columns
        assert len(result) > 0
        # Oil & Gas should be the largest sector
        assert result.index[0] == "Oil & Gas"

    def test_regional_benchmark(self, sample_data):
        result = regional_benchmark(sample_data)
        assert "total_revenue" in result.columns
        assert len(result) == 6  # 6 regions in dataset

    def test_growth_leaders_returns_correct_count(self, sample_data):
        result = growth_leaders(sample_data, top_n=3)
        assert len(result) == 3

    def test_growth_leaders_sorted_descending(self, sample_data):
        result = growth_leaders(sample_data, top_n=5)
        growths = result["revenue_growth_pct"].tolist()
        assert growths == sorted(growths, reverse=True)

    def test_sustainability_scores_range(self, sample_data):
        """Top sustainability companies with 100% renewables should score above 90."""
        result = sustainability_score(sample_data)
        # Companies with 100% renewables and low carbon should score above 90
        top_company = result.iloc[0]
        assert top_company["sustainability_score"] > 90, (
            f"Top sustainability score is only {top_company['sustainability_score']}"
        )

    def test_competitive_positioning_valid_sector(self, sample_data):
        result = competitive_positioning(sample_data, "Renewables")
        assert result is not None
        assert "market_share_pct" in result.columns
        # Market shares should sum to 100%
        assert abs(result["market_share_pct"].sum() - 100.0) < 0.5

    def test_competitive_positioning_invalid_sector(self, sample_data):
        result = competitive_positioning(sample_data, "Blockchain Mining")
        assert result is None


# --- Edge Case Tests ---

class TestEdgeCases:
    def test_empty_sector_comparison(self, sample_data):
        result = competitive_positioning(sample_data, "Nuclear")
        assert result is not None
        assert len(result) == 1  # Only one nuclear company

    def test_growth_leaders_with_negative_growth(self, sample_data):
        result = growth_leaders(sample_data, top_n=20)
        # Some companies should have negative growth
        assert (result["revenue_growth_pct"] < 0).any()
