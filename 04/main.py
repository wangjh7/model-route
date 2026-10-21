# =============================================================================
#  pytest 集成测试（Mock LLM）
#  用"当前解释器"在 `04/` 目录下启动pytest, 并把pytest的退出码透传给shell
# =============================================================================
#
#  FakeLLM：按预设 replies 顺序返回，替代真实 API
#  run_agent_stub：两轮编排 —— tool JSON → 执行工具 → 最终答案
#
#  运行：python main.py        # 推荐，自动切 cwd + 透传退出码
#       或 cd 04 && pytest -v
# =============================================================================

import subprocess
import sys

if __name__ == "__main__":
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v"],
        cwd=__import__("pathlib").Path(__file__).resolve().parent,
    )
    raise SystemExit(result.returncode)