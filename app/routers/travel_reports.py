"""
旅行报告管理 API路由

管理旅行规划和攻略的报告：
- 规划报告
- 攻略报告
- Token使用统计
- 报告导出
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import json
from io import BytesIO

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/travel/reports", tags=["旅行报告管理"])


# ============================================================
# 数据模型
# ============================================================

class TravelReport(BaseModel):
    """旅行报告"""
    id: str
    report_type: str  # plan/guide
    title: str
    destination: str
    user_id: int
    username: str
    days: Optional[int] = None
    budget_level: Optional[str] = None
    content: Dict[str, Any]
    summary: str
    token_usage: Dict[str, int]
    agent_logs: List[Dict[str, Any]]
    created_at: str
    updated_at: str


class ReportListResponse(BaseModel):
    """报告列表响应"""
    reports: List[TravelReport]
    total: int


class TokenUsage(BaseModel):
    """Token使用统计"""
    total_tokens: int
    input_tokens: int
    output_tokens: int
    by_model: Dict[str, int]
    by_date: Dict[str, int]
    estimated_cost: float


class ReportExportRequest(BaseModel):
    """报告导出请求"""
    report_ids: List[str]
    format: str = Field("json", description="导出格式: json/csv/html")


# ============================================================
# 内存存储 (生产环境应使用数据库)
# ============================================================

_reports_store = {}
_report_counter = 0
_token_usage_store = {}  # {date: {model: tokens}}


def get_next_report_id():
    """生成下一个报告ID"""
    global _report_counter
    _report_counter += 1
    return f"report_{_report_counter}_{datetime.utcnow().timestamp()}"


def create_report(report_data: dict) -> dict:
    """创建报告"""
    report = {
        "id": get_next_report_id(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        **report_data
    }

    _reports_store[report["id"]] = report

    # 记录Token使用
    if report.get("token_usage"):
        record_token_usage(report["token_usage"])

    return report


def record_token_usage(token_usage: dict):
    """记录Token使用"""
    today = datetime.utcnow().strftime("%Y-%m-%d")

    if today not in _token_usage_store:
        _token_usage_store[today] = {}

    for model, tokens in token_usage.items():
        _token_usage_store[today][model] = _token_usage_store[today].get(model, 0) + tokens


def get_user_reports(user_id: int, report_type: Optional[str] = None) -> list:
    """获取用户报告"""
    reports = list(_reports_store.values())
    reports = [r for r in reports if r.get("user_id") == user_id]

    if report_type:
        reports = [r for r in reports if r.get("report_type") == report_type]

    reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return reports


def get_token_stats(days: int = 30) -> dict:
    """获取Token使用统计"""
    from datetime import timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=days)
    cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")

    total_tokens = 0
    input_tokens = 0
    output_tokens = 0
    by_model = {}
    by_date = {}

    for date, models in _token_usage_store.items():
        if date >= cutoff_date_str:
            by_date[date] = sum(models.values())
            for model, tokens in models.items():
                by_model[model] = by_model.get(model, 0) + tokens
                total_tokens += tokens

    # 估算成本 (DeepSeek定价)
    total_cost = (by_model.get("deepseek-chat", 0) / 1000000) * 1.0  # 1元/百万token

    return {
        "total_tokens": total_tokens,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "by_model": by_model,
        "by_date": by_date,
        "estimated_cost": total_cost
    }


# ============================================================
# API端点
# ============================================================

@router.get("/", response_model=ReportListResponse)
async def get_reports(
    user_id: int = Query(1),
    report_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取报告列表"""
    reports = get_user_reports(user_id, report_type)

    total = len(reports)

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated_reports = reports[start:end]

    return ReportListResponse(
        reports=[TravelReport(**r) for r in paginated_reports],
        total=total
    )


@router.get("/{report_id}", response_model=TravelReport)
async def get_report_detail(report_id: str):
    """获取报告详情"""
    if report_id not in _reports_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"报告不存在: {report_id}"
        )

    return TravelReport(**_reports_store[report_id])


@router.get("/token-usage", response_model=TokenUsage)
async def get_token_usage_stats(
    days: int = Query(30, ge=1, le=365)
):
    """获取Token使用统计"""
    stats = get_token_stats(days)
    return TokenUsage(**stats)


