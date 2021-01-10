import math
import random

'''
class market:
    #market object that defines a market of various solar systems
    def __init__(self):
        self.systems=[] # list of systems in the market
'''

class planet:
    #planet object
    def __init__(self,coords,own,lenlab,lengoods):
        #physical properties

        self.location=coords #len 2 tuple that delinates where the celestial body is

        '''
        self.type=t #type of planet
        self.size=s #size of planet as a scaling factor, limits avaliable space
        self.temp=temperature #temperature of planet
        self.water=w #how wet the planet is
        '''

        #economic properties
        self.pops=[] #list of pops on the planet
        self.industries={} #list of planetary industries

        self.ownership=own #ownership of industries on planet are planet-wide

        self.dividend=0 #amount of money that can be split
        self.investment=0 #amount of money each pop class has invested in planet's industries

        #market lists
        self.orders=[] #list of orders the planet has, essentially the planet's market
        self.wages=[1]*lenlab
        self.prices=[1]*lengoods

        self.labDemand=[0]*lenlab
        self.labSupply=[0]*lenlab #labour demand and supply lists for the planet
        self.labMoney=[0]*lenlab #amount of money buyers are putting up for each type of labour

        self.demand=[0]*lengoods
        self.supply=[0]*lengoods #planetary supply and demand


    #planet-scope economic functions
    def get_investment(self):
        #goes through pops on planet and if the pops have enough savings gets them to invest in the planet's industries
        #do this before pops sell labour but after pops buy goods (beginning of cycle say)
        for i in range(len(self.pops)):
            needsCost=sum([price_list(need, self.prices) for need in self.pops[i].needs]) #this assumes pops all have the same needs
            if self.pops[i].savings>(10*needsCost*self.pops[i].population): #buffer
                invest=self.pops[i].savings-(10*needsCost*self.pops[i].population)
                self.investment+=invest
                self.ownership.pops[self.pops[i].poptype]+=invest
                self.pops[i].savings-=invest

    def use_investment(self,techDict):
        #if there's enough investment in the planet's industries, spawn new industries on the planet that's the most profitable
        techList=[tech for key,tech in techDict.items()]
        profitpercents=[tech.profit_percent(self.wages,self.prices) for key,tech in techDict.items()] #how profitable each technique is

        #this sorts techniques by profit percentage
        zipped=zip(profitpercents,range(len(techList)))
        sortedzip=sorted(zipped)

        techsSorted=[techList[y] for x,y in sortedzip]
        profitpercents.sort()

        #if need to speed up this function, can get rid of negative value factories

        startCap=sum(self.prices)/len(self.prices)*1000 #average cost of goods times 500
        numInds=math.floor(self.investment/startCap) #max factories being made

        #the Jefferson method is used to determine which productions they use
        quotients=profitpercents #will change once calculations finished
        numIndList=[0]*len(quotients)

        while(sum(numIndList)<numInds):
            index=quotients.index(max(quotients))
            numIndList[index]+=1
            quotients[index]=profitpercents[index]/(numIndList[index]+1)

        for i in range(len(numIndList)):
            for j in range(numIndList[i]):
                newid=generate_id()
                self.industries[newid]=industry(newid,"A",techsSorted[i],1,startCap,0,len(self.wages),len(self.prices)) #industry starts with 1 size free of charge
                self.industries[newid].new=5 #5 turn grace period on giving out dividends

        self.investment-=numInds*startCap


    def give_dividends(self):
        #excess money generated by industries goes into dividends, then gets distributed to the respective owners
        #this should be called after planning phase

        #collecting dividends
        self.dividend=0
        for key,ind in self.industries.items():
            operatingCosts=ind.production.costs(self.wages,self.prices)*ind.size
            if ind.new>0:
                ind.new-=1
            elif ind.savings>(5*operatingCosts):
                #excess of money, take off the top as hard cap
                dividend=ind.savings-(5*operatingCosts)
                ind.savings-=dividend
                self.dividend+=dividend

        #making payments, currently pops only
        classes=[0]*len(self.ownership.pops)

        for pop in self.pops:
            classes[pop.poptype]+=pop.population
        totalShare=self.ownership.sum()
        divClassShares=[x/totalShare for x in self.ownership.pops]
        for i in range(len(self.pops)):
            div=self.dividend*self.pops[i].population/classes[self.pops[i].poptype]*divClassShares[self.pops[i].poptype]

            self.pops[i].income+=div
            self.pops[i].savings+=div
            self.pops[i].dividend=div #not +=

        #reset dividends
        self.dividend=0

    def purge(self):
        #purges all the dead industries from the roll
        deadIndKeys=[]
        for key,ind in self.industries.items():
            if (ind.savings<0.000001)or(ind.size<=0):
                deadIndKeys.append(key)
        for key in deadIndKeys:
            self.investment+=self.industries[key].savings
            del self.industries[key]


