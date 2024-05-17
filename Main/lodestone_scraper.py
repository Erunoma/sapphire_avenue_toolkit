import json
from bs4 import BeautifulSoup
import requests
import re
from pprint import pprint
from traceback import print_exc
import csv

import item_search
import crafting_calculator
def search_lodestone_character_list(name, server):
    char_info=[]
    #Linje 14 er skrevet delvis af ChatGPT
    if bool(re.search(r"\s", name))==True:
        print("This name has a space")
        name=name.replace(" ","+")
    cleaner=re.compile('<.*?>')
    print(f"url: https://na.finalfantasyxiv.com/lodestone/character/?q={name}&worldname={server}")
   
    if server:
        page=requests.get(f"https://na.finalfantasyxiv.com/lodestone/character/?q={name}&worldname={server}")
        if page.status_code!=200:
            raise Exception
    else:
        page=requests.get(f"https://na.finalfantasyxiv.com/lodestone/character/?q={name}")
        if page.status_code!=200:
            raise Exception
   
        
    #Linje 31-32 er taget fra mit tidligere-lavet Scraping program fra praktikken
    soup = BeautifulSoup(page.content, "html.parser")
    clean_text=re.sub(cleaner, '', str(soup))
    
    #print(clean_text)
    #print(soup)
    html_listings=soup.find_all("div",{"class":"entry"})
    
    results=[]
    for entry in html_listings:
        try:
            char_name_all=str(entry.find("p",{"class":"entry__name"}))
            char_name_result=re.search('>(.*?)<',char_name_all)
            if char_name_result:
                char_name=char_name_result.group(1)
                print(char_name)

            char_ids=entry.find_all("a", {"class":"entry__link"})
            char_id_full=f"{char_ids[0]['href']}".split("/")
            char_id=f"/profiles?id={char_id_full[3]}"
            print(char_id)

            char_icons=entry.find_all("img")
            char_icon=char_icons[0]["src"]
            print(char_icon)

            results.append([char_name,char_id,char_icon])

        except:
            char_name=None
            char_id=None
            char_icon=None
   

    char_info_dict={
                "results":results
            }    
    #pprint(char_info_dict)
    return char_info_dict


def get_lodestone_info(id):
    cleaner=re.compile('<.*?>')
    page=requests.get(f"https://na.finalfantasyxiv.com/lodestone/character/{id}/")
    soup = BeautifulSoup(page.content, "html.parser")
    clean_text=re.sub(cleaner, '', str(soup))
    #print(soup)
    div_class=soup.find("div",{"class":"character__detail__image"})
    a_class=div_class.find("a")
    profile_picture_href=a_class.get("href")
    profile_server=soup.find("p", {"class":"frame__chara__world"}).get_text().split(" ")
    print(profile_server[0])
    profile_info=[profile_picture_href, profile_server[0]]
    print(f"This is the portrait: {profile_picture_href}")

    return profile_info

      #Reflection: Hidden elements in HTML  
def get_minion_collection(id):

    is_collecting=True
    cleaner=re.compile('<.*?>')
    page=requests.get(f"https://na.finalfantasyxiv.com/lodestone/character/{id}/minion/")
    soup = BeautifulSoup(page.content, "html.parser")

   
    all_minions=soup.find_all("li", {"class":"minion__list_icon"})

    minion_names=[]
    minion_collecting=[]


    
    #print(len(all_minions))
    for minion in all_minions:
        try:
            if is_collecting==True:
                minion_href_collecing=minion.get('data-tooltip_href').split("/")
                if check_href(minion_href_collecing)==False:
                    #print(minion_href_collecing[6])
                    minion_page=requests.get(f"https://na.finalfantasyxiv.com/{minion.get('data-tooltip_href')}")
                    print(f"Searching site: https://na.finalfantasyxiv.com/{minion.get('data-tooltip_href')}")
                    minion_page_soup=BeautifulSoup(minion_page.content, "html.parser")
                    #print(f"This is the header: {minion_page_soup.find('h4',{'class':'minion__header__label'}).text}")
                    minion_name_collecting=minion_page_soup.find('h4',{'class':'minion__header__label'}).text

                    minion_id=item_search.get_item_id_from_name(minion_name_collecting)
                    minion_icon_id=item_search.find_item_icon_id(minion_id)
                    minion_icon_path=crafting_calculator.find_picture_path(minion_icon_id)
                    minion_collecting.append([minion_name_collecting, minion_href_collecing[6], minion_icon_path])
                else:
                    pass
        #BUG: If a new minion appears, it won't get loaded in on the first go
            minion_href=minion.get('data-tooltip_href').split("/")
            minion_names.append(get_minion_name(minion_href[6]))
        except:
            print_exc()
        
    if is_collecting==True:
        update_minion_file(minion_collecting)
    print(minion_names)

    return minion_names

