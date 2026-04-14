from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


LEAVE_RULES = {
    '病假': {'annual_limit': 30, 'pay_rate': 0.8, 'approval_chain': ['manager', 'hr']},
    '事假': {'annual_limit': 15, 'pay_rate': 0.0, 'approval_chain': ['manager', 'hr']},
    '丧假': {'annual_limit': 5, 'pay_rate': 1.0, 'approval_chain': ['manager', 'hr']},
    '年假': {'annual_limit': 10, 'pay_rate': 1.0, 'approval_chain': ['manager']},
    '婚假': {'annual_limit': 3, 'pay_rate': 1.0, 'approval_chain': ['manager', 'hr']},
    '产假': {'annual_limit': 128, 'pay_rate': 1.0, 'approval_chain': ['manager', 'hr', 'boss']},
    '调休': {'annual_limit': 30, 'pay_rate': 1.0, 'approval_chain': ['manager']},
}

PERFORMANCE_RULES = {
    'A': {'min_score': 90, 'multiplier': 1.3},
    'B': {'min_score': 80, 'multiplier': 1.0},
    'C': {'min_score': 70, 'multiplier': 0.8},
    'D': {'min_score': 0, 'multiplier': 0.5},
}


@dataclass
class AttendanceJudgement:
    status: str
    late_minutes: int = 0
    early_minutes: int = 0
    work_hours: float = 0.0


class RuleEngine:
    work_start = '09:00'
    work_end = '18:00'
    late_threshold = 5
    early_threshold = 5
    absent_threshold_hours = 4

    @staticmethod
    def parse_time(value: str) -> datetime:
        return datetime.strptime(value, '%H:%M')

    def validate_leave(self, leave_type: str, days: float) -> dict[str, Any]:
        rule = LEAVE_RULES.get(leave_type)
        if not rule:
            return {'valid': False, 'reason': '不支持的请假类型'}
        if days > rule['annual_limit']:
            return {'valid': False, 'reason': f'{leave_type}超出年度上限'}
        return {'valid': True, 'rule': rule}

    def evaluate_attendance(self, check_in: str | None, check_out: str | None) -> AttendanceJudgement:
        if not check_in or not check_out:
            return AttendanceJudgement(status='缺卡')

        start = self.parse_time(self.work_start)
        end = self.parse_time(self.work_end)
        actual_in = self.parse_time(check_in)
        actual_out = self.parse_time(check_out)
        late_minutes = max(0, int((actual_in - start).total_seconds() // 60))
        early_minutes = max(0, int((end - actual_out).total_seconds() // 60))
        work_hours = round((actual_out - actual_in).total_seconds() / 3600, 2)

        if work_hours < self.absent_threshold_hours:
            return AttendanceJudgement(status='旷工', late_minutes=late_minutes, early_minutes=early_minutes, work_hours=work_hours)
        if late_minutes >= self.late_threshold and early_minutes >= self.early_threshold:
            return AttendanceJudgement(status='迟到早退', late_minutes=late_minutes, early_minutes=early_minutes, work_hours=work_hours)
        if late_minutes >= self.late_threshold:
            return AttendanceJudgement(status='迟到', late_minutes=late_minutes, work_hours=work_hours)
        if early_minutes >= self.early_threshold:
            return AttendanceJudgement(status='早退', early_minutes=early_minutes, work_hours=work_hours)
        return AttendanceJudgement(status='正常', work_hours=work_hours)

    def get_performance_grade(self, score: float) -> str:
        for grade, rule in PERFORMANCE_RULES.items():
            if score >= rule['min_score']:
                return grade
        return 'D'

    def validate_performance_distribution(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        counts = {key: 0 for key in PERFORMANCE_RULES}
        for item in records:
            grade = item.get('grade') or self.get_performance_grade(float(item.get('score', 0)))
            counts[grade] = counts.get(grade, 0) + 1
        total = max(len(records), 1)
        a_ratio = counts['A'] / total
        passed = a_ratio <= 0.3
        return {
            'distribution': counts,
            'passed': passed,
            'comment': 'A档占比超过30%，建议复核。' if not passed else '绩效分布合理。',
        }

    def calculate_salary(self, employee: dict[str, Any], attendance_records: list[dict[str, Any]], leave_records: list[dict[str, Any]], performance_record: dict[str, Any] | None) -> dict[str, Any]:
        basic = float(employee.get('salary_base', 0))
        subsidy = round(basic * 0.08, 2)
        score = float((performance_record or {}).get('score', 80))
        grade = (performance_record or {}).get('grade') or self.get_performance_grade(score)
        performance_base = float(employee.get('performance_base', 0))
        performance_coefficient = PERFORMANCE_RULES[grade]['multiplier']
        performance_pay = round(performance_base * performance_coefficient, 2)

        abnormal_days = len([item for item in attendance_records if item.get('status') in ['迟到', '早退', '缺卡', '旷工', '迟到早退']])
        attendance_deduction = round(abnormal_days * 50, 2)
        overtime_hours = round(sum(max(float(item.get('overtime_hours', item.get('overtimeHours', 0)) or 0), 0) for item in attendance_records), 2)
        hourly_rate = basic / 21.75 / 8 if basic else 0
        overtime_pay = round(hourly_rate * overtime_hours * 1.5, 2)

        leave_deduction = 0.0
        for leave in leave_records:
            leave_type = leave.get('leave_type', '事假')
            days = float(leave.get('days', 0))
            rule = LEAVE_RULES.get(leave_type, LEAVE_RULES['事假'])
            if rule['pay_rate'] < 1:
                leave_deduction += round((1 - rule['pay_rate']) * basic / 21.75 * days, 2)

        social_security_base = float(employee.get('social_security_base', 0) or 0)
        housing_fund_base = float(employee.get('housing_fund_base', 0) or 0)
        social_security_personal = round(social_security_base * 0.105, 2)
        housing_fund_personal = round(housing_fund_base * 0.07, 2)
        social_security_employer = round(social_security_base * 0.16, 2)
        housing_fund_employer = round(housing_fund_base * 0.07, 2)
        pre_tax_salary = round(basic + subsidy + performance_pay + overtime_pay - attendance_deduction - leave_deduction, 2)
        tax = self.calculate_tax(pre_tax_salary)
        actual = round(pre_tax_salary - social_security_personal - housing_fund_personal - tax, 2)
        return {
            'basic': basic,
            'subsidy': subsidy,
            'performance': performance_pay,
            'performance_coefficient': performance_coefficient,
            'overtime_hours': overtime_hours,
            'overtime_pay': overtime_pay,
            'attendance_deduction': attendance_deduction,
            'leave_deduction': round(leave_deduction, 2),
            'pre_tax_salary': pre_tax_salary,
            'social_security_personal': social_security_personal,
            'housing_fund_personal': housing_fund_personal,
            'social_security_employer': social_security_employer,
            'housing_fund_employer': housing_fund_employer,
            'tax': tax,
            'actual': actual,
            'grade': grade,
        }

    @staticmethod
    def calculate_tax(amount: float) -> float:
        taxable = max(amount - 5000, 0)
        if taxable <= 3000:
            return round(taxable * 0.03, 2)
        if taxable <= 12000:
            return round(taxable * 0.1 - 210, 2)
        return round(taxable * 0.2 - 1410, 2)
