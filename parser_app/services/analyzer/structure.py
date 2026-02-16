from lxml import html
from collections import defaultdict
import hashlib
from typing import List
from core.schemas import Candidate

def element_signature(el) -> str:
    """Возвращает строку тег + отсортированные классы."""
    tag = el.tag
    if not isinstance(tag, str):
        # Если вдруг попал не HtmlElement (но по логике сюда приходят только они)
        tag = "unknown"
    classes = sorted(el.get('class', '').split())
    if classes:
        return f"{tag}.{'.'.join(classes)}"
    else:
        return tag

def build_signature_for_element(el) -> str:
    """Строит сигнатуру элемента на основе его дочерних элементов первого уровня."""
    children_sigs = []
    for child in el.iterchildren():
        if not isinstance(child, html.HtmlElement):
            continue
        if child.tag in ['script', 'style', 'noscript']:
            continue
        children_sigs.append(element_signature(child))
    children_sigs.sort()
    parent_sig = element_signature(el)
    sig_str = f"{parent_sig}|{','.join(children_sigs)}|{len(children_sigs)}"
    return hashlib.md5(sig_str.encode()).hexdigest()

def generate_css_selector(el) -> str:
    """Генерирует простой CSS-селектор для элемента."""
    if el.get('id'):
        return f"#{el.get('id')}"
    selector = el.tag
    if el.get('class'):
        classes = '.'.join(el.get('class').split())
        selector += f".{classes}"
    parent = el.getparent()
    if parent is not None and isinstance(parent, html.HtmlElement):
        siblings = list(parent.iterchildren(tag=el.tag))
        if len(siblings) > 1:
            index = siblings.index(el) + 1
            selector += f":nth-child({index})"
    return selector

def find_repeating_blocks(html_content: str) -> List[Candidate]:
    tree = html.fromstring(html_content)
    body = tree.body
    if body is None:
        return []

    candidates_by_sig = defaultdict(list)

    for el in body.iterdescendants():
        if not isinstance(el, html.HtmlElement):
            continue
        if el.tag in ['script', 'style', 'noscript']:
            continue
        sig = build_signature_for_element(el)
        candidates_by_sig[sig].append(el)

    groups = []
    for sig, elements in candidates_by_sig.items():
        if len(elements) >= 3:
            # Ищем общего родителя (для простоты берём родителя первого элемента)
            container = elements[0].getparent()
            if container is None or not isinstance(container, html.HtmlElement):
                continue
            selector = generate_css_selector(container)
            example_items = [html.tostring(el, encoding='unicode')[:500] for el in elements[:3]]
            groups.append(Candidate(
                id=len(groups) + 1,
                container_selector=selector,
                example_items=example_items,
                count=len(elements)
            ))
    return groups