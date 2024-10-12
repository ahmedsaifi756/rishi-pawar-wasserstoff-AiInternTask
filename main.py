import requests
import json
import re
import string
import time
import psutil
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from collections import Counter

# Function to clean text and split into tokens
def preprocess_text(text):
    lower_text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return lower_text.split()

# Function to extract keywords from the text
def find_keywords(text, specific_terms=None, limit=5):
    tokens = preprocess_text(text)
    frequency = Counter(tokens)

    if specific_terms:
        specific_keywords = [word for word in tokens if word in specific_terms]
        if specific_keywords:
            return specific_keywords[:limit]

    return [word for word, _ in frequency.most_common(limit)]

# Function to create a summary based on document length
def generate_summary(text, length_category):
    sentences = text.split('. ')
    if length_category == 'short':
        return sentences[0].strip()  # One sentence for short documents
    elif length_category == 'medium':
        return '. '.join([s.strip() for s in sentences[:3]]).strip()  # Three sentences for medium
    else:
        return '. '.join([s.strip() for s in sentences[:5]]).strip()  # Five sentences for long

# Function to determine the length category of the document
def determine_length_category(text):
    word_count = len(preprocess_text(text))
    if word_count < 100:
        return 'short'
    elif word_count < 500:
        return 'medium'
    else:
        return 'long'

# Function to establish a connection to MongoDB
def initialize_mongodb():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        database = client['pdf_database']
        return database['pdfs']
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        return None

# Function to download a PDF from a given URL
def download_pdf(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Download failed for {url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None

# Simulated text extraction from PDF
def extract_text_from_pdf_content(pdf_content):
    return "Simulated PDF content for testing. This is the second sentence. This is the third sentence. This is the fourth sentence."

# Function to handle processing of each PDF
def handle_pdf(pdf_identifier, url, pdf_collection, specific_terms):
    pdf_data = download_pdf(url)
    if pdf_data:
        text = extract_text_from_pdf_content(pdf_data)
        if text:
            length_category = determine_length_category(text)
            summary = generate_summary(text, length_category)
            keywords = find_keywords(text, specific_terms)
            document = {
                "pdf_key": pdf_identifier,
                "url": url,
                "summary": summary,
                "keywords": keywords,
                "text": text[:500]
            }
            pdf_collection.insert_one(document)
            print(f"Successfully processed and stored {pdf_identifier}")

# Function to load the dataset from a JSON file
def load_json_dataset(file_path):
    try:
        with open(file_path) as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading dataset: {str(e)}")
        return {}

# Function to log performance metrics
def report_performance_metrics(start_time, end_time, total_pdfs):
    duration = end_time - start_time
    cpu_load = psutil.cpu_percent()
    memory_stats = psutil.virtual_memory()

    print("\nPerformance Report:")
    print(f"Total PDFs processed: {total_pdfs}")
    print(f"Processing duration: {duration:.2f} seconds")
    print(f"CPU usage: {cpu_load}%")
    print(f"Memory usage: {memory_stats.percent}%")
    print(f"Available memory: {memory_stats.available / (1024 * 1024):.2f} MB")
    print(f"Used memory: {memory_stats.used / (1024 * 1024):.2f} MB")
    print(f"Total memory: {memory_stats.total / (1024 * 1024):.2f} MB")

# Main function to execute the pipeline
def execute_pipeline():
    start_time = time.time()
    dataset = load_json_dataset('dataset.json')
    pdf_collection = initialize_mongodb()
    if pdf_collection is None:
        return

    specific_terms = ['technology', 'innovation', 'ai', 'development', 'research']

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(handle_pdf, pdf_key, url, pdf_collection, specific_terms) for pdf_key, url in dataset.items()]

    for future in futures:
        future.result()

    end_time = time.time()
    report_performance_metrics(start_time, end_time, len(dataset))

    for pdf in pdf_collection.find():
        print(f"PDF Key: {pdf['pdf_key']}, Summary: {pdf['summary']}, Keywords: {pdf['keywords']}")

if __name__ == "__main__":
    execute_pipeline()
