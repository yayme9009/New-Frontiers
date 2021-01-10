#this is the main file that calls all other files

from market import *
from IO import *
#from classes import *

#intitalize all the variables
[labDict,goodsDict]=read_labGoods()
techniques=read_techniques(labDict,goodsDict)
needs=read_needs(goodsDict)
poptypes=read_poptypes()
planets=read_planets(labDict,goodsDict,techniques,poptypes,[[needs]])

write_log_header()
write_goods_header({v: k for k, v in labDict.items()},{v: k for k, v in goodsDict.items()})

#initialize the starting goods the market has
for planet in planets:
    for key,ind in planet.industries.items():
        ind.goods_init()


for i in range(250):
    market(planets,techniques,len(labDict),len(goodsDict))
    #print(planets[0].industries[0].savings,planets[0].industries[1].savings,planets[0].industries[2].savings)
    #print(planets[0].industries[0].size, planets[0].industries[1].size, planets[0].industries[2].size)
    #print(planets[0].industries[0].capital, planets[0].industries[1].capital, planets[0].industries[2].capital)


    #print(planets[0].pops[0].savings,planets[0].pops[1].savings)

    print(i,len(planets[0].industries))
    write_to_log(i,planets)
    write_goods(planets)