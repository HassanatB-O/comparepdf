from flask import Flask, request, render_template, redirect, flash
import os
import hashlib

def file_hash(filepath):
    # Calculates the SHA1 hash of a file, reads in chunks
    hasher = hashlib.sha1()
    with open(filepath, 'rb') as file:
        while True:
            chunk = file.read(1024 * 1024) 
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def compare_pdfs(fileName1, fileName2):

    flash(f"Comparing {fileName1} and {fileName2}...")

    try:
        hash1 = file_hash(fileName1)
        hash2 = file_hash(fileName2)

        if hash1 == hash2:
            return f"The PDF files '{os.path.basename(fileName1)}' and '{os.path.basename(fileName2)}' are identical (based on SHA1 hash) "
        else:    
            return f"The PDF files '{os.path.basename(fileName1)}' and '{os.path.basename(fileName2)}' are different (based on SHA1 hash) "
    except FileNotFoundError:
        return "Error: One or both files not found for comparison."
    except Exception as e:
        return f"An error occured during comparison: {e}"
    
app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_super_secret_key_here_replace_me'

UPLOAD_FOLDER = 'temp_uploads' #creates a variable to handle file upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # this helps to store in app.config

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        # to check if the files are present in the request
        if "pdf1" not in request.files or 'pdf2' not in request.files:
            flash("Please select both PDF files.", 'error')
            return render_template('index.html')
        
        pdf1_file = request.files['pdf1']
        pdf2_file = request.files['pdf2']
        
        # to check if filenames are provided
        if pdf1_file.filename == '' or pdf2_file.filename == '':
            flash("Please select both PDF files.", 'error')
            return render_template('index.html')
        
        filepath1 = None
        filepath2 = None
        comparison_result = "An unknown error occured."

        try:
            # Save files temporarily
            file1 = os.path.join(app.config['UPLOAD_FOLDER'], pdf1_file.filename)
            file2 = os.path.join(app.config['UPLOAD_FOLDER'], pdf2_file.filename)

            pdf1_file.save(file1)
            pdf2_file.save(file2)

            filepath1 = file1
            filepath2 = file2

            print(f"Files saved: {filepath1}, {filepath2}")

            comparison_result = compare_pdfs(filepath1, filepath2)
        
        except Exception as e:
            flash(f"An unexpected error occured: {e}", 'error')
            print(f"Error: {e}")
            comparison_result = f"Error during processing: {e}"
        
        finally:
            if filepath1 and os.path.exists(filepath1):
                os.remove(filepath1)
                print(f"Removed temporary file: {filepath1}")
            if filepath2 and os.path.exists(filepath2):
                os.remove(filepath2)
                print(f"Removed temporary file: {filepath2}")
        
        return render_template('results.html', result=comparison_result)
    
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
