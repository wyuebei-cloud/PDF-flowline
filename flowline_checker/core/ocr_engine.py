from PIL import Image
import cv2
import numpy as np
from google import genai
from google.genai import types
import os
import sys

class OCREngine:
    def __init__(self, api_key=None):
        self.api_key = api_key
        
        # Load API key from file if not explicitly passed
        if not self.api_key:
            if getattr(sys, 'frozen', False):
                # Running as packaged executable, look in same directory as the .exe
                project_root = os.path.dirname(sys.executable)
            else:
                # Running from source, look in project root (3 levels up from this file)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
                
            key_path = os.path.join(project_root, 'api_key.txt')
            
            if os.path.exists(key_path):
                with open(key_path, 'r') as f:
                    self.api_key = f.read().strip()
                    
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            print("WARNING: Gemini SDK requires an API key in api_key.txt to work.")
    
    def preprocess_for_ocr(self, img_path_or_array):
        # Determine if input is path or numpy array
        if isinstance(img_path_or_array, str):
            image = cv2.imread(img_path_or_array)
        else:
            image = img_path_or_array
            
        # 1. Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        res = clahe.apply(gray)
        
        # 3. Upscale if too small (spec says < 100px height)
        height, width = res.shape
        if height < 100:
            res = cv2.resize(res, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
            
        # 4. Binary threshold (Otsu)
        _, thresh = cv2.threshold(res, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh

    def recognize_elevation(self, image_array):
        if self.api_key:
            return self._recognize_with_gemini(image_array)
        else:
            return None, "NO_API_KEY_FOUND", None

    def _recognize_with_gemini(self, image_array):
        # Convert preprocessed numpy array to bytes for Gemini
        is_success, buffer = cv2.imencode(".png", image_array)
        if not is_success:
            return None, "Encoding error", None
            
        img_bytes = buffer.tobytes()
        
        # Define the content to send
        # We specify extracting a single numeric value (elevation)
        prompt = "This is a cropped image from a civil grading plan. Extract the elevation number (it might end with FS). Respond ONLY with the numerical value (e.g., 32.01). If no number is found, respond 'NULL'."
        
        # New SDK supports PIL images directly in the contents
        if len(image_array.shape) == 2:
            pil_img = Image.fromarray(cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB))
        else:
            pil_img = Image.fromarray(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))
        
        # Define fallback models due to API instability
        models_to_try = [
            'gemini-3.1-flash-lite',
            'gemini-2.5-flash-lite',
            'gemini-2.0-flash-lite'
        ]
        
        last_error = ""
        
        for model_name in models_to_try:
            try:
                if '3.1' in model_name:
                    config = types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_level='LOW')
                    )
                else:
                    config = None

                response = self.client.models.generate_content(
                    model=model_name,
                    contents=[prompt, pil_img],
                    config=config
                )
                
                text = response.text.strip()
                if "NULL" in text or not any(c.isdigit() for c in text):
                    return None, text, model_name
                    
                # Clean non-numeric except decimal
                clean_text = "".join(c for c in text if c.isdigit() or c == '.')
                
                try:
                    val = float(clean_text)
                    return val, clean_text, model_name
                except ValueError:
                    return None, clean_text, model_name
                    
            except Exception as e:
                # Capture the error and try the next fallback model
                last_error = str(e)
                continue
                
        # If loop finishes without returning, all models failed
        return None, f"API_ERROR: {last_error}", None

