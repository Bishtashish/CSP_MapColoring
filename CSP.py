import fiona
import random
import geopandas as geo
import numpy as np
import matplotlib.pyplot as plot
from descartes import PolygonPatch
import webcolors as wc


#  USA Map
# cities = geo.read_file("map/states_21basic/states.shp")


# Australian Map
cities = geo.read_file("map/Australian States Shapefile/States map.shp")
cities = cities.rename(columns={'NAME': 'STATE_NAME'})


# add Neighbours to the respective row in new Column


def generateNeighbor():
    cities["NEIGHBORS"] = None
    global colMax
    for index, state in cities.iterrows():   
        # get 'not disjoint' countries
        neighbors = cities[~cities.geometry.disjoint(state.geometry)].STATE_NAME.tolist()
        # remove own name from the list
        neighbors = [ name for name in neighbors if state.STATE_NAME != name ]
        # add names of neighbors as NEIGHBORS value
        if len(neighbors) > colMax:
            colMax=len(neighbors)
        cities.at[index, "NEIGHBORS"] = ", ".join(neighbors) 
    
# for index, row in cities.iterrows():  
#      neighbors = cities[cities.geometry.touches(row['geometry'])].STATE_NAME.tolist() 
#      neighbors = neighbors.remove(row.STATE_NAME)
#      cities.at[index, "NEIGHBORS"] = ", ".join(neighbors)


# cities.to_file("map/states_21basic/newfile.shp")  

 


def colorArray():
    colorCount =0
    global colMax
    # for key, value, index  in enumerate(wc.CSS3_NAMES_TO_HEX.items(), len(wc.CSS3_NAMES_TO_HEX.items())):
    for key, value in wc.CSS3_NAMES_TO_HEX.items():
        # if colorCount %(len(int(wc.CSS3_NAMES_TO_HEX.items())/colMax)//1) == 0:
        colorCount += 1
        if colorCount%10==0:
            colors.add(key)
            if len(colors) == colMax:
                break                                                  

def DFS_Recursive(visited1, state, index):
    usedColor=set()
    if state not in visited1:
        # if cities.at[index, "NEIGHBORS"] == "":
        if citiesDFS.loc[citiesDFS.STATE_NAME == state.strip(), "NEIGHBORS"].empty:    
            citiesDFS.loc[index].COLOR=list(colors)[0]
            visited1.add(state)
        else:               
            for neighbor in citiesDFS.loc[citiesDFS.STATE_NAME == state.strip(), "NEIGHBORS"].values[0].split(","):
                neighbor=neighbor.strip()
                # if  not citiesDFS[citiesDFS.STATE_NAME==neighbor].COLOR.tolist()[0] =="":  
                if  not citiesDFS.loc[citiesDFS.STATE_NAME==neighbor,"COLOR"].empty:           
                # if  not citiesDFS.loc[citiesDFS.STATE_NAME==neighbor,"COLOR"].items == "": 
                    # usedColor.add(citiesDFS[citiesDFS.STATE_NAME==neighbor].COLOR.tolist().pop(0))
                    # usedColor.add(citiesDFS[citiesDFS.STATE_NAME==neighbor].COLOR.tolist())
                     usedColor.add(citiesDFS[citiesDFS.STATE_NAME==neighbor].COLOR.tolist()[0])
               
            for color in colors:
                if(color not in usedColor):
                    # cities.at[index,"COLOR"]=color
                    citiesDFS.loc[index, "COLOR"] = color
                    visited1.add(state)
                    break
          
            for neighbor in set(citiesDFS.loc[citiesDFS.STATE_NAME == state, "NEIGHBORS"].values[0].split(",")) -  visited1:
                 # DFS_Recursive(visited1, neighbor, cities[cities["STATE_NAME"]==neighbor].index.astype(int))
                 # DFS_Recursive(visited1, neighbor, citiesDFS.loc[citiesDFS.STATE_NAME == neighbor].index)
                if neighbor.strip() != "":
                    neighbor=neighbor.strip()                    
                    DFS_Recursive(visited1, neighbor, citiesDFS.loc[citiesDFS.STATE_NAME == neighbor].index.values.astype(int)[0])
                     # DFS_Recursive(visited1, neighbor, citiesDFS.loc[citiesDFS.STATE_NAME == neighbor].index)




