# 📄 Adobe Hackathon – Round 1A Submission
## Challenge: Understand Your Document

---

## 🚀 Approach

This solution performs **automatic outline extraction** from PDF documents by identifying the document title and classifying headings (H1, H2, H3) based on their visual and layout features.

### ✨ Key Steps:
1. **PDF Parsing**: All pages are parsed using `PyMuPDF` (`fitz`) to extract text blocks, lines, spans, and layout metadata (font size, position, bold/italic flags).
2. **Font Analysis**:
   - The largest font across the document is assumed to be the title.
   - Font sizes across the document are used to estimate heading candidates.
3. **Heading Scoring**:
   - Each text span is scored based on visual cues:
     - Font size (relative to max/average)
     - Bold/italic flags
     - Layout position
     - Title case or uppercase
     - Line span count (to filter paragraphs)
   - Very short capitalized tokens like `"W I T H"` are ignored.
4. **Heading Classification**:
   - Based on the score, each span is labeled as:
     - `H1` (high score, typically main section)
     - `H2` (moderate score)
     - `H3` (lower-level headings)
5. **H1 Merging**:
   - Consecutive `H1` spans on the same line (e.g., "Learn", "Italian") are merged into a single heading like "Learn Italian".

---

## 🧠 Models & Libraries Used

| Component              | Description                        |
|------------------------|------------------------------------|
| `PyMuPDF (fitz)`       | PDF parsing and text layout        |
| `NumPy`                | Font statistics and scoring        |
| **No internet-required model used** | Keeps the container lightweight and offline-compatible |

🛑 **No Transformer models or external dependencies** were used to ensure:
- Total model size < 200MB
- Full offline compatibility
- Fast processing within 10 seconds

---

## ⚙️ Build & Run Instructions

> 💡 Your solution is Dockerized to match the evaluation environment (Linux, AMD64).

### 📦 1. Build the Docker Image

```bash
docker build --platform linux/amd64 -t pdfextractor:round1a .

docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdfextractor:round1a
