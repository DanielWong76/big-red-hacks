from gradio_client import Client

client = Client("DanielWong76/unspool")

def call_llm(instruction, input):
    result = client.predict(
		instruction=instruction,
		input_text=input,
		api_name="/predict"
    )
    return result