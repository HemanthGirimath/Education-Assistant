import google.generativeai as genai
import os
import PyPDF2 


GEMINI_API_KEY = None
GEMINI_MODEL_NAME = 'gemini-2.0-flash'  

def configure_gemini(api_key, model_name):
    """
    Configures the Gemini API with the provided API key and model name.

    Args:
        api_key: Your Google Gemini API key.
        model_name: The name of the Gemini model to use (e.g., 'gemini-pro', 'gemini-1.5-flash-001').
    """
    global GEMINI_API_KEY, GEMINI_MODEL_NAME  # Access global variables
    GEMINI_API_KEY = api_key
    GEMINI_MODEL_NAME = model_name
    genai.configure(api_key=GEMINI_API_KEY)  # Configure right away

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        A string containing the extracted text, or None if an error occurs.
    """
    try:
        with open(pdf_path, 'rb') as file:  # Open in binary read mode
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:  # Iterate through pages
                text += page.extract_text() + "\n"  # Extract text from each page
            return text
    except FileNotFoundError:
        print(f"Error: PDF file not found: {pdf_path}")
        return None
    except Exception as e:
        print(f"Error reading PDF file {pdf_path}: {e}")
        return None

def summarize_files_with_gemini(file_paths):
    """
    Summarizes the content of multiple files using the configured Gemini model.
    Now supports both .txt and .pdf files.

    Args:
        file_paths: A list of strings, where each string is the path to a text file.

    Returns:
        None. Prints the summarized text to the console.  Handles potential errors.
    """
    global GEMINI_API_KEY, GEMINI_MODEL_NAME

    if GEMINI_API_KEY is None or GEMINI_MODEL_NAME is None:
        print("Error: Gemini API not configured. Call configure_gemini() first.")
        return

    try:
        # Select the Gemini model
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)

        # Build the prompt
        prompt_text = "Summarize the following text concisely, capturing the key points:\n\n"

        # Read the content of each file and append to the prompt
        full_text = ""
        for file_path in file_paths:
            try:
                if file_path.lower().endswith('.pdf'):
                    file_content = extract_text_from_pdf(file_path)  # Extract text from PDF
                    if file_content is None:
                        continue  # Skip to the next file if PDF extraction failed
                else: # Assume it's a text file
                    with open(file_path, 'r', encoding='utf-8') as f:  # Handle encoding
                        file_content = f.read()

                full_text += file_content + "\n\n"  # Add separator between files
            except FileNotFoundError:
                print(f"Error: File not found: {file_path}")
                return  # Or continue if you want to process the other files
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return

        if not full_text:
            print("No file content to summarize.")
            return

        prompt = prompt_text + full_text

        # Generate the summary using the Gemini model
        try:
            response = model.generate_content(prompt)
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                print(f"Gemini blocked the response: {response.prompt_feedback.block_reason}")
            else:
                print("Summarized Text:\n", response.text)
        except Exception as e:
            print(f"Error generating summary from Gemini: {e}")


    except Exception as e:
        print(f"An error occurred: {e}")

# Example Usage:  (Replace with your actual file paths and API key)
if __name__ == '__main__':
    # Load API key from environment variable (recommended)
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set. Please set your Gemini API key.")
    else:
        # Configure Gemini with the API key and model name
        configure_gemini(api_key, GEMINI_MODEL_NAME)

        # Get file paths from the user
        file_paths = []
        while True:
            file_path = input("Enter a file path (or type 'done'): ")
            if file_path.lower() == 'done':
                break
            file_paths.append(file_path)

        # Test the function with user-provided file paths
        if file_paths:
            summarize_files_with_gemini(file_paths)
        else:
            print("No file paths provided.  Exiting.")