from .utils.agent_utils import Toolkit, create_msg_delete
from .utils.agent_states import AgentState, InvestDebateState, RiskDebateState
from .utils.memory import FinancialSituationMemory

# 旅行系统的导入（group_a, group_b, group_c）
try:
    from .group_a.user_requirement_analyst import user_requirement_analyst_node
    from .group_a.destination_matcher import match_destinations
except ImportError:
    pass

# 股票分析系统导入（已删除，添加 try-except）
try:
    from .analysts.fundamentals_analyst import create_fundamentals_analyst
    from .analysts.market_analyst import create_market_analyst
    from .analysts.news_analyst import create_news_analyst
except ImportError:
    pass

try:
    from .researchers.bear_researcher import create_bear_researcher
    from .researchers.bull_researcher import create_bull_researcher
except ImportError:
    pass

try:
    from .risk_mgmt.aggresive_debator import create_risky_debator
    from .risk_mgmt.conservative_debator import create_safe_debator
    from .risk_mgmt.neutral_debator import create_neutral_debator
except ImportError:
    pass

try:
    from .managers.research_manager import create_research_manager
    from .managers.risk_manager import create_risk_manager
except ImportError:
    pass

try:
    from .trader.trader import create_trader
except ImportError:
    pass

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

__all__ = [
    "FinancialSituationMemory",
    "Toolkit",
    "AgentState",
    "create_msg_delete",
    "InvestDebateState",
    "RiskDebateState",
    # 旅行系统
    "user_requirement_analyst_node",
    "match_destinations",
]

# 动态添加存在的股票系统导出
try:
    __all__.extend([
        "create_bear_researcher",
        "create_bull_researcher",
        "create_research_manager",
        "create_fundamentals_analyst",
        "create_market_analyst",
        "create_neutral_debator",
        "create_news_analyst",
        "create_risky_debator",
        "create_risk_manager",
        "create_safe_debator",
        "create_trader",
    ])
except:
    pass
