# File: src/gemini_python_app/main.py

from flask import Flask, jsonify
import os
from google.cloud import storage, firestore

# Initialize the Flask application with the package name.
app = Flask("gemini_python_app")

# --- Google Cloud Client Initialization ---
# These clients will automatically use Application Default Credentials (ADC)
# when running locally or the service account when deployed to Cloud Run.

# Initialize a Cloud Storage client
storage_client = storage.Client()

# Initialize a Firestore client
firestore_client = firestore.Client()

# --- Configuration (Optional, but good practice for dynamic values) ---
# You can set these as environment variables in Cloud Run for production
# For local testing, you can hardcode them or use a .env file (not covered here for brevity)
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "my-gemini-app-data-bucket-123") # REPLACE with your actual bucket name
FIRESTORE_COLLECTION_NAME = os.environ.get("FIRESTORE_COLLECTION_NAME", "my_data")

@app.route('/')
def hello_world():
    """
    Simple Flask route that returns a greeting.
    """
    port = int(os.environ.get("PORT", 8080))
    return f"Hello from Gemini project on Cloud Run! Listening on port {port}"

@app.route('/storage_example')
def storage_example():
    """
    Demonstrates listing objects in a Google Cloud Storage bucket.
    """
    try:
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blobs = bucket.list_blobs(max_results=5) # List up to 5 objects

        object_names = [blob.name for blob in blobs]
        return jsonify({
            "status": "success",
            "message": f"Successfully listed objects from bucket '{GCS_BUCKET_NAME}'",
            "objects": object_names
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to access Cloud Storage: {str(e)}"
        }), 500

@app.route('/firestore_example')
def firestore_example():
    """
    Demonstrates adding and retrieving data from Firestore.
    """
    collection_ref = firestore_client.collection(FIRESTORE_COLLECTION_NAME)
    try:
        # Add a new document
        doc_ref = collection_ref.add({
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Hello from Flask app!'
        })
        new_doc_id = doc_ref[1].id # doc_ref is a tuple (update_time, document_reference)

        # Retrieve documents
        docs = collection_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(3).stream()
        data = []
        for doc in docs:
            doc_dict = doc.to_dict()
            doc_dict['id'] = doc.id
            # Convert Firestore Timestamp to string for JSON serialization if present
            if 'timestamp' in doc_dict and hasattr(doc_dict['timestamp'], 'isoformat'):
                doc_dict['timestamp'] = doc_dict['timestamp'].isoformat()
            data.append(doc_dict)

        return jsonify({
            "status": "success",
            "message": f"Added document with ID: {new_doc_id}. Retrieved recent documents.",
            "recent_data": data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to access Firestore: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("Running Flask app locally...")
    # IMPORTANT: Replace "your-unique-gemini-bucket-name" with your actual GCS bucket name
    # You can set environment variables for local testing like this:
    # os.environ["GCS_BUCKET_NAME"] = "your-unique-gemini-bucket-name"
    # os.environ["FIRESTORE_COLLECTION_NAME"] = "my_data"
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))