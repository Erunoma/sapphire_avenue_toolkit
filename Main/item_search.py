from traceback import print_exc
from sys import exit
import json
import requests
from pprint import pprint
from datetime import datetime
def get_item_names_from_id():
    items=[]
    with open("data/item_id_names.json",'r') as file:
        item_ids=json.load(file)

    for id in item_ids:
        if item_ids[id]["en"]:
            items.append(item_ids[id]["en"])
    return items


def get_item_id_from_name(item_name):
    with open("data/item_id_names.json",'r') as file:
        item_list=json.load(file)
    for item in item_list:
        #print(f"Checking item id: {item} for {item_name}")
        #print(f"English name of current id: {item_list[item]['en']}")
        if item_list[item]["en"]==item_name:
            new_item_id=item
        else:
            pass
    if new_item_id:
        print(f"Found ID:{new_item_id}")
        return new_item_id
    else:
        print(f"Did not find any ID for {item_name}... returning None")
        return None

def item_lookup(item_id, server):
    listings=[]
    try:
        json_item=requests.get(f"https://universalis.app/api/v2/{server}/{item_id}")
        
        if json_item.status_code==200:
            item_json=json_item.json()
            last_update_time=last_update(item_json)
            pprint(item_json)
            
            for listing in item_json["listings"]:
                listing_data={"retainer_name":listing["retainerName"],"listing_quantity":listing["quantity"],
                              "price_per_unit":listing["pricePerUnit"],"listing_total":listing["total"]}
                
                listings.append(listing_data)
            pprint(listings)

            
    except:
        print("Failed to get result")
        print(print_exc())
    
    
    return [listings, last_update_time]

def find_lowest_price_per_unit(listings):
    lowest_price_per_item=1000000000
    for listing in listings:
        if listing["price_per_unit"]<=lowest_price_per_item:
                    lowest_price_per_item=listing["price_per_unit"]
    return lowest_price_per_item

def last_update(json_item):
    print(json_item["lastUploadTime"])
    last_time_epoch=json_item["lastUploadTime"]
    
    
    converted_timestamp=datetime.fromtimestamp(last_time_epoch / 1000)
    converted_timestamp=converted_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return converted_timestamp
    

def find_item_icon_id(item_id):
    try:
        data=requests.get(f"https://xivapi.com/item/{item_id}")
        if data.status_code==200:
            print("Searching data for ID...")
            json_data=data.json()
            icon_id=json_data["IconID"]
            return icon_id
        else:
            raise Exception
    except:
        print(print_exc)
        return None
    