def get_mount_collection(id):
    is_collecting=True
    cleaner=re.compile('<.*?>')
    page=requests.get(f"https://na.finalfantasyxiv.com/lodestone/character/{id}/mount/")
    soup = BeautifulSoup(page.content, "html.parser")
    
    all_mounts=soup.find_all("li", {"class":"mount__list_icon"})

    mount_names=[]
    mount_collecting=[]
    
    #print(len(all_minions))
    for mount in all_mounts:
        try:
            if is_collecting==True:
                mount_href_collecting=mount.get('data-tooltip_href').split("/")
                if check_href_mounts(mount_href_collecting)==False:
                    #print(minion_href_collecing[6])
                    mount_page=requests.get(f"https://na.finalfantasyxiv.com/{mount.get('data-tooltip_href')}")
                    print(f"Searching site: https://na.finalfantasyxiv.com/{mount.get('data-tooltip_href')}")
                    mount_page_soup=BeautifulSoup(mount_page.content, "html.parser")
                    mount_item_a=mount_page_soup.find("a", {"class":"mount__item_icon js__chara_tooltip"})
                    mount_item_name=str(mount_item_a.get("data-tooltip"))
                    print(f"Mount item: {mount_item_name}")
                    
                    

                    mount_id=item_search.get_item_id_from_name(mount_item_name)
                    mount_icon_id=item_search.find_item_icon_id(mount_id)
                    mount_icon_path=crafting_calculator.find_picture_path(mount_icon_id)
                    mount_collecting.append([mount_item_name, mount_href_collecting[6], mount_icon_path])
                else:
                    pass
        #BUG: If a new mount appears, it won't get loaded in on the first go
            mount_href=mount.get('data-tooltip_href').split("/")
            mount_names.append(get_mount_name(mount_href[6]))
        except:
            print_exc()
            
        
    if is_collecting==True:
        update_mount_file(mount_collecting)
    print(mount_names)
    
    return mount_names
    
    

def check_href(href):
    is_true=False
    with open ("data/minion_information.csv", 'r') as read_file:
        reader=csv.reader(read_file)
        #print(f"This is the href:{href[6]}")
        for line in reader:
            
            if href[6]==line[1]:
                is_true=True
                break
    if is_true==True:
        #print("Minion already exists")
        return True
    else:
        #print("New minion found")
        return False
        
def check_href_mounts(href):
    is_true=False
    with open ("data/mount_information.csv", 'r') as read_file:
        reader=csv.reader(read_file)
        #print(f"This is the href:{href[6]}")
        for line in reader:
            
            if href[6]==line[1]:
                is_true=True
                break
    if is_true==True:
        #print("Mount already exists")
        return True
    else:
        #print("New Mount found")
        return False
            
       
def get_minion_name(href):
    csv_list=[]
    with open ("data/minion_information.csv", 'r') as read_file:
        reader=csv.reader(read_file)
        for line in reader:
            if href==line[1]:
                return line[0]
            else:
                pass
def get_mount_name(href):
    csv_list=[]
    with open ("data/mount_information.csv", 'r') as read_file:
        reader=csv.reader(read_file)
        for line in reader:
            if href==line[1]:
                return line[0]
            else:
                pass
  

    

def update_minion_file(minions):
   
    csv_list=[]
    minions_to_add=[]
    with open ("data/minion_information.csv", 'r') as read_file:
        reader=csv.reader(read_file)
        for line in reader:
            csv_list.append(line)

        minions_in_csv={}
        minions_in_csv["minions"]=csv_list
        #pprint(minions_in_csv)
        for minion in minions:
            result=any(minion[1] in sublist for sublist in minions_in_csv["minions"])
            if result:
                pass
            else:
                minions_to_add.append(minion)
                 
    with open ("data/minion_information.csv",'a') as append_file:
        writer=csv.writer(append_file)
        for line in minions_to_add:
            writer.writerow(line)

    pass
