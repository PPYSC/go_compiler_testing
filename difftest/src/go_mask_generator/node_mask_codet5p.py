from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch


class NodeMaskCodet5p:
    def __init__(self):
        self.checkpoint1 = "/home/shareduser/ysc/go_compiler_testing/rlgo/src/generator/huggingface_cache/models--Salesforce--codet5p-220m/snapshots/bcef69c847f3218e9f980baadad708efdffb2541"
        self.checkpoint2 = "/home/shareduser/ysc/go_compiler_testing/rlgo/src/generator/saved_model/checkpoint-77300"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint1, cache_dir="/home/shareduser/ysc/go_compiler_testing/rlgo/src/generator/huggingface_cache")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.checkpoint2).to(self.device)

    def generate(self, masked_code):
        encoding = self.tokenizer(masked_code, return_tensors="pt").to(self.device)
        outputs = self.model.generate(do_sample=True, **encoding, max_new_tokens=60)
        code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return code
