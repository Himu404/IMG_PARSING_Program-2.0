import io
import os
import time  # Import the time module
from google.cloud import vision
from vertexai.generative_models import GenerativeModel
import re
import openpyxl

# Update with your actual project ID
project_id = "GOOGLE_PROJECT_ID"

# Initialize GenerativeModel
model = GenerativeModel(model_name="gemini-1.5-flash-001")

# Label mapping for phone numbers
phone_labels = ["fax", "phone", "phone 1", "phone 2", "phone 3", "home phone", "cell phone", "business"]
phone_standard_labels = ["Phone-1", "Phone-2", "Phone-3"]

phone_label_mapping = {}
for idx, label in enumerate(phone_labels):
    if idx < len(phone_standard_labels):
        phone_label_mapping[label.lower()] = phone_standard_labels[idx]

# Function to extract text from image using Google Cloud Vision API
def extract_text_from_image(image_path, client):
    try:
        # Loads the image into memory
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        # Performs text detection on the image file
        response = client.text_detection(image=image)
        texts = response.text_annotations

        # Extract and return only the first text annotation (formatted text)
        if texts:
            return texts[0].description.strip()

    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None

# Function to remove text within parentheses
def remove_bracketed_text(text):
    return re.sub(r'\s*\([^)]*\)\s*', '', text)

# Function to check if a value is invalid
def is_invalid_value(value):
    value = value.strip()
    return value == '' or value == 'N/A' or value == '9' * len(value) or re.match(r'\(.*\)', value)

# Function to preprocess Gemini input text
def preprocess_gemini_input(text, label_mapping):
    for label, standard_label in label_mapping.items():
        text = re.sub(rf'\*\*{label.capitalize()}:\*\*', f'**{standard_label}:**', text)
    return text

# Function to save progress to Excel file
def save_progress_to_excel(wb, file_path):
    try:
        wb.save(file_path)
        print(f"Progress saved to {file_path}")
    except Exception as e:
        print(f"Error saving progress to Excel: {e}")

# Function to process images and parse the combined response
def process_images_and_parse_response(image_paths, json_key_path):
    try:
        # Set the environment variable for authentication
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = json_key_path

        # Initialize Vision API client
        client = vision.ImageAnnotatorClient()

        # Initialize Excel workbook and worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Serial Number", "Image Name", "First Name", "Last Name", "Address", "City", "State", "Zip", "E-mail", "Phone-1", "Phone-2", "Phone-3", "Owner ID"])

        # List to store extracted texts from all images
        all_extracted_texts = []

        # Define the Excel file path
        excel_file_path = os.path.join(os.path.dirname(image_paths[0]), "extracted_details.xlsx")

        # Process images in batches of maximum 10
        batch_size = 10
        serial_number = 1
        for i in range(0, len(image_paths), batch_size):
            batch_image_paths = image_paths[i:i+batch_size]  # Get a batch of up to 10 images

            # Extract text from each image and collect in all_extracted_texts
            for image_path in batch_image_paths:
                extracted_text = extract_text_from_image(image_path, client)
                if extracted_text:
                    all_extracted_texts.append(extracted_text)
                else:
                    print(f"Failed to extract text from image: {image_path}")

            # Check if the batch size is reached or it's the last batch
            if len(all_extracted_texts) >= batch_size or i + batch_size >= len(image_paths):
                # Combine all extracted texts into a single request payload for Gemini
                combined_text = "\n\n".join(all_extracted_texts)  # Separate each image's text with double newline

                # Preprocess combined text for Gemini
                processed_text = preprocess_gemini_input(combined_text, phone_label_mapping)

                # Print processed text before sending to Gemini
                print(f"Processed Text for Gemini (Batch {i//batch_size + 1}):\n{processed_text}")

                try:
                    # Example: Generate content using processed_text with Gemini
                    response = model.generate_content(
                        f"""
                        {processed_text}
                        Please provide the following details for all owner records:
                        **First Name:** 
                        **Last Name:** 
                        **Address:** 
                        **City:** 
                        **State:** 
                        **Zip:** 
                        **E-mail:** 
                        **Phone-1:** 
                        **Phone-2:** 
                        **Phone-3:** 
                        **Owner ID:** 
                        """
                    )
                    generated_text = response.text.strip()
                except Exception as e:
                    print(f"Error generating content with Gemini: {e}")
                    continue

                # Extract and print all fields from Gemini response, replacing invalid values with spaces
                fields = ["First Name", "Last Name", "Address", "City", "State", "Zip", "E-mail", "Phone-1", "Phone-2", "Phone-3", "Owner ID"]
                values_dict = {field: [] for field in fields}
                for field in fields:
                    values = re.findall(rf'\*\*{field}:\*\* (.*?)$', generated_text, re.MULTILINE)
                    for value in values:
                        clean_value = remove_bracketed_text(value.strip())
                        if is_invalid_value(clean_value):
                            clean_value = ""  # Replace invalid values with a space
                        values_dict[field].append(clean_value)

                    print(f"Extracted {field}s:")
                    for idx, value in enumerate(values_dict[field]):
                        print(f"{idx + 1}. {value}")

                # Write extracted data to Excel worksheet
                for idx, image_path in enumerate(batch_image_paths):
                    image_name = os.path.basename(image_path)
                    ws.append([serial_number, image_name] + [values_dict[field][idx] if idx < len(values_dict[field]) else "" for field in fields])
                    serial_number += 1

                # Clear the list for the next batch
                all_extracted_texts = []

                # Save progress after each batch
                save_progress_to_excel(wb, excel_file_path)

                # Introduce a 30-second cooldown after every 10 batches
                if (i + batch_size) % (batch_size * 10) == 0:
                    print(f"Cooldown for 30 seconds to manage Vertex AI API rate limits...")
                    time.sleep(60)  # Sleep for 30 seconds

        # Save final Excel file
        save_progress_to_excel(wb, excel_file_path)
        print(f"\nFinal Excel file saved: {excel_file_path}")

    except Exception as e:
        print(f"Error processing images and generating content: {e}")

# Example usage
if __name__ == "__main__":
    # Path to the folder containing images
    folder_path = r'C:\Users\Himu\Desktop\test'

    # Path to your service account key JSON fil
    json_key_path = r'GOOGLE_APPLICATION_CREDENTIALS'

    # List all image paths in the folder
    image_paths = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path)
                   if filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Process images and generate content using Gemini
    process_images_and_parse_response(image_paths, json_key_path)
