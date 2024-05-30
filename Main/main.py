#Installed modules
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from traceback import print_exc
from sys import exit
from pprint import pprint

#Own Modules
import item_search
import crafting_calculator
import lodestone_scraper

#Used for development on PC
is_local=True

#Initlizing Flask
app = Flask(__name__, template_folder='html')

#Starts the server either locally or on the network 
def start():
    try:
        if is_local==True:
            app.run(host='localhost', port=43435)
        else:
            app.run(host='0.0.0.0', port=43435)
        
    except:
        print(print_exc())
        exit()
        
#Main page. All non-defined urls are sent here with the 'def redirect()'
@app.route("/main")
def main():
    return render_template("front_page.html")

#The Item Search Page
@app.route("/item_search", methods=['GET','POST'])
def item_searching():
    #Searches the /data/item_id_names.json and creates a list of all items in it.
    item_list=item_search.get_item_names_from_id()
    try:
        #If 'search' is in the URL, this code will be executed, otherwise loads item search page with only the search bar
        if request.args.get('search'):
            #Takes the item name from the generated url
            item_name=request.args.get('search')
            
            #Gets the IP of the device that is searching
            request_ip=request.remote_addr
            #Gets the server from the genereated url
            selected_server=request.args.get('server')

            print(f"Server selected: {selected_server}")
            print(f"Search term: {item_name}")
            print(f"Requested by: {request_ip}")

            #Finds the ID, Icon and path to icon from the item name alone
            item_id=item_search.get_item_id_from_name(item_name)
            icon_id=item_search.find_item_icon_id(item_id)
            item_icon_path=crafting_calculator.find_picture_path(icon_id)

            #Gets the listing information from the item. A maximum of 50 is obtained
            all_listing_information=item_search.item_lookup(item_id,selected_server)
            print(f"Result: {all_listing_information}")

            #If there is any listings, this if-section will be executed
            if all_listing_information[0][0]!=None:
                #Gets the listings, the time since last update and finds the lowest price of all listings and then renders the page
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
    #Searches the /data/item_id_names.json and creates a list of all items in it.
    item_list=item_search.get_item_names_from_id()
    try:
        #If 'search' is in the URL, this code will be executed, otherwise loads item search page with only the search bar
        if request.args.get('search'):
            #Takes the item name from the generated url
            item_name=request.args.get('search')
            #TODO: Put up a request per IP per minute lock
            request_ip=request.remote_addr
            #Gets the server from the genereated url
            selected_server=request.args.get('server')

            print(f"Server selected: {selected_server}")
            print(f"Search term: {item_name}")
            print(f"Requested by: {request_ip}")

            #Finds the ID, Icon and path to icon from the item name alone
            item_id=item_search.get_item_id_from_name(item_name)
            icon_id=item_search.find_item_icon_id(item_id)
            item_icon_path=crafting_calculator.find_picture_path(icon_id)

            #Gets the listing information for the searched item
            item_listing=item_search.item_lookup(item_id, selected_server)
            #Finds the recipe in the json of the item
            item_recipe=crafting_calculator.find_recipe(item_name, item_id, selected_server)
            #Finds the lowest price from the listings
            lowest_price_per_unit=item_search.find_lowest_price_per_unit(item_listing[0])
            #If there is a recipe for this item, this if-section will be executed
            if item_recipe != None:
                #Adds up the prices of all compoents to get a total
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



@app.route("/profiles", methods=["GET","POST"])
def player_collection():
    if request.method=="POST":
       try:
            #Gets the server and character name from the generated url
            print(f"This is the form:")
            server=""
            char_name_input=""
            for key, value in request.form.items():
                print(key, value) 
                if key=="server":
                    server=value
                if key=="char_name_input":
                    char_name_input=value
            if char_name_input:
                #Searches the lodestone for the profile link and picture of all found characters
                result_dict=lodestone_scraper.search_lodestone_character_list(char_name_input,server)
                for entry in result_dict["results"]:
                    print(entry)
            return render_template("character_search_results.html",result_dict=result_dict)
       except:
           return render_template("character_search_error.html")
    
    
    if request.method=="GET":
        try:
            #Gets the ID from the generated URL
            if request.args.get('id'):
                char_id=request.args.get('id')
                print(char_id)
                #Loads the profile page for the chosen character
                lodestone_info=lodestone_scraper.get_lodestone_info(char_id)
                #Finds all the minions the character owns
                collection_minion_names=lodestone_scraper.get_minion_collection(char_id)
                #Sorts and figures out which minions the player is missing
                unowned_minions=lodestone_scraper.get_unowned_minions(collection_minion_names)
               
                owned_icons=[]
                unowned_icons=[]
                
                owned_sellable=[]
                unowned_sellable=[]
                #Goes through every minion the character owns, and finds the icon and if the minion is sellable on the market
                for minion in collection_minion_names:
                    owned_icons.append(lodestone_scraper.get_stored_minion_image_path(minion))
                    owned_sellable.append(lodestone_scraper.get_stored_sellable(minion, "minion_information.csv"))
                #Zip-funktionen funder via ChatGPT
                owned_info=list(zip(collection_minion_names, owned_icons,owned_sellable))
                #Goes through every minion the character does not own, and finds the icon and if the minion is sellable on the market
                for minion in unowned_minions:
                    unowned_icons.append(lodestone_scraper.get_stored_minion_image_path(minion))
                    unowned_sellable.append(lodestone_scraper.get_stored_sellable(minion, "minion_information.csv"))
                unowned_info=list(zip(unowned_minions, unowned_icons, unowned_sellable))

                #This section is the same as above, but with the mounts instead
                collection_mounts_names=lodestone_scraper.get_mount_collection(char_id)
                unowned_mounts=lodestone_scraper.get_unowned_mounts(collection_mounts_names)

                owned_mount_icons=[]
                unowned_mount_icons=[]

                owned_mount_sellable=[]
                unowned_mount_sellable=[]

                for mount in collection_mounts_names:
                    owned_mount_icons.append(lodestone_scraper.get_stored_mount_image_path(mount))
                    owned_mount_sellable.append(lodestone_scraper.get_stored_sellable(mount, "mount_information.csv"))
                print(owned_mount_sellable)
                    

                owned_mount_info=list(zip(collection_mounts_names, owned_mount_icons, owned_mount_sellable))
            
                for mount in unowned_mounts:
                    unowned_mount_icons.append(lodestone_scraper.get_stored_mount_image_path(mount))
                    unowned_mount_sellable.append(lodestone_scraper.get_stored_sellable(mount, "mount_information.csv"))
                print(unowned_mount_sellable)
                unowned_mount_info=list(zip(unowned_mounts, unowned_mount_icons, unowned_mount_sellable))
            
                #TODO: Find unowned minions and display them both sequensially on the site with the name, icon, status and price
                #TODO: Add a "Total gil needed to finish collection" counter
                #print(owned_mount_info)
                #print(unowned_mount_info)
                #print(owned_sellable)
                #print(unowned_sellable)
                
                return render_template("character_search_profile.html", char_id=char_id, lodestone_info=lodestone_info, 
                                   owned_minions=owned_info, unowned_minions=unowned_info, owned_icons=owned_icons,
                                   owned_mounts=owned_mount_info, unowned_mounts=unowned_mount_info)
        except:
            print_exc()
            return render_template("character_search_error.html")
    return render_template("character_search_main.html")
    


@app.route("/")
def redirect():
    return app.redirect("/main")


if __name__=='__main__':
    start()