
import os
import pandas as pd

def find_translation_files(directory, main_filename):
	"""
	Find all files in the directory with '_translated' in the filename, excluding the main file.
	"""
	files = []
	for fname in os.listdir(directory):
		if fname == main_filename:
			continue
		if '_translated' in fname.lower() and fname.lower().endswith(('.xlsx', '.xls')):
			files.append(os.path.join(directory, fname))
	return files

def load_excel_columns(filepath):
	"""
	Load an Excel file and return its columns as a list.
	"""
	df = pd.read_excel(filepath)
	return df.columns.tolist()

def merge_translations(main_file, translation_files, columns_to_merge, id_column='Respondent.Serial'):
	print("[MERGE LOG] main_file loaded successfully.")
	print(f"[MERGE LOG] merge_translations called with main_file={main_file}, translation_files={translation_files}, columns_to_merge={columns_to_merge}, id_column={id_column}")
	# --- Overlap and column diagnostics (like debug_id_overlap.py) ---
	try:
		print(f"[MERGE LOG] Attempting to load main_file: {main_file}")
		main_df = pd.read_excel(main_file)
		print("[MERGE LOG] main_file loaded successfully.")
		main_df[id_column] = main_df[id_column].astype(str).str.strip().str.lower()


		if not translation_files:
			print("[MERGE LOG] No translation files provided.")
			return None

		# Build combined lookup dict from all translation files
		lookup = {}
		for tf in translation_files:
			try:
				trans_df = pd.read_excel(tf)
				trans_df[id_column] = trans_df[id_column].astype(str).str.strip().str.lower()
				for _, row in trans_df.iterrows():
					rid = str(row[id_column]).strip().lower()
					for col in trans_df.columns:
						lookup[(rid, col.strip().lower())] = row[col]
			except Exception as e:
				print(f"[MERGE LOG] ERROR loading translation file {tf}: {e}")

		main_col_map = {c.lower(): c for c in main_df.columns}

		for col in columns_to_merge:
			main_col = main_col_map.get(col.lower(), col)
			new_col = f"{main_col}_ENG_Trans"
			merged_col = []
			found_count = 0
			not_found_count = 0
			debug_samples = []
			for idx, row in main_df.iterrows():
				respondent_id = str(row.get(id_column)).strip().lower()
				val = lookup.get((respondent_id, col.strip().lower()), '')
				if pd.notna(val) and str(val).strip():
					merged_col.append(val)
					found_count += 1
				else:
					merged_col.append('')
					not_found_count += 1
				if col.lower() == 'outro' and len(debug_samples) < 5:
					debug_samples.append((respondent_id, val))
			if col.lower() == 'outro':
				print("\n[DEBUG] Sample merging for 'outro' (first 5):")
				print("Respondent.Serial | Merged value")
				for rid, merged in debug_samples:
					print(f"{rid} | {merged}")
			print(f"[DEBUG] For column '{col}': {found_count} found, {not_found_count} not found.")
			if new_col in main_df.columns:
				main_df[new_col] = merged_col
			else:
				main_df.insert(main_df.columns.get_loc(main_col) + 1, new_col, merged_col)
		return main_df
	except Exception as e:
		print(f"[MERGE LOG] ERROR in merge_translations: {e}")
		return None

	main_cols = set([c.lower().strip() for c in main_df.columns])
	trans_cols = set([c.lower().strip() for c in trans_df.columns])
	matching_cols = main_cols & trans_cols
	main_only = main_cols - trans_cols
	trans_only = trans_cols - main_cols
	print("\n[MERGE LOG] Columns in BOTH main and translation file:")
	print(sorted(matching_cols))
	print("\n[MERGE LOG] Columns ONLY in main file:")
	print(sorted(main_only))
	print("\n[MERGE LOG] Columns ONLY in translation file:")
	print(sorted(trans_only))

	# Check if 'outro' column exists and has data in translation file
	for col in columns_to_merge:
		if col.lower().strip() in trans_cols:
			outro_col = [c for c in trans_df.columns if c.lower().strip() == col.lower().strip()][0]
			overlap_df = trans_df[trans_df[id_column].isin(overlap)]
			non_empty = overlap_df[overlap_df[outro_col].notna() & (overlap_df[outro_col].astype(str).str.strip() != '')]
			print(f"[MERGE LOG] Rows in translation file with non-empty '{col}' for overlapping Respondent.Serials: {len(non_empty)}")
			print(f"[MERGE LOG] Sample non-empty '{col}' values for overlapping Respondent.Serials:")
			print(non_empty[[id_column, outro_col]].head(10))
		else:
			print(f"[MERGE LOG] '{col}' column not found in translation file.")
	"""
	Merge English translations from translation_files into main_file for selected columns.
	Returns a new DataFrame with merged columns.
	"""
	print(f"[MERGE LOG] Attempting to load main_file: {main_file}")
	try:
		main_df = pd.read_excel(main_file)
	except Exception as e:
		print(f"[MERGE LOG] ERROR loading main_file: {e}")
		return None
	main_df[id_column] = main_df[id_column].astype(str).str.strip().str.lower()

	# Only support one translation file for now (can be extended)
	if not translation_files:
		raise ValueError("No translation files provided.")
	trans_df = pd.read_excel(translation_files[0])
	trans_df[id_column] = trans_df[id_column].astype(str).str.strip().str.lower()

	# Build lookup dict: (respondent.serial, col) -> value
	lookup = {}
	for _, row in trans_df.iterrows():
		rid = str(row[id_column]).strip().lower()
		for col in trans_df.columns:
			lookup[(rid, col.strip().lower())] = row[col]

	main_col_map = {c.lower(): c for c in main_df.columns}

	for col in columns_to_merge:
		main_col = main_col_map.get(col.lower(), col)
		new_col = f"{main_col}_ENG_Trans"
		merged_col = []
		found_count = 0
		not_found_count = 0
		debug_samples = []
		for idx, row in main_df.iterrows():
			respondent_id = str(row.get(id_column)).strip().lower()
			val = lookup.get((respondent_id, col.strip().lower()), '')
			if pd.notna(val) and str(val).strip():
				merged_col.append(val)
				found_count += 1
			else:
				merged_col.append('')
				not_found_count += 1
			if col.lower() == 'outro' and len(debug_samples) < 5:
				debug_samples.append((respondent_id, val))
		if col.lower() == 'outro':
			print("\n[DEBUG] Sample merging for 'outro' (first 5):")
			print("Respondent.Serial | Merged value")
			for rid, merged in debug_samples:
				print(f"{rid} | {merged}")
		print(f"[DEBUG] For column '{col}': {found_count} found, {not_found_count} not found.")
		if new_col in main_df.columns:
			main_df[new_col] = merged_col
		else:
			main_df.insert(main_df.columns.get_loc(main_col) + 1, new_col, merged_col)
	return main_df

def save_merged_excel(df, output_path):
	"""
	Save the merged DataFrame to an Excel file.
	"""
	df.to_excel(output_path, index=False)

