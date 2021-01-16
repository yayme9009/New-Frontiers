from classes import *

#this file contains all the input and output functions

def read_labGoods(filepath="scenario\\goods.txt"):
    #this reads in a file that states the names of goods and labour types and returns two dictionaries that index a number to their name
    file=open(filepath)
    lines=file.readlines()

    labEnd=False #counter that determines when the labour section is over

    labour={}
    goods={}
    counter=0 #counter for goods or labour produced

    #first is going to be labour
    for line in lines:
        if not labEnd:
            if line!="\n":
                labour[line[:-1]]=counter
                counter+=1
            else:
                labEnd=True
                counter=0
        else:
            if line!="\n":
                goods[line[:-1]]=counter
                counter+=1

    file.close()

    return [labour,goods]

def read_techniques(labourDict,goodsDict,filepath="scenario\\techniques.txt"):
    #reads a production technique file at filepath
    #first name, labourtype needed, then inputs,outputs,capital and size units all separated by empty lines "\n" and separated by 3 dashes

    file=open(filepath)
    lines=file.readlines()
    techniques={}
    stage=0 #reading name, labour type, then inputs, outputs, capital and size units (up to 5)

    lab=0
    name=""
    inputGoods=[]
    inputAmounts=[]
    outputGoods=[]
    outputAmounts=[]
    capital=[0]*len(goodsDict)
    size=[0]*len(goodsDict)
    for line in lines:
        if (line!="\n")and(line!="---\n"):
            if stage==0:
                name=line[:-1]
                stage+=1
            elif stage==1:
                #labour type
                lab=labourDict[line[:-1]]
                stage+=1
            elif stage==2:
                #inputs
                halves=line[:-1].split(":")
                inputGoods.append(goodsDict[halves[0].strip()])
                inputAmounts.append(float(halves[1].strip()))
            elif stage==3:
                #outputs
                halves = line[:-1].split(":")
                outputGoods.append(goodsDict[halves[0].strip()])
                outputAmounts.append(float(halves[1].strip()))
            elif stage==4:
                #capital unit
                halves=line[:-1].split(":")
                capital[goodsDict[halves[0].strip()]]=float(halves[1].strip())
            elif stage==5:
                #size unit
                halves = line[:-1].split(":")
                size[goodsDict[halves[0].strip()]] = float(halves[1].strip())
        elif line=="\n":
            stage+=1 #new stage
        else:
            #first create new technique object
            techniques[name]=technique(lab,inputGoods,inputAmounts,outputGoods,outputAmounts,capital,size)
            #reset all technique variables
            name=""
            lab = 0
            inputGoods = []
            inputAmounts = []
            outputGoods = []
            outputAmounts = []
            capital = [0] * len(goodsDict)
            size = [0] * len(goodsDict)
            stage=0

            #this also means you need a ---\n to end the file (including the newline!)

    file.close()
    return techniques

def read_needs(goodsDict,filepath="scenario\\needs.txt"):
    #reads needs of pops
    #TODO: have a hierarchy of pop needs
    #TODO: have different sets of needs for different pops
    needs=[0]*len(goodsDict)
    file=open(filepath)
    lines=file.readlines()
    for line in lines:
        halves=line.split(":")
        needs[goodsDict[halves[0].strip()]]=float(halves[1].strip())

    return needs

def read_poptypes(filepath="scenario\\poptypes.txt"):
    #read types of pops
    file=open(filepath)
    lines=file.readlines()
    returnDict={}
    for i in range(len(lines)):
        returnDict[lines[i][:-1]]=i
    return returnDict

def read_planets(labourDict,goodsDict,techniquesDict,popTypesDict,needslist,filepath="scenario\\planets.txt"):
    #reads in economic data for all planets
    #uses empty lines to seperate sections and triple dashes to separate planets
    #if/when solar systems are implemented split those by triple asterisks
    #implement diff labour types as well
    file=open(filepath)
    lines=file.readlines()

    stage=0
    planets=[]
    planetCounter=0

    for line in lines:
        if (line!="\n")and(line!="***\n"):
            if stage==0:
                #ownership data about the planet's industries
                params=line.split(",")
                own=ownership(len(popTypesDict))
                own.pops=[float(x) for x in params[:len(popTypesDict)]]
                #TODO: when implementing companies have something here
                #maybe separate by semicolon
                #TODO: when implementing governments put something here
                planets.append(planet((0,0),own,len(labourDict),len(goodsDict)))
            elif stage==1:
                #currently this means pop information
                #right now only size and savings needed, separated by spaces
                params=line.split(",")
                planets[planetCounter].pops.append(pop(len(planets[planetCounter].pops),popTypesDict[params[0]],int(params[1]),float(params[2]),needslist[0])) #currently has only one set of needs, fix later
            elif stage==2:
                #industries
                #parameters: name, name of production technique, size, savings, capital level
                params=line.split(",")
                newid=generate_id()
                planets[planetCounter].industries[newid]=industry(newid,params[0],techniquesDict[params[1]],int(params[2]),float(params[3]),int(params[4]),len(labourDict),len(goodsDict))
        elif line=="\n":
            stage+=1
        else:
            #new planet
            planetCounter+=1
            #planets.append(planet((0,0),len(labourDict),len(goodsDict),len(popTypesDict)))
            stage=0

    file.close()

    return planets










