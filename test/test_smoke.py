"""冒烟测试：确认测试环境本身可用。

背景：仓库刚建立时 test/ 下还没有业务用例，而 pytest.ini 里 testpaths = test ——
若该目录为空或不存在，pytest 会直接失败（exit 4），PR 一开就变红。
本文件保证 CI 从第一天起是绿的。

重要：这里**只做环境自检**，不去断言仓库里其它文件是否存在。
原因：`CONTRIBUTING.md` 在 main 分支上而不在 dev 上，`docs/interface.md` 也可能还没合进 dev，
一旦断言它们存在，CI 就会因为“文件还没到位”而误报失败（曾踩过这个坑）。

M1（规则地基）完成后，test/ 下会有真实的 test_rule.py 等用例，届时本文件可删除，CI 行为不变。
"""

import sys
from pathlib import Path

THIS_FILE = Path(__file__).resolve()


def test_python_version_at_least_39():
    """项目要求 Python 3.9+（见 README / CONTRIBUTING）。"""
    assert sys.version_info >= (3, 9), f"需要 Python 3.9+，当前 {sys.version}"


def test_test_file_lives_in_test_directory():
    """测试文件必须位于仓库根的 test/ 目录下（pytest.ini 的 testpaths 约定）。"""
    assert THIS_FILE.parent.name == "test", f"测试文件位置异常：{THIS_FILE}"
