import openai
import os

# Load your OpenAI API key from an environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def upload_document(file_path):
    """
    Uploads a document to OpenAI and returns the document ID.
    :param file_path: Path to the document to upload
    :return: Document ID
    """
    response = openai.File.create(
        file=open(file_path),
        purpose='answers'
    )
    return response['id']

def query_gpt4(prompt, document_id=None):
    """
    Queries GPT-4 with a given prompt and an optional document.
    :param prompt: Prompt to ask GPT-4
    :param document_id: Uploaded document ID to use as context (optional)
    :return: The response text from GPT-4
    """
    model = "gpt-4"  # or use "text-davinci-003" or other GPT-4 model names
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        documents=[document_id] if document_id else None,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Example Usage
if __name__ == "__main__":
    # Path to your document
    document_path = 'path_to_your_document.txt'
    document_id = upload_document(document_path)
    print(f"Document uploaded with ID: {document_id}")

    # Query GPT-4 with your prompt
    prompt = "Based on the document, summarize the main points."
    response = query_gpt4(prompt, document_id)
    print("GPT-4 Response:", response)
