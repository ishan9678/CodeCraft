# Import necessary libraries
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

import os

os.environ.get('HF_TOKEN')

# Hugging Face model name
model_name = "meta-llama/Llama-3.2-1B"

# Load the tokenizer and model from Hugging Face model hub
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Initialize the pipeline for text generation using the Llama model on CPU
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Define a prompt for the model
prompt = "Once upon a time in a small village"

# Generate text based on the prompt using the Llama model
generated_texts = pipe(prompt, max_length=100, num_return_sequences=1)

# Print the generated output
for i, result in enumerate(generated_texts):
    print(f"Generated Text {i+1}: {result['generated_text']}")

