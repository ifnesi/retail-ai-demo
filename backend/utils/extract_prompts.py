#!/usr/bin/env python3
"""
Extract system prompts and input context templates from Flink SQL files.
This ensures the frontend always displays the correct prompts without hardcoding.
"""
import re
import os
import json
from pathlib import Path

# SQL files containing the models
PROMPT_SQL_FILES = {
    "CART_RECOVERY": os.path.join("sql", "CART_ABANDONMENT_NUDGE.sql"),
    "STORE_PERSONALIZATION": os.path.join("sql", "STORE_PERSONALIZATION.sql"),
    "PARTNER_AD": os.path.join("sql", "PARTNER_AD_GENERATOR.sql"),
}

# SQL files containing the CONCAT templates for input context
# Key format: function name will be build{Key}Context
# e.g., "CartRecovery" -> buildCartRecoveryContext
CONTEXT_SQL_FILES = {
    "CartRecovery": os.path.join("sql", "RETAIL_DEMO_CART_RECOVERY_MESSAGES.sql"),
    "Store": os.path.join("sql", "RETAIL_DEMO_STORE_VISIT_CONTEXT.sql"),
    "PartnerAd": os.path.join("sql", "RETAIL_DEMO_PARTNER_BROWSE_ADS.sql"),
}


def extract_system_prompt(sql_content):
    """
    Extract the bedrock.system_prompt value from SQL content.
    Handles multi-line strings within single quotes.
    """
    # Pattern to match 'bedrock.system_prompt' = 'content'
    # Using DOTALL flag to match across multiple lines
    pattern = r"'bedrock\.system_prompt'\s*=\s*'([^']+)'"

    match = re.search(pattern, sql_content, re.DOTALL)
    if match:
        # Get the captured group and clean it up
        prompt = match.group(1)
        # Remove any extra whitespace/newlines
        prompt = " ".join(prompt.split())
        return prompt
    return None


def extract_concat_template(sql_content):
    """
    Extract the CONCAT statement from ML_PREDICT and convert to JavaScript template.
    Returns the JavaScript template string or None if not found.
    """
    # Find the CONCAT block within ML_PREDICT
    pattern = r"CONCAT\s*\((.*?)\)\s*\)\s*\)\s*AS"
    match = re.search(pattern, sql_content, re.DOTALL)

    if not match:
        return None

    concat_content = match.group(1).strip()

    # Split by commas, respecting nested parentheses and quoted strings
    parts = split_concat_args(concat_content)

    # Convert each part to JavaScript
    js_parts = list()
    for part in parts:
        js_part = convert_sql_to_js(part.strip())
        if js_part:
            js_parts.append(js_part)

    # Join all parts into a single template string
    return "".join(js_parts)


def split_concat_args(concat_content):
    """
    Split CONCAT arguments by comma, respecting nested parentheses and quotes.
    """
    parts = list()
    current = ""
    paren_depth = 0
    in_quotes = False

    for i, char in enumerate(concat_content):
        if char == "'" and (i == 0 or concat_content[i - 1] != "\\"):
            in_quotes = not in_quotes
            current += char
        elif not in_quotes:
            if char == "(":
                paren_depth += 1
                current += char
            elif char == ")":
                paren_depth -= 1
                current += char
            elif char == "," and paren_depth == 0:
                if current.strip():
                    parts.append(current.strip())
                current = ""
            else:
                current += char
        else:
            current += char

    if current.strip():
        parts.append(current.strip())

    return parts


def convert_sql_to_js(sql_part):
    """
    Convert a SQL expression to JavaScript template literal syntax.
    """
    sql_part = sql_part.strip()

    if not sql_part:
        return ""

    # String literal - remove quotes and return as-is for template
    if sql_part.startswith("'") and sql_part.endswith("'"):
        return sql_part[1:-1]

    # COALESCE(CAST(field AS STRING), 'default') - nested functions
    nested_coalesce_match = re.match(
        r"COALESCE\s*\(\s*CAST\s*\(\s*([a-z_]+\.[a-z_]+)\s+AS\s+STRING\s*\)\s*,\s*'([^']*)'\s*\)",
        sql_part,
        re.IGNORECASE,
    )
    if nested_coalesce_match:
        field = nested_coalesce_match.group(1)
        default = nested_coalesce_match.group(2)
        # Don't add default in convert_field_reference since COALESCE provides it
        js_field = convert_field_reference(field, add_default=False)
        return f"${{{js_field} || '{default}'}}"

    # COALESCE(field, 'default') - simple form
    coalesce_match = re.match(
        r"COALESCE\s*\(\s*([a-z_]+\.[a-z_]+)\s*,\s*'([^']*)'\s*\)",
        sql_part,
        re.IGNORECASE,
    )
    if coalesce_match:
        field = coalesce_match.group(1)
        default = coalesce_match.group(2)
        # Don't add default in convert_field_reference since COALESCE provides it
        js_field = convert_field_reference(field, add_default=False)
        return f"${{{js_field} || '{default}'}}"

    # CAST(field AS STRING) or CAST(expression AS STRING)
    cast_match = re.match(
        r"CAST\s*\(\s*([^)]+)\s+AS\s+STRING\s*\)", sql_part, re.IGNORECASE
    )
    if cast_match:
        inner_expr = cast_match.group(1).strip()
        # Check if inner expression is a field reference
        if re.match(r"^[a-z_]+\.[a-z_]+$", inner_expr, re.IGNORECASE):
            js_field = convert_field_reference(inner_expr)
            return f"${{{js_field}}}"
        else:
            # Complex expression - just convert field references
            js_expr = convert_field_reference(inner_expr)
            return f"${{{js_expr}}}"

    # DATE_FORMAT(...) - special handling for date formatting
    if sql_part.upper().startswith("DATE_FORMAT"):
        return "${visitTime}"

    # FROM_UNIXTIME - also date related
    if "FROM_UNIXTIME" in sql_part.upper():
        return "${visitTime}"

    # Plain field reference (a.field, p.field, s.field)
    if re.match(r"^[a-z_]+\.[a-z_]+$", sql_part, re.IGNORECASE):
        js_field = convert_field_reference(sql_part)
        return f"${{{js_field}}}"

    # If we can't parse it, return empty (skip it)
    return ""