class pop:
    def __init__(self,i,ptype,popln,s,need):
        #the type of labour pops produce should be in a lookup table of some kind
        self.id=i #id number that keeps track of the pop's database entry

        self.poptype=ptype #type of pop, affects what they do as well as

        self.population=popln
        self.savings=s #liquid cash the pop has
        self.needs=need #list of list of goods the pops need
        self.needsmet=[0]*len(need) #how fufilled pop needs are
        self.bought=[0]*len(need)

        self.labourTier=0 #for now all labour is the same

        # self.poptype=  #type of pop

        #economic planning variables

        self.income=0 #amount of money made last turn
        self.dividend=0 #amount of money made from ownership of industries

        self.expenses=0 #amount of money spent last turn

        #political variables

    def labour(self):
        #reset planning variables
        self.income=0

        #produces a labour selling order, labourTuple is the list of labour tiers and what good id they correspond to
        return sellOrder(self.id,True, True, self.labourTier,self.population,0) #one labour unit produced per population

    def use_stock(self):
        #generates a fulfillment index based on what the pop has bought
        self.needsmet=[0]*len(self.needsmet)
        for i in range(len(self.needs)):
            fulfill=0
            goodsNeeded=0
            for j in range(len(self.needs[i])):
                if self.needs[i][j]==0:
                    continue
                goodsAmt=self.bought[j]
                goodsUsed=min(goodsAmt,self.population*self.needs[i][j])

                self.bought[j]-=goodsUsed

                fulfill+=math.sqrt(goodsUsed/self.population*self.needs[i][j])
                goodsNeeded+=1
            self.needsmet[i]=(fulfill*1.0/goodsNeeded)

        self.bought=[0]*len(self.bought) #clear storage item

    def buy_orders(self,prices):
        #function that decides what to do with the income the pop has

        orders=[]
        budget=self.savings

        #first go through the life needs, currerntly pops spend all their money on needs

        for i in range(len(self.needs)):
            unitPrice=price_list(self.needs[i],prices)*self.population #how much full fulfillment of the need tier costs
            multiplyFactor=min(1.0, budget/unitPrice)
            buyList = [x*multiplyFactor*self.population for x in self.needs[i]]
            orders+=list_to_order(buyList, self.id, False, True, True, 0)
            budget-=unitPrice*multiplyFactor
            if budget<0:
                break

        #print(budget,prices,unitPrice)

        return orders


