# -*- coding: utf-8 -*-
from vietnamese_nsfw_filter import count_hits, is_explicit, deaccent


def test_deaccent_unifies_accents_and_font_corruption():
    assert deaccent("Dương Vật") == "duong vat"
    assert deaccent("duơng vật") == "duong vat"   # ư mất dấu -> u
    assert deaccent("Đâm") == "dam"


def test_clean_text_zero_hits():
    clean = ("Hôm nay trời đẹp, cả nhà cùng ra đồng gặt lúa, bà kể chuyện cổ tích, "
             "đám trẻ cười đùa vui vẻ bên bờ ruộng bậc thang.") * 3
    assert count_hits(clean) == 0
    assert is_explicit(clean) is False


def test_explicit_text_many_hits():
    smut = ("Hắn đút dương vật vào âm đạo, làm tình mãnh liệt, "
            "nàng rên rỉ dâm đãng, dâm thủy chảy ra, cuối cùng hắn xuất tinh.")
    assert count_hits(smut) >= 5
    assert is_explicit(smut, threshold=3) is True


def test_font_corrupted_still_detected():
    # bản mất dấu (font lỗi) vẫn bắt qua lớp de-accent
    broken = "hắn đút duong vat vao am dao, xuat tinh, giao hop nhieu lan"
    assert count_hits(broken) >= 3


def test_native_vulgar_terms():
    text = "Thằng kia chửi địt mẹ, đồ lồn, cái cặc gì đây, đồ nứng."
    assert count_hits(text) >= 4


def test_no_false_positive_on_homographs():
    # buổi/lớn/đám/đảm KHÔNG bị nhầm thành buồi/lồn/dâm
    text = ("Buổi sáng đám đông lớn dần, cô gái đảm đang nấu cơm, "
            "cậu bé lớn lên ngoan ngoãn, ngồi xuống, đứng dậy.") * 2
    assert count_hits(text) == 0
