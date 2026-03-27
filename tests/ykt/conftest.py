# ========================================
# 雨课堂：测试数据从环境 YAML 的 ykt_config_file 加载（见 config/environments/ykt/*.yaml）
# 临时覆盖：pytest ... --data-file=ykt/xxx.yaml
# ========================================

import os

import pytest

from utils.data_loader import load_yaml


@pytest.fixture(scope="session")
def ykt_data(request, env_config) -> dict:
    """
    按环境配置 ykt_config_file 加载 data 下 YAML。

    优先级：--data-file > 环境变量 YKT_DATA_FILE > env_config['ykt_config_file'] > ykt/prod_config.yaml
    """
    rel = request.config.getoption("--data-file")
    if not rel:
        rel = os.getenv("YKT_DATA_FILE", "").strip()
    if not rel:
        rel = (env_config.get("ykt_config_file") or "").strip()
    if not rel:
        rel = "ykt/prod_config.yaml"
    rel = rel.replace("\\", "/").lstrip("/")
    return load_yaml(rel)
