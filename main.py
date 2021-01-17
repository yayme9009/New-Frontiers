#this is the main file that calls all other files

from market import *
from IO import *
import time
#from classes import *

#intitalize all the variables
[labDict,goodsDict]=read_labGoods()
techniques=read_techniques(labDict,goodsDict)
needs=read_needs(goodsDict)
poptypes=read_poptypes()
planets=read_planets(labDict,goodsDict,techniques,poptypes,[[needs]])

write_log_header()
write_goods_header({v: k for k, v in labDict.items()},{v: k for k, v in goodsDict.items()})
write_time_header()

#initialize the starting goods the market has
for planet in planets:
    planet.update_marketCache(techniques)
    for key,ind in planet.industries.items():
        ind.goods_init()



for i in range(1000):

    t=time.process_time_ns()

    times=market(planets,techniques,len(labDict),len(goodsDict))
    #print(planets[0].industries[0].savings,planets[0].industries[1].savings,planets[0].industries[2].savings)
    #print(planets[0].industries[0].size, planets[0].industries[1].size, planets[0].industries[2].size)
    #print(planets[0].industries[0].capital, planets[0].industries[1].capital, planets[0].industries[2].capital)

    tMarket=time.process_time_ns()-t

    #print(planets[0].pops[0].needsmet,planets[0].pops[1].needsmet)

    print(i,len(planets[0].industries))

    #planets[0].pops[0].savings+=10000

    write_to_log(i,planets)
    write_goods(planets)

    write_time(tMarket,times,len(planets[0].industries))
