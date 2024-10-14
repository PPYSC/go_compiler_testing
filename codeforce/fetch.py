import os
import requests
from bs4 import BeautifulSoup
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_codeforces_problems():
    url = 'https://codeforces.com/api/problemset.problems'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching problems: {e}")
        return {'result': {'problems': []}}

def fetch_problem_details(contest_id, problem_index):
    url = f'https://codeforces.com/problemset/problem/{contest_id}/{problem_index}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        sample_tests = soup.find_all('div', {'class': 'sample-test'})
        samples = []
        for sample in sample_tests:
            inputs = sample.find('div', {'class': 'input'}).pre.text.strip()
            outputs = sample.find('div', {'class': 'output'}).pre.text.strip()
            samples.append({'input': inputs, 'output': outputs})
        
        return samples
    except requests.RequestException as e:
        logging.error(f"Error fetching problem details: {e}")
        return []

def fetch_problem_submissions(contest_id, problem_index):
    url = f'https://codeforces.com/api/contest.status?contestId={contest_id}&from=1'
    try:
        response = requests.get(url)
        response.raise_for_status()
        submissions_data = response.json()
        
        if submissions_data['status'] == 'OK':
            submissions = submissions_data['result']
            
            go_submissions = []
            for submission in submissions:
                if submission['problem']['index'] == problem_index and submission['programmingLanguage'] == 'Go':
                    submission_id = submission['id']
                    submission_code = fetch_submission_code(contest_id, submission_id)
                    if submission_code is not None:
                        go_submissions.append({'submission_id': submission_id, 'code': submission_code})
                    time.sleep(6)
                    
            return go_submissions
        else:
            logging.warning(f"Non-OK response status: {submissions_data['status']}")
            return []
    except requests.RequestException as e:
        logging.error(f"Error fetching problem submissions: {e}")
        return []

def fetch_submission_code(contest_id, submission_id):
    url = f'https://codeforces.com/contest/{contest_id}/submission/{submission_id}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        source_element = soup.find('pre', {'id': 'program-source-text'})
        if source_element is not None:
            return source_element.text.strip()
        else:
            logging.warning(f"No code found for submission {submission_id}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error fetching submission code: {e}")
        return None

def save_to_jsonl(entry, path):
    try:
        with open(path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except IOError as e:
        logging.error(f"Error saving to file: {e}")

def main(path):
    problems_data = fetch_codeforces_problems()
    problem_list = problems_data['result']['problems']
    
    for problem in problem_list:
        contest_id = problem['contestId']
        problem_index = problem['index']
        
        logging.info(f'Fetching data for problem {contest_id}{problem_index}')
        
        samples = fetch_problem_details(contest_id, problem_index)
        go_submissions = fetch_problem_submissions(contest_id, problem_index)
        
        entry = {
            'contestId': contest_id,
            'index': problem_index,
            'samples': samples,
            'go_submissions': go_submissions
        }
        
        save_to_jsonl(entry, path)
        
        time.sleep(1)

if __name__ == '__main__':
    path = './codeforces_data.jsonl'
    if os.path.exists(path):
        logging.info(f"File '{path}' already exists. Exiting.")
    else:
        main(path)