import torch
from transformers import RobertaTokenizer

from data_io.file_io import data_from_jsonl, data_to_jsonl_append


MODEL_PATH = "/bigdata/qiuhan/go_dt/codet5-small-go_generation_v2"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = RobertaTokenizer.from_pretrained(MODEL_PATH)
model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH).to(device)

SEED_PATH = "/bigdata/qiuhan/go_dt/tmp_model/seed.jsonl"
RST_PATH = "/bigdata/qiuhan/go_dt/tmp_model/rst.jsonl"


for i, src_line in enumerate(data_from_jsonl(SEED_PATH)):
    for j in range(0, 10):
        input_ids = tokenizer.encode(src_line["input"], return_tensors="pt").to(self.device)
        output = model.generate(input_ids=input_ids, max_new_tokens=256)
        output_text = tokenizer.decode(output[0], skip_special_tokens=True)
        #data_to_jsonl_append(RST_PATH, {"id": f"{i}_{j}", "output": output_text})
        print({"id": f"{i}_{j}", "output": output_text})

