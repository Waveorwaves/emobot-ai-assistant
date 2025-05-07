# test_gemini_connection.py
import os
import google.generativeai as genai

def test_gemini():
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyBVAnfJ2pBNIliT7N2evGM16c7SZwtiUio")
    model_name = os.environ.get("GEMINI_MODEL", "models/gemini-2.5-pro-exp-03-25")
    
    print(f"Testing Gemini API with model: {model_name}")
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    try:
        # Create model
        model = genai.GenerativeModel(model_name)
        
        # Generate content (synchronous)
        response = model.generate_content("Hello, Gemini! Please respond with a short greeting.")
        
        print("Success! Gemini responded with:")
        print(response.text)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_gemini()