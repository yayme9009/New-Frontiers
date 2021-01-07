#this is the main file that calls all other files

from market import *
from IO import *
#from classes import *

#intitalize all the variables
[labDict,goodsDict]=read_labGoods()
techniques=read_techniques(labDict,goodsDict)
needs=read_needs(goodsDict)
planets=read_planets(labDict,goodsDict,techniques,[[needs]])

write_log_header()
write_goods_header({v: k for k, v in labDict.items()},{v: k for k, v in goodsDict.items()})

#initialize the starting goods the market has
for planet in planets:
    for i in range(len(planet.industries)):
        planet.industries[i].goods_init()


for i in range(250):
    market(planets,len(labDict),len(goodsDict))
    #print(planets[0].industries[0].savings,planets[0].industries[1].savings,planets[0].industries[2].savings)
    write_to_log(i,planets)
    write_goods(planets)