def DFS_ForwardChecking(visited1, state, index):
    if state not in visited1:
        if citiesForward.loc[citiesForward.STATE_NAME == state.strip(), "NEIGHBORS"].empty:    
            citiesForward.loc[index].COLOR=list(colors)[0]
            visited1.add(state)
        else:
            color=citiesForward.loc[index, "COLOR"].split(",")[0]
            citiesForward.loc[index, "COLOR"]=color
            visited1.add(state)
            neighbors = set()
            for string1 in citiesForward.loc[citiesForward.STATE_NAME == state, "NEIGHBORS"].values[0].split(","):
                 neighbors.add(string1.strip())
            # for neighbor in neighbors-visited1:
            for neighbor in neighbors.difference(visited1):
                if neighbor.strip() != "":
                #     neighbor=neighbor.strip() 
                    availableColor =set(citiesForward.loc[citiesForward.STATE_NAME==neighbor,"COLOR"].values[0].split(",")) - set(color.split(","))         
                    citiesForward.loc[citiesForward.STATE_NAME==neighbor,"COLOR"]=",".join(availableColor)                                       
              
            for neighbor in neighbors.difference(visited1):
                 if neighbor.strip() != "":
                     DFS_ForwardChecking(visited1, neighbor, citiesForward.loc[citiesForward.STATE_NAME == neighbor].index.values.astype(int)[0])

        

#  Colouring of individual states
def plotCountryPatch( axes, country_name, fcolor ):
    # plot a country on the provided axes        
    nami = citiesDFS[citiesDFS.STATE_NAME == country_name]       
    namigm = nami.__geo_interface__['features']  # geopandas's geo_interface
    namig0 = {'type': namigm[0]['geometry']['type'], \
              'coordinates': namigm[0]['geometry']['coordinates']}
    axes.add_patch(PolygonPatch( namig0, fc=fcolor, ec="black", alpha=0.85, zorder=2 ))

def plotCountryPatchF( axes, country_name, fcolor ):
    # plot a country on the provided axes        
    nami = citiesForward[citiesDFS.STATE_NAME == country_name]       
    namigm = nami.__geo_interface__['features']  # geopandas's geo_interface
    namig0 = {'type': namigm[0]['geometry']['type'], \
              'coordinates': namigm[0]['geometry']['coordinates']}
    axes.add_patch(PolygonPatch( namig0, fc=fcolor, ec="black", alpha=0.85, zorder=2 ))

# plotCountryPatch(ax2, 'New York', 'red')

colMax=0
colors=set()

ax2 = cities.plot(figsize=(8,8), edgecolor=u'black', cmap='Pastel1')
generateNeighbor()

colorArray()

visited1=set()


# # DFS()

citiesDFS= cities.copy()
citiesDFS["COLOR"]=""
citiesDFS["COLOR"] = citiesDFS["COLOR"].astype("string")
for index, state in citiesDFS.iterrows():
    name=state.STATE_NAME.strip()
    DFS_Recursive(visited1, name , index)


for index, state in citiesDFS.iterrows():
    plotCountryPatch(ax2, state.STATE_NAME.strip(), state.COLOR.strip())
    
          
    
# DFS + Forward Checking   

# citiesForward= cities.copy()
# citiesForward["COLOR"]=",".join(colors)
# citiesForward["COLOR"] = citiesForward["COLOR"].astype("string")
# for index, state in citiesForward.iterrows():
#     name=state.STATE_NAME.strip()
#     DFS_ForwardChecking(visited1, name , index)


# for index, state in citiesForward.iterrows():
#     plotCountryPatchF(ax2, state.STATE_NAME.strip(), state.COLOR.split(",")[0])
    
    
# DFS + Forward Checking + Propogation through Singleton Domains    


plot.ylabel('Latitude')
plot.xlabel('Longitude')
# cities.plot()
plot.show();

