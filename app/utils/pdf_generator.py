"""
攻略PDF生成器

将旅行攻略转换为PDF格式，支持打印和分享
"""

import logging
from datetime import datetime
from typing import Optional
from io import BytesIO

logger = logging.getLogger(__name__)


class GuidePDFGenerator:
    """攻略PDF生成器"""

    def __init__(self):
        pass

    def generate_html_content(
        self,
        guide: dict,
        author_info: Optional[dict] = None
    ) -> str:
        """
        生成攻略的HTML内容

        Args:
            guide: 攻略数据字典
            author_info: 作者信息

        Returns:
            HTML字符串
        """
        # 提取数据
        title = guide.get("title", "旅行攻略")
        description = guide.get("description", "")
        destination = guide.get("destination", "")
        days = guide.get("days", 0)
        budget_level = guide.get("budget_level", "")
        travel_style = guide.get("travel_style", "")
        cover_image = guide.get("cover_image", "")
        interest_tags = guide.get("interest_tags", [])

        itinerary = guide.get("itinerary", {})
        budget_breakdown = guide.get("budget_breakdown", {})
        attractions = guide.get("attractions", [])
        accommodation = guide.get("accommodation", {})
        transportation = guide.get("transportation", {})

        daily_itinerary = itinerary.get("daily_itinerary", [])

        # 生成HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #667eea;
        }}

        .header h1 {{
            color: #667eea;
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .header .meta {{
            color: #666;
            font-size: 14px;
        }}

        .cover-image {{
            width: 100%;
            max-height: 300px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 20px;
        }}

        .section {{
            margin-bottom: 30px;
        }}

        .section h2 {{
            color: #667eea;
            font-size: 20px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}

        .info-item {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
        }}

        .info-label {{
            color: #666;
            font-size: 12px;
            margin-bottom: 5px;
        }}

        .info-value {{
            color: #333;
            font-size: 16px;
            font-weight: 600;
        }}

        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }}

        .tag {{
            background: #e0e7ff;
            color: #3730a3;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
        }}

        .day-plan {{
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            background: #fafafa;
        }}

        .day-plan h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}

        .time-slot {{
            display: flex;
            margin-bottom: 10px;
            align-items: flex-start;
        }}

        .time {{
            min-width: 100px;
            color: #667eea;
            font-weight: 600;
            font-size: 14px;
        }}

        .activity {{
            flex: 1;
        }}

        .budget-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .budget-table th,
        .budget-table td {{
            border: 1px solid #e0e0e0;
            padding: 12px;
            text-align: left;
        }}

        .budget-table th {{
            background: #667eea;
            color: white;
        }}

        .budget-table tr:nth-child(even) {{
            background: #f9f9f9;
        }}

        .attraction-list {{
            list-style: none;
        }}

        .attraction-item {{
            background: #f9f9f9;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
            border-radius: 0 8px 8px 0;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #999;
            font-size: 12px;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
            .section {{
                page-break-inside: avoid;
            }}
            .day-plan {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>{title}</h1>
            <div class="meta">
                目的地: {destination} |
                天数: {days}天 |
                预算: {budget_level} |
                风格: {travel_style or '探索'}
            </div>
        </div>

        {"<img src='" + cover_image + "' class='cover-image'>" if cover_image else ""}

        <!-- 描述 -->
        {"<div class='section'><h2>攻略简介</h2><p>" + description + "</p></div>" if description else ""}

        <!-- 标签 -->
        {self._render_tags(interest_tags) if interest_tags else ""}

        <!-- 基本信息 -->
        <div class="section">
            <h2>行程信息</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">目的地</div>
                    <div class="info-value">{destination}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">行程天数</div>
                    <div class="info-value">{days}天</div>
                </div>
                <div class="info-item">
                    <div class="info-label">预算级别</div>
                    <div class="info-value">{self._format_budget(budget_level)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">旅行风格</div>
                    <div="info-value">{self._format_style(travel_style)}</div>
                </div>
            </div>
        </div>

        <!-- 每日行程 -->
        <div class="section">
            <h2>详细行程</h2>
            {self._render_itinerary(daily_itinerary)}
        </div>

        <!-- 预算分解 -->
        <div class="section">
            <h2>费用预算</h2>
            {self._render_budget(budget_breakdown)}
        </div>

        <!-- 推荐景点 -->
        {self._render_attractions(attractions) if attractions else ""}

        <!-- 住宿信息 -->
        {self._render_accommodation(accommodation) if accommodation else ""}

        <!-- 交通信息 -->
        {self._render_transportation(transportation) if transportation else ""}

        <!-- 页脚 -->
        <div class="footer">
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p>由旅行规划系统AI生成 | 攻略ID: {guide.get('id', 'N/A')}</p>
        </div>
    </div>
</body>
</html>
        """

        return html

    def _render_tags(self, tags: list) -> str:
        """渲染标签"""
        if not tags:
            return ""
        return '<div class="tags">' + ''.join(f'<span class="tag">{tag}</span>' for tag in tags) + '</div>'

    def _render_itinerary(self, daily_itinerary: list) -> str:
        """渲染行程"""
        if not daily_itinerary:
            return "<p>暂无详细行程</p>"

        html = ""
        for day_plan in daily_itinerary:
            html += f"""
        <div class="day-plan">
            <h3>第{day_plan.get('day', '?')}天: {day_plan.get('theme', '')}</h3>
            """

            # 上午
            morning = day_plan.get('morning', {})
            if morning:
                html += self._render_time_slot("上午", morning.get('time', ''), morning.get('activity', ''))

            # 午餐
            lunch = day_plan.get('lunch', {})
            if lunch:
                html += self._render_time_slot("午餐", lunch.get('time', ''), lunch.get('activity', ''))

            # 下午
            afternoon = day_plan.get('afternoon', {})
            if afternoon:
                html += self._render_time_slot("下午", afternoon.get('time', ''), afternoon.get('activity', ''))

            # 晚餐
            dinner = day_plan.get('dinner', {})
            if dinner:
                html += self._render_time_slot("晚餐", dinner.get('time', ''), dinner.get('activity', ''))

            # 晚上
            evening = day_plan.get('evening', {})
            if evening:
                html += self._render_time_slot("晚上", evening.get('time', ''), evening.get('activity', ''))

            html += "</div>"

        return html

    def _render_time_slot(self, period: str, time_range: str, activity: str) -> str:
        """渲染时间段"""
        return f"""
            <div class="time-slot">
            <div class="time">{period}: {time_range}</div>
                <div class="activity">{activity}</div>
            </div>
        """

    def _render_budget(self, budget_breakdown: dict) -> str:
        """渲染预算"""
        if not budget_breakdown:
            return "<p>暂无预算信息</p>"

        total = budget_breakdown.get('total_budget', 0)
        daily_avg = budget_breakdown.get('daily_average', 0)
        per_person = budget_breakdown.get('per_person_average', 0)

        html = f"""
        <p style="margin-bottom: 15px;">
            <strong>总预算:</strong> {total:,} 元 |
            <strong>日均:</strong> {daily_avg:,} 元/人 |
            <strong>人均:</strong> {per_person:,} 元
        </p>
        <table class="budget-table">
            <thead>
                <tr>
                    <th>项目</th>
                    <th>金额(元)</th>
                    <th>说明</th>
                </tr>
            </thead>
            <tbody>
        """

        items = [
            ('transportation', '交通', budget_breakdown.get('transportation', {})),
            ('accommodation', '住宿', budget_breakdown.get('accommodation', {})),
            ('meals', '餐饮', budget_breakdown.get('meals', {})),
            ('attractions', '景点', budget_breakdown.get('attractions', {})),
            ('miscellaneous', '其他', budget_breakdown.get('miscellaneous', {}))
        ]

        for key, name, data in items:
            amount = data.get('amount', 0)
            desc = data.get('description', '')
            html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{amount:,}</td>
                    <td>{desc}</td>
                </tr>
            """

        html += f"""
            </tbody>
        </table>

        <!-- 省钱建议 -->
        {self._render_tips(budget_breakdown.get('money_saving_tips', []))}
        """

        return html

    def _render_tips(self, tips: list) -> str:
        """渲染省钱建议"""
        if not tips:
            return ""
        return f"""
        <div style="background: #fffbeb; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <strong style="color: #b45309;">💡 省钱建议:</strong>
            <ul style="margin: 10px 0 10px 20px;">
                {"".join(f"<li>{tip}</li>" for tip in tips[:5])}
            </ul>
        </div>
        """

    def _render_attractions(self, attractions: list) -> str:
        """渲染景点列表"""
        if not attractions:
            return ""

        html = '<ul class="attraction-list">'
        for attr in attractions[:10]:
            html += f"""
                <li class="attraction-item">
                    <strong>{attr.get('name', '未知')}</strong>
                    {f" - {attr.get('description', '')[:100]}..." if attr.get('description') else ''}
                </li>
            """
        html += '</ul>'
        return html

    def _render_accommodation(self, accommodation: dict) -> str:
        """渲染住宿信息"""
        if not accommodation:
            return ""
        return f"""
        <div class="section">
            <h2>住宿信息</h2>
            <p><strong>类型:</strong> {accommodation.get('type', '')}</p>
            <p><strong>预算:</strong> {accommodation.get('budget', '')}元/晚</p>
        </div>
        """

    def _render_transportation(self, transportation: dict) -> str:
        """渲染交通信息"""
        if not transportation:
            return ""
        return f"""
        <div class="section">
            <h2>交通信息</h2>
            <p><strong>方式:</strong> {transportation.get('type', '')}</p>
            <p><strong>预算:</strong> {transportation.get('budget', '')}元</p>
        </div>
        """

    def _format_budget(self, budget: str) -> str:
        """格式化预算"""
        mapping = {
            'low': '经济',
            'medium': '舒适',
            'high': '豪华'
        }
        return mapping.get(budget, budget)

    def _format_style(self, style: str) -> str:
        """格式化风格"""
        mapping = {
            'immersive': '深度沉浸',
            'exploration': '全面探索',
            'relaxed': '休闲度假'
        }
        return mapping.get(style, style)

    def generate_pdf(
        self,
        guide: dict,
        author_info: Optional[dict] = None
    ) -> bytes:
        """
        生成PDF文件

        Args:
            guide: 攻略数据字典
            author_info: 作者信息

        Returns:
            PDF文件的二进制数据
        """
        try:
            from weasyprint import HTML, CSS

            # 生成HTML内容
            html_content = self.generate_html_content(guide, author_info)

            # 自定义CSS
            css = """
                @page {
                    size: A4;
                    margin: 2cm;
                    @top-right {
                        content: "Page " counter(page) " of " counter(pages);
                        font-size: 10pt;
                        color: #666;
                    }
                }
                @page:first {
                    @top-right {
                        content: "";
                    }
                }
            """

            # 生成PDF
            pdf_bytes = HTML(string=html_content).write_pdf(
                stylesheets=[CSS(string=css)],
                presentational_hints=True
            )

            return pdf_bytes

        except ImportError:
            logger.warning("weasyprint未安装，使用reportlab作为备选")
            return self._generate_pdf_with_reportlab(guide, author_info)

    def _generate_pdf_with_reportlab(self, guide: dict, author_info: Optional[dict] = None) -> bytes:
        """使用reportlab生成PDF（备选方案）"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase.ttfonts import TTFont

            buffer = BytesIO()

            # 创建PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=18)

            # 获取样式
            styles = getSampleStyleSheet()

            # 自定义标题样式
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=24,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=30
            )

            # 构建内容
            story = []

            # 标题
            title = guide.get('title', '旅行攻略')
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.3*inch))

            # 基本信息表格
            data = [
                ['项目', '信息'],
                ['目的地', guide.get('destination', '')],
                ['天数', f"{guide.get('days', 0)}天"],
                ['预算级别', self._format_budget(guide.get('budget_level', ''))],
                ['旅行风格', self._format_style(guide.get('travel_style', ''))],
            ]

            # 添加描述
            if guide.get('description'):
                data.append(['描述', guide.get('description')[:100] + '...'])

            table = Table(data, colWidths=[100, 400])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table)
            story.append(Spacer(1, 0.5*inch))

            # 行程信息
            itinerary = guide.get('itinerary', {})
            daily_itinerary = itinerary.get('daily_itinerary', [])
            if daily_itinerary:
                story.append(Paragraph('详细行程', title_style))
                story.append(Spacer(1, 0.2*inch))

                for day_plan in daily_itinerary[:5]:  # 最多显示5天
                    day_num = day_plan.get('day', '?')
                    theme = day_plan.get('theme', '')
                    story.append(Paragraph(f'第{day_num}天: {theme}', styles['Heading2']))

                    # 时间段
                    for period in ['morning', 'lunch', 'afternoon', 'dinner', 'evening']:
                        period_data = day_plan.get(period, {})
                        if period_data:
                            activity = period_data.get('activity', '')
                            time_range = period_data.get('time', '')
                            period_name = {
                                'morning': '上午',
                                'lunch': '午餐',
                                'afternoon': '下午',
                                'dinner': '晚餐',
                                'evening': '晚上'
                            }.get(period, period)

                            story.append(Paragraph(
                                f'{period_name}: {time_range} - {activity}',
                                styles['Normal']
                            ))

                    story.append(Spacer(1, 0.2*inch))

            # 预算信息
            budget = guide.get('budget_breakdown', {})
            if budget:
                story.append(Paragraph('费用预算', title_style))
                story.append(Spacer(1, 0.2*inch))

                total_budget = budget.get('total_budget', 0)
                story.append(Paragraph(f'总预算: {total_budget} 元', styles['Normal']))

                # 预算明细
                budget_items = []
                for key, name in [
                    ('transportation', '交通'),
                    ('accommodation', '住宿'),
                    ('meals', '餐饮'),
                    ('attractions', '景点'),
                    ('miscellaneous', '其他')
                ]:
                    item_data = budget.get(key, {})
                    if item_data and isinstance(item_data, dict):
                        amount = item_data.get('amount', 0)
                        if amount:
                            budget_items.append([name, f'{amount} 元'])

                if budget_items:
                    budget_table = Table(budget_items, colWidths=[100, 400])
                    budget_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(budget_table)

            # 页脚
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(
                f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")} | 由旅行规划系统AI生成',
                styles['Normal']
            ))

            # 生成PDF
            doc.build(story)

            pdf_bytes = buffer.getvalue()
            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF生成失败: {e}")
            raise


def getSampleStyleSheet():
    """获取PDF样式"""
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.platypus import ParagraphStyle

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle',
                            parent=styles['Heading1'],
                            fontSize=24,
                            textColor=colors.HexColor('#667eea'),
                            spaceAfter=30)
    )
    return styles


# ============================================================
# 便捷函数
# ============================================================

_generator = None


def get_pdf_generator() -> GuidePDFGenerator:
    """获取PDF生成器单例"""
    global _generator
    if _generator is None:
        _generator = GuidePDFGenerator()
    return _generator


def generate_guide_pdf(guide: dict, author_info: dict = None) -> bytes:
    """
    生成攻略PDF

    Args:
        guide: 攻略数据字典
        author_info: 作者信息

    Returns:
        PDF文件的二进制数据
    """
    generator = get_pdf_generator()
    return generator.generate_pdf(guide, author_info)
