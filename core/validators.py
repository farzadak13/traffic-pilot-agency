import re
import logging

logger = logging.getLogger(__name__)


def extract_budget_numbers(markdown_text: str) -> dict:
    """
    اعداد بودجه را از جدول مارک‌داون استخراج می‌کند.
    """
    result = {
        "row_budgets": [],
        "influencer_budget": None,
        "declared_total": None,
        "errors": []
    }

    lines = markdown_text.split("\n")

    in_table_1 = False
    in_table_3 = False
    header_passed_1 = False
    header_passed_3 = False

    for line in lines:
        line = line.strip()

        # تشخیص شروع جدول ۱
        if "جدول 1" in line or "تقویم فید" in line:
            in_table_1 = True
            in_table_3 = False
            header_passed_1 = False
            continue

        # تشخیص شروع جدول ۳
        if "جدول 3" in line or "اینفلوئنسر" in line:
            in_table_3 = True
            in_table_1 = False
            header_passed_3 = False
            continue

        # تشخیص شروع جدول ۲ یا ۴ (پایان جدول ۱)
        if in_table_1 and ("جدول 2" in line or "جدول 4" in line or "استوری" in line or "بحران" in line):
            in_table_1 = False

        # تشخیص شروع جدول ۴ (پایان جدول ۳)
        if in_table_3 and ("جدول 4" in line or "بحران" in line):
            in_table_3 = False

        # پردازش ردیف‌های جدول ۱
        if in_table_1 and line.startswith("|"):
            # رد کردن هدر و separator
            if "روز" in line or "---" in line or "فرمت" in line:
                header_passed_1 = True
                continue

            if not header_passed_1:
                continue

            # ردیف جمع کل
            if "جمع" in line or "total" in line.lower():
                numbers = re.findall(r'[\d,،]+', line)
                for n in numbers:
                    clean = n.replace(",", "").replace("،", "")
                    if clean.isdigit() and len(clean) >= 5:
                        result["declared_total"] = int(clean)
                        break
                continue

            # استخراج بودجه از ستون هشتم (ایندکس ۷)
            cells = [c.strip() for c in line.split("|")]
            cells = [c for c in cells if c != ""]

            if len(cells) >= 8:
                budget_cell = cells[7]
                numbers = re.findall(r'[\d,،]+', budget_cell)
                for n in numbers:
                    clean = n.replace(",", "").replace("،", "")
                    if clean.isdigit() and len(clean) >= 3:
                        result["row_budgets"].append(int(clean))
                        break
                else:
                    # سلول خالی یا بدون عدد
                    result["row_budgets"].append(None)

        # پردازش ردیف‌های جدول ۳
        if in_table_3 and line.startswith("|"):
            if "فالوور" in line or "---" in line or "بودجه" in line:
                header_passed_3 = True
                continue

            if not header_passed_3:
                continue

            cells = [c.strip() for c in line.split("|")]
            cells = [c for c in cells if c != ""]

            if len(cells) >= 2:
                budget_cell = cells[1]
                numbers = re.findall(r'[\d,،]+', budget_cell)
                for n in numbers:
                    clean = n.replace(",", "").replace("،", "")
                    if clean.isdigit() and len(clean) >= 5:
                        result["influencer_budget"] = int(clean)
                        break

    return result


