import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import merge_core
import logging
import time

class TranslationMergeApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Translation Merge Tool")
		self.main_file = None
		self.translation_files = []
		self.columns = []
		self.column_vars = []

		self.setup_ui()

	def setup_ui(self):
		frame = ttk.Frame(self.root, padding=10)
		frame.pack(fill=tk.BOTH, expand=True)

		# Main file selection
		self.main_file_label = ttk.Label(frame, text="No main file selected.")
		self.main_file_label.pack(anchor=tk.W)
		ttk.Button(frame, text="Select Main File", command=self.select_main_file).pack(anchor=tk.W, pady=5)

		# Translation files info
		self.trans_files_label = ttk.Label(frame, text="Translation files: 0 found.")
		self.trans_files_label.pack(anchor=tk.W, pady=(10,0))
		self.trans_files_list_label = ttk.Label(frame, text="")
		self.trans_files_list_label.pack(anchor=tk.W)

		# Status label
		self.status_label = ttk.Label(frame, text="Ready.", foreground="blue")
		self.status_label.pack(anchor=tk.W, pady=(10,0))


		# Columns checklist with scrollbar
		columns_frame_outer = ttk.LabelFrame(frame, text="Columns to Merge", padding=5)
		columns_frame_outer.pack(fill=tk.BOTH, expand=True, pady=10)

		canvas = tk.Canvas(columns_frame_outer, height=200)
		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		scrollbar = ttk.Scrollbar(columns_frame_outer, orient="vertical", command=canvas.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.columns_frame = ttk.Frame(canvas)
		self.columns_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
		)
		canvas.create_window((0, 0), window=self.columns_frame, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		# Merge button
		self.merge_btn = ttk.Button(frame, text="Merge and Save", command=self.merge_and_save, state=tk.DISABLED)
		self.merge_btn.pack(anchor=tk.E, pady=5)

	def select_main_file(self):
		file_path = filedialog.askopenfilename(
			title="Select Main Survey Excel File",
			filetypes=[("Excel files", "*.xlsx *.xls")]
		)
		if file_path:
			self.main_file = file_path
			self.main_file_label.config(text=f"Main file: {os.path.basename(file_path)}")
			self.scan_translation_files()
			self.load_columns()
			self.merge_btn.config(state=tk.NORMAL)
		else:
			self.main_file_label.config(text="No main file selected.")
			self.trans_files_label.config(text="Translation files: 0 found.")
			self.clear_columns()
			self.merge_btn.config(state=tk.DISABLED)

	def scan_translation_files(self):
		directory = os.path.dirname(self.main_file)
		main_filename = os.path.basename(self.main_file)
		self.translation_files = merge_core.find_translation_files(directory, main_filename)
		self.trans_files_label.config(text=f"Translation files: {len(self.translation_files)} found.")
		if self.translation_files:
			file_names = '\n'.join([os.path.basename(f) for f in self.translation_files])
			self.trans_files_list_label.config(text=f"Files found:\n{file_names}")
		else:
			self.trans_files_list_label.config(text="")

	def load_columns(self):
		self.clear_columns()
		if not self.main_file:
			return
		self.columns = merge_core.load_excel_columns(self.main_file)
		self.column_vars = []
		for col in self.columns:
			var = tk.BooleanVar()
			cb = ttk.Checkbutton(self.columns_frame, text=col, variable=var)
			cb.pack(anchor=tk.W)
			self.column_vars.append((var, col))

	def clear_columns(self):
		for widget in self.columns_frame.winfo_children():
			widget.destroy()
		self.column_vars = []

	def merge_and_save(self):
		self.status_label.config(text="Step 1: Loading main Excel file...")
		selected_cols = [col for var, col in self.column_vars if var.get()]
		if not selected_cols:
			messagebox.showwarning("No Columns Selected", "Please select at least one column to merge.")
			return
		if not self.translation_files:
			messagebox.showwarning("No Translation Files", "No translation files found in the directory.")
			return

		start_time = time.time()
		log_lines = []
		log_lines.append("\n--- Translation Merge Run ---")
		log_lines.append(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
		log_lines.append("")
		# End time and run time will be added after merge
		#
		# File info
		log_lines.append(f"Main file: {self.main_file}")
		log_lines.append(f"Translation files: {', '.join(self.translation_files)}")
		log_lines.append(f"Number of translation files: {len(self.translation_files)}")
		log_lines.append("")
		# Columns merged
		log_lines.append(f"Columns merged: {', '.join(selected_cols)}")
		log_lines.append("")

		try:
			self.status_label.config(text="Step 2: Merging translations...")
			print(f"[GUI LOG] Calling merge_translations with main_file={self.main_file}, translation_files={self.translation_files}, selected_cols={selected_cols}")

			result = merge_core.merge_translations(
				self.main_file,
				self.translation_files,
				selected_cols
			)
			if result is None:
				self.status_label.config(text="Error: Merge failed or file could not be loaded.")
				print("[GUI LOG] merge_translations returned None. Merge failed or file could not be loaded.")
				return
			merged_df, merge_stats = result

			self.status_label.config(text="Step 3: Counting missing rows...")
			# Count rows not found in translation files
			not_found = 0
			id_column = 'Respondent.Serial'
			for col in selected_cols:
				new_col = f"{col}_ENG_Trans"
				if new_col in merged_df.columns:
					not_found += merged_df[new_col].isna().sum() + (merged_df[new_col] == '').sum()

			self.status_label.config(text="Step 4: Saving merged Excel file...")
			# Generate default output filename: originalfilename_Merged.xlsx
			base_name = os.path.splitext(os.path.basename(self.main_file))[0]
			default_output = f"{base_name}_Merged.xlsx"
			save_path = filedialog.asksaveasfilename(
				title="Save Merged Excel File",
				defaultextension=".xlsx",
				filetypes=[("Excel files", "*.xlsx")],
				initialfile=default_output
			)
			if save_path:
				merge_core.save_merged_excel(merged_df, save_path)
				end_time = time.time()
				run_time = end_time - start_time
				log_lines.insert(2, f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
				log_lines.insert(3, f"Run time (seconds): {run_time:.2f}")
				log_lines.append(f"Number of rows not found in translation files (by Respondent.Serial): {not_found}")
				log_lines.append("")
				log_lines.append(f"Path to the saved merged file: {save_path}")
				# Add per-country, per-column merge stats
				log_lines.append("")
				log_lines.append("--- Per-country, per-column merge stats ---")
				for country, col_stats in merge_stats.items():
					log_lines.append(f"{country}")
					for col, count in col_stats.items():
						log_lines.append(f"  {col} - {count} non blank cells merged")
					log_lines.append("")
				# Write log to the same directory as the saved Excel file, as .txt
				log_path = os.path.join(os.path.dirname(save_path), "translation_merge.txt")
				with open(log_path, "a", encoding="utf-8") as f:
					for line in log_lines:
						f.write(line + "\n")
				self.status_label.config(text="Done! Merged file saved.")
				messagebox.showinfo("Success", f"Merged file saved to:\n{save_path}\nLog saved to:\n{log_path}")
			else:
				self.status_label.config(text="Save cancelled.")
		except Exception as e:
			self.status_label.config(text=f"Error: {e}")
			if 'log_path' in locals():
				with open(log_path, "a", encoding="utf-8") as f:
					f.write(f"Error: {e}\n")
			messagebox.showerror("Error", f"An error occurred:\n{e}")

if __name__ == "__main__":
	root = tk.Tk()
	app = TranslationMergeApp(root)
	root.mainloop()