@router.post("/export")
async def export_reports(request: ReportExportRequest):
    """导出报告"""
    reports = [_reports_store.get(rid) for rid in request.report_ids]
    reports = [r for r in reports if r]

    if not reports:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有找到可导出的报告"
        )

    if request.format == "json":
        # JSON导出
        json_data = json.dumps(reports, ensure_ascii=False, indent=2)
        return Response(
            content=json_data,
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=travel_reports.json"
            }
        )

    elif request.format == "csv":
        # CSV导出
        import csv
        output = BytesIO()
        writer = csv.writer(output)

        # 表头
        writer.writerow([
            "ID", "类型", "标题", "目的地", "用户", "天数",
            "预算", "创建时间", "Token使用"
        ])

        # 数据行
        for report in reports:
            writer.writerow([
                report.get("id"),
                report.get("report_type"),
                report.get("title"),
                report.get("destination"),
                report.get("username"),
                report.get("days"),
                report.get("budget_level"),
                report.get("created_at"),
                sum(report.get("token_usage", {}).values())
            ])

        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=travel_reports.csv"
            }
        )

    elif request.format == "html":
        # HTML导出
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>旅行报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>旅行报告</h1>
    <table>
        <tr>
            <th>标题</th>
            <th>目的地</th>
            <th>用户</th>
            <th>天数</th>
            <th>创建时间</th>
        </tr>
"""

        for report in reports:
            html += f"""
        <tr>
            <td>{report.get('title')}</td>
            <td>{report.get('destination')}</td>
            <td>{report.get('username')}</td>
            <td>{report.get('days')}</td>
            <td>{report.get('created_at')}</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        return Response(
            content=html,
            media_type="text/html",
            headers={
                "Content-Disposition": "attachment; filename=travel_reports.html"
            }
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的导出格式: {request.format}"
        )


@router.delete("/{report_id}")
async def delete_report(report_id: str, user_id: int = 1):
    """删除报告"""
    if report_id not in _reports_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"报告不存在: {report_id}"
        )

    report = _reports_store[report_id]

    if report.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此报告"
        )

    del _reports_store[report_id]

    return {"success": True, "message": "报告已删除"}


@router.get("/stats/summary")
async def get_reports_summary(
    user_id: int = Query(1)
):
    """获取报告汇总统计"""
    reports = get_user_reports(user_id)

    total_reports = len(reports)
    plan_reports = len([r for r in reports if r.get("report_type") == "plan"])
    guide_reports = len([r for r in reports if r.get("report_type") == "guide"])

    # 目的地统计
    destinations = {}
    for r in reports:
        dest = r.get("destination", "未知")
        destinations[dest] = destinations.get(dest, 0) + 1

    # Token使用
    total_tokens = sum(
        sum(r.get("token_usage", {}).values())
        for r in reports
    )

    return {
        "total_reports": total_reports,
        "plan_reports": plan_reports,
        "guide_reports": guide_reports,
        "top_destinations": sorted(destinations.items(), key=lambda x: x[1], reverse=True)[:5],
        "total_tokens_used": total_tokens
    }


# ============================================================
# 便捷函数：创建各类报告
# ============================================================

def create_plan_report(
    user_id: int,
    username: str,
    destination: str,
    days: int,
    budget: str,
    plan_data: dict,
    agent_logs: list,
    token_usage: dict
) -> str:
    """创建规划报告"""
    report = create_report({
        "report_type": "plan",
        "title": f"{destination} {days}天旅行规划",
        "destination": destination,
        "user_id": user_id,
        "username": username,
        "days": days,
        "budget_level": budget,
        "content": plan_data,
        "summary": f"为{username}生成的{destination}{days}天旅行规划",
        "token_usage": token_usage,
        "agent_logs": agent_logs
    })

    logger.info(f"创建规划报告: {report['id']}")
    return report["id"]


def create_guide_report(
    user_id: int,
    username: str,
    guide_data: dict,
    token_usage: dict
) -> str:
    """创建攻略报告"""
    report = create_report({
        "report_type": "guide",
        "title": guide_data.get("title", "旅行攻略"),
        "destination": guide_data.get("destination", ""),
        "user_id": user_id,
        "username": username,
        "days": guide_data.get("days"),
        "budget_level": guide_data.get("budget_level"),
        "content": guide_data,
        "summary": guide_data.get("description", "")[:100],
        "token_usage": token_usage,
        "agent_logs": []
    })

    logger.info(f"创建攻略报告: {report['id']}")
    return report["id"]


# 导出函数
__all__ = [
    "create_plan_report",
    "create_guide_report",
    "get_token_stats"
]
