import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import os
import merge_core
import logging
import time


class TranslationMergeApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Translation Merge Tool")
		self.root.geometry("700x750")
		self.root.resizable(False, False)
		self.main_file = None
		self.translation_files = []
		self.columns = []
		self.column_vars = []
		self.theme = "flatly"
		self.style = tb.Style(self.theme)
		self.setup_ui()

	def setup_ui(self):
		# Menu bar for theme switching
		menubar = tb.Menu(self.root)
		theme_menu = tb.Menu(menubar, tearoff=0)
		for theme in self.style.theme_names():
			theme_menu.add_command(label=theme, command=lambda t=theme: self.change_theme(t))
		menubar.add_cascade(label="Settings", menu=theme_menu)
		self.root.config(menu=menubar)

		# --- Main container frame ---
		container = tb.Frame(self.root)
		container.pack(fill=BOTH, expand=True)

		# --- Scrollable main content area ---
		main_canvas = tb.Canvas(container, borderwidth=0, highlightthickness=0)
		main_canvas.pack(side=LEFT, fill=BOTH, expand=True)
		vscroll = tb.Scrollbar(container, orient="vertical", command=main_canvas.yview)
		vscroll.pack(side=RIGHT, fill=Y)
		main_canvas.configure(yscrollcommand=vscroll.set)

		# Centered content frame with max width
		max_content_width = 600
		frame = tb.Frame(main_canvas, padding=20)
		def _center_content(event):
			canvas_width = event.width
			x = max((canvas_width - max_content_width) // 2, 0)
			main_canvas.coords("content_window", x, 0)
			main_canvas.itemconfig("content_window", width=min(canvas_width, max_content_width))
		frame.bind(
			"<Configure>",
			lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
		)
		main_canvas.bind("<Configure>", _center_content)
		main_canvas.create_window((0, 0), window=frame, anchor="n", width=max_content_width, tags=("content_window",))

		# App title
		title = tb.Label(frame, text="Translation Merge Tool", font=("Segoe UI", 22, "bold underline"), anchor=CENTER)
		title.pack(fill=X, pady=(0, 5))
		subtitle = tb.Label(frame, text="Easily merge translations from multiple Excel files into your main survey file.\nSelect columns, handle column mismatches, and get detailed logs.", font=("Segoe UI", 12), anchor=CENTER, justify=CENTER)
		subtitle.pack(fill=X, pady=(0, 15))

		# Main file selection
		self.main_file_label = tb.Label(frame, text="No main file selected.", font=("Segoe UI", 10, "bold"))
		self.main_file_label.pack(anchor=W, pady=(0, 2))
		tb.Button(frame, text="Select Main File", command=self.select_main_file, bootstyle=PRIMARY, width=20).pack(anchor=W, pady=5)

		# Translation files info
		self.trans_files_label = tb.Label(frame, text="Translation files: 0 found.", font=("Segoe UI", 10))
		self.trans_files_label.pack(anchor=W, pady=(10,0))
		self.trans_files_list_label = tb.Label(frame, text="", font=("Segoe UI", 9))
		self.trans_files_list_label.pack(anchor=W)

		# Columns checklist with scrollbar
		columns_frame_outer = tb.Labelframe(frame, text="Columns to Merge", padding=10, bootstyle=INFO)
		columns_frame_outer.pack(fill=BOTH, expand=True, pady=15)

		canvas = tb.Canvas(columns_frame_outer, height=220)
		canvas.pack(side=LEFT, fill=BOTH, expand=True)

		scrollbar = tb.Scrollbar(columns_frame_outer, orient="vertical", command=canvas.yview)
		scrollbar.pack(side=RIGHT, fill=Y)

		self.columns_frame = tb.Frame(canvas)
		self.columns_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
		)
		canvas.create_window((0, 0), window=self.columns_frame, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		# Option: Rename columns by order
		self.rename_cols_var = tb.BooleanVar()
		self.rename_cols_cb = tb.Checkbutton(frame, text="Rename columns in translation files by order (force match)", variable=self.rename_cols_var, bootstyle=SECONDARY)
		self.rename_cols_cb.pack(anchor=W, pady=(5,0))

		# Merge button (large and always visible)
		self.merge_btn = tb.Button(frame, text="Merge and Save", command=self.merge_and_save, state="disabled", bootstyle=SUCCESS, width=30, padding=10)
		self.merge_btn.pack(anchor=CENTER, pady=15)

		# --- Fixed status bar at the bottom ---
		self.status_bar = tb.Label(self.root, text="Ready.", font=("Segoe UI", 11, "bold"), anchor=W, bootstyle=INFO)
		self.status_bar.pack(side=BOTTOM, fill=X)

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
			self.merge_btn.config(state="normal")
		else:
			self.main_file_label.config(text="No main file selected.")
			self.trans_files_label.config(text="Translation files: 0 found.")
			self.clear_columns()
			self.merge_btn.config(state="disabled")

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
			var = tb.BooleanVar()
			cb = tb.Checkbutton(self.columns_frame, text=col, variable=var, bootstyle=INFO)
			cb.pack(anchor=W)
			self.column_vars.append((var, col))

	def clear_columns(self):
		for widget in self.columns_frame.winfo_children():
			widget.destroy()
		self.column_vars = []

	def merge_and_save(self):
		self.status_bar.config(text="Step 1 of 4: Loading main Excel file...", bootstyle=INFO)
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

		# If rename columns by order is checked, confirm and perform renaming
		if self.rename_cols_var.get():
			proceed = messagebox.askyesno(
				"Rename Columns by Order",
				"This will rename the columns in each translation file to match the main file, by order.\n\n"
				"This is only safe if the translation files have the same column order as the main file.\n\n"
				"Are you sure you want to proceed? (A backup of each translation file will be created.)"
			)
			if not proceed:
				self.status_bar.config(text="Column renaming cancelled.", bootstyle=WARNING)
				return
			# Perform renaming and backup
			main_columns = self.columns
			import shutil
			backup_dir = os.path.join(os.path.dirname(self.main_file), "backups")
			os.makedirs(backup_dir, exist_ok=True)
			for tf in self.translation_files:
				try:
					import pandas as pd
					# Backup original file in backups folder
					backup_path = os.path.join(backup_dir, os.path.basename(tf) + ".bak")
					if not os.path.exists(backup_path):
						shutil.copy2(tf, backup_path)
					df = pd.read_excel(tf)
					if len(df.columns) == len(main_columns):
						df.columns = main_columns
						df.to_excel(tf, index=False)
					else:
						messagebox.showwarning("Column Count Mismatch", f"File {os.path.basename(tf)} not renamed: column count does not match main file.")
				except Exception as e:
					messagebox.showerror("Error Renaming Columns", f"Error renaming columns in {os.path.basename(tf)}: {e}")
		# End time and run time will be added after merge
		#
		# File info
		log_lines.append(f"Main file: {self.main_file}")
		log_lines.append(f"Translation files: {', '.join(self.translation_files)}")
		log_lines.append(f"Number of translation files: {len(self.translation_files)}")
		log_lines.append("")
		# Columns merged (one per line)
		log_lines.append("Columns merged:")
		for col in selected_cols:
			log_lines.append(f"  {col}")
		log_lines.append("")

		try:
			self.status_bar.config(text="Step 2 of 4: Merging translations...", bootstyle=INFO)
			print(f"[GUI LOG] Calling merge_translations with main_file={self.main_file}, translation_files={self.translation_files}, selected_cols={selected_cols}")

			result = merge_core.merge_translations(
				self.main_file,
				self.translation_files,
				selected_cols
			)
			if result is None or len(result) < 3:
				self.status_label.config(text="Error: Merge failed or file could not be loaded.")
				print("[GUI LOG] merge_translations returned None. Merge failed or file could not be loaded.")
				return
			merged_df, merge_stats, col_mismatch_stats = result

			self.status_bar.config(text="Step 3 of 4: Counting missing rows...", bootstyle=INFO)
			# Count rows not found in translation files
			not_found = 0
			id_column = 'Respondent.Serial'
			for col in selected_cols:
				new_col = f"{col}_ENG_Trans"
				if new_col in merged_df.columns:
					not_found += merged_df[new_col].isna().sum() + (merged_df[new_col] == '').sum()

			self.status_bar.config(text="Step 4 of 4: Saving merged Excel file...", bootstyle=INFO)
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
				# Add column mismatches before per-country stats
				log_lines.append("")
				log_lines.append("--- Column mismatches (columns missing in translation files) ---")
				if col_mismatch_stats:
					for country, missing_cols in col_mismatch_stats.items():
						log_lines.append(f"{country}:")
						for col in missing_cols:
							log_lines.append(f"  {col}")
						log_lines.append("")
				else:
					log_lines.append("None. All columns matched in all translation files.")
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
				self.status_bar.config(text="Done! Merged file saved.", bootstyle=SUCCESS)
				messagebox.showinfo("Success", f"Merged file saved to:\n{save_path}\nLog saved to:\n{log_path}")
			else:
				self.status_bar.config(text="Save cancelled.", bootstyle=WARNING)
		except Exception as e:
			self.status_bar.config(text=f"Error: {e}", bootstyle=DANGER)
			if 'log_path' in locals():
				with open(log_path, "a", encoding="utf-8") as f:
					f.write(f"Error: {e}\n")
			messagebox.showerror("Error", f"An error occurred:\n{e}")

	def change_theme(self, theme_name):
		self.style.theme_use(theme_name)
		self.theme = theme_name

if __name__ == "__main__":
	app = tb.Window(themename="flatly")
	TranslationMergeApp(app)
	app.mainloop()
