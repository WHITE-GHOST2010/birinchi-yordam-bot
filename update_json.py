import json

with open('app/body_map_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

mapping = {
    'shoulder': ['left_shoulder', 'right_shoulder'],
    'arm': ['left_arm', 'right_arm'],
    'hand': ['left_hand', 'right_hand'],
    'thigh': ['left_thigh', 'right_thigh'],
    'knee': ['left_knee', 'right_knee'],
    'shin': ['left_shin', 'right_shin'],
    'foot': ['left_foot', 'right_foot']
}

for old_key, new_keys in mapping.items():
    if old_key in data:
        base_data = data[old_key]
        
        left_data = json.loads(json.dumps(base_data))
        t = left_data['title']
        t = t.replace('Yelka', "Chap yelka").replace('Qo\'l', "Chap qo'l").replace('Kaft', 'Chap kaft')
        t = t.replace('Son', 'Chap son').replace('Tizza', 'Chap tizza').replace('Boldir', 'Chap boldir').replace('Panja', 'Chap panja')
        left_data['title'] = t
        data[new_keys[0]] = left_data
        
        right_data = json.loads(json.dumps(base_data))
        t = right_data['title']
        t = t.replace('Yelka', "O'ng yelka").replace('Qo\'l', "O'ng qo'l").replace('Kaft', "O'ng kaft")
        t = t.replace('Son', "O'ng son").replace('Tizza', "O'ng tizza").replace('Boldir', "O'ng boldir").replace('Panja', "O'ng panja")
        right_data['title'] = t
        data[new_keys[1]] = right_data
        
        del data[old_key]

with open('app/body_map_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON successfully updated!")
