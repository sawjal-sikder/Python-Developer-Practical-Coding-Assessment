# PDF Translation & Watermarking API Engine

A robust, production-ready Django REST Framework (DRF) API for advanced PDF processing. This application provides secure, high-performance endpoints to translate PDF document contents between languages and apply customized vector-based text watermarks across pages.

---

## Key Features

1. **Intelligent PDF Translator (`/api/translate-pdf/`)**
   - Extracts text page-by-page from an uploaded PDF.
   - Optimizes translations using **Google batch translation** (grouping pages with `|||` delimiters) to dramatically reduce API requests and avoid rate limits.
   - Incorporates an exponential-backoff retry mechanism and a page-by-page fallback pipeline for absolute resilience.
   - Renders translated text in multiple complex scripts (including Arabic, Bangla, Japanese, Korean, Hindi, and Urdu) with pixel-perfect accuracy.

2. **Stylized PDF Watermarking (`/editor/pdf/watermark/`)**
   - Overlays transparent, high-fidelity text watermarks across all pages of a PDF.
   - Supports **7 precise coordinates**: `top-left`, `top-center`, `top-right`, `center` (diagonally rotated), `bottom-left`, `bottom-center`, and `bottom-right`.
   - Accepts hex color codes (`#FF0000`) and customizable opacity values (`0.0` - `1.0`).
   - Supports multi-lingual watermark text with automatic font selection and registration.

3. **Fully Embedded & Registered Fonts**
   - Ships with high-quality, pre-registered **Google Noto** fonts for robust multi-lingual rendering across PDFs and watermarks:
     - **Bangla (`bn`)**: Noto Sans Bengali (`NotoSansBengali-Regular.ttf`)
     - **Korean (`ko`)**: Noto Sans Korean (`NotoSansKR-Regular.ttf`)
     - **Japanese (`ja`)**: Noto Sans Japanese (`NotoSansJP-Regular.ttf`)
     - **Hindi (`hi`)**: Noto Sans Devanagari (`NotoSansDevanagari-Regular.ttf`)
     - **Arabic (`ar`)**: Noto Sans Arabic (`NotoSansArabic-Regular.ttf`)
     - **Urdu (`ur`)**: Noto Nastaliq Urdu (`NotoNastaliqUrdu-Regular.ttf`)

---

## 1. Cloning the Project from GitHub

First, clone the repository to your local machine and navigate into the project directory:

```bash
git clone https://github.com/sawjal-sikder/Python-Developer-Practical-Coding-Assessment
cd Python-Developer-Practical-Coding-Assessment
```

---

## 2. Environment Setup

### Step 2.1: Create & Activate Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

**On Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 2.2: Install Dependencies

Install all required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2.3: Download the Noto Sans Bengali Font

The PDF generation engine requires the `NotoSansBengali-Regular.ttf` TrueType font file. Run the following command from the project root to download the official verified font from Google Fonts:

```bash
mkdir -p services/utils/fonts
curl -L "https://raw.githubusercontent.com/googlefonts/noto-fonts/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf" -o services/utils/fonts/NotoSansBengali-Regular.ttf
```

### Step 2.4: Apply Database Migrations

Set up your local SQLite database:

```bash
python manage.py migrate
```

---

## 3. Running the Project

Start the Django development server:

```bash
python manage.py runserver
```

The server will spin up and run at **`http://127.0.0.1:8000/`**.

---

## 4. Testing with Postman

You can also test both endpoints using Postman by sending `multipart/form-data` requests.

### 1. API A — PDF Language Translator (`POST /api/translate-pdf/`)

- **URL**: `http://127.0.0.1:8000/api/translate-pdf/`
- **Method**: `POST`
- **Body**: Select **form-data**
- **Headers**: None required (Postman automatically sets the correct `Content-Type: multipart/form-data` boundary).
- **Form Parameters**:
  | Key | Type | Value / Description | Example |
  | :--- | :--- | :--- | :--- |
  | `file` | **File** | Click the dropdown to select _File_, then click _Select Files_ to upload your PDF. | `sample.pdf` |
  | `source_language` | **Text** | The language code of the original text. | `en` |
  | `target_language` | **Text** | The desired language code for translation. | `bn` (Bangla), `es` (Spanish), `hi` (Hindi) |