class industry:
    def __init__(self,i,n,prod,s1,s2,c,lenlab,lengoods): #prod is an object that describes a production process
        self.id=i #id number in database

        self.name=n

        self.production=prod #the production process this industry undergoes
        self.size=s1 #maximum thoroughput of this industry (how many units of self.production it can do)
        self.savings=s2 #give enough starting funds to fund the max amount of production in the first round
        self.capital=c #amount of capital goods that enhance this industry's production

        self.labStock=[0]*lenlab #stock of labour the industry has
        self.stock=[0]*lengoods #will be filled with good ledger entries

        #should probably include some level of tech here


        #economic planning variables

        self.new=0 #if >0, prevents giving out dividends

        self.input=[] #list of goods destined for production input

        self.avgProd=0 #average productivity of the industry given capital and actual units of production

        self.caplvl=c #desired level of capital in the industry
        self.sizelvl=s1

        self.prodPlanLvl=self.size #desired level of production in the industry
        self.prodActLvl=self.size #actual level of production in the industry last turn

        #set these planning variables ^ above to their max to start off with

        self.income=s2
        self.labour=0
        self.expansion=0 #funds devoted to expansion
        self.returned=0 #funds devoted to paying down loans
        self.maintenance=0 #funds devoted to maintaining capital, provides the c in c/v or OOC
        self.expenses=s2 #expenses last turn

        #marxian indicators
        self.ROP=0
        self.ROSV=0
        self.OOC=0

    #for a typical market cycle, want to call labour market->.use()->.planning()->.sell()->.buy()->market transfers
    #I put planning after production so that an industry can pop up with only starting capital

    def goods_init(self):
        #this initializes stocks for industries at game start
        for i in range(len(self.production.inGoods)):
            self.stock[self.production.inGoods[i]]+=self.production.inAmts[i]*self.size

        #assumes starting prices of 1
        self.expenses=price_list(self.stock,[1]*len(self.stock))
        self.income=self.expenses #needed to avoid planning wonkiness

    def planning(self,labprices,prices):
        #planning function that sets levels of production for the next turn
        #should set prodplanlvl, caplvl and sizelvl
        profitpercent=(self.income-self.expenses+self.expansion+self.returned)/(self.expenses-self.expansion-self.returned) #this measure is intended to be a measure of the profitability of the company, so expansion costs and debt repayments are excluded

        if self.savings<0:
            print("b",self.savings)

        budget=self.savings

        unitCost=self.production.costs(labprices,prices)

        #remember the following cost variables represent the cost of adding 10 of each
        capitalCost = price_list(self.production.capitalUnit, prices) #maintaincost is 1/10th capitalCost
        sizeCost=price_list(self.production.sizeUnit,prices)

        # maintenance of capital, each capital costs 1/10th the goods needed to build it
        budget -= self.capital / 100 * capitalCost
        budget -= self.size / 100 * sizeCost

        if budget>0:

            canAfford=budget/unitCost

            if profitpercent<0:
                #if this production is losing money
                self.prodPlanLvl=min(canAfford,self.prodPlanLvl*(1+max(-0.9,(profitpercent)))) #maximum production cut from turn to turn is 90%

                budget-=self.prodPlanLvl*unitCost

            else:
                self.prodPlanLvl=min(self.size, self.prodActLvl*(1+max(1,profitpercent)), canAfford)
                budget-=self.prodPlanLvl*unitCost

            #keep a reserve of half last turns operating expenses, modified by the profit% they had last turn
            keep=(self.expenses-self.expansion-self.returned)/bound((0.2,5),2/(1-(profitpercent*2.5)))
            if keep<0:
                print("\t",keep)
            budget-=(self.expenses-self.expansion-self.returned)/bound((0.2,5),2/(1-(profitpercent*2.5)))

            if budget>0:
                #profit% shows the current profitability of the production technique, the higher it is the less sense it makes to make it more intensive vs extensive
                #this is where adding space vs adding capital comes into play

                #expansionPlan=budget/max(sizeCost,capitalCost)/2 #this variable shows the target amount of expansion this industry wants to do

                if profitpercent<0:
                    #if profit is negative no increase in size will ever be profitable, dump resources into intensity
                    expansionPlan=budget/(2*capitalCost)
                    self.caplvl=self.capital+(expansionPlan)
                    self.sizelvl=self.size

                else:
                    #else, mixture of capital intensity and size expansion
                    sizeCapRatio=sizeCost/capitalCost #how expensive expanding by size is compared to capital

                    expandRatio=bound((0,1),0.5*(sizeCapRatio/5+1)*(profitpercent*5+1)) #higher means more extensive vs intensive investment
                    #first sizeCapRatio measures how expensive it is to build capital instead of size
                    #then profit% modifies whether adding more space or intensity is profitable

                    expansionPlan=budget/((expandRatio*sizeCost)+((1-expandRatio)*capitalCost))/2 #modify the amount of capacity you want to add

                    self.caplvl=(1-expandRatio)*expansionPlan+self.capital
                    self.sizelvl=(expandRatio)*expansionPlan+self.size


            else:
                #no money for expansion, set up flag for a loan if profitable, bank will reject if enterprise losing money
                self.caplvl = self.capital
                self.sizelvl = self.size

                #TODO: loan flag here when banks implemented

        else:
            self.caplvl=self.capital
            self.sizelvl=self.size

        #calculate Marxian indicators
        surplus=(self.income-self.maintenance-self.labour)
        try:
            self.ROP=surplus/(self.maintenance+self.labour)
        except ZeroDivisionError:
            self.ROP=0
        try:
            self.ROSV=surplus/(surplus+self.labour)
        except ZeroDivisionError:
            self.ROSV=0
        try:
            self.OOC=self.maintenance / self.labour
        except ZeroDivisionError:
            self.OOC=0

        #reset planning variables, important for future market stuff
        self.income=0
        self.expenses=0
        # reset planning variables
        self.expansion = 0
        self.returned = 0
        self.maintenance = 0
        self.labour = 0

    def use(self,prices):
        #main action function, where industry acts on all the goods it bought

        #uses capital goods and expansion goods to expand and such
        capDiff=self.caplvl-self.capital
        sizeDiff=self.sizelvl-self.size

        capitalCost=price_list(self.production.capitalUnit,prices)
        sizeCost=price_list(self.production.sizeUnit,prices)

        #add to industry size and level of capital

        goodChange=[0]*len(self.stock)
        possibleCap=max(0,capDiff+(self.capital/100)) #possible units of capital goods that can be added with correction factor for maintenance

        #if capDiff>0:
        for i in range(len(self.production.capitalUnit)):
            if self.production.capitalUnit[i]!=0:
                possibleCap=min(possibleCap,self.stock[i]/self.production.capitalUnit[i])

        goodChange=[possibleCap*x for x in self.production.capitalUnit]
        remove_stock(self.stock,goodChange)

        expandCapital=max(0,(possibleCap)-(self.capital/100))
        self.capital+=expandCapital #add capital
        self.expansion+=expandCapital*capitalCost
        self.maintenance+=min(possibleCap-expandCapital, self.capital/100)*capitalCost

        goodChange=[0]*len(self.stock)
        possibleSize=max(0,sizeDiff+self.size/100)
        for i in range(len(self.production.sizeUnit)):
            if self.production.sizeUnit[i]!=0:
                possibleSize=min(possibleSize,self.stock[i]/self.production.sizeUnit[i])

        goodChange=[possibleSize*x for x in self.production.sizeUnit]
        remove_stock(self.stock,goodChange)

        expandSize=max(possibleSize-(self.size/100),0)
        self.size+=expandSize #add size
        self.expansion+=expandSize*sizeCost
        self.maintenance+=min(possibleSize-expandSize,self.size/100)*sizeCost

        #here the industry uses up it's items, call the production function
        self.produce()

        #if failed to get goods to maintain capital, start lowering capital
        if expandCapital<(self.capital/100):
            self.capital-=max(1,self.capital*(expandCapital/(self.capital/100))/4) #maybe should have %age scaling factor that increases the longer the factory failed to maintain it's capital
        self.capital=max(self.capital,0)

        if expandSize<(self.size/100):
            self.size -= max(1, self.size * (expandSize / (self.size / 100)) / 4)  # maybe should have %age scaling factor that increases the longer the factory failed to maintain it's capital
        self.size = max(self.size, 0)


    def produce(self):
        #churn out however many units of output the industry decided upon making or can actually produce
        #prodPlanLvl should already be set before this function is called
        self.prodActLvl=min(self.prodPlanLvl,self.find_max_produce())

        #first remove stock
        #not sure if this is nessecary, since stock cleared every turn

        self.stock=[0]*len(self.stock) #just get rid of all stock, maybe implement stock holdovers later on
        self.labStock=[0]*len(self.labStock)

        #here we add the products

        #outunits is the production function, it's a parabola until a certain point where it levels off
        x=self.prodActLvl #for clarity
        if x>(self.size/2):
            outUnits=2*x-(x**2/self.size)
        else:
            outUnits=x+self.size/4

        #outUnits+=self.capital

        outUnits*=1+((self.capital)/self.size)

        for i in range(len(self.production.outGoods)): #production
            self.stock[self.production.outGoods[i]]=self.production.outAmts[i]*outUnits #not += since this wipes the original stock

    def find_max_produce(self):
        # returns the maximum units of output this industry can generate from it's current stock
        canMake = min(self.size,self.labStock[self.production.labour])
        for i in range(len(self.production.inGoods)):  # iterate through the input goods
            canMake = min(self.stock[self.production.inGoods[i]]/ self.production.inAmts[i], canMake)
        return canMake

    def sell(self):
        #returns a list of orders that sells the stuff the company has produced
        orders=[]
        for out in self.production.outGoods:
            orders.append(sellOrder(self.id, False, False,out, self.stock[out],1))
        return orders

    def buy_labour(self):
        #function that puts out buy orders for labour based on previously calculated planning variables

        return buyOrder(self.id, True, False, self.production.labour, self.prodPlanLvl,1)

    def buy_goods(self,prices):
        newCap=(self.caplvl-self.capital)
        newSize=(self.sizelvl-self.size)

        #function that puts out buy orders for goods that are needed for production and growth
        orderlist=[0]*len(self.stock)

        capitalCost=price_list(self.production.capitalUnit,prices)
        sizeCost = price_list(self.production.sizeUnit, prices)

        if (newCap*capitalCost+(newSize*sizeCost))>self.savings:
            print("a",newCap,capitalCost,newSize,sizeCost,self.savings)

        alreadySpent=0

        #buy maintenance goods first
        buyingUnits=min(self.size/100*sizeCost,self.savings/sizeCost)
        alreadySpent=buyingUnits*sizeCost

        add_stock(orderlist, [x*buyingUnits for x in self.production.sizeUnit])

        if alreadySpent>=self.savings:
            return list_to_order(orderlist,self.id,False,False,True,1)

        buyingUnits=min(self.capital/100*capitalCost,(self.savings-alreadySpent)/capitalCost)
        alreadySpent+=buyingUnits*capitalCost

        add_stock(orderlist,[x*buyingUnits for x in self.production.capitalUnit])

        if alreadySpent>=self.savings:
            return list_to_order(orderlist,self.id,False,False,True,1)

        #expansion plans here, should already be priced in self.planning()

        add_stock(orderlist,[x*newCap for x in self.production.capitalUnit])
        add_stock(orderlist,[x*newSize for x in self.production.sizeUnit])

        #print(self.production.capitalUnit)

        orderlist=list_to_order(orderlist,self.id,False,False,True,1)

        #finally buy goods for production
        for i in range(len(self.production.inGoods)):
            orderlist.append(buyOrder(self.id,False,False,self.production.inGoods[i],self.production.inAmts[i]*self.prodPlanLvl,1))

        return orderlist

