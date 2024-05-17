from traceback import print_exc
from sys import exit
import json
import requests
from pprint import pprint
import pyxivapi
import item_search

def find_recipe(item_name,item_id, server):
    
    try:
        print("Searching XIVAPI for item...")
        data=requests.get(f"https://xivapi.com/item/{item_id}")
        if data.status_code==200:
            
            print("Searching data for recipe ID...")
            json_data=data.json()
        
            
            recipe_id=json_data["GameContentLinks"]["Recipe"]["ItemResult"]
            if recipe_id:
                print(f"Found ID: {recipe_id[0]}")
                recipe_data=requests.get(f"https://xivapi.com/recipe/{recipe_id[0]}")
                if recipe_data:
                    print("Searching recipe data for components...")
                    recipe_json=recipe_data.json()
                    ingredient_values= {key: value for key, value in recipe_json.items() if key.startswith("AmountIngredient") and value >0}
                    print(f"extracted this recipe amount:{ingredient_values}")
                    
                    print("Searching first component...")
                    #Has {id : amount}
                    
                    

                    component_ids=[]
                    ingredient_amounts=[]
                    for key in ingredient_values:
                        ingredient_amounts.append(ingredient_values[key])

                    for key in ingredient_values:
                        ingredient_search_number=int(key.split("AmountIngredient")[1])
                        print(f"Search number are as follows: {ingredient_search_number}")
                        component_ids.append(recipe_json[f"ItemIngredient{ingredient_search_number}"]["ID"])
                    component_names=[]

                    for component in component_ids:
                        component_names.append(find_component_name(component))  
                    print(f"Component ids: {component_ids}, ingredient amounts: {ingredient_amounts}")

                    components_lowest_price=[]
                    for component in component_ids:
                        
                        item_listing=item_search.item_lookup(component,server)
                        
                        lowest_price=item_search.find_lowest_price_per_unit(item_listing[0])
                        components_lowest_price.append(lowest_price)

                    components_icon_paths=[]
                    for component in component_ids:

                        icon_id=item_search.find_item_icon_id(component)
                        print(f"Icon ID: ")
                        components_icon_paths.append(find_picture_path(icon_id))
                    component_information_tuple=[x for x in zip(component_ids,ingredient_amounts,component_names,components_lowest_price, components_icon_paths)]
                        
                    print(f"This is the final info: {component_information_tuple}")
                    return component_information_tuple
                else:
                    raise Exception
            else:
                raise Exception
        else:
            raise Exception
    except:
        print(print_exc())
        return None
    pass




def pad(num, length, pad_left):
    return length * (num - len(pad_left)) + pad_left



def find_picture_path(icon_id):
    #Pathing funktionen her er blevet oversat delvist til Python via ChatGPT fra kilde: https://xivapi.com/docs/Icons
    icon_id=str(icon_id)
    print(f"Searching for path to item with Icon ID: {icon_id}")
    
    # Check the length of icon_id
    if len(icon_id) >= 6:
        icon_id = pad(5, "0", icon_id)
    else:
        icon_id = '0' + pad(5, "0", icon_id)

    # Now we can build the folder from the padded icon_id
    if len(icon_id) >= 6:
        folder_id = icon_id[0] + icon_id[1] + icon_id[2] + '000'
    else:
        folder_id = '0' + icon_id[1] + icon_id[2] + '000'

    # Concatenate the folder_id and icon_id to form the path
    path = 'static/icons/' + folder_id + '/' + icon_id + '.png'
    print(path)
    return path



def find_component_name(id):
    with open("data/item_id_names.json",'r') as file:
        item_json=json.load(file)
        print(f"Returning name of {id}: {item_json[f'{id}']['en']}")
        
        return item_json[f"{id}"]["en"]
    pass