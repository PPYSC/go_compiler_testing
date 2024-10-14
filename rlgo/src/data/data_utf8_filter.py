import json

def filter_valid_utf8_lines(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            try:
                # 尝试解码为 JSON 格式
                data = json.loads(line)
                # 尝试访问并解码 "code" 字段
                if isinstance(data, dict) and "code" in data:
                    code = data["code"]
                    # 尝试编码为 utf-8 来检查是否有无效字节
                    code.encode('utf-8')
                # 写入新文件
                outfile.write(line)
            except (UnicodeDecodeError, json.JSONDecodeError):
                # 跳过无法解码的行
                continue

input_path = '/home/shareduser/ysc/go_compiler_testing/rlgo/src/data/data_go_testcase_nocomment_token_size_filtered.jsonl'
output_path = '/home/shareduser/ysc/go_compiler_testing/rlgo/src/data/data_go_testcase_nocomment_token_size_utf8_filtered.jsonl'

filter_valid_utf8_lines(input_path, output_path)