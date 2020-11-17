class pop:
    def __init__(self,popln,s,need):
        #the type of labour pops produce should be in a lookup table of some kind

        self.population=popln
        self.savings=s #liquid cash the pop has
        self.needs=need #list of list of goods the pops need
        self.needsmet=[0*len(need)] #how fufilled pop needs are
        self.bought=[]

        # self.poptype=  #type of pop

        #economic planning variables

        self.income=s #amount of money made last turn
        self.expenses=0 #amount of money spent last turn

        #political variables


class industry:
    def __init__(self,n,prod,s1,s2,c): #prod is an object that describes a production process

        self.name=n

        self.production=prod #the production process this industry undergoes
        self.size=s1 #maximum thoroughput of this industry (how many units of self.production it can do)
        self.savings=s2
        self.capital=c #amount of capital goods that enhance this industry's production
        #should probably include some level of tech here


        #economic planning variables

        self.input=[] #list of goods destined for production input

        self.avgProd=0 #average productivity of the industry given capital and actual units of production

        self.caplevel=c #desired level of capital in the industry

        self.prodPlanLvl=0 #desired level of production in the industry
        self.prodActLvl=0 #actual level of production in the industry last turn

        self.income=s2
        self.expenses=0 #expenses last turn

    def production(self,inputUnits):
        #returns the amount of output units produced from a number of input
        #the function's derivative over units of production reaches a first maximum then asymptotically reaches 0
        #the level of capital in the industry multiplicatively increases production more the less you're producing
        self.avgProd=max(0,)


class order:
    #transaction object used to keep track of goods and services on the market
    def __init__(self,ID,buying,good):
        self.actorID=ID #this is an ID object of the economic actor placing the order
        self.isBuying=buying
        self.goodID=good

class buyOrder(order):
    def __init__(self,ID,good,cash):
        super(buyOrder, self).__init__(ID, True, good)
        self.money=cash #amount of money the actor is paying
        self.amount=0 #amount of goods bought
        self.moneyChange=0 #amount of money that changes hands

class sellOrder(order):
    def __init__(self,ID,good,amt):
        super(sellOrder, self).__init__(ID, False, good)
        self.amount=amt #amount of stuff that actor is selling
        self.money=0 #money gained from sale
        self.moneyChange=0 #amount of money that changes hands, could use self.money but this retains consistency with buyOrder


class technique:
    #defines a production technique industries use to produce goods
    def __init__(self,inputGoods,inputAmts,outputGoods,outputAmts):
        self.inGoods=inputGoods #list of input goods in order
        self.inAmts=inputAmts #list of input amounts in order of self.inputGoods
        self.outGoods=outputGoods
        self.outAmts=outputAmts #same as inputs

