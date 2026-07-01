"""
SQL WHERE clause builder with parameterized bindings.
Safe, flexible, and production-ready.
"""

import logging

SUPPORTED_OPERATORS = {'=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN'}

logger = logging.getLogger(__name__)


def build(conditions: list, allowed_columns=None) -> tuple:
    """
    Build parameterized WHERE conditions from a list of condition dicts.

    Each condition dict:
        {'column': str, 'operator': str, 'value': str}

    Returns:
        (conditions_str, params_dict)

    - conditions_str: SQL fragment (WITHOUT 'WHERE')
    - params_dict: bound parameters for safe execution
    """

    if not conditions:
        return ("", {})

    clauses = []
    params = {}
    param_index = 0

    for cond in conditions:
        column = str(cond.get('column', '')).strip()
        operator = str(cond.get('operator', '')).strip().upper()
        value = cond.get('value', '')

        #  Validate column exists in allowed list
        if allowed_columns is not None and column not in allowed_columns:
            logger.warning(f"[query_builder] Column '{column}' not allowed — skipped.")
            continue

        #  Basic column name safety
        if not column.isidentifier():
            logger.warning(f"[query_builder] Invalid column name '{column}' — skipped.")
            continue

        #  Validate operator
        if operator not in SUPPORTED_OPERATORS:
            logger.warning(f"[query_builder] Operator '{operator}' not supported — skipped.")
            continue

        #  Handle IN operator
        if operator == 'IN':
            items = [v.strip() for v in str(value).split(',') if v.strip()]

            #  Prevent empty IN clause
            if not items:
                logger.warning(f"[query_builder] Empty IN values for column '{column}' — skipped.")
                continue

            placeholders = []

            for i, item in enumerate(items):
                key = f"p{param_index}_{i}"
                params[key] = _coerce(item)
                placeholders.append(f":{key}")

            clause = f"{column} IN ({', '.join(placeholders)})"
            clauses.append(clause)

        #  All other operators
        else:
            key = f"p{param_index}"
            params[key] = _coerce(value)
            clauses.append(f"{column} {operator} :{key}")

        param_index += 1

    if not clauses:
        return ("", {})

    return (' AND '.join(clauses), params)


def _coerce(value: str):
    """
    Try to cast string to int or float; fallback to string.
    Cleans whitespace to avoid subtle bugs.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        pass

    try:
        return float(value)
    except (ValueError, TypeError):
        pass

    return str(value).strip()











# """SQL WHERE clause builder with parameterized bindings."""

# import logging

# SUPPORTED_OPERATORS = {'=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN'}

# logger = logging.getLogger(__name__)


# def build(conditions: list, allowed_columns=None) -> tuple:
#     """Build parameterized WHERE conditions from a list of condition dicts.

#     Each dict: {'column': str, 'operator': str, 'value': str}
#     Returns (conditions_str, params_dict) where conditions_str does NOT include
#     the 'WHERE' keyword — the caller appends it.
#     Returns ("", {}) for empty / all-skipped conditions.
#     """
#     if not conditions:
#         return ("", {})

#     clauses = []
#     params = {}
#     param_index = 0

#     for cond in conditions:
#         column = cond.get('column', '').strip()
#         operator = cond.get('operator', '').strip().upper()
#         value = cond.get('value', '')

#         # Validate column against whitelist
#         if allowed_columns is not None and column not in allowed_columns:
#             logger.warning(f"[query_builder] Column '{column}' not in allowed_columns — skipped.")
#             continue

#         # Validate operator
#         if operator not in SUPPORTED_OPERATORS:
#             logger.warning(f"[query_builder] Operator '{operator}' not supported — skipped.")
#             continue

#         if operator == 'IN':
#             # Split comma-separated value string into a list
#             items = [v.strip() for v in str(value).split(',') if v.strip()]
#             placeholders = []
#             for i, item in enumerate(items):
#                 key = f"p{param_index}_{i}"
#                 params[key] = _coerce(item)
#                 placeholders.append(f":{key}")
#             clause = f"{column} IN ({', '.join(placeholders)})"
#             clauses.append(clause)
#         else:
#             key = f"p{param_index}"
#             params[key] = _coerce(value)
#             clauses.append(f"{column} {operator} :{key}")

#         param_index += 1

#     if not clauses:
#         return ("", {})

#     return (' AND '.join(clauses), params)


# def _coerce(value: str):
#     """Try to cast string to int or float; fall back to string."""
#     try:
#         return int(value)
#     except (ValueError, TypeError):
#         pass
#     try:
#         return float(value)
#     except (ValueError, TypeError):
#         pass
#     return value
