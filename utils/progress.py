from typing import Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.style import Style

console = Console()


class AgentProgress:
    def __init__(self, mode: str = "cli", st_ref=None):
        self.mode = mode  # "cli" or "streamlit"
        self.st = st_ref  # 仅 streamlit 模式下需要传入 st 模块
        self.agent_status: Dict[str, str] = {}
        self.started = False

        if self.mode == "cli":
            self.table = Table(show_header=False, box=None, padding=(0, 1))
            self.live = Live(self.table, console=console, refresh_per_second=4)

    def start(self):
        if self.mode == "cli" and not self.started:
            self.live.start()
            self.started = True

    def stop(self):
        if self.mode == "cli" and self.started:
            self.live.stop()
            self.started = False

    def update_status(self, agent_name: str, status: str = ""):
        self.agent_status[agent_name] = status
        self._refresh_display()

    def _refresh_display(self):
        if self.mode == "cli":
            self._render_cli()
        elif self.mode == "streamlit":
            self._render_streamlit()

    def _render_cli(self):
        self.table.columns.clear()
        self.table.add_column(width=100)

        for agent_name in sorted(self.agent_status):
            status = self.agent_status[agent_name]

            if status.lower() == "done":
                style = Style(color="green", bold=True)
                symbol = "✓"
            elif status.lower() == "error":
                style = Style(color="red", bold=True)
                symbol = "✗"
            else:
                style = Style(color="yellow")
                symbol = "⋯"

            agent_display = agent_name.replace("_agent", "").replace("_", " ").title()
            status_text = Text()
            status_text.append(f"{symbol} ", style=style)
            status_text.append(f"{agent_display:<20} {status}", style=style)

            self.table.add_row(status_text)

    def _render_streamlit(self):
        if self.st:
            self.st.sidebar.markdown("### 🟢 Agent 状态")
            for name, status in self.agent_status.items():
                self.st.sidebar.write(f"**{name}**: {status}")


# 默认实例（CLI 模式）
progress = AgentProgress(mode="streamlit")