> **Pro Tip for Postman**: Since the response is a binary PDF, click the arrow next to the **Send** button and select **Send and Download**. This will prompt you to save the returned PDF file directly to your computer.

---

### 2. API B — PDF Watermark (simplified) (`POST /editor/pdf/watermark/`)

- **URL**: `http://127.0.0.1:8000/editor/pdf/watermark/`
- **Method**: `POST`
- **Body**: Select **form-data**
- **Form Parameters**:
  | Key | Type | Value / Description | Example |
  | :--- | :--- | :--- | :--- |
  | `file` | **File** | Click the dropdown to select _File_, then click _Select Files_ to upload your PDF. | `sample.pdf` |
  | `text` | **Text** | The text of the watermark (supports multi-lingual Unicode). | `CONFIDENTIAL` or `গোপনীয়` |
  | `position` | **Text** | Location of the watermark: `top-left`, `top-center`, `top-right`, `center`, `bottom-left`, `bottom-center`, `bottom-right`. | `center` |
  | `opacity` | **Text** | A decimal transparency value between `0.0` (invisible) and `1.0` (fully opaque). | `0.35` |
  | `color` | **Text** | A standard hex color code. | `#FF0000` (Red) or `#4B0082` (Indigo) |

> **Pro Tip for Postman**: Just like the translation endpoint, use the **Send and Download** option in Postman to save the watermarked PDF file locally.

---

## 5. Interactive Testing with Swagger UI

The project has **`drf-spectacular`** integrated out-of-the-box, providing a beautifully documented, interactive REST API explorer.

1. Open your browser and navigate to the Swagger UI page:
   **`http://127.0.0.1:8000/api/schema/swagger-ui/`**
2. You will see two categorized tags: **PDF Language Translation** and **PDF Watermarking**.

### Testing the Translation API

1. Expand the **POST `/api/translate-pdf/`** endpoint.
2. Click **Try it out** on the upper right corner.
3. Provide the required `multipart/form-data` fields:
   - **`file`**: Click **Browse / Choose File** and upload any standard PDF document.
   - **`source_language`**: Input the language code of the original PDF text, e.g., `en`.
   - **`target_language`**: Input the desired language code for translation, e.g., `bn` (for Bangla) or `es` (for Spanish).
4. Click the blue **Execute** button.
5. In the response section below, you will receive a standard `200 OK` status, and a **Download file** link. Click it to download your newly translated PDF!

### Testing the Watermarking API

1. Expand the **POST `/editor/pdf/watermark/`** endpoint.
2. Click **Try it out**.
3. Fill in the required form fields:
   - **`file`**: Upload your source PDF document.
   - **`text`**: Enter the watermark string (e.g., `CONFIDENTIAL` or `গোপনীয়`).
   - **`position`**: Choose one of the valid positions: `top-left`, `top-center`, `top-right`, `center`, `bottom-left`, `bottom-center`, `bottom-right`.
   - **`opacity`**: Set a decimal opacity value between `0.0` (invisible) and `1.0` (fully opaque) (e.g., `0.35`).
   - **`color`**: Enter a valid hex color code (e.g., `#FF0000` or `#4B0082`).
4. Click **Execute**.
5. Click **Download file** in the response section to get your watermarked PDF document with transparent styled vector overlay text.

---

## 6. Running the Automated Tests

The repository includes a comprehensive, modular unit and integration test suite organized under the `services/tests/` package directory:

- `test_translator.py`: Covers single text/page-by-page translation logic & translation API view.
- `test_pdf_processing.py`: Covers PDF extraction & multi-lingual PDF generation algorithms.
- `test_watermark.py`: Covers PDF watermarking utility & watermarking API view.

To run the test suite:

```bash
python manage.py test
```

A clean run should output:

```text
System check identified no issues (0 silenced).
..........................
----------------------------------------------------------------------
Ran 26 tests in 0.42s

OK
```
