# Translation Merge Tool - User Guide

## What is this app?
The Translation Merge Tool is a user-friendly application for survey researchers and analysts. It helps you merge English translations from multiple Excel files into your main survey data file, making it easy to review and analyze open-ended or comment responses in one place.

## What does it do?
- Scans your folder for translation files (with `_translated` in the name).
- Lets you pick which columns to merge (e.g., open-ended questions).
- Merges translations into your main file, creating new columns for the merged data.
- Provides detailed logging and diagnostics for transparency and troubleshooting.
- Offers an option to force column names in translation files to match the main file (by order), with automatic backups for safety.

## How to use the app

### 1. Start the app
- Run `python translation_merge_gui.py` (or use the provided `.exe` if available).

### 2. Select your main file
- Click "Select Main File" and choose your main survey Excel file (e.g., `AllData_Overall.xlsx`).
- The app will automatically find translation files in the same folder.

### 3. Review translation files
- The app lists all translation files it found (files with `_translated` in the name).

### 4. Choose columns to merge
- Tick the checkboxes for the columns you want to merge translations for.

### 5. (Optional) Use the rename columns option
- If your translation files have had their column names changed (e.g., by Google Translate), tick the box labeled:
  `Rename columns in translation files by order (force match)`
- This will rename the columns in each translation file to match the main file, by order. A backup will be saved in a `backups` folder.
- Only use this if you are sure the column order matches!

### 6. Merge and save
- Click "Merge and Save".
- Choose where to save your merged file. The app will suggest a filename like `YourMainFile_Merged.xlsx`.
- The app will process the files, merge the translations, and save the result.

### 7. Review the log
- After merging, a log file (`translation_merge.txt`) will be created in the same folder as your merged file.
- The log includes:
  - Which columns were merged
  - Any columns missing in translation files (per country)
  - Per-country, per-column merge stats
  - Any errors or warnings

## Tips & Warnings
- Always check the log file for any issues or missing data.
- If you use the rename columns option, check the `backups` folder for your original translation files.
- If you see a warning about column count mismatch, do not use the rename option for that file.
- All Excel files are excluded from git version control for your data privacy.

## Need help?
- If you have questions or run into issues, check the log file first.
- For further help, contact shaun.gibson@yonderdatasolutions.com or open an issue on the project repository.
