import pandas as pd

main_file = "P027822__Overall.xlsx"
trans_file = "P027822__DEU_translated.xlsx"
id_column = "Respondent.Serial"



main_df = pd.read_excel(main_file)
trans_df = pd.read_excel(trans_file)

# Normalize IDs
main_ids = set(main_df[id_column].astype(str).str.strip())
trans_ids = set(trans_df[id_column].astype(str).str.strip())

# Print samples
print("Sample Respondent.Serial from main file:", list(main_ids)[:10])
print("Sample Respondent.Serial from translation file:", list(trans_ids)[:10])

# Print intersection size
overlap = main_ids & trans_ids
print(f"Number of IDs in main file: {len(main_ids)}")
print(f"Number of IDs in translation file: {len(trans_ids)}")
print(f"Number of overlapping IDs: {len(overlap)}")
print("Sample overlapping IDs:", list(overlap)[:10])

# Compare columns (case-insensitive, stripped)
main_cols = set([c.lower().strip() for c in main_df.columns])
trans_cols = set([c.lower().strip() for c in trans_df.columns])
matching_cols = main_cols & trans_cols
main_only = main_cols - trans_cols
trans_only = trans_cols - main_cols
print("\nColumns in BOTH main and translation file:")
print(sorted(matching_cols))
print("\nColumns ONLY in main file:")
print(sorted(main_only))
print("\nColumns ONLY in translation file:")
print(sorted(trans_only))

# Check if 'outro' column exists and has data in translation file
if 'outro' in trans_cols:
    outro_col = [c for c in trans_df.columns if c.lower().strip() == 'outro'][0]
    # Only consider overlapping Respondent.Serials
    overlap_df = trans_df[trans_df[id_column].astype(str).str.strip().isin(overlap)]
    non_empty = overlap_df[overlap_df[outro_col].notna() & (overlap_df[outro_col].astype(str).str.strip() != '')]
    print(f"Rows in translation file with non-empty 'outro' for overlapping Respondent.Serials: {len(non_empty)}")
    print("Sample non-empty 'outro' values for overlapping Respondent.Serials:")
    print(non_empty[[id_column, outro_col]].head(10))
else:
    print("'outro' column not found in translation file.")
