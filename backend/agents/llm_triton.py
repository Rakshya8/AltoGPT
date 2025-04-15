from transformers import AutoTokenizer
import numpy as np
import requests
import json

class TritonPhi2Client:
    def __init__(self, triton_url: str):
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2")
        self.triton_url = triton_url.rstrip("/")
        self.model_name = "phi-2"

    def invoke(self, prompt: str):
        tokens = self.tokenizer(prompt, return_tensors="np", padding=True)
        input_ids = tokens["input_ids"].astype(np.int32)

        # Prepare request
        inputs = [{
            "name": "input_ids",
            "shape": list(input_ids.shape),
            "datatype": "INT32",
            "data": input_ids.tolist()
        }]
        outputs = [{"name": "logits"}]

        payload = {
            "inputs": inputs,
            "outputs": outputs
        }

        infer_url = f"{self.triton_url}/v2/models/{self.model_name}/infer"
        response = requests.post(infer_url, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"Inference failed: {response.text}")

        result = response.json()
        logits = np.array(result["outputs"][0]["data"]).reshape(input_ids.shape + (-1,))
        predicted_ids = np.argmax(logits, axis=-1)

        output_text = self.tokenizer.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        return type("LLMResponse", (), {"content": output_text})()
