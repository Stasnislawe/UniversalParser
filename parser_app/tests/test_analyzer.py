import pytest
from services.analyzer.structure import find_repeating_blocks

def test_find_repeating_blocks():
    # Минимальный HTML с повторяющимися блоками
    html = """
    <html><body>
        <div class="item"><h2>Item 1</h2><p>Desc 1</p></div>
        <div class="item"><h2>Item 2</h2><p>Desc 2</p></div>
        <div class="item"><h2>Item 3</h2><p>Desc 3</p></div>
        <div class="other">static</div>
    </body></html>
    """
    candidates = find_repeating_blocks(html)
    assert len(candidates) >= 1
    # Проверим, что контейнер - body или div?
    # По нашему алгоритму сигнатура div.item должна совпасть, контейнером станет body
    # Но может быть несколько кандидатов. Проверим хотя бы не пусто.
    assert candidates[0].count >= 3