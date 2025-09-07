
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
	try:
		print(f"[MERGE LOG] Attempting to load main_file: {main_file}")
		main_df = pd.read_excel(main_file)
		print("[MERGE LOG] main_file loaded successfully.")
		main_df[id_column] = main_df[id_column].astype(str).str.strip().str.lower()

		if not translation_files:
			print("[MERGE LOG] No translation files provided.")
			return None, None, None

		# Build combined lookup dict from all translation files
		lookup = {}
		per_file_col_counts = {}  # {filename: {col: count}}
		col_mismatches = {}  # {country: [missing_col1, ...]}
		for tf in translation_files:
			try:
				trans_df = pd.read_excel(tf)
				trans_df[id_column] = trans_df[id_column].astype(str).str.strip().str.lower()
				country = os.path.splitext(os.path.basename(tf))[0].split('__')[-1].replace('_translated','').upper()
				if country not in per_file_col_counts:
					per_file_col_counts[country] = {}
				# Detect column mismatches
				trans_cols_lc = set([c.strip().lower() for c in trans_df.columns])
				missing_cols = [col for col in columns_to_merge if col.strip().lower() not in trans_cols_lc]
				if missing_cols:
					col_mismatches[country] = missing_cols
				for col in columns_to_merge:
					col_lc = col.strip().lower()
					if col_lc in trans_cols_lc:
						col_actual = [c for c in trans_df.columns if c.strip().lower() == col_lc][0]
						non_blank = trans_df[trans_df[col_actual].notna() & (trans_df[col_actual].astype(str).str.strip() != '')]
						per_file_col_counts[country][col] = non_blank.shape[0]
				for _, row in trans_df.iterrows():
					rid = str(row[id_column]).strip().lower()
					for col in trans_df.columns:
						lookup[(rid, col.strip().lower())] = row[col]
			except Exception as e:
				print(f"[MERGE LOG] ERROR loading translation file {tf}: {e}")
		# Return this dict for logging
		merge_stats = per_file_col_counts
		col_mismatch_stats = col_mismatches

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
		return main_df, merge_stats, col_mismatch_stats
	except Exception as e:
		print(f"[MERGE LOG] ERROR in merge_translations: {e}")
		return None, None, None


def save_merged_excel(df, output_path):
	"""
	Save the merged DataFrame to an Excel file.
	"""
	df.to_excel(output_path, index=False)