class order:
    #transaction object used to keep track of goods and services on the market
    def __init__(self,ID,lab,pop,buying,good,sec):
        self.actorID=ID #this is an ID object of the economic actor placing the order
        self.isLabour=lab
        self.isPop=pop #true if pop and false if industry
        self.isBuying=buying
        self.goodID=good
        self.sector=sec #sector, 0 for pop, 1 for industry, 2 for government

class buyOrder(order):
    def __init__(self,ID,lab,pop,good,amt,sec):
        super(buyOrder, self).__init__(ID,lab,pop, True, good,sec)
        #self.money=cash #amount of money the actor is paying
        self.amount=amt #amount of goods that the actor wants to buy
        self.moneyChange=0 #amount of money that changes hands

class sellOrder(order):
    def __init__(self,ID,lab,pop,good,amt,sec):
        super(sellOrder, self).__init__(ID,lab,pop, False, good,sec)
        self.amount=amt #amount of stuff that actor is selling
        #self.money=0 #money gained from sale
        self.moneyChange=0 #amount of money that changes hands, could use self.money but this retains consistency with buyOrder


class technique:
    #defines a production technique industries use to produce goods
    def __init__(self,lab,inputGoods,inputAmts,outputGoods,outputAmts,cap,size):
        self.labour=lab #the labour type this technique needs

        self.inGoods=inputGoods #list of input goods in order
        self.inAmts=inputAmts #list of input amounts in order of self.inputGoods
        self.outGoods=outputGoods
        self.outAmts=outputAmts #same as inputs

        self.capitalUnit=cap #how much increasing capital by 10 costs in goods
        self.sizeUnit=size #how much increasing size by 10 costs in goods

    def revenue(self,prices):
        outputs=0
        for i in range(len(self.outGoods)):
            outputs+=self.outAmts[i]*prices[i]
        return outputs

    def costs(self,labprices,prices):
        inputs=labprices[self.labour] #price of 1 unit of labour

        for i in range(len(self.inGoods)):
            inputs += self.inAmts[i] * prices[i]
        return inputs

    def profit(self,labprices,prices):
        #returns the estimated profit of this technique based on prices
        '''
        inputs=0
        outputs=0

        for i in range(len(self.inGoods)):
            inputs+=self.inAmts[i]*prices[i]
        for i in range(len(self.outGoods)):
            outputs += self.outAmts[i] * prices[i]
        '''

        return self.revenue(prices)-self.costs(labprices,prices)

    def profit_percent(self,labprices,prices):
        #returns the profit over the expenses percentage
        '''
        inputs = 0
        outputs = 0

        for i in range(len(self.inGoods)):
            inputs += self.inAmts[i] * prices[i]
        for i in range(len(self.outGoods)):
            outputs += self.outAmts[i] * prices[i]
        '''

        return (self.revenue(prices)-self.costs(labprices,prices))/self.costs(labprices,prices)

