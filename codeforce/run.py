import os
import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_codeforces_problems():
    url = 'https://codeforces.com/api/problemset.problems'
    response = requests.get(url)
    return response.json()

def fetch_problem_details(contest_id, problem_index):
    url = f'https://codeforces.com/problemset/problem/{contest_id}/{problem_index}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    sample_tests = soup.find_all('div', {'class': 'sample-test'})
    samples = []
    for sample in sample_tests:
        inputs = sample.find('div', {'class': 'input'}).pre.text.strip()
        outputs = sample.find('div', {'class': 'output'}).pre.text.strip()
        samples.append({'input': inputs, 'output': outputs})
    
    return samples

def fetch_problem_submissions(contest_id, problem_index):
    url = f'https://codeforces.com/api/contest.status?contestId={contest_id}&from=1'
    response = requests.get(url)
    
    go_submissions = []

    try:
        submissions_data = response.json()
    except:
        return go_submissions
    
    if submissions_data['status'] == 'OK':
        submissions = submissions_data['result']
        
        for submission in submissions:
            if submission['problem']['index'] == problem_index and submission['programmingLanguage'] == 'Go':
                submission_id = submission['id']
                submission_code = fetch_submission_code(contest_id, submission_id)
                if submission_code is not None:
                  go_submissions.append({'submission_id': submission_id, 'code': submission_code})
    
    return go_submissions

def fetch_submission_code(contest_id, submission_id):
    url = f'https://codeforces.com/contest/{contest_id}/submission/{submission_id}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    source_elememt = soup.find('pre', {'id': 'program-source-text'})
    
    if source_elememt is not None:
      code = source_elememt.text.strip()
    else:
      code = None
    return code

def save_to_jsonl(entry, path):
    with open(path, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def main(path):
    problems_data = fetch_codeforces_problems()
    problem_list = problems_data['result']['problems']
    
    for problem in problem_list:
        contest_id = problem['contestId']
        problem_index = problem['index']
        
        print(f'Fetching data for problem {contest_id}{problem_index}')
        
        samples = fetch_problem_details(contest_id, problem_index)
        
        go_submissions = fetch_problem_submissions(contest_id, problem_index)
        
        entry = {
            'contestId': contest_id,
            'index': problem_index,
            'samples': samples,
            'go_submissions': go_submissions
        }
        
        save_to_jsonl(entry, path)
        
        time.sleep(2)

if __name__ == '__main__':
    path = './codeforces_data.jsonl'
    if os.path.exists(path):
        print(f"File '{path}' already exists. Exiting.")
    else:
        main(path)