def validate_budget(
    markdown_text: str,
    total_budget: int
) -> dict:
    """
    بودجه‌های خروجی مدل را اعتبارسنجی می‌کند.

    Returns:
        dict با کلیدهای:
        - is_valid: bool
        - warnings: list[str]
        - errors: list[str]
        - summary: dict
    """
    result = {
        "is_valid": True,
        "warnings": [],
        "errors": [],
        "summary": {}
    }

    extracted = extract_budget_numbers(markdown_text)
    row_budgets = extracted["row_budgets"]
    influencer_budget = extracted["influencer_budget"]
    declared_total = extracted["declared_total"]

    # ---- بررسی تعداد ردیف‌ها ----
    if len(row_budgets) < 7:
        result["errors"].append(
            f"فقط {len(row_budgets)} ردیف از ۷ ردیف بودجه دارند."
        )
        result["is_valid"] = False

    # ---- بررسی سلول‌های خالی ----
    empty_rows = [
        i + 1 for i, b in enumerate(row_budgets) if b is None
    ]
    if empty_rows:
        result["errors"].append(
            f"ردیف‌های {empty_rows} بودجه ندارند."
        )
        result["is_valid"] = False

    # ---- محاسبه جمع بودجه بوست ----
    valid_budgets = [b for b in row_budgets if b is not None]
    actual_boost_total = sum(valid_budgets)
    expected_boost = int(total_budget * 0.70)
    expected_influencer = int(total_budget * 0.30)

    result["summary"] = {
        "total_budget": total_budget,
        "expected_boost": expected_boost,
        "actual_boost": actual_boost_total,
        "expected_influencer": expected_influencer,
        "actual_influencer": influencer_budget,
        "declared_total": declared_total,
        "row_budgets": row_budgets,
        "row_count": len(row_budgets)
    }

    # ---- بررسی جمع بوست ----
    tolerance = int(expected_boost * 0.05)  # ۵٪ خطای مجاز

    if abs(actual_boost_total - expected_boost) > tolerance:
        diff = actual_boost_total - expected_boost
        direction = "بیشتر" if diff > 0 else "کمتر"
        result["warnings"].append(
            f"جمع بودجه بوست ({actual_boost_total:,} تومان) "
            f"حدود {abs(diff):,} تومان از مقدار مورد انتظار "
            f"({expected_boost:,} تومان) {direction} است."
        )

    # ---- بررسی بودجه اینفلوئنسر ----
    if influencer_budget is None:
        result["warnings"].append(
            "بودجه اینفلوئنسر در جدول ۳ پیدا نشد."
        )
    else:
        inf_tolerance = int(expected_influencer * 0.05)
        if abs(influencer_budget - expected_influencer) > inf_tolerance:
            diff = influencer_budget - expected_influencer
            direction = "بیشتر" if diff > 0 else "کمتر"
            result["warnings"].append(
                f"بودجه اینفلوئنسر ({influencer_budget:,} تومان) "
                f"حدود {abs(diff):,} تومان از مقدار مورد انتظار "
                f"({expected_influencer:,} تومان) {direction} است."
            )

    # ---- بررسی بودجه‌های تکراری ----
    non_none = [b for b in row_budgets if b is not None]
    if len(non_none) != len(set(non_none)):
        result["warnings"].append(
            "برخی روزها بودجه یکسان دارند."
        )

    # ---- بررسی جمع کل اعلام‌شده ----
    if declared_total is not None:
        if abs(declared_total - actual_boost_total) > tolerance:
            result["warnings"].append(
                f"جمع کل اعلام‌شده در جدول ({declared_total:,}) "
                f"با جمع واقعی ({actual_boost_total:,}) مطابقت ندارد."
            )

    return result


def validate_reach(markdown_text: str) -> dict:
    """
    Reach ارگانیک روزها را بررسی می‌کند.
    """
    result = {
        "is_valid": True,
        "warnings": []
    }

    lines = markdown_text.split("\n")
    in_table_1 = False
    header_passed = False

    reach_data = []  # list of (format, organic_reach)

    for line in lines:
        line_stripped = line.strip()

        if "جدول 1" in line_stripped or "تقویم فید" in line_stripped:
            in_table_1 = True
            header_passed = False
            continue

        if in_table_1 and ("جدول 2" in line_stripped or "استوری" in line_stripped):
            in_table_1 = False

        if in_table_1 and line_stripped.startswith("|"):
            if "روز" in line_stripped or "---" in line_stripped:
                header_passed = True
                continue

            if not header_passed:
                continue

            if "جمع" in line_stripped:
                continue

            cells = [c.strip() for c in line_stripped.split("|")]
            cells = [c for c in cells if c != ""]

            if len(cells) >= 9:
                fmt = cells[1].strip() if len(cells) > 1 else ""
                reach_cell = cells[8] if len(cells) > 8 else ""
                numbers = re.findall(r'[\d,،]+', reach_cell)
                for n in numbers:
                    clean = n.replace(",", "").replace("،", "")
                    if clean.isdigit():
                        reach_data.append((fmt, int(clean)))
                        break

    # بررسی تکراری بودن
    reaches = [r for _, r in reach_data]
    if len(reaches) != len(set(reaches)):
        result["warnings"].append(
            "برخی روزها Reach ارگانیک یکسان دارند."
        )

    # بررسی نسبت ریلز به پست
    reel_reaches = [r for f, r in reach_data if "ریلز" in f]
    post_reaches = [r for f, r in reach_data if "تک" in f or "عکس" in f]

    if reel_reaches and post_reaches:
        avg_reel = sum(reel_reaches) / len(reel_reaches)
        avg_post = sum(post_reaches) / len(post_reaches)

        if avg_reel < avg_post * 2.5:
            result["warnings"].append(
                f"Reach ریلز (میانگین: {int(avg_reel):,}) "
                f"باید حداقل ۳ برابر پست معمولی "
                f"(میانگین: {int(avg_post):,}) باشد."
            )

    return result
