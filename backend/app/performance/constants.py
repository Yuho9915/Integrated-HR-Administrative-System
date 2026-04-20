CYCLE_OPTIONS = ['月度', '季度', '年度']
STATUS_OPTIONS = ['待员工提交', '待经理审核', '经理退回修改', '待HR审核', 'HR退回修改', '已确认发布']
WEIGHTS = {'performance': 0.6, 'attitude': 0.2, 'ability': 0.2}
GRADE_CONFIG = {
    'S': {'min': 90, 'coef': 1.5},
    'A': {'min': 80, 'coef': 1.2},
    'B': {'min': 70, 'coef': 1.0},
    'C': {'min': 60, 'coef': 0.8},
    'D': {'min': 0, 'coef': 0.5},
}
IMPORT_HEADERS = {
    'employeeNo': ['工号'],
    'name': ['姓名'],
    'department': ['部门'],
    'position': ['岗位'],
    'cycleType': ['绩效周期'],
    'assessmentYear': ['考核年份'],
    'assessmentMonth': ['考核月份'],
    'performanceScore': ['业绩指标得分'],
    'attitudeScore': ['工作态度得分'],
    'abilityScore': ['能力表现得分'],
    'totalScore': ['综合总分'],
    'grade': ['绩效等级'],
    'coefficient': ['绩效系数'],
    'selfReview': ['员工自评'],
    'managerReview': ['上级评价'],
    'monthlyWorkContent': ['月度工作内容'],
    'achievementHighlights': ['突出业绩'],
    'status': ['考核状态'],
    'remark': ['备注'],
}
