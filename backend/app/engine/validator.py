"""
Validator Layer - Result Verification and Compliance Checking

Provides result validation, compliance checking, and output sanitization
for the LangGraph agent orchestration engine.
"""

import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ValidationStatus(str, Enum):
    """Status of validation result."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class ComplianceLevel(str, Enum):
    """Compliance severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""

    code: str
    message: str
    level: ComplianceLevel
    field: str | None = None
    suggestion: str | None = None
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validation process."""

    status: ValidationStatus
    issues: list[ValidationIssue] = dataclasses.field(default_factory=list)
    validated_at: datetime = dataclasses.field(default_factory=datetime.now)
    validator_name: str = ""
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed without critical/high issues."""
        critical_levels = {ComplianceLevel.CRITICAL, ComplianceLevel.HIGH}
        return not any(issue.level in critical_levels for issue in self.issues)

    def add_issue(
        self,
        code: str,
        message: str,
        level: ComplianceLevel = ComplianceLevel.MEDIUM,
        **kwargs: Any,
    ) -> None:
        """Add a validation issue."""
        self.issues.append(
            ValidationIssue(code=code, message=message, level=level, **kwargs)
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "status": self.status.value,
            "is_valid": self.is_valid,
            "issues": [
                {
                    "code": i.code,
                    "message": i.message,
                    "level": i.level.value,
                    "field": i.field,
                    "suggestion": i.suggestion,
                }
                for i in self.issues
            ],
            "validated_at": self.validated_at.isoformat(),
            "validator_name": self.validator_name,
        }


