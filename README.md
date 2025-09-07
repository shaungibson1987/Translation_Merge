
# Translation Merge Tool

A user-friendly Python GUI tool to merge English translations from multiple survey data files into a main survey file. Designed for survey researchers and analysts who need to combine open-ended or comment translations from several sources into a single, easy-to-review Excel file.

---

## Features

- **Multi-file Support:** Merge translations from any number of *_translated.xlsx files.
- **Column Selection:** Choose which columns to merge via checkboxes in the GUI.
- **Robust Matching:** Matches respondents by `Respondent.Serial` (case-insensitive, whitespace-stripped).
- **Diagnostics & Logging:** Logs ID and column overlap, sample merged values, and all errors for easy troubleshooting.
- **Safe by Default:** `.gitignore` excludes all `.xlsx` files to protect sensitive data.
- **Error Handling:** Gracefully handles missing files, columns, or data.

---

## How It Works

1. **Select the Main File:**  
	Use the GUI to select your main Excel file (e.g., `AllData_Overall.xlsx`).

2. **Automatic Translation File Detection:**  
	The app scans the same directory for all files with `_translated` in the filename.

3. **Choose Columns:**  
	The GUI lists all columns in the main file. Select which ones you want to merge translations for.

4. **Merge Process:**  
	For each selected column, the tool creates a new column (e.g., `outro_ENG_Trans`) and fills it with translations from all available files, using the last non-empty value found for each respondent.

5. **Save Results:**  
	The merged file is saved as a new Excel file (e.g., `AllData_Overall_with_English.xlsx`), with original and translated columns side by side.

---

## Example

Suppose you have:
- Main file: `AllData_Overall.xlsx`
- Translation files: `AllData_German_translated.xlsx`, `AllData_French_translated.xlsx`, etc.

You select columns `outro` and `Q_Misconception`.  
The tool creates `outro_ENG_Trans` and `Q_Misconception_ENG_Trans` in the output file, merging translations for each respondent.

---

## Installation

1. Clone this repository.
2. Create and activate a Python virtual environment:
	```
	python -m venv venv
	source venv/Scripts/activate  # On Windows (bash)
	```
3. Install dependencies:
	```
	pip install -r requirements.txt
	```

---

## Usage

1. Run the GUI:
	```
	python translation_merge_gui.py
	```
2. Follow the prompts to select your main file and columns.
3. Click "Merge and Save" to generate the merged Excel file.

---

## Logging & Troubleshooting

- All merge steps, errors, and diagnostics are logged to the console and `translation_merge.log`.
- If you encounter issues, check the log for details on file loading, ID overlap, and column matches.

---

## Security

- All `.xlsx` files are excluded from version control via `.gitignore` to protect sensitive data.

---

## Contributing

Pull requests and suggestions are welcome! Please open an issue for any bugs or feature requests.

## Recent Updates

- Now supports merging from multiple translation files (not just one).
- Robust error handling and logging: all file loading and merge steps are logged, and errors are reported with clear messages.
- Diagnostics: The merge process logs ID and column overlap, and sample merged values, to help debug any issues.
- .gitignore updated to exclude all .xlsx files for data privacy.
- GUI and core logic are now robust to missing/invalid files and columns.
