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


def test_english_loanwords():
    text = "Thằng này toàn xem phim porn với hentai, search sex suốt ngày."
    assert count_hits(text) >= 3


def test_weak_layer_opt_in():
    text = "Hai người lên giường, quan hệ tình dục, rồi ngủ với nhau."
    base = count_hits(text)                      # default: ít/không (toàn từ WEAK)
    broad = count_hits(text, include_weak=True)  # bật WEAK -> bắt nhiều hơn
    assert broad > base


def test_char_stretching_evasion():
    # né filter bằng kéo dài ký tự vẫn bị bắt
    assert count_hits("đồ lồnnnn, địtttt mẹ, cặcccc") >= 3


def test_teencode_profanity():
    assert count_hits("vcl thằng này, vkl, đcm mày, đồ đĩ chó") >= 3


def test_regional_slang_in_weak_layer():
    # lóng/ẩn dụ vùng miền chỉ tính khi bật weak (vì đa nghĩa)
    text = "Cái chim với cái bướm, cậu nhỏ, của quý, vùng kín, núi đôi."
    assert count_hits(text) == 0
    assert count_hits(text, include_weak=True) >= 4


def test_no_fp_on_combat_and_homographs():
    # văn tiên hiệp/hành động + đồng âm KHÔNG bị đếm (đâm vào/tiến nhập/trận trường/ám đạo...)
    text = ("Hắn đâm vào, thọc vào, thâm nhập, tiến nhập đan điền, mở hỏa huyệt, mạch huyệt. "
            "Ra trận trường, làm việc tinh tế, đi qua ám đạo theo đường cũ, giao hoán bảo vật, "
            "ăn cục khoai, nhà thờ cổ.") * 3
    assert count_hits(text) < 3, f"FP! count={count_hits(text)}"
    # bản sex thật (đúng dấu) vẫn bắt
    assert count_hits("dương vật cọ vào âm đạo, dương cụ cương cứng, làm tình, đạt cực khoái") >= 4


def test_no_false_positive_on_homographs():
    # buổi/lớn/đám/đảm KHÔNG bị nhầm thành buồi/lồn/dâm
    text = ("Buổi sáng đám đông lớn dần, cô gái đảm đang nấu cơm, "
            "cậu bé lớn lên ngoan ngoãn, ngồi xuống, đứng dậy.") * 2
    assert count_hits(text) == 0