class ownership:
    #ownership object that determines where the dividends of this the industry go
    def __init__(self,lenclasses):
        self.pops=[0]*lenclasses #only pops of the same planet get the dividends
        self.companies={}
        self.government=0
        self.total=0

    def sum(self):
        #gives sum of total investments into this company
        #numbers are arbitrary and relative
        returnsum=sum(self.pops)
        for key,value in self.companies.items():
            returnsum+=value

        return returnsum+self.government











class stock:
    #data object that represents the stock of goods a company has
    def __init__(self):
        self.entries=[] #list of things it has

    def add_good(self,goodId,amt):
        #adds goods to stock
        index=find_first_index(self.entries,goodId)
        if index==-1:
            self.entries.append([goodId,amt])
        else:
            self.entries[index][1]+=amt

    def remove_good(self,goodId,amt):
        #wrapper for add_good
        self.add_good(goodId,-1*amt)

    def get_amt(self,goodID):
        #returns the amount of good represented by goodID
        index=find_first_index(self.entries,goodID)
        if index==-1:
            return 0 #no such entry
        return self.entries[index][1]

    #utility functions
    def to_list(self,goodslen):
        #turns this stock into a list
        returnList=[]
        for i in range(len(goodslen)):
            returnList.append(self.get_amt(i))
        return returnList

    def empty(self):
        self.entries=[]