#output functions
def write_log_header(filepath="data\\log.csv"):
    file=open(filepath,"w")
    file.write("Turn #,Population,Needs Fulfillment,GDP,Money Supply,Pop Savings,Industrial Savings,Total Capacity,Average Capital,Rate of Profit,Rate of Surplus Value,Organic Composition of Capital\n")
    file.close()

def write_to_log(turnnum,planets,filepath="data\\log.csv"):
    file=open(filepath,"a")

    writeString=str(turnnum)+","
    population=0
    fulfillavg=0
    fulfill=0
    money=0
    GDP=0
    companySize=0
    popSavings=0
    indSavings=0
    GINI=0
    for planet in planets:
        money+=planet.investment

        #GINI=calculate_GINI(planet.pops)

        for pop in planet.pops:
            population+=pop.population
            fulfill+=sum(pop.needsmet)/len(pop.needsmet)
            money+=pop.savings
            popSavings+=pop.savings
            GDP+=pop.income-pop.dividend #avoid double-counting

        fulfillavg+=fulfill/len(planet.pops)
        #GDP+=price_list(planet.supply,planet.prices)


        for key,ind in planet.industries.items():
            companySize+=ind.size
            money+=ind.savings
            indSavings+=ind.savings
            GDP+=ind.income

    fulfillavg=fulfillavg/len(planets)
    writeString+=str(population)+","+str(fulfillavg)+","+str(GDP)+","+str(money)+","+str(popSavings)+","+str(indSavings)+","

    #Marxian indicators
    ROP=0
    OOC=0
    ROSV=0
    capital=0
    for planet in planets:
        for key,ind in planet.industries.items():
            ROP+=ind.ROP*ind.size/companySize
            OOC+=ind.OOC*ind.size/companySize
            ROSV+=ind.ROSV*ind.size/companySize
            capital+=ind.capital
        capital=capital/len(planet.industries)
    capital=capital/len(planets)


    writeString+=str(companySize)+","+str(capital)+","+str(ROP)+","+str(ROSV)+","+str(OOC)+"\n"

    file.write(writeString)

    file.close()

def write_goods_header(invlabDict,invgoodsDict,filePath="data\\goods.csv"):
    #since there's only one planet no need for # of planet data here
    writeString=""
    file=open(filePath,"w")
    for i in range(len(invlabDict)):
        labour=invlabDict[i]
        writeString+=labour+"Price,"+labour+"Demand,"+labour+"Supply,"
    for i in range(len(invgoodsDict)):
        good=invgoodsDict[i]
        writeString+=good+"Price,"+good+"Demand,"+good+"Supply,"
    file.write(writeString[:-1]+"\n")
    file.close()

def write_goods(planets,filePath="data\\goods.csv"):
    #currently since there's one planet only one set of wages and prices are set
    writeString=""
    file=open(filePath,"a")

    planet=planets[0]

    for i in range(len(planets[0].wages)):
        writeString+=str(planets[0].wages[i])+","+str(planets[0].labDemand[i])+","+str(planets[0].labSupply[i])+","
    for i in range(len(planets[0].prices)):
        writeString += str(planets[0].prices[i]) + "," + str(planets[0].demand[i]) + "," + str(planets[0].supply[i]) + ","

    file.write(writeString[:-1]+"\n")
    file.close()


def split_with_quotes(string):
    #splits string at spaces except between quotation marks

    quotes=string.split("\"")
    returnlist=quotes[0].split()
    inQuote=True #since starting at 2nd unit
    if len(quotes)==0:
        return returnlist
    for i in range(1,len(quotes)):
        if inQuote:
            returnlist.append(quotes[i])
        else:
            returnlist.append(quotes[i].split())
        inQuote=not inQuote

    return returnlist

def calculate_GINI(pops):
    #given a pops list, this function will calculate their income inequality
    incomes=[]
    populations=[]
    for pop in pops:
        incomes.append(pop.income)
        populations.append(pop.population)
    #zip them together and sort by income
    zipped=zip(incomes,populations)
    sortedLists=sorted(zipped)
    incomes = []
    populations = []
    for x,y in sortedLists:
        incomes.append(x)
        populations.append(y)
    totalPop = sum(populations)
    totalInc = sum(incomes)

    incomeShare=incomes[0]/totalInc
    popShare=populations[0]/totalPop
    area=(incomes[0]/totalInc)*(populations[0]/totalPop)/2 #first pop add here

    for i in range(1,len(pops)):
        area+=incomeShare*popShare+((incomes[i]/totalInc)*(populations[i]/totalPop)/2)

    return (0.5-area)/0.5