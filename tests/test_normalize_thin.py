# -*- coding: utf-8 -*-
from vietnamese_nsfw_filter import normalize, is_thin


def test_normalize_idempotent_and_collapses():
    raw = "Xin  chào\r\n\r\n\r\nthế   giới ."
    out = normalize(raw)
    assert "  " not in out          # gộp space thừa
    assert "\r" not in out
    assert " ." not in out          # bỏ space trước dấu câu
    assert normalize(out) == out    # idempotent


def test_is_thin_login_gate():
    thin, reason = is_thin("Bạn cần đăng nhập để đọc chương này.")
    assert thin and reason.startswith("boilerplate")


def test_is_thin_too_short():
    thin, reason = is_thin("Ngắn.")
    assert thin and reason.startswith("too_short")


def test_not_thin_for_real_chapter():
    text = "Một chương truyện dài với nội dung thật sự đầy đủ. " * 20
    thin, reason = is_thin(text)
    assert thin is False and reason == "ok"