class database:
    #database class that keeps track of ids and such
    def __init__(self):
        self.indices=[]
        self.entries=[]

    def find_object(self,id):
        #returns object with given ID
        return self.entries[self.indices.index(id)]

    def next_id(self):
        #finds the next available id in the database
        if not self.indices:
            return 0
        else:
            index = -1

            # finds first available id
            for i in range(len(self.indices)):
                # i/indices[i] should be 1 (the same) if the id is filled
                if i / self.indices[i] != 1:
                    index = i
                    break
            if index != -1:  # found id gap
                return index
            else:  # else append to end
                return len(self.indices)


    def add_object(self,obj):
        #adds an object to the database
        if len(self.indices)==0:
            self.indices.append(0)
            self.entries.append(obj)
        else:
            index=-1

            #finds first available id
            for i in range(len(self.indices)):
                #i/indices[i] should be 1 (the same) if the id is filled
                if i/self.indices[i]!=1:
                    index=i
                    break
            if index!=-1: #found id gap
                self.indices.insert(index,self.indices[index-1]+1) #inserts lowest available id
                self.entries.insert(index,obj)
            else: #else append to end
                self.indices.append(len(self.indices))
                self.entries.append(obj)

    def delete_object(self,index):
        #delete object from database
        self.entries.pop(self.indices.index(index))
        self.indices.remove(index)

'''
class stock:
    def __init__(self):
        self.entries=[] #stock entries
    def add_stock(self,g,amount):
        

class entry:
    #good stock entry, only has two attributes
    def __init__(self,g,amount):
        self.good=g #good name
        self.amt=amount
'''

def find_first_index(list, num):
    #takes a 2D list and a number and returns the first index such that list[index][0]=num, or -1 if not there
    if not list:
        return -1

    index=-1
    for i in range(len(list)):
        if list[index][0]==num:
            index=i
            break
    return index

def price_list(list,prices):
    #takes a list of goods and returns the price of them all
    price=0
    for i in range(len(list)):
        price+=list[i]*prices[i]
    return price

def list_to_order(list, id, lab, pop, buy,sec):
    #converts a list of goods into the appropriate list of orders
    orders=[]
    if buy:
        for i in range(len(list)):
            if list[i]!=0:
                orders.append(buyOrder(id,lab,pop,i,list[i],sec))
    else:
        for i in range(len(list)):
            if list[i]!=0:
                orders.append(sellOrder(id,lab,pop,i,list[i],sec))
    return orders

def add_stock(stock,list):
    #takes two list stocks of equal length and adds
    for i in range(len(stock)):
        stock[i]+=list[i]

def remove_stock(stock,list):
    list2=[-1*x for x in list]
    add_stock(stock,list2)

def bound(bounds, value):
    #given a (lower, upper) bound tuple in bounds and a value, returns either the value or the appropriate upper or lower bound
    #eg bound((1,3),2) will return 2 but bound((1,3),4) will return 4
    if value>bounds[1]:
        return bounds[1]
    elif value<bounds[0]:
        return bounds[0]
    return value


def generate_id():
    #generates a new unique ID
    random.seed()
    return random.random()
