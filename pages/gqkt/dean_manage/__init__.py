# ========================================
# 教务管理模块
# ========================================

from .user_manage_page import UserManagePage
from .role_manage_page import RoleManagePage
from .semester_manage_page import SemesterManagePage
from .admin_class_manage_page import AdminClassManagePage
from .course_manage_page import CourseManagePage

__all__ = ['UserManagePage', 'RoleManagePage', 'SemesterManagePage', 'AdminClassManagePage', 'CourseManagePage']
