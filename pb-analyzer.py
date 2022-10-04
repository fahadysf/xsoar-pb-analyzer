#!/usr/bin/env python3

import argparse
import json
import yaml


# Setup Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--playbook',
                    required=True,
                    action='store',
                    dest='pb_path',
                    help='Base Playbook to Analyze'
                    )
parser.add_argument('-c', '--contentpath',
                    required=True,
                    action='store',
                    dest='content_path',
                    help='Content folder (Extracted Content Pack \
                        or Bundle Directory)'
                    )
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help='Verbose Output'
                    )
args = parser.parse_args()

# Analysis Output Structure
# Example..
'''
results = {
    'base_tasks': 0,
    'branchingdepth': 0,
    'subplaybooks': 0,
    'subplaybookdepth': 0,
    'subplaybook_list': [],
    'task_by_type': {
        'automation': 0,
        'integration_command': 0,
        'manual': 0,
        'conditional': 0
    },
    'branch_analysis': {}  # Nested Analysis of Branches and sub-playbooks
}
'''


def read_yaml(path: str):
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def analyze_task_types(tasks: str):
    """_summary_

    Args:
        tasks (_type_): _description_
    """
    tasks_by_type = dict()
    tasks_by_type['regular_tasks_breakdown'] = dict()
    tasks_by_type['regular_tasks_breakdown']['commands'] = {
        "count": 0,
        "script_set": list()
    }
    tasks_by_type['regular_tasks_breakdown']['automations'] = dict()
    tasks_by_type['regular_tasks_breakdown']['automations'] = {
        "count": 0,
        "script_set": list()
    }
    for k in tasks.keys():
        t = tasks[k]
        if not t['type'] in tasks_by_type.keys():
            tasks_by_type[t['type']] = 1
        else:
            tasks_by_type[t['type']] += 1

        # Do some analysis on regular tasks
        if t['type'] == 'regular':
            if t['task']['iscommand']:
                tasks_by_type['regular_tasks_breakdown']['commands']['count'] += 1
                if 'script' in t['task'].keys():
                    tasks_by_type['regular_tasks_breakdown']['commands']['script_set'].append(
                        t['task']['script']
                    )
            else:
                tasks_by_type['regular_tasks_breakdown']['automations']['count'] += 1
                if 'script' in t['task'].keys():
                    tasks_by_type['regular_tasks_breakdown']['automations']['script_set'].append(
                        t['task']['script']
                    )
    # Remove duplicates from script_sets
    css = tasks_by_type['regular_tasks_breakdown']['commands']["script_set"]
    tasks_by_type['regular_tasks_breakdown']['commands']["script_set"] = list(
        set(css))
    oss = tasks_by_type['regular_tasks_breakdown']['automations']["script_set"]
    tasks_by_type['regular_tasks_breakdown']['automations']["script_set"] = list(
        set(oss))
    return tasks_by_type


def analyze_playbook(pb_path: str = args.pb_path,
                     content_path: str = args.content_path,
                     branch_analysis: bool = True):
    """_summary_

    Args:
        pb_path (str, optional):
            Base Playbook Path. Defaults to args.pb_path.
        content_path (str, optional):
            Extracted content pack or bundle directory.
            Defaults to args.content_path.
        branch_analysis (bool, optional):
            Flag to analyze branches. Defaults to True.

    Returns:
        dict: Results dictionary
    """
    data = read_yaml(pb_path)
    print(f'Playbook path: {pb_path}')
    print(f'Content path: {content_path}')
    results = dict()
    results['base_tasks'] = len(data['tasks'])
    results['tasks_by_type'] = analyze_task_types(data['tasks'])
    return results


if __name__ == '__main__':
    try:
        results = analyze_playbook(pb_path=args.pb_path)
        print(json.dumps(results, indent=2, sort_keys=True))
        exit(0)
    except Exception:
        raise
        exit(1)
