import time
import requests
from deep_translator.exceptions import TranslationNotFound, LanguageNotSupportedException

# Apply requests monkeypatch to bypass Google Translate 500 error for default python-requests User-Agent
original_get = requests.get

def patched_get(url, *args, **kwargs):
    if "translate.google" in str(url):
        headers = kwargs.get("headers") or {}
        if "User-Agent" not in headers:
            headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
            kwargs["headers"] = headers
    return original_get(url, *args, **kwargs)

requests.get = patched_get

from deep_translator import GoogleTranslator


def translate_text(
    text,
    source_language,
    target_language
):
    if not text.strip():
        return text

    # Normalize language codes
    source_language = source_language.lower()
    target_language = target_language.lower()

    if source_language == target_language:
        return text

    translator = GoogleTranslator(
        source=source_language,
        target=target_language,
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            translated = translator.translate(text)
            if translated:
                print(translated)
                return translated
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1.0 * (attempt + 1))
                continue
            # Fallback to original text instead of crashing the request
            print(f"Transletor text failed after {max_retries} attempts. Returning original text.")
            print(f"text: {text}")
            return text
    print(f"Transletor text failed after {max_retries} attempts. Returning original text.")
    print(f"text: {text}")
    return text


def translate_pages(
    pages,
    source_language,
    target_language
):
    if not pages:
        return []

    # Normalize language codes
    source_language = source_language.lower()
    target_language = target_language.lower()

    if source_language == target_language:
        return list(pages)

    # We use ' ||| ' as the separator for batch translation
    separator = ' ||| '
    
    # Keep track of empty pages and non-empty pages
    translated_pages = ["" for _ in pages]
    non_empty_indices = [i for i, page in enumerate(pages) if page.strip()]
    
    if not non_empty_indices:
        return translated_pages

    # Group non-empty pages into chunks of at most 4000 characters
    chunks = []
    current_chunk_indices = []
    current_chunk_len = 0
    
    for idx in non_empty_indices:
        page_text = pages[idx].strip()
        added_len = len(page_text) + (len(separator) if current_chunk_indices else 0)
        
        if current_chunk_len + added_len > 4000 and current_chunk_indices:
            chunks.append((current_chunk_indices, current_chunk_len))
            current_chunk_indices = [idx]
            current_chunk_len = len(page_text)
        else:
            current_chunk_indices.append(idx)
            current_chunk_len += added_len
            
    if current_chunk_indices:
        chunks.append((current_chunk_indices, current_chunk_len))

    # Translate each chunk using GoogleTranslator
    translator = GoogleTranslator(source=source_language, target=target_language)
    
    for chunk_indices, _ in chunks:
        combined_text = separator.join(pages[idx].strip() for idx in chunk_indices)
        
        translated_text = ""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                translated_text = translator.translate(combined_text)
                if translated_text:
                    break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break
        
        if translated_text:
            # Split the translated text back into pages
            parts = [part.strip() for part in translated_text.split('|||')]
            if len(parts) == len(chunk_indices):
                for idx, part in zip(chunk_indices, parts):
                    translated_pages[idx] = part
            else:
                # If the parts count doesn't match, force page-by-page fallback
                translated_text = ""

        # Page-by-page fallback for this chunk if batch translation failed or structure mismatched
        if not translated_text:
            for idx in chunk_indices:
                page_text = pages[idx].strip()
                page_translated = ""
                for attempt in range(max_retries):
                    try:
                        page_translated = translator.translate(page_text)
                        break
                    except Exception:
                        if attempt < max_retries - 1:
                            time.sleep(1.5 * (attempt + 1))
                            continue
                        page_translated = page_text  # Final fallback to original text
                translated_pages[idx] = page_translated

    for page in translated_pages:
        if page.strip():
            print(page)

    return translated_pages
