import os
import json
import fitz  # PyMuPDF
import numpy as np

def get_span_score(span, max_font, avg_font, page_width, line_spans_count):
    text = span["text"].strip()
    size = span["size"]
    flags = span["flags"]
    bbox = span["bbox"]

    if not text or not text.isprintable() or len(text) < 2:
        return 0
    if text.isupper() and len(text.replace(" ", "")) <= 3:
        return 0  # Filter out very short all-caps like W I T H

    if size < avg_font * 1.0:  # Slightly stricter than 0.9
        return 0
    if line_spans_count > 4:   # Allow up to 4 spans (was 5)
        return 0
    if bbox[0] > page_width * 0.35:
        return 0

    score = 0
    if size >= max_font * 0.80:
        score += 3
    elif size >= max_font * 0.60:
        score += 2
    elif size >= avg_font * 1.0:
        score += 1

    if flags & 2 or flags & 8:
        score += 1
    if text.istitle() or text.isupper():
        score += 1

    return score



def classify_level(score):
    if score >= 4:
        return "H1"
    elif score >= 2:
        return "H2"
    elif score >= 1:
        return "H3"
    return None




def extract_headings_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    headings = []
    max_font = 0
    title = ""
    font_sizes = []

    # Pass 1: determine max_font and avg_font from all pages
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    font_sizes.append(span["size"])
                    text = span["text"].strip()
                    if span["size"] > max_font and len(text) > 1:
                        max_font = span["size"]
                        title = text
    avg_font = np.mean(font_sizes)

    # Pass 2: extract headings with merged H1s
    for page_number, page in enumerate(doc, 1):
        page_width = page.rect.width
        pending_h1_parts = []

        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                line_spans = line.get("spans", [])
                line_spans_count = len(line_spans)

                for span in line_spans:
                    text = span["text"].strip()
                    score = get_span_score(span, max_font, avg_font, page_width, line_spans_count)
                    level = classify_level(score)

                    if level == "H1":
                        pending_h1_parts.append(text)
                    else:
                        if pending_h1_parts:
                            combined_text = " ".join(pending_h1_parts)
                            headings.append({
                                "level": "H1",
                                "text": combined_text,
                                "page": page_number
                            })
                            pending_h1_parts = []

                        if level:
                            headings.append({
                                "level": level,
                                "text": text,
                                "page": page_number
                            })

        # Flush any remaining H1 parts at the end of the page
        if pending_h1_parts:
            combined_text = " ".join(pending_h1_parts)
            headings.append({
                "level": "H1",
                "text": combined_text,
                "page": page_number
            })

    return {
        "title": title,
        "outline": headings
    }


def process_all_pdfs(input_dir="/app/input", output_dir="/app/output"):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            try:
                print(f"✅ Processing {filename}...")
                pdf_path = os.path.join(input_dir, filename)
                result = extract_headings_from_pdf(pdf_path)

                json_name = os.path.splitext(filename)[0] + ".json"
                output_path = os.path.join(output_dir, json_name)

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"❌ Failed to process {filename}: {e}")


if __name__ == "__main__":
    process_all_pdfs()
