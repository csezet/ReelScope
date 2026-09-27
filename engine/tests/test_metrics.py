import pytest
from reelscope_engine.metrics.formulas import (
    calculate_engagement_rate,
    calculate_completion_rate,
    calculate_save_rate,
    calculate_share_rate,
    calculate_follower_conversion,
    calculate_velocity_24h,
    calculate_growth_ratio_7d_24h
)

def test_engagement_rate():
    # views = 1000, likes = 50, comments = 10, shares = 5, saves = 15 => 80 / 1000 = 8.0%
    assert calculate_engagement_rate(50, 10, 5, 15, 1000) == 8.0
    # Zero views should return None (No fake zeroes)
    assert calculate_engagement_rate(10, 5, 2, 1, 0) is None
    # None views should return None
    assert calculate_engagement_rate(10, 5, 2, 1, None) is None

def test_completion_rate():
    # completed = 400, views = 1000 => 40.0%
    assert calculate_completion_rate(400, 1000) == 40.0
    # If completed_views is None, returns None (No fake zeroes)
    assert calculate_completion_rate(None, 1000) is None
    assert calculate_completion_rate(400, 0) is None

def test_save_and_share_rates():
    assert calculate_save_rate(50, 1000) == 5.0
    assert calculate_save_rate(None, 1000) is None
    assert calculate_share_rate(25, 1000) == 2.5
    assert calculate_share_rate(None, 1000) is None

def test_velocity_and_growth_ratio():
    assert calculate_velocity_24h(2400) == 100.0
    assert calculate_velocity_24h(None) is None
    assert calculate_growth_ratio_7d_24h(5000, 2500) == 2.0
    assert calculate_growth_ratio_7d_24h(None, 2500) is None
    assert calculate_growth_ratio_7d_24h(5000, 0) is None
