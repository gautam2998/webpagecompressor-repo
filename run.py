from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import gzip

# Function to fetch and parse a webpage with headers to mimic a browser
def fetch_and_parse(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None, f"Error: Unable to fetch the page (Status Code: {response.status_code})"
    soup = BeautifulSoup(response.content, 'html.parser')

    for tag in soup(['head', 'header', 'footer', 'script', 'style', 'meta']):
        tag.decompose()  # Remove the tag and its contents

    return soup, None

# Function to extract text from webpage
def extract_text(soup):
    text = ''
    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text += tag.get_text(separator=' ', strip=True) + '\n'
    return text

# Function to calculate compression ratio
def calculate_compression_ratio(text):
    original_size = len(text.encode('utf-8'))
    compressed_data = gzip.compress(text.encode('utf-8'))
    compressed_size = len(compressed_data)
    compression_ratio = original_size / compressed_size
    return compression_ratio

# Flask app instance
app = Flask(__name__)

@app.route('/api/analyze-url', methods=['POST'])
def analyze_url():
    # Get URL from request data
    data = request.get_json()
    # url = data.get('url')
    url = data.get('url')
   
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Fetch and parse the webpage
    soup, error = fetch_and_parse(url)
    if error:
        return jsonify({'error': error}), 500

    # Extract text from the webpage
    extracted_text = extract_text(soup)
    if not extracted_text:
        return jsonify({'error': 'No content found on the webpage'}), 404

    # Calculate compression ratio
    compression_ratio = calculate_compression_ratio(extracted_text)
    
    # Return response
    return jsonify({
        'url': url,
        'compression_ratio': round(compression_ratio, 2),
        'original_size': len(extracted_text.encode('utf-8')),
        'compressed_size': len(gzip.compress(extracted_text.encode('utf-8')))
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 