class BaseValidator(ABC):
    """Abstract base class for validators."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Validator name for identification."""
        ...

    @abstractmethod
    async def validate(
        self,
        data: Any,
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate the given data."""
        ...


class ResultValidator(BaseValidator):
    """
    Validates execution results for correctness and completeness.

    Checks for required fields, data types, and format compliance.
    """

    @property
    def name(self) -> str:
        return "result_validator"

    def __init__(self) -> None:
        self._required_fields: list[str] = ["output", "agent"]
        self._type_rules: dict[str, type] = {}

    def add_required_field(self, field: str, expected_type: type | None = None) -> None:
        """Add a required field with optional type constraint."""
        self._required_fields.append(field)
        if expected_type:
            self._type_rules[field] = expected_type

    async def validate(
        self,
        data: Any,
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Validate execution result."""
        result = ValidationResult(
            status=ValidationStatus.PASSED,
            validator_name=self.name,
        )

        if not isinstance(data, dict):
            result.status = ValidationStatus.FAILED
            result.add_issue(
                code="INVALID_TYPE",
                message="Result must be a dictionary",
                level=ComplianceLevel.CRITICAL,
            )
            return result

        # Check required fields
        for field_name in self._required_fields:
            if field_name not in data:
                result.add_issue(
                    code="MISSING_FIELD",
                    message=f"Required field '{field_name}' is missing",
                    level=ComplianceLevel.HIGH,
                    field=field_name,
                )

        # Check type constraints
        for field_name, expected_type in self._type_rules.items():
            if field_name in data and not isinstance(data[field_name], expected_type):
                result.add_issue(
                    code="TYPE_MISMATCH",
                    message=f"Field '{field_name}' should be {expected_type.__name__}",
                    level=ComplianceLevel.MEDIUM,
                    field=field_name,
                )

        # Update status based on issues
        if any(i.level == ComplianceLevel.CRITICAL for i in result.issues):
            result.status = ValidationStatus.FAILED
        elif any(i.level == ComplianceLevel.HIGH for i in result.issues):
            result.status = ValidationStatus.FAILED
        elif result.issues:
            result.status = ValidationStatus.WARNING

        return result


class ComplianceChecker(BaseValidator):
    """
    Checks results against compliance rules and policies.

    Enforces data governance, security, and business rules.
    """

    @property
    def name(self) -> str:
        return "compliance_checker"

    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []
        self._sensitive_patterns: list[str] = [
            r"\b\d{15,19}\b",  # Credit card numbers
            r"\b\d{18}[\dXx]\b",  # Chinese ID numbers
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        ]

    def add_rule(
        self,
        name: str,
        check_fn: Any,
        level: ComplianceLevel = ComplianceLevel.MEDIUM,
    ) -> None:
        """Add a compliance rule."""
        self._rules.append({
            "name": name,
            "check": check_fn,
            "level": level,
        })

    async def validate(
        self,
        data: Any,
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Check compliance against registered rules."""
        result = ValidationResult(
            status=ValidationStatus.PASSED,
            validator_name=self.name,
        )

        # Check for sensitive data exposure
        await self._check_sensitive_data(data, result)

        # Run custom rules
        for rule in self._rules:
            try:
                check_fn = rule["check"]
                if not check_fn(data, context):
                    result.add_issue(
                        code=f"RULE_{rule['name'].upper()}",
                        message=f"Compliance rule '{rule['name']}' violated",
                        level=rule["level"],
                    )
            except Exception as e:
                result.add_issue(
                    code="RULE_ERROR",
                    message=f"Error checking rule '{rule['name']}': {e}",
                    level=ComplianceLevel.INFO,
                )

        # Update status
        if any(i.level in {ComplianceLevel.CRITICAL, ComplianceLevel.HIGH}
               for i in result.issues):
            result.status = ValidationStatus.FAILED
        elif result.issues:
            result.status = ValidationStatus.WARNING

        return result

    async def _check_sensitive_data(
        self,
        data: Any,
        result: ValidationResult,
    ) -> None:
        """Check for potential sensitive data exposure."""
        import re

        def check_value(value: Any, path: str = "") -> None:
            if isinstance(value, str):
                for pattern in self._sensitive_patterns:
                    if re.search(pattern, value):
                        result.add_issue(
                            code="SENSITIVE_DATA",
                            message=f"Potential sensitive data detected at {path}",
                            level=ComplianceLevel.HIGH,
                            field=path,
                            suggestion="Mask or remove sensitive data before output",
                        )
                        break
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_value(v, f"{path}.{k}" if path else k)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    check_value(item, f"{path}[{i}]")

        check_value(data)


class OutputSanitizer:
    """
    Sanitizes output data for safe consumption.

    Masks sensitive data, validates format, and cleans output.
    """

    def __init__(self) -> None:
        self._mask_patterns: list[tuple[str, str]] = [
            (r"\b(\d{4})\d{8,12}(\d{4})\b", r"\1****\2"),  # Card numbers
            (r"\b(\d{6})\d{8}([\dXx]{4})\b", r"\1********\2"),  # ID numbers
        ]

    def add_mask_pattern(self, pattern: str, replacement: str) -> None:
        """Add a pattern for data masking."""
        self._mask_patterns.append((pattern, replacement))

    def sanitize(self, data: Any) -> Any:
        """Sanitize data by applying mask patterns."""
        import re

        def sanitize_value(value: Any) -> Any:
            if isinstance(value, str):
                result = value
                for pattern, replacement in self._mask_patterns:
                    result = re.sub(pattern, replacement, result)
                return result
            elif isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_value(item) for item in value]
            else:
                return value

        return sanitize_value(data)


class Validator:
    """
    Main validator component for the LangGraph engine.

    Orchestrates result validation, compliance checking, and output sanitization.
    Acts as a LangGraph node for the validation phase.
    """

    def __init__(
        self,
        result_validator: ResultValidator | None = None,
        compliance_checker: ComplianceChecker | None = None,
        sanitizer: OutputSanitizer | None = None,
    ) -> None:
        self.result_validator = result_validator or ResultValidator()
        self.compliance_checker = compliance_checker or ComplianceChecker()
        self.sanitizer = sanitizer or OutputSanitizer()

    async def validate(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute full validation pipeline:
        1. Validate result structure
        2. Check compliance
        3. Sanitize output
        """
        execution_result = state.get("execution_result", {})

        # Step 1: Result validation
        result_validation = await self.result_validator.validate(
            execution_result, state
        )

        # Step 2: Compliance check
        compliance_result = await self.compliance_checker.validate(
            execution_result, state
        )

        # Step 3: Sanitize output
        sanitized_output = self.sanitizer.sanitize(execution_result)

        # Aggregate validation results
        all_passed = (
            result_validation.is_valid and compliance_result.is_valid
        )
        all_issues = result_validation.issues + compliance_result.issues

        return {
            **state,
            "validated_output": sanitized_output,
            "validation_status": "passed" if all_passed else "failed",
            "validation_issues": [i.to_dict() if hasattr(i, 'to_dict') else {
                "code": i.code,
                "message": i.message,
                "level": i.level.value,
            } for i in all_issues],
        }

    async def __call__(
        self, state: dict[str, Any]
    ) -> dict[str, Any]:
        """LangGraph node interface for validation."""
        return await self.validate(state)


# Default validator instance
default_validator = Validator()
