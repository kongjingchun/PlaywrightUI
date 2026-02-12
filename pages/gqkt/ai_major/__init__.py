# ========================================
# AI 专业管理模块
# ========================================

from .major_manage_page import MajorManagePage
from .major_portal_manage_page import MajorPortalManagePage
from .major_ai_model.major_graph_model import MajorGraphOverviewPage, MajorCourseGroupGraphPage
from .training_program_manage_page import TrainingProgramManagePage

__all__ = ['MajorManagePage', 'MajorPortalManagePage', 'MajorGraphOverviewPage', 'MajorCourseGroupGraphPage', 'TrainingProgramManagePage']
