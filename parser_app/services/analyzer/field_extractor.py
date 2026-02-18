from lxml import html
from typing import List, Dict, Any, Tuple
from core.schemas import Field
import re

def is_number(s: str) -> bool:
    """Проверяет, можно ли строку считать числом (целое или с плавающей точкой)."""
    s = s.strip().replace(',', '.').replace(' ', '')
    try:
        float(s)
        return True
    except ValueError:
        return False


import logging

logger = logging.getLogger(__name__)


def extract_fields_from_blocks(blocks_html: List[str], base_url: str = None) -> List[Field]:
    logger.debug(f"Processing {len(blocks_html)} blocks")
    field_candidates: Dict[str, List[Tuple[str, str]]] = {}

    for i, block_html in enumerate(blocks_html):
        logger.debug(f"Processing block {i}, HTML length: {len(block_html)}")
        tree = html.fromstring(block_html)
        for el in tree.iter():
            if el.tag in ['script', 'style', 'noscript']:
                continue
            text = el.text_content().strip()
            if text and len(text) > 1:
                selector = _generate_relative_selector(el)
                field_candidates.setdefault(selector, []).append(('text', text))
                logger.debug(f"  Found text: {selector} = {text[:50]}...")
            if el.tag == 'a':
                href = el.get('href')
                if href:
                    selector = _generate_relative_selector(el) + '[href]'
                    field_candidates.setdefault(selector, []).append(('link', href))
                    logger.debug(f"  Found link: {selector} = {href}")
            if el.tag == 'img':
                src = el.get('src')
                if src:
                    selector = _generate_relative_selector(el) + '[src]'
                    field_candidates.setdefault(selector, []).append(('image', src))
                    logger.debug(f"  Found image: {selector} = {src}")

    logger.debug(
        f"Field candidates before filter: { {k: [(v[0], v[1][:50]) for v in values] for k, values in field_candidates.items()} }")

    fields = []
    for selector, values in field_candidates.items():
        # ослабим фильтрацию для диагностики
        # if len(values) < 2:
        #     continue
        # unique_values = set(v[1] for v in values)
        # if len(unique_values) == 1:
        #     continue
        type_ = values[0][0]
        if type_ == 'text' and all(is_number(v[1]) for v in values):
            type_ = 'number'
        name = selector.replace('.', '_').replace('[', '_').replace(']', '').replace(':', '_')
        example = values[0][1]
        attribute = None
        if type_ in ('link', 'image'):
            if '[href]' in selector:
                attribute = 'href'
            elif '[src]' in selector:
                attribute = 'src'
        fields.append(Field(
            name=name,
            selector=selector,
            type=type_,
            example=example,
            attribute=attribute
        ))

    logger.debug(f"Fields after filter (temporary unfiltered): {[f.dict() for f in fields]}")
    return fields


def _generate_relative_selector(el) -> str:
    """Генерирует CSS-селектор для элемента относительно родителя (без учёта контейнера)."""
    # Простейшая генерация по тегу и классу
    selector = el.tag
    if el.get('class'):
        # Берем классы, соединяем точками
        classes = '.'.join(el.get('class').split())
        selector += f".{classes}"
    return selector