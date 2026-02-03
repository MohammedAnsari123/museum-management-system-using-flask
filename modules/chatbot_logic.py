import os

# Try to import ML libraries, handle missing libs for non-GPU/Low-Memory environments
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("WARNING: ML libraries (torch/transformers) not found. Chatbot will be disabled.")

# Default to a smaller model for cloud deployment if local is missing
CLOUD_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
LOCAL_MODEL_PATH = os.path.join(os.getcwd(), "models", "qwen_1_8b_chat")

_generator = None

def get_generator():
    """
    Lazily initializes the text generation pipeline.
    Checks for local model first, then falls back to Hugging Face Hub.
    """
    global _generator
    
    if not ML_AVAILABLE:
        return None

    if _generator is None:
        try:
            # Determine which model to load
            if os.path.exists(LOCAL_MODEL_PATH):
                model_source = LOCAL_MODEL_PATH
                print(f"Loading Local AI Model: {model_source}...")
            else:
                model_source = CLOUD_MODEL_ID
                print(f"Local model not found. Downloading/Loading Cloud AI Model: {model_source}...")
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {device}")

            # Use float16 for GPU, float32 for CPU (or bfloat16 if supported)
            torch_dtype = torch.float16 if device == "cuda" else torch.float32
            
            _generator = pipeline(
                "text-generation",
                model=model_source,
                torch_dtype=torch_dtype,
                device_map="auto"
            )
            print(f"AI Model {model_source} loaded successfully.")
            
        except Exception as e:
            print(f"CRITICAL: Failed to load AI model. {e}")
            return None
            
    return _generator

def is_domain_relevant(query):
    """
    Checks if the query is related to the museum domain.
    """
    query_lower = query.lower()
    
    domain_keywords = [
        'museum', 'art', 'history', 'ticket', 'booking', 'price', 
        'entry', 'location', 'time', 'guide', 'tour', 'exhibit', 
        'gallery', 'statue', 'painting', 'ancient', 'culture', 
        'heritage', 'india', 'delhi', 'mumbai', 'payment', 'cost',
        'open', 'close', 'map', 'contact', 'address', 'recommend',
        'place', 'visit', 'best', 'famous'
    ]
    
    allow_list = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'help', 'who are you', 'thank', 'thanks']
    
    if any(word in query_lower for word in allow_list):
        return True
        
    return any(keyword in query_lower for keyword in domain_keywords)

def get_chatbot_response(query, history=None):
    """
    Generates a response using the loaded model.
    """
    if not query:
        return "I didn't catch that. Could you please repeat?"

    if not is_domain_relevant(query):
        return "I specialize in Indian museums and history. Please ask me about museum visits, tickets, or historical artifacts!"

    if not ML_AVAILABLE:
        return "I am currently in 'Lite Mode' due to server limits. The AI Brain is disabled, but you can still use the Booking and Museum features!"

    generator = get_generator()
    if generator is None:
        return "I'm currently downloading my brain updates (Model Loading) or the AI is unavailable. Please try again in a minute!"

    messages = [
        {
            "role": "system",
            "content": (
                "You are PixelPast AI, a helpful and knowledgeable Museum Guide for Indian Museums. "
                "Keep your answers concise (under 100 words). "
                "Only answer questions about museums, history, culture, and tickets. "
                "If asked about other topics, politely decline."
            )
        },
        {"role": "user", "content": query}
    ]

    try:
        prompt = generator.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        outputs = generator(
            prompt,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95
        )

        generated_text = outputs[0]["generated_text"]

        # Parse logic dependent on model output format, generally works for Qwen/Chat models
        if "<|im_start|>assistant" in generated_text:
            response = generated_text.split("<|im_start|>assistant")[-1].strip()
        else:
            # Fallback for models that might just append
            # Try to remove the prompt from the start
            if generated_text.startswith(prompt):
                 response = generated_text[len(prompt):].strip()
            else:
                 response = generated_text

        return response

    except Exception as e:
        print(f"Inference Error: {e}")
        return "I'm having trouble thinking right now. Please try again."
