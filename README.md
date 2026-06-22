# Field-Notes-Digitization-Bernhardt-Lab

This repository contains tools for digitizing scanned field notes from water sampling forms. 
The goal of this project is to reduce manual data entry from scanned field notes by producing a structured CSV that can be used for downstream ecological or water quality analysis.

The current workflow uses a vision-language model, Qwen2.5-VL, to extract structured data from PDF field notes and export the results as a CSV file.

The main extraction goal is to identify whether each sampling site has a handwritten algae mention in the remarks field.

## Output

The notebook produces a CSV with the following columns:

| Column          | Description                                         |
| --------------- | --------------------------------------------------- |
| `source_file`   | Name of the original PDF file                       |
| `date`          | Date collected, extracted from the form             |
| `site`          | Sampling site name                                  |
| `algae_present` | Boolean value indicating whether algae is mentioned |
| `evidence_text` | Text or visual evidence used by the model           |

Example output:

```csv
source_file,date,site,algae_present,evidence_text
20220404 Notes.pdf,2022-04-04,WS-1,True,Algae d/s v-notch
20220404 Notes.pdf,2022-04-04,WS-2,True,ALGAE
20220404 Notes.pdf,2022-04-04,WS-3,True,ALGAE
```

## Repository Contents

```text
Field-Notes-Digitization-Bernhardt-Lab/
├── qwen_test.ipynb              # Main Colab notebook using Qwen2.5-VL
├── test_paddle_ocr.py           # PaddleOCR test script
├── paddle+preprocessing.py      # PaddleOCR preprocessing experiment
├── test_easy_ocr.py             # EasyOCR test script
├── .gitignore
└── README.md
```

## Recommended Workflow

The recommended workflow is to use the `qwen_test.ipynb` notebook in Google Colab.

The notebook:

1. Installs the required Python packages.
2. Uploads a ZIP file containing multiple PDF field notes.
3. Unzips the PDF files.
4. Converts page 2 of each PDF into an image.
5. Sends each page image to Qwen2.5-VL.
6. Extracts date, site, algae presence, and evidence text.
7. Appends all rows into a single pandas DataFrame.
8. Exports the final result to `algae_results.csv`.

## Requirements

The notebook is intended to run in Google Colab with GPU access.

Recommended GPU:

```text
A100
```

Required Python packages:

```bash
pip install transformers accelerate qwen-vl-utils pypdfium2 pillow pandas
```

The notebook also requires a Hugging Face token (selected Qwen model requires authentication).

## Setup Instructions

1. Open `qwen_test.ipynb` in Google Colab.
2. Go to:

```text
Runtime → Change runtime type
```

3. Select a GPU runtime, preferably A100.
4. Add your Hugging Face token to Colab Secrets as:

```text
HF_TOKEN
```

5. Run the notebook cells in order.
6. Upload a ZIP file containing the PDF field notes when prompted.
7. Download the generated CSV at the end.

## Input Format

The expected input is a ZIP file containing one or more PDF files.

Example:

```text
field_notes.zip
├── 20220308 Notes.pdf
├── 20220314 Notes.pdf
├── 20220404 Notes.pdf
└── 20220425 Notes.pdf
```

The current workflow processes page 2 of each PDF.

## Model

The current notebook uses Qwen2.5-VL for visual document understanding. Instead of relying on traditional OCR alone, the model reads the page image and directly returns structured JSON.

This is useful for handwritten field notes because the task is not full-page transcription. The task is to determine whether each site row contains an algae-related note.

## Notes on Accuracy

Model has had promising performance on small batch of 8 images, idenfyting all instances of algae present correctly.

Validation checks performed to check accuracy for sample of 8 images:

* Confirmed that every expected site appears.
* Checked that the date is correct.
* Check all rows.
* Reviewed any failed files listed in the notebook.

The `evidence_text` column is included to make manual review easier.

## Previous OCR Experiments

This repository also includes earlier experiments with:

* EasyOCR
* PaddleOCR
* PaddleOCR with preprocessing

These approaches were useful for testing traditional OCR, but the current Qwen-based workflow is better aligned with the project goal and results in better accuracy.

## Future Improvements

Possible future additions:

* Add a simple upload/run/download button interface in Colab.
* Add validation for expected site names.


# Excel Field Notes Extraction

In addition to the PDF/Qwen workflow, this repository includes a lightweight command-line utility for extracting algae observations from Excel field note files.

## Expected Excel Format

The script expects a worksheet named:

```text
field notes
```

The following cells are used:

| Location | Description     |
| -------- | --------------- |
| G3       | Collection date |
| A8:A18   | Site names      |
| H8:H18   | Remarks         |

The script extracts:

* Date
* Site
* Algae presence
* Original remarks text

and exports the results to a CSV file.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Process all Excel files in a folder:

```bash
python extract_excel_field_notes.py ./excel_files
```

Specify a custom output file:

```bash
python extract_excel_field_notes.py ./excel_files -o algae_results.csv
```

## Output

Example CSV:

```csv
source_file,date,site,algae_present,evidence_text
field_notes.xlsx,4/9/2018,WS-1,True,Algae d/s
field_notes.xlsx,4/9/2018,WS-2,False,
field_notes.xlsx,4/9/2018,WS-3,True,ALGAE
```

## Notes

* The script searches all `.xlsx` files in the supplied folder.
* Dates are exported in `M/D/YYYY` format.
* Empty remarks are treated as no algae observation.
* The script preserves the original remarks text in the output CSV for review.

## Author

Developed by Melosa Rao for field notes digitization work associated with Bernhardt Lab.

