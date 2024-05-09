#Installed modules
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from traceback import print_exc
from sys import exit
from pprint import pprint
import json
import requests

#Own Modules
import item_search
import crafting_calculator

is_local=True

app = Flask(__name__, template_folder='html')

def start():
    try:
        if is_local==True:
            app.run(host='localhost', port=43435)
        else:
            app.run(host='0.0.0.0', port=43435)
    except:
        print(print_exc())
        exit()
        

@app.route("/main")
def main():
    return render_template("front_page.html")

@app.route("/item_search", methods=['GET','POST'])
def item_searching():
    item_list=item_search.get_item_names_from_id()
    try:
        if request.args.get('search'):

            item_name=request.args.get('search')
            #TODO: Put up a request per IP per minute lock
            request_ip=request.remote_addr
            selected_server=request.args.get('server')
            print(f"Server selected: {selected_server}")
            print(f"Search term: {item_name}")
            print(f"Requested by: {request_ip}")
            item_id=item_search.get_item_id_from_name(item_name)
            icon_id=item_search.find_item_icon_id(item_id)
            item_icon_path=crafting_calculator.find_picture_path(icon_id)

            all_listing_information=item_search.item_lookup(item_id,selected_server)
            print(f"Result: {all_listing_information}")
            if all_listing_information[0][0]!=None:

                listing_information=all_listing_information[0]
                listing_timestamp=all_listing_information[1]
                lowest_price_per_unit=item_search.find_lowest_price_per_unit(listing_information)
                print(f"Lowest price found: {lowest_price_per_unit}")
                #print(listing_information[0])
                return render_template("item_result.html", item_list=item_list, item_id=item_id,server=selected_server,
                           item_name=item_name, listing_information=listing_information, 
                           lowest_price_per_unit=lowest_price_per_unit, listing_timestamp=listing_timestamp, item_icon_path=item_icon_path)
            else:
                raise Exception
    except:
        return render_template("item_result_error.html", item_list=item_list)
        
    return render_template("item_search_main.html",item_list=item_list)



@app.route("/item_craft_info", methods=['GET'])
def craft_calculator():
    item_list=item_search.get_item_names_from_id()
    
    try:
        if request.args.get('search'):
            item_name=request.args.get('search')
            #TODO: Put up a request per IP per minute lock
            request_ip=request.remote_addr
            selected_server=request.args.get('server')
            print(f"Server selected: {selected_server}")
            print(f"Search term: {item_name}")
            print(f"Requested by: {request_ip}")
            item_id=item_search.get_item_id_from_name(item_name)
            
            icon_id=item_search.find_item_icon_id(item_id)
            item_icon_path=crafting_calculator.find_picture_path(icon_id)
            print(item_icon_path)
            item_listing=item_search.item_lookup(item_id, selected_server)
            
            item_recipe=crafting_calculator.find_recipe(item_name, item_id, selected_server)
            lowest_price_per_unit=item_search.find_lowest_price_per_unit(item_listing[0])
            if item_recipe != None:
                total_price_for_components=0
                for component in item_recipe:
                    print(f"Component range: {component[1]}")
                    for amount_of_component in range (component[1]):
                        total_price_for_components+=component[3]
                print(f"total price for components = {total_price_for_components}")
            else:
                raise Exception
            
            return render_template("item_craft_info_result.html", item_list=item_list, item_name=item_name, 
                                   server=selected_server, 
                                   item_recipe=item_recipe, listing_timestamp=item_listing[1], 
                                   craft_listing=item_listing[0], lowest_price_per_unit=lowest_price_per_unit, 
                                   total_price_for_components=total_price_for_components, item_icon_path=item_icon_path)

    except:
        print(print_exc())
        return render_template("craft_result_error.html",item_list=item_list)

    return render_template("item_craft_info_main.html", item_list=item_list)



@app.route("/")
def redirect():
    return app.redirect("/main")


if __name__=='__main__':
    start()
    


#TODO: Make the last server selected saved
#TODO: Loading template
