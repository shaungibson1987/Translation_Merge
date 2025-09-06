# Translation Merge Tool - Project Notes

## Project Goal
Create a user-friendly GUI tool to merge English translations from multiple translated survey data files into a single main (overall) survey data file. The tool should:
- Automatically find all relevant translation files in the same directory as the main file.
- Let the user select which columns to merge translations for (via checkboxes).
- For each selected column, add a new column to the main file with the English translation, matched by Respondent.Serial.
- Save a new Excel file with the merged results, making it easy to compare original and translated text side by side.

## User Workflow
1. **User selects the overall file** (main Excel file with all survey data for all countries).
2. **App scans the same directory** for all files with '_translated' in the filename (case-insensitive).
3. **App loads the overall file and lists all columns** with checkboxes.
   - User ticks the columns they want to merge translations for (e.g., open ends, comments).
4. **For each selected column:**
   - The app creates a new column right next to it, named `<original_column>_ENG_Trans`.
   - For each respondent (matched by Respondent.Serial), the app looks through all the _translated files and merges the English translation into the new column.
   - If multiple translation files have a value for the same respondent/column, the app uses the first non-empty value it finds.
   - If no translation is found, the new column is left blank for that respondent.
5. **App saves a new Excel file** (e.g., 'Overall_with_English.xlsx') with the original and new translation columns side by side.

## Implementation Plan
- **Folder Structure:**
  ```
  translation_merge/
  ├── translation_merge_gui.py      # Main Tkinter GUI
  ├── merge_core.py                 # Core logic for merging translations
  ├── requirements.txt              # Dependencies
  ├── README.md                     # Usage instructions
  └── NOTES.md                      # (This file)
  ```
- **Dependencies:**
  - pandas
  - openpyxl
  - tk (Tkinter)

- **GUI Features:**
  - File dialog to select the overall file
  - Automatic scan for *_translated* files
  - Checkbox list of columns from the overall file
  - Progress/status updates
  - Error handling and user-friendly messages

- **Core Logic (merge_core.py):**
  - Load the overall file and all *_translated* files
  - For each selected column, create a new column `<col>_ENG_Trans`
  - For each Respondent.Serial, merge in the first available translation from any file
  - Save the merged result as a new Excel file

- **Naming Conventions:**
  - New columns: `<original_column>_ENG_Trans`
  - Output file: `Overall_with_English.xlsx` (or similar)

- **Edge Cases:**
  - If a respondent is missing in a translation file, leave the new column blank for that row
  - If multiple translation files have a value, use the first non-empty value
  - If a column is not found in a translation file, skip it for that file

## Example Scenario
- Main file: `AllData_Overall.xlsx`
- Translated files: `AllData_French_translated.xlsx`, `AllData_Spanish_translated.xlsx`, etc.
- User selects columns: `QCQualityOE`, `QCChoiceOE`
- Result: `AllData_Overall_with_English.xlsx` with new columns `QCQualityOE_ENG_Trans`, `QCChoiceOE_ENG_Trans` containing merged English translations for each respondent.

## Next Steps
1. Open this folder as your workspace in VS Code.
2. Use this NOTES.md to remind the AI of your requirements.
3. Ask for scaffolding, implementation, or further customization as needed.

---

**This file preserves the full context and requirements for your translation merge tool. Paste or reference it in your new workspace to continue development seamlessly!**