def update_mount_file(mounts):
    try:
        csv_list=[]
        mounts_to_add=[]
        with open ("data/mount_information.csv", 'r') as read_file:
            reader=csv.reader(read_file)
            for line in reader:
                csv_list.append(line)

            mounts_in_csv={}
            mounts_in_csv["minions"]=csv_list
            #pprint(minions_in_csv)
            for mount in mounts:
                result=any(mount[1] in sublist for sublist in mounts_in_csv["minions"])
                if result:
                    pass
                else:
                    mounts_to_add.append(mount)
                 
        with open ("data/mount_information.csv",'a') as append_file:
            writer=csv.writer(append_file)
            for line in mounts_to_add:
                writer.writerow(line)
    except:
        print_exc()
    pass

def get_unowned_minions(owned_minions):
    unowned_minions_names=[]

    with open ("data/minion_information.csv", 'r') as read_file:
        reader=csv.reader(read_file)

        owned_minions_dict={}
        owned_minions_dict["names"]=owned_minions
        for line in reader:
            #print(f"Checking name: {line[0]}")
            
            if line[0] in owned_minions_dict["names"]:
                #print("Found name")
                pass
            else:
                #print("Did not find name")
                unowned_minions_names.append(line[0])



    
    #print(f"Full list of unowned minions: {unowned_minions_names}")
    return unowned_minions_names

def get_unowned_mounts(owned_mounts):
    unowned_mounts_names=[]

    with open ("data/mount_information.csv", 'r') as read_file:
        reader=csv.reader(read_file)

        owned_mounts_dict={}
        owned_mounts_dict["names"]=owned_mounts
        for line in reader:
            #print(f"Checking name: {line[0]}")
            
            if line[0] in owned_mounts_dict["names"]:
                #print("Found name")
                pass
            else:
                #print("Did not find name")
                unowned_mounts_names.append(line[0])



    
    #print(f"Full list of unowned mounts: {unowned_mounts_names}")
    return unowned_mounts_names                

def get_stored_minion_image_path(item_name):
    with open("data/minion_information.csv", 'r') as file:
        reader=csv.reader(file)
        for line in reader:
            if item_name==line[0]:
                return line[2]
            
        if item_name:
            pass
        else:
            return None
           
def get_stored_mount_image_path(item_name):
    with open("data/mount_information.csv", 'r') as file:
        reader=csv.reader(file)
        for line in reader:
            if item_name==line[0]:
                return line[2]
            
        if item_name:
            pass
        else:
            return None



def csv_sell_status_overwriter():
    try:
    
        with open ("data/minion_information.csv",'r+', newline='') as minion_file:
            minion_info=[]
            reader=csv.reader(minion_file)
            writer=csv.writer(minion_file)
            for line in reader:
                print(f"Checking line: {line}")
                name=line[0]
                minion_id=item_search.get_item_id_from_name(name)
                all_listing_information=item_search.item_lookup(minion_id,"Spriggan")
                print(all_listing_information[0])
                if all_listing_information[0]:
                    if all_listing_information[0][0]!=None:
                        line.append(True)
                    else:
                        line.append(False)
                else:
                    line.append(False)
                minion_info.append(line)

            writer.writerows(minion_info)
        
        """
        with open ("data/mount_information.csv",'r+', newline='') as mount_file:
            mount_info=[]
            reader=csv.reader(mount_file)
            writer=csv.writer(mount_file)
            for line in reader:
                print(f"Checking line: {line}")
                name=line[0]
                minion_id=item_search.get_item_id_from_name(name)
                all_listing_information=item_search.item_lookup(minion_id,"Spriggan")
                print(all_listing_information[0])
                if all_listing_information[0]:
                    if all_listing_information[0][0]!=None:
                        line.append(True)
                    else:
                        line.append(False)
                else:
                    line.append(False)
                mount_info.append(line)

            writer.writerows(mount_info)
            """

        
    except:
        print_exc()

def get_stored_sellable(minion,csv_file):
    try:
        with open(f"data/{csv_file}", 'r') as file: 
            reader=csv.reader(file)
            print(f"CSV: file: {csv_file}")
            for line in reader:
                #print(f"Line of: {minion} is : {line[3]}")
                #print(f"Checking {minion} vs {line[0]}")
                if minion==line[0]:
                    return line[3]
            return False
    except:
        return False

