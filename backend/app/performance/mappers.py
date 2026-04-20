from datetime import datetime

from app.performance.constants import CYCLE_OPTIONS, GRADE_CONFIG, WEIGHTS
from app.services.seed import DEFAULT_DATA


def normalize_text(value) -> str:
    if value is None:
        return ''
    return str(value).strip()


def to_number(value, default: float = 0.0) -> float:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return default


def to_int(value, default: int | None = None) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def grade_from_score(score: float) -> str:
    for name, cfg in GRADE_CONFIG.items():
        if score >= cfg['min']:
            return name
    return 'D'


def coefficient_from_grade(grade: str) -> float:
    return float(GRADE_CONFIG.get(grade, GRADE_CONFIG['D'])['coef'])


def calculate_total_score(record: dict) -> float:
    return round(
        to_number(record.get('performanceScore')) * WEIGHTS['performance']
        + to_number(record.get('attitudeScore')) * WEIGHTS['attitude']
        + to_number(record.get('abilityScore')) * WEIGHTS['ability'],
        2,
    )


def build_period(cycle_type: str, year: int, month: int | None) -> str:
    if cycle_type == '月度' and month:
        return f'{year}-{str(month).zfill(2)}'
    if cycle_type == '季度' and month:
        return f'{year}年Q{month}'
    return str(year)


def employee_lookup(repository) -> dict[str, dict]:
    employees = repository.list('employees')
    return {
        normalize_text(item.get('employee_no') or item.get('employeeNo')): item
        for item in employees
        if normalize_text(item.get('employee_no') or item.get('employeeNo'))
    }


def actor_profile(repository, user: dict, employee_map: dict[str, dict]) -> dict:
    matched = next((item for item in repository.list('users') if item.get('username') == user['username']), None)
    if not matched:
        matched = next((item for item in DEFAULT_DATA['users'] if item.get('username') == user['username']), {})
    employee_no = normalize_text(matched.get('employeeNo'))
    employee = employee_map.get(employee_no, {})
    return {
        'employeeNo': employee_no,
        'department': employee.get('department') or matched.get('department', ''),
    }


def hydrate_performance_record(item: dict, employee_map: dict[str, dict]) -> dict:
    employee_no = normalize_text(item.get('employeeNo') or item.get('employee_no'))
    employee = employee_map.get(employee_no, {})
    cycle_type = normalize_text(item.get('cycleType') or item.get('periodType')) or '月度'
    assessment_year = to_int(item.get('assessmentYear') or item.get('year'), datetime.utcnow().year) or datetime.utcnow().year
    assessment_month = to_int(item.get('assessmentMonth') or item.get('month'))
    total_score = to_number(item.get('totalScore') or item.get('score'))
    if total_score == 0 and any([item.get('performanceScore'), item.get('attitudeScore'), item.get('abilityScore')]):
        total_score = calculate_total_score(item)
    grade = normalize_text(item.get('grade')) or grade_from_score(total_score)
    return {
        **item,
        'employeeNo': employee_no or item.get('employeeNo', ''),
        'name': item.get('name') or employee.get('name', ''),
        'department': item.get('department') or employee.get('department', ''),
        'position': item.get('position') or employee.get('position', ''),
        'cycleType': cycle_type if cycle_type in CYCLE_OPTIONS else '月度',
        'assessmentYear': assessment_year,
        'assessmentMonth': assessment_month,
        'performanceScore': to_number(item.get('performanceScore')),
        'attitudeScore': to_number(item.get('attitudeScore')),
        'abilityScore': to_number(item.get('abilityScore')),
        'totalScore': total_score,
        'score': total_score,
        'grade': grade if grade in GRADE_CONFIG else grade_from_score(total_score),
        'coefficient': to_number(item.get('coefficient'), coefficient_from_grade(grade)),
        'selfReview': normalize_text(item.get('selfReview')),
        'monthlyWorkContent': normalize_text(item.get('monthlyWorkContent')),
        'achievementHighlights': normalize_text(item.get('achievementHighlights')),
        'managerReview': normalize_text(item.get('managerReview')),
        'status': normalize_text(item.get('status')) or '待员工提交',
        'reviewer': normalize_text(item.get('reviewer')),
        'remark': normalize_text(item.get('remark')),
        'period': build_period(cycle_type, assessment_year, assessment_month),
    }