def convert_field_reference(sql_field, add_default=True):
    """
    Convert SQL field reference to JavaScript data property access.
    Examples:
      a.username -> data.username || 'N/A'
      p.cart_value -> data.cart_value?.toFixed(2) || '0.00'
      s.items_count -> data.items_count || 0

    Args:
        sql_field: The SQL field reference (e.g., 'a.username', 's.last_product_price')
        add_default: Whether to add a default value. Set to False when inside COALESCE.
    """
    # Remove table alias (a., p., s., etc.)
    if "." in sql_field:
        field_name = sql_field.split(".", 1)[1]
    else:
        field_name = sql_field

    # Special formatting for specific fields
    if field_name in ["cart_value", "last_product_price"]:
        if add_default:
            return f"data.{field_name}?.toFixed(2) || '0.00'"
        else:
            return f"data.{field_name}?.toFixed(2)"
    elif field_name == "items_count":
        if add_default:
            return f"data.{field_name} || 0"
        else:
            return f"data.{field_name}"
    else:
        if add_default:
            return f"data.{field_name} || 'N/A'"
        else:
            return f"data.{field_name}"


def generate_context_builders_js(context_templates):
    """
    Generate JavaScript file with context builder functions.
    Completely dynamic - loops through all templates and generates functions.
    """
    # Build header dynamically from SQL file names
    sql_files = [os.path.basename(path) for path in CONTEXT_SQL_FILES.values()]
    file_list = "\n// - ".join([""] + sql_files)

    js_code = f"""// Auto-generated from Flink SQL CONCAT templates
// DO NOT EDIT - Run backend/utils/extract_prompts.py to regenerate
//
// These functions are dynamically generated from:{file_list}

"""

    # Generate function for each template
    for func_name, template in context_templates.items():
        # Function name: build{FuncName}Context
        full_func_name = f"build{func_name}Context"

        # Check if template uses visitTime (for date formatting)
        if "${visitTime}" in template:
            js_code += f"""export const {full_func_name} = (data) => {{
  const visitTime = data.visit_time ? new Date(data.visit_time).toLocaleString('en-US', {{
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }}) : 'N/A';
  return `{template}`;
}};

"""
        else:
            js_code += f"""export const {full_func_name} = (data) => {{
  return `{template}`;
}};

"""

    return js_code


def main():
    script_dir = Path(__file__).parent
    prompts = dict()

    # Extract system prompts
    print("Extracting system prompts (Flink SQL CREATE MODEL)...")
    for key, sql_file in PROMPT_SQL_FILES.items():
        sql_path = script_dir / sql_file

        if not sql_path.exists():
            print(f"  Warning: SQL file not found: {sql_path}")
            continue

        with open(sql_path, "r") as f:
            sql_content = f.read()

        prompt = extract_system_prompt(sql_content)
        if prompt:
            prompts[key] = prompt
            print(f"  ✓ Extracted prompt from {sql_file}")
        else:
            print(f"  ✗ Could not extract prompt from {sql_file}")

    # Extract context templates from CONCAT statements
    print("\nExtracting input context templates (Flink SQL CREATE TABLE)...")
    context_templates = dict()
    for key, sql_file in CONTEXT_SQL_FILES.items():
        sql_path = script_dir / sql_file

        if not sql_path.exists():
            print(f"  Warning: SQL file not found: {sql_path}")
            continue

        with open(sql_path, "r") as f:
            sql_content = f.read()

        template = extract_concat_template(sql_content)
        if template:
            context_templates[key] = template
            print(f"  ✓ Extracted CONCAT template from {sql_file}")
        else:
            print(f"  ✗ Could not extract CONCAT template from {sql_file}")

    # Write system prompts to JSON file
    prompts_output_path = os.path.join(
        script_dir.parent.parent,
        "frontend",
        "src",
        "config",
        "system-prompts.json",
    )
    with open(prompts_output_path, "w") as f:
        json.dump(prompts, f, indent=2)

    print(f"\n✓ System prompts extracted to: {prompts_output_path}")
    print(f"  Found {len(prompts)} prompts")

    # Write context builders to JavaScript file
    if context_templates:
        js_code = generate_context_builders_js(context_templates)
        context_output_path = os.path.join(
            script_dir.parent.parent,
            "frontend",
            "src",
            "utils",
            "contextBuilders.js",
        )
        with open(context_output_path, "w") as f:
            f.write(js_code)

        print(f"\n✓ Context builders generated at: {context_output_path}")
        print(f"  Generated {len(context_templates)} builder functions")


if __name__ == "__main__":
    main()
