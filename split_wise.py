from splitwise import Splitwise
import requests
import json
import pandas as pd



request_url = "https://secure.splitwise.com/api/v3.0/"
def send_info_to_splitwise(df, payer, group_name, total_cost, place, date):
    curr_name_info = requests.get(
        request_url + "get_current_user",
        headers={
            "Authorization": "Bearer Qbp3qYfUCOkoGOcXwz5AyVqSdgDDymTtdg8sZVwP"
        }
    ).json()["user"]
    
    cost_breakdown = {row["Name"]: row["Cost"] for index, row in df.iterrows()}
    print(cost_breakdown)
    
    friend_list = requests.get(
        request_url + "get_friends",
        headers={
            "Authorization": "Bearer Qbp3qYfUCOkoGOcXwz5AyVqSdgDDymTtdg8sZVwP"
        }
    )
    # print(json.dumps(friend_list.json(), indent=4))
    
    name_id_dict = {}
    name_set = set(map(str.lower,cost_breakdown.keys()))
    if curr_name_info["first_name"] in cost_breakdown.keys():
        name_id_dict[curr_name_info["first_name"]] = curr_name_info["id"]
        name_set.remove(curr_name_info["first_name"].lower())
    
    # print(name_set)
    for friend_info in friend_list.json()["friends"]:
        if friend_info["first_name"].lower() in name_set:
            name_id_dict[friend_info["first_name"]] = friend_info["id"]
            name_set.remove(friend_info["first_name"].lower())
    # print("After iteration: " + str(name_set))
    # print(str(name_id_dict))
    if len(name_set) > 0:
        raise ValueError("The following names do not have splitwise: " + str(name_set))
    
    
    group_list = requests.get(
        request_url + "/get_groups",
        headers={
            "Authorization": "Bearer Qbp3qYfUCOkoGOcXwz5AyVqSdgDDymTtdg8sZVwP"
        }
    )
    
    # print(json.dumps(group_list.json(), indent = 2))
    group_id = -1
    for group_info in group_list.json()["groups"]:
        if group_info["id"] == 0:
            continue
        if group_info["name"] == group_name:
            group_id = group_info["id"]
            break
    if group_id == -1:
        request_body = {}
        request_body["name"] = group_name
        count = 0
        for name_id in name_id_dict.values():
            user_format = f"users__{count}__id"
            request_body[user_format] = name_id
            count += 1
        print(json.dumps(request_body, indent=2))
        create_group_request = requests.post(
            request_url + "create_group",
            json=request_body,
            headers={
                "Authorization": "Bearer Qbp3qYfUCOkoGOcXwz5AyVqSdgDDymTtdg8sZVwP"
            }
        ).json()
        group_id = create_group_request["group"]["id"]
    group_name_info = requests.get(
        request_url + "/get_group/" + str(group_id),
        headers={
            "Authorization": "Bearer Qbp3qYfUCOkoGOcXwz5AyVqSdgDDymTtdg8sZVwP"
        }
    ).json()
    print(json.dumps(group_name_info, indent=2))
    
    request_body = {}
    request_body["group_id"] = group_id
    request_body["cost"] = str(total_cost)
    request_body["description"] = f"{place}: {date}"
        
    count = 0
    for name in cost_breakdown.keys():
        user_format = f"users__{count}__"
        request_body[f"{user_format}user_id"] = name_id_dict[name]
        print(name_id_dict)
        request_body[f"{user_format}paid_share"] = str(total_cost) if payer == name else "0"
        
        request_body[f"{user_format}owed_share"] = str(cost_breakdown[name])
        
        count += 1
    print(request_body)
    
    add_expense_request = requests.post(
        request_url + "create_expense",
        json=request_body,
        headers={
            "Authorization": "Bearer Qbp3qYfUCOkoGOcXwz5AyVqSdgDDymTtdg8sZVwP"
        }
    ).json()
    
    print(json.dumps(add_expense_request, indent=4))
    
    # for name, name_id in name_id_dict.items():
        
    # for name in cost_breakdown.keys():
        
    