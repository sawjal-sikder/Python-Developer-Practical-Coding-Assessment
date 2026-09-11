# PDF Translation & Watermarking API Engine

A robust, production-ready Django REST Framework (DRF) API for advanced PDF processing. This application provides secure, high-performance endpoints to translate PDF document contents between languages and apply customized vector-based text watermarks across pages.

---

## Key Features

1. **Intelligent PDF Translator (`/api/translate-pdf/`)**
   * Extracts text page-by-page from an uploaded PDF.
   * Optimizes translations using **Google batch translation** (grouping pages with `|||` delimiters) to dramatically reduce API requests and avoid rate limits.
   * Incorporates an exponential-backoff retry mechanism and a page-by-page fallback pipeline for absolute resilience.
   * Renders translated text (including complex Bangla Unicode scripts) with pixel-perfect accuracy.

2. **Stylized PDF Watermarking (`/editor/pdf/watermark/`)**
   * Overlays transparent, high-fidelity text watermarks across all pages of a PDF.
   * Supports **7 precise coordinates**: `top-left`, `top-center`, `top-right`, `center` (diagonally rotated), `bottom-left`, `bottom-center`, and `bottom-right`.
   * Accepts hex color codes (`#FF0000`) and customizable opacity values (`0.0` - `1.0`).
   * Supports multilingual watermark text including automatic Bangla Unicode font registration.

3. **Fully Embedded Fonts**
   * Ships with embedded **Noto Sans Bengali Regular** font support, enabling seamless rendering of native Bengali characters without layout corruption.

---

## 1. Cloning the Project from GitHub

First, clone the repository to your local machine and navigate into the project directory:

```bash
git clone https://github.com/your-username/Python-Developer-Practical-Coding-Assessment.git
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

## 4. Interactive Testing with Swagger UI

The project has **`drf-spectacular`** integrated out-of-the-box, providing a beautifully documented, interactive REST API explorer.

1. Open your browser and navigate to the Swagger UI page:
   **`http://127.0.0.1:8000/api/schema/swagger-ui/`**
2. You will see two categorized tags: **PDF Language Translation** and **PDF Watermarking**.

### Testing the Translation API

1. Expand the **POST `/api/translate-pdf/`** endpoint.
2. Click **Try it out** on the upper right corner.
3. Provide the required `multipart/form-data` fields:
   * **`file`**: Click **Browse / Choose File** and upload any standard PDF document.
   * **`source_language`**: Input the language code of the original PDF text, e.g., `en`.
   * **`target_language`**: Input the desired language code for translation, e.g., `bn` (for Bangla) or `es` (for Spanish).
4. Click the blue **Execute** button.
5. In the response section below, you will receive a standard `200 OK` status, and a **Download file** link. Click it to download your newly translated PDF!

### Testing the Watermarking API

1. Expand the **POST `/editor/pdf/watermark/`** endpoint.
2. Click **Try it out**.
3. Fill in the required form fields:
   * **`file`**: Upload your source PDF document.
   * **`text`**: Enter the watermark string (e.g., `CONFIDENTIAL` or `গোপনীয়`).
   * **`position`**: Choose one of the valid positions: `top-left`, `top-center`, `top-right`, `center`, `bottom-left`, `bottom-center`, `bottom-right`.
   * **`opacity`**: Set a decimal opacity value between `0.0` (invisible) and `1.0` (fully opaque) (e.g., `0.35`).
   * **`color`**: Enter a valid hex color code (e.g., `#FF0000` or `#4B0082`).
4. Click **Execute**.
5. Click **Download file** in the response section to get your watermarked PDF document with transparent styled vector overlay text.

---

## 5. Running the Automated Tests

The repository includes a comprehensive unit and integration test suite covering serializers, PDF utility pipelines, and API views.

To run the test suite:

```bash
python manage.py test
```

A clean run should output:
```text
System check identified no issues (0 silenced).
..........
----------------------------------------------------------------------
Ran 10 tests in 0.65s

OK
```
