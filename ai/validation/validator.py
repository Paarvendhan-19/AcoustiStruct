"""Deterministic validation engine — validates extracted fields against schema rules.

This does NOT depend on LLMs. It uses the form schema to enforce constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional


@dataclass
class ValidationError:
    field_key: str
    error_type: str  # required | invalid_type | invalid_range | invalid_enum | invalid_format
    message: str
    current_value: Any = None


@dataclass
class ValidationResult:
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_field(
    field_key: str,
    value: Any,
    field_schema: dict,
    is_submission: bool = False,
) -> list[ValidationError]:
    """Validate a single field value against its schema definition."""
    errors = []
    field_type = field_schema.get("field_type", "string")
    required = field_schema.get("required", False)
    min_val = field_schema.get("min_value")
    max_val = field_schema.get("max_value")
    enum_values = field_schema.get("enum_values")

    # Required check (only enforced on submission)
    if required and is_submission and (value is None or value == "" or value == "null"):
        errors.append(ValidationError(
            field_key=field_key,
            error_type="required",
            message=f"{field_schema.get('label', field_key)} is required",
            current_value=value,
        ))
        return errors

    if value is None or value == "" or value == "null":
        return errors  # Not required, null is fine

    # Type validation
    if field_type in ("integer", "float"):
        try:
            numeric_val = float(value)
            if field_type == "integer" and not float(value).is_integer():
                errors.append(ValidationError(
                    field_key=field_key,
                    error_type="invalid_type",
                    message=f"{field_schema.get('label', field_key)} must be a whole number",
                    current_value=value,
                ))
            # Range validation
            if min_val is not None and numeric_val < min_val:
                errors.append(ValidationError(
                    field_key=field_key,
                    error_type="invalid_range",
                    message=f"{field_schema.get('label', field_key)} must be at least {min_val}",
                    current_value=value,
                ))
            if max_val is not None and numeric_val > max_val:
                errors.append(ValidationError(
                    field_key=field_key,
                    error_type="invalid_range",
                    message=f"{field_schema.get('label', field_key)} must be at most {max_val}",
                    current_value=value,
                ))
        except (ValueError, TypeError):
            errors.append(ValidationError(
                field_key=field_key,
                error_type="invalid_type",
                message=f"{field_schema.get('label', field_key)} must be a number",
                current_value=value,
            ))

    elif field_type == "boolean":
        if str(value).lower() not in ("true", "false", "1", "0", "yes", "no"):
            errors.append(ValidationError(
                field_key=field_key,
                error_type="invalid_type",
                message=f"{field_schema.get('label', field_key)} must be true or false",
                current_value=value,
            ))

    elif field_type == "date":
        if isinstance(value, str):
            try:
                date.fromisoformat(value)
            except ValueError:
                errors.append(ValidationError(
                    field_key=field_key,
                    error_type="invalid_format",
                    message=f"{field_schema.get('label', field_key)} must be a valid date (YYYY-MM-DD)",
                    current_value=value,
                ))

    elif field_type == "enum":
        if enum_values and str(value) not in [str(v) for v in enum_values]:
            errors.append(ValidationError(
                field_key=field_key,
                error_type="invalid_enum",
                message=f"{field_schema.get('label', field_key)} must be one of: {', '.join(str(v) for v in enum_values)}",
                current_value=value,
            ))

    elif field_type == "multiselect":
        if enum_values and isinstance(value, (list, str)):
            vals = value if isinstance(value, list) else [v.strip() for v in str(value).split(",")]
            invalid = [v for v in vals if v not in [str(ev) for ev in enum_values]]
            if invalid:
                errors.append(ValidationError(
                    field_key=field_key,
                    error_type="invalid_enum",
                    message=f"Invalid values for {field_schema.get('label', field_key)}: {', '.join(invalid)}",
                    current_value=value,
                ))

    return errors


def validate_extraction(
    fields: dict[str, Any],
    schema: list[dict],
    is_submission: bool = False,
) -> ValidationResult:
    """Validate all extracted fields against the form schema."""
    all_errors = []
    warnings = []

    schema_map = {f.get("field_key", f.get("id", "")): f for f in schema}

    for field_key, field_def in schema_map.items():
        value = fields.get(field_key)
        errors = validate_field(field_key, value, field_def, is_submission)
        all_errors.extend(errors)

    # Check for unknown fields (not in schema)
    for field_key in fields:
        if field_key not in schema_map:
            warnings.append(f"Field '{field_key}' is not defined in the schema and will be ignored")

    return ValidationResult(
        valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=warnings,
    )
