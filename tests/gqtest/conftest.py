# ========================================
# 光穹 gqtest 共用 fixtures
# ========================================

import pytest

from utils.data_loader import load_yaml


@pytest.fixture(scope="session")
def gqkt_data() -> dict:
    """与 load_yaml(\"gqkt/gqkt_config.yaml\") 一致（含环境 gqkt_config_file / ENV 解析）。"""
    return load_yaml("gqkt/gqkt_config.yaml")
