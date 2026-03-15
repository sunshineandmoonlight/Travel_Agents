"""
PDF生成服务 - 用于导出旅行攻略
"""

import os
import logging
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFGeneratorService:
    """PDF生成服务"""

    def __init__(self):
        self.output_dir = Path("exports/travel_guides")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_guide_pdf(
        self,
        guide_data: Dict,
        output_path: Optional[str] = None
    ) -> str:
        """
        生成旅行攻略PDF

        Args:
            guide_data: 攻略数据
            output_path: 输出文件路径，如不指定则自动生成

        Returns:
            PDF文件路径
        """
        try:
            # 使用报告服务中的PDF生成器
            from app.utils.pdf_generator import TravelGuidePDFGenerator

            generator = TravelGuidePDFGenerator()

            # 如果没有指定输出路径，自动生成
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                destination = guide_data.get('destination', 'unknown')
                safe_destination = self._sanitize_filename(destination)
                output_path = str(self.output_dir / f"{safe_destination}_攻略_{timestamp}.pdf")

            # 生成PDF
            generator.generate(
                guide_data=guide_data,
                output_path=output_path
            )

            logger.info(f"PDF生成成功: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"PDF生成失败: {e}")
            raise

    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除非法字符
        """
        # 移除或替换非法字符
        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in illegal_chars:
            filename = filename.replace(char, '_')

        # 限制长度
        if len(filename) > 50:
            filename = filename[:50]

        return filename.strip()

    def check_pdf_requirements(self) -> Dict[str, any]:
        """
        检查PDF生成依赖
        """
        requirements = {
            "reportlab": False,
            "weasyprint": False,
            "chinese_font": False
        }

        try:
            import reportlab
            requirements["reportlab"] = True
        except ImportError:
            pass

        try:
            import weasyprint
            requirements["weasyprint"] = True
        except ImportError:
            pass

        # 检查中文字体
        font_paths = [
            "C:/Windows/Fonts/simsun.ttc",  # Windows
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
            "/System/Library/Fonts/PingFang.ttc",  # macOS
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                requirements["chinese_font"] = True
                break

        return requirements


# 全局单例
_pdf_service = None


def get_pdf_service() -> PDFGeneratorService:
    """获取PDF服务单例"""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFGeneratorService()
    return _pdf_service
