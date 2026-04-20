from app.performance.mappers import employee_lookup, grade_from_score, hydrate_performance_record, normalize_text


def filter_rows(
    rows: list[dict],
    keyword: str = '',
    department: str = '',
    position: str = '',
    cycle_type: str = '',
    assessment_year: int | None = None,
    assessment_month: int | None = None,
    status: str = '',
) -> list[dict]:
    text = normalize_text(keyword).lower()
    result = []
    for row in rows:
        if text and text not in str(row.get('employeeNo', '')).lower() and text not in str(row.get('name', '')).lower():
            continue
        if department and row.get('department') != department:
            continue
        if position and row.get('position') != position:
            continue
        if cycle_type and row.get('cycleType') != cycle_type:
            continue
        if assessment_year is not None and row.get('assessmentYear') != assessment_year:
            continue
        if assessment_month is not None and row.get('assessmentMonth') != assessment_month:
            continue
        if status and row.get('status') != status:
            continue
        result.append(row)
    return result


def performance_history(repository, employee_no: str, current_id: str | None = None) -> list[dict]:
    employee_map = employee_lookup(repository)
    rows = [hydrate_performance_record(item, employee_map) for item in repository.list('performance')]
    history = [row for row in rows if row.get('employeeNo') == employee_no and row.get('id') != current_id]
    history.sort(key=lambda item: (item.get('assessmentYear', 0), item.get('assessmentMonth') or 0), reverse=True)
    return history[:6]


def build_report_snapshot(rows: list[dict]) -> dict:
    scores = [float(item.get('totalScore') or item.get('score') or 0) for item in rows]
    average_score = round(sum(scores) / len(scores), 2) if scores else 0
    pass_count = len([score for score in scores if score >= 70])
    distribution = {grade: 0 for grade in ['S', 'A', 'B', 'C', 'D']}
    department_summary: dict[str, dict] = {}
    for row in rows:
        grade = normalize_text(row.get('grade')) or grade_from_score(float(row.get('totalScore') or row.get('score') or 0))
        if grade in distribution:
            distribution[grade] += 1
        dept = normalize_text(row.get('department')) or '未分配部门'
        bucket = department_summary.setdefault(dept, {'department': dept, 'count': 0, 'totalScore': 0.0, 'employees': []})
        score = float(row.get('totalScore') or row.get('score') or 0)
        bucket['count'] += 1
        bucket['totalScore'] += score
        bucket['employees'].append({'name': row.get('name', ''), 'score': round(score, 2), 'grade': grade, 'position': row.get('position', '')})
    department_comparison = []
    for item in department_summary.values():
        avg = round(item['totalScore'] / item['count'], 2) if item['count'] else 0
        department_comparison.append({'department': item['department'], 'count': item['count'], 'averageScore': avg})
    department_comparison.sort(key=lambda item: item['averageScore'], reverse=True)
    sorted_rows = sorted(rows, key=lambda item: float(item.get('totalScore') or item.get('score') or 0), reverse=True)
    excellent_cases = [
        {
            'name': item.get('name', ''),
            'department': item.get('department', ''),
            'score': round(float(item.get('totalScore') or item.get('score') or 0), 2),
            'grade': item.get('grade', ''),
        }
        for item in sorted_rows[:3]
    ]
    improvement_cases = [
        {
            'name': item.get('name', ''),
            'department': item.get('department', ''),
            'score': round(float(item.get('totalScore') or item.get('score') or 0), 2),
            'grade': item.get('grade', ''),
        }
        for item in sorted(rows, key=lambda item: float(item.get('totalScore') or item.get('score') or 0))[:3]
    ]
    return {
        'recordCount': len(rows),
        'averageScore': average_score,
        'passRate': round((pass_count / len(rows) * 100), 2) if rows else 0,
        'distribution': distribution,
        'departmentComparison': department_comparison,
        'excellentCases': excellent_cases,
        'improvementCases': improvement_cases,
    }
