import io
import pytest
import pandas as pd
from reelscope_engine.importers import generate_preview, validate_mapped_data, commit_import_to_db
from reelscope_engine.db import get_db

def test_importer_preview_and_mapping():
    csv_data = b"id,created,video_views,likes_count\npost_1,2024-05-01 10:00:00,1500,120\npost_2,2024-05-02 11:00:00,2500,200\n"
    preview = generate_preview(csv_data, "test.csv")
    assert preview["total_columns"] == 4
    assert preview["suggested_mapping"]["post_id"] == "id"
    assert preview["suggested_mapping"]["views"] == "video_views"
    assert len(preview["preview_rows"]) == 2

def test_importer_validation_and_commit():
    conn = get_db()
    df = pd.DataFrame([
        {"p_id": "test_imp_1", "p_date": "2024-05-01 12:00:00", "v_count": 500, "l_count": 30},
        {"p_id": "test_imp_2", "p_date": "2024-05-02 12:00:00", "v_count": 800, "l_count": 50}
    ])
    mapping = {"post_id": "p_id", "published_at": "p_date", "views": "v_count", "likes": "l_count"}
    
    val = validate_mapped_data(df, mapping)
    assert val["is_valid"] is True
    assert val["invalid_dates"] == 0

    import uuid
    test_hash = f"hash_test_{uuid.uuid4().hex[:12]}"
    res = commit_import_to_db(conn, df, mapping, file_hash=test_hash, source_name="test_upload.csv")
    assert res["status"] == "success"
    assert res["rows_imported"] == 2
