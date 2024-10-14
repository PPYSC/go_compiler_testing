import json

def process_jsonl(path, dst_path):
    with open(path, 'r', encoding='utf-8') as infile, open(dst_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = json.loads(line)
            submissions = data.get('go_submissions', [])
            samples = data.get('samples', [])
            contest_id = data.get('contestId')
            index = data.get('index')

            if len(samples) == 0 and len(submissions) != 0:
                print(f'contestId: {contest_id}, index: {index}')
            else:
                for submission in submissions:
                    result = {
                        "code": submission.get("code", ""),
                        "samples": samples
                    }
                    outfile.write(json.dumps(result) + '\n')

path = './codeforces_data.jsonl'
dst_path = './proceed_data.jsonl'
process_jsonl(path, dst_path)
