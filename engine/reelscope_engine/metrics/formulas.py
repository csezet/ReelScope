from typing import Optional, Union

def calculate_engagement_rate(likes: int, comments: int, shares: int, saves: int, views: int) -> Optional[float]:
    """Calculate Engagement Rate: (likes + comments + shares + saves) / views * 100%."""
    if views is None or views <= 0:
        return None
    total_eng = (likes or 0) + (comments or 0) + (shares or 0) + (saves or 0)
    return round((total_eng / views) * 100.0, 2)

def calculate_completion_rate(completed_views: Optional[int], views: int) -> Optional[float]:
    """Calculate Completion Rate: completed_views / views * 100%. Returns None if completed_views is absent."""
    if completed_views is None or views is None or views <= 0:
        return None
    return round((completed_views / views) * 100.0, 2)

def calculate_save_rate(saves: Optional[int], views: int) -> Optional[float]:
    """Calculate Save Rate: saves / views * 100%."""
    if saves is None or views is None or views <= 0:
        return None
    return round((saves / views) * 100.0, 2)

def calculate_share_rate(shares: Optional[int], views: int) -> Optional[float]:
    """Calculate Share Rate: shares / views * 100%."""
    if shares is None or views is None or views <= 0:
        return None
    return round((shares / views) * 100.0, 2)

def calculate_follower_conversion(followers_gained: Optional[int], views: int) -> Optional[float]:
    """Calculate Follower Conversion: followers_gained / views * 100%."""
    if followers_gained is None or views is None or views <= 0:
        return None
    return round((followers_gained / views) * 100.0, 3)

def calculate_velocity_24h(views_at_24h: Optional[int]) -> Optional[float]:
    """Calculate 24h Velocity: views_at_24h / 24."""
    if views_at_24h is None:
        return None
    return round(views_at_24h / 24.0, 1)

def calculate_growth_ratio_7d_24h(views_7d: Optional[int], views_24h: Optional[int]) -> Optional[float]:
    """Calculate 7d / 24h Growth Ratio."""
    if views_7d is None or views_24h is None or views_24h <= 0:
        return None
    return round(views_7d / views_24h, 2)
