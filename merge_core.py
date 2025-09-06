
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
	"""
	Merge English translations from translation_files into main_file for selected columns.
	Returns a new DataFrame with merged columns.
	"""
	main_df = pd.read_excel(main_file)
	# Load all translation files into a list of DataFrames
	translation_dfs = [pd.read_excel(f) for f in translation_files]

	for col in columns_to_merge:
		new_col = f"{col}_ENG_Trans"
		merged_col = []
		for idx, row in main_df.iterrows():
			respondent_id = row.get(id_column)
			translation = ''
			for tdf in translation_dfs:
				match = tdf[tdf.get(id_column) == respondent_id]
				if not match.empty:
					val = match.iloc[0].get(col, '')
					if pd.notna(val) and str(val).strip():
						translation = val
						break
			merged_col.append(translation)
		main_df.insert(main_df.columns.get_loc(col) + 1, new_col, merged_col)
	return main_df

def save_merged_excel(df, output_path):
	"""
	Save the merged DataFrame to an Excel file.
	"""
	df.to_excel(output_path, index=False)

