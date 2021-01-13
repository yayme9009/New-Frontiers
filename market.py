#from classes import *
from math import pow,e

#for a typical market cycle, want to call labour market->.use()->.planning()->.sell()->.buy()->market transfers
#don't forget to update planning variables


#TODO: if no supply of good market crashes, handle exception

def market(planets,techDict,lenLab,lenGoods):
    #this function iterates through planets and generates a list of orders that will go into the market
    #this function deals with the first turn of the market: the production cycle


    for i in range(len(planets)):
        #this loop deals with the production of labour
        #since labour markets are planet-specific, this is an easy target for parallelization, maybe split this off into it's own separate function

        planets[i].orders=[] #clear any orders from previous turns

        #first generate labour from pops
        for j in range(len(planets[i].pops)):
            planets[i].orders.append(planets[i].pops[j].labour(planets[i].prices))
            planets[i].pops[j].income=0

        #then generate production orders from industries
        for key,ind in planets[i].industries.items():
            planets[i].orders.append(ind.buy_labour())

        [planets[i].labDemand,planets[i].labSupply]=demand_supply(planets[i].orders,lenLab)

        #this caches the demand filled
        demandFill=[] #supply/demand
        for j in range(lenLab):
            try:
                demandFill.append(planets[i].labSupply[j]/planets[i].labDemand[j])
            except ZeroDivisionError:
                demandFill.append(-1) #no supply

        for order in planets[i].orders:
            if demandFill[order.goodID]!=-1:
                if order.sector==0: #population
                    #technically since only pops sell labour could just skip this if else statement but seems like bad code
                    if not order.isBuying:
                        inc=planets[i].wages[order.goodID]*order.amount*min(1,1/demandFill[order.goodID])
                        planets[i].pops[order.actorID].savings+=inc
                        planets[i].pops[order.actorID].income+=inc
                    else:
                        planets[i].pops[order.actorID].savings-=planets[i].wages[order.goodID]*order.amount*min(1,demandFill[order.goodID])
                elif order.sector==1: #industry
                    #same logic as above
                    if not order.isBuying:
                        inc=planets[i].wages[order.goodID] * order.amount * min(1, 1/demandFill[order.goodID])
                        planets[i].industries[order.actorID].savings += inc
                        planets[i].industries[order.actorID].income+=inc

                    else:
                        # add labour into stock
                        goodsBought=order.amount * min(1, demandFill[order.goodID])
                        planets[i].industries[order.actorID].labStock[order.goodID]+=goodsBought

                        exp=planets[i].wages[order.goodID] * goodsBought
                        planets[i].industries[order.actorID].savings -= exp
                        planets[i].industries[order.actorID].expenses += exp
                        planets[i].industries[order.actorID].labour+=exp



        #change prices up or down
        maxWagePriceChange=0.5 #how fast the prices change
        minWage=0.0 #price floor

        for j in range(lenLab):
            if demandFill[j]>1 or (demandFill[j]==-1): #oversupply or no demand, therefore -1
                #max %age change in price 10%
                if demandFill[j]==-1:
                    planets[i].wages[j]-=planets[i].wages[j]*0.1

                pricePercentChange=(0.1)/(1+pow(e,-(demandFill[j]-1)/2))

                planets[i].wages[j]=max(minWage,planets[i].wages[j]*(1-pricePercentChange))
            else: #undersupply
                if demandFill[j]==0: #no supply
                    planets[i].wages[j]+=max(planets[i].wages[j]*0.1,maxWagePriceChange) #force price change up to get demand in
                else:
                    pricePercentChange=(0.1)/(1+pow(e,-(1/demandFill[j]-1)/2))

                    planets[i].wages[j]+=max(planets[i].wages[j]*pricePercentChange,maxWagePriceChange*pricePercentChange)

        planets[i].orders=[]

        #here industries give out dividends and new industries created

        planets[i].give_dividends()
        planets[i].use_investment(techDict)
        planets[i].purge()

        #production phase, uses stock of goods to generate goods for sale & prep for next phase
        for key,ind in planets[i].industries.items():
            ind.use(planets[i].prices)

            #selling goods produced
            planets[i].orders+=ind.sell()
            planets[i].orders+=ind.planning(planets[i].wages,planets[i].prices)


        #goods market phase, sell goods to planetary market, split the market resolution into it's own function? TODO: split the market cycle into their own functions
        #get consumer demands as well
        for j in range(len(planets[i].pops)):
            planets[i].orders+=planets[i].pops[j].buy_orders(planets[i].prices)

        #throw everything out into the market and sort it out
        [planets[i].demand,planets[i].supply]=demand_supply(planets[i].orders,lenGoods)

        demandFill = []  # supply/demand
        for j in range(lenGoods):
            try:
                demandFill.append(planets[i].supply[j] / planets[i].demand[j])
            except ZeroDivisionError:
                demandFill.append(-1)  # no supply

        for order in planets[i].orders:
            if demandFill[order.goodID] != -1:
                if order.sector == 0:  # population
                    if not order.isBuying:
                        goodsSold=order.amount * min(1,1/demandFill[order.goodID])
                        planets[i].pops[order.actorID].bought[order.goodID]-=goodsSold

                        planets[i].pops[order.actorID].savings += planets[i].prices[order.goodID] * goodsSold
                    else:
                        goodsBought=order.amount * min(1,demandFill[order.goodID])

                        planets[i].pops[order.actorID].bought[order.goodID] += goodsBought

                        planets[i].pops[order.actorID].savings -= planets[i].prices[order.goodID] * goodsBought

                        if planets[i].pops[order.actorID].savings<goodsBought*planets[i].prices[order.goodID]:

                            print("\t",planets[i].pops[order.actorID].savings,order.amount*planets[i].prices[order.goodID],order.actorID)

                elif order.sector == 1:  # industry
                    if not order.isBuying:
                        goodsSold=order.amount * min(1, 1 / demandFill[order.goodID])
                        planets[i].industries[order.actorID].stock[order.goodID] -= goodsSold

                        inc = planets[i].prices[order.goodID] * goodsSold
                        planets[i].industries[order.actorID].savings += inc
                        planets[i].industries[order.actorID].income += inc
                    else:
                        goodsBought=order.amount * min(1, demandFill[order.goodID])
                        planets[i].industries[order.actorID].stock[order.goodID] += goodsBought

                        exp = planets[i].prices[order.goodID] * goodsBought
                        planets[i].industries[order.actorID].savings -= exp
                        planets[i].industries[order.actorID].expenses += exp

                        if planets[i].industries[order.actorID].savings<0:
                            print(planets[i].industries[order.actorID].savings, planets[i].industries[order.actorID].savings+exp)

        maxPriceChange=0.5
        minPrice=0.0
        for j in range(lenGoods):
            if demandFill[j]>1 or (demandFill[j]==-1): #oversupply
                if demandFill[j]==-1:
                    planets[i].prices[j]*=0.9 #cut by 10%
                else:
                    pricePercentChange = (0.1) / (1 + pow(e, -(demandFill[j] - 1) / 2))
                    planets[i].prices[j]=max(minPrice,planets[i].prices[j]*(1-pricePercentChange))
            else: #undersupply
                if demandFill[j]==0: #no supply
                    planets[i].prices[j]+=max(maxPriceChange,planets[i].prices[j]*0.1) #force big price change up to get demand in
                else:
                    pricePercentChange = (0.1) / (1 + pow(e, -(1 / demandFill[j] - 1) / 2))
                    planets[i].prices[j]+=max(maxPriceChange*pricePercentChange,planets[i].prices[j]*pricePercentChange)

        #now pops use the stock they've bought
        for j in range(len(planets[i].pops)):
            planets[i].pops[j].use_stock()
            #planets[i].pops[j].grow()

        #here pops invest in planet
        planets[i].get_investment()
        planets[i].adjust_RandomFactor()


def demand_supply(orders,lenprices):
    #this function takes the list of orders and spits out total [demand,supply] lists of each.
    demandlist=[0]*lenprices
    supplylist=[0]*lenprices
    for order in orders:
        if order.isBuying:
            demandlist[order.goodID]+=order.amount
        else:
            supplylist[order.goodID]+=order.amount
    return [demandlist,supplylist]