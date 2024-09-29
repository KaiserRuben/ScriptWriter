from typing import Dict, Any


def compare_scene_numbers(scene_num1: str, scene_num2: str) -> int:
    # Convert scene numbers to lists of integers
    num1 = list(map(int, scene_num1.split('.')))
    num2 = list(map(int, scene_num2.split('.')))

    # Pad the shorter list with zeros
    max_length = max(len(num1), len(num2))
    num1 += [0] * (max_length - len(num1))
    num2 += [0] * (max_length - len(num2))

    # Compare the lists
    if num1 < num2:
        return -1
    elif num1 > num2:
        return 1
    else:
        return 0


def sort_json_content(json_data: Dict[str, Any]) -> Dict[str, Any]:
    # Sort acts
    json_data['acts'] = sorted(json_data['acts'], key=lambda x: x['act_number'])

    # Sort scenes and sub-scenes within each act
    for act in json_data['acts']:
        act['scenes'] = sorted(act['scenes'], key=lambda x: float(x['scene_number']))

        for scene in act['scenes']:
            if 'sub_scenes' in scene:
                scene['sub_scenes'] = sorted(scene['sub_scenes'], key=lambda x: x['sub_scene_number'])

    return json_data
