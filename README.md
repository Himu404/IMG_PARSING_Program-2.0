# Image Text Extraction and Parsing

This repository contains a Python script for extracting text from images using the Google Cloud Vision API and then processing the extracted text using Gemini's GenerativeModel. The extracted and processed data is saved into an Excel file for easy access and analysis.

## Features

- Extracts text from images using Google Cloud Vision API.
- Processes extracted text with Gemini's GenerativeModel to retrieve structured data.
- Saves processed data into an Excel file with appropriate labels.
- Handles phone number labels and invalid values gracefully.
- Supports batch processing with automatic saving and cooldown periods to manage API rate limits.

## Requirements

- Python 3.7 or higher
- Google Cloud Vision API credentials
- Gemini AI API credentials

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/image-text-extraction.git
    cd image-text-extraction
    ```

2. **Create and activate a virtual environment (optional but recommended):**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install required packages:**

    ```sh
    pip install -r requirements.txt
    ```

    Create a `requirements.txt` file with the following content:

    ```txt
    google-cloud-vision
    vertexai
    openpyxl
    ```

4. **Set up your Google Cloud Vision API credentials:**

    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project or select an existing one.
    - Enable the Vision API for your project.
    - Create a service account key in JSON format and download it.
    - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your JSON key file:

      ```sh
      export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
      ```

5. **Set up your Gemini AI API credentials:**

    - Follow the instructions provided by Gemini AI to obtain your API key and set it up.

## Usage

1. **Place your images in a folder.**

2. **Update the script with your paths:**

    - Set the `folder_path` variable to the path of your images folder.
    - Set the `json_key_path` variable to the path of your Google Cloud Vision API service account JSON key file.

3. **Run the script:**

    ```sh
    python script.py
    ```

## Script Explanation

- **Extract Text from Image**: The script uses the Google Cloud Vision API to detect and extract text from images.
- **Remove Bracketed Text**: A function to clean up extracted text by removing any text within parentheses.
- **Check Invalid Values**: A function to identify and handle invalid values.
- **Preprocess Gemini Input**: A function to preprocess the extracted text before sending it to the Gemini AI API.
- **Save Progress to Excel**: A function to save the extracted and processed data into an Excel file.
- **Process Images and Parse Response**: The main function that orchestrates the entire workflow from image text extraction to saving the final data into an Excel file.

## Notes

- The script processes images in batches of 10 and includes a cooldown period after every 100 images to manage API rate limits.
- Adjust the `batch_size` and cooldown period as needed based on your requirements and API limits.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.

## Contact

For questions or suggestions, please contact najmulhaqe164@gmail.com.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
