import customtkinter as ctk
from tkinter import filedialog
import os
import pandas as pd
import joblib

class FileBrowseFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.file_path = ctk.StringVar()
        self.file_path_string = ""
        
        self.browse_button = ctk.CTkButton(self, text="Browse for CSV", command=self.browse_file)
        self.browse_button.pack(pady=10)

        self.file_label = ctk.CTkLabel(self, textvariable=self.file_path)
        self.file_label.pack(pady=5)

    def browse_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.file_path.set(file)
            self.file_path_string = file
    
    def get_file_path_string(self):
        return self.file_path_string


class CheckboxFrame(ctk.CTkFrame):
    def __init__(self, master, file_list):
        super().__init__(master)
        
        self.file_list = file_list
        self.checkbox_vars = []
        
        for i, file in enumerate(self.file_list):
            var = ctk.IntVar()
            checkbox = ctk.CTkCheckBox(self, text=file, variable=var)
            row = i % 5 # for gui
            column = i // 5 # for gui
            checkbox.grid(row=row, column=column, pady=5, padx=5, sticky="nsew")
            self.checkbox_vars.append(var)

    def get_selected_files(self):
        selected_files = []
        for i, var in enumerate(self.checkbox_vars):
            if (var.get() == 1):
                selected_files.append(self.file_list[i])
        return selected_files


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("900x600")
        self.title("FindMyWEC")

        self.combobox = ctk.CTkComboBox(self, values=["Browse for CSV", "Select Test CSV"], command=self.on_combobox_change)
        self.combobox.grid(row=0, column=0, pady=20, padx=20, sticky="n")
        self.combobox.set("Select an Option") # Default startup 'option'

        self.frame = None
        self.file_list = ["test_data_401", "test_data_402", "test_data_403", "test_data_404", "test_data_405", \
            "test_data_406", "test_data_407", "test_data_408", "test_data_409", "test_data_410"]
        
        # Create button spanning the entire window
        self.predict_button = ctk.CTkButton(self, text="Predict", command=self.on_predict, width=200)
        self.predict_button.grid(row=2, column=0, pady=20, padx=20, sticky="ew")
        
        self.predict_label = ctk.CTkLabel(self, text="Prediction(s): ", anchor="center")
        self.predict_label.grid(row=3, column=0, pady=2, padx=20, sticky="ew")

        # Change layout to expand column
        self.grid_columnconfigure(0, weight=1)
        
        self.model_path = "./WECsRandomForest.pkl"
        self.model=joblib.load(self.model_path)
        
        self.prediction_mapping = {0: "Adelaide", 1: "Perth", 2: "Sydney", 3: "Tasmania"}

    def on_combobox_change(self, selected_option):
        # Clear the current frame if one exists
        if self.frame:
            self.frame.destroy()

        # Change the frame based on the selected option
        if selected_option == "Browse for CSV":
            self.frame = FileBrowseFrame(self)
            self.frame.grid(row=1, column=0, pady=20, padx=20, sticky="ew")
        elif selected_option == "Select Test CSV":
            self.frame = CheckboxFrame(self, self.file_list)
            self.frame.grid(row=1, column=0, pady=20, padx=20, sticky="ew")
 

    def on_predict(self):
        # Get selected files from the active frame
        file = None
        selected_files = None
        prediction_output = None
        if isinstance(self.frame, FileBrowseFrame):
            file = self.frame.get_file_path_string()
            print(f"Selected file: {file}")
            prediction_output = self.process_and_predict_browsed_csv(file)
        elif isinstance(self.frame, CheckboxFrame):
            selected_files = self.frame.get_selected_files()
            print(f"Selected files: {', '.join(selected_files)}")
            prediction_output = self.process_and_predict_csvs(selected_files)
        
        self.predict_label.configure(text=prediction_output)

    
    def process_and_predict_browsed_csv(self, selected_file):
        file_path = selected_file
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, header=None)
                print(df.shape)
                
                if (df.shape != (1,49)):
                    return f"Problem with the input file. Make sure it contains 1 row and 49 columns only."
                
                else:
                    prediction = self.model.predict(df)
                    prediction_result = f"Prediction for {os.path.basename(file_path)}: {self.prediction_mapping.get(prediction[0])}\n"
                    return prediction_result
                
            except Exception as e:
                print(f"Problem with file {file_path} the errorx: {e}")
                return f"Error with the file: {file_path}"
         
    
    def process_and_predict_csvs(self, selected_files):        
        results = []
        for file in selected_files:
            file_path = f"./wecs_test_data/{file}.csv"
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path, header=None)
                    prediction = self.model.predict(df)
                    prediction_result = f"Prediction for {file}: {self.prediction_mapping.get(prediction[0])}"
                    results.append(prediction_result)
                except Exception as e:
                    print(f"Problem with file {file_path} the error: {e}")
                    
        format_results = "\n".join(results)

        return format_results

if __name__ == "__main__":
    app = App()
    app.mainloop()
