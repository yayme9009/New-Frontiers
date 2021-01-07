from classes import *

#this file contains all the input and output functions

def read_labGoods(filepath="goods.txt"):
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

def read_techniques(labourDict,goodsDict,filepath="techniques.txt"):
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
                capital[goodsDict[halves[0].strip()]]=int(halves[1].strip())
            elif stage==5:
                #size unit
                halves = line[:-1].split(":")
                size[goodsDict[halves[0].strip()]] = int(halves[1].strip())
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

def read_needs(goodsDict,filepath="needs.txt"):
    #reads needs of pops
    #TODO: have different sets of needs for different pops
    needs=[0*len(goodsDict)]
    file=open(filepath)
    lines=file.readlines()
    for line in lines:
        halves=line.split(":")
        needs[goodsDict[halves[0].strip()]]=float(halves[1].strip())

    return needs

def read_planets(labourDict,goodsDict,techniquesDict,needslist,filepath="planets.txt"):
    #reads in economic data for all planets
    #uses empty lines to seperate sections and triple dashes to separate planets
    #if/when solar systems are implemented split those by triple asterisks
    #implement diff labour types as well
    file=open(filepath)
    lines=file.readlines()

    stage=0
    planets=[planet((0,0),len(labourDict),len(goodsDict))]
    planetCounter=0

    for line in lines:
        if (line!="\n")and(line!="***\n"):
            if stage==0:
                #currently this means pop information
                #right now only size and savings needed, separated by spaces
                params=line.split(",")
                planets[planetCounter].pops.append(pop(len(planets[planetCounter].pops)-1,int(params[0]),float(params[1]),needslist[0])) #currently has only one set of needs, fix later
            elif stage==1:
                #industries
                #parameters: name, name of production technique, size, savings, capital level
                params=line.split(",")
                planets[planetCounter].industries.append(industry(len(planets[planetCounter].industries)-1,params[0],techniquesDict[params[1]],int(params[2]),float(params[3]),int(params[4]),len(labourDict),len(goodsDict)))
        elif line=="\n":
            stage+=1
        else:
            #new planet
            planetCounter+=1
            planets.append(planet((0,0),len(labourDict),len(goodsDict)))
            stage=0

    file.close()

    return planets



#output functions
def write_log_header(filepath="log.csv"):
    file=open(filepath,"w")
    file.write("Turn #,Population,Needs Fulfillment,GDP,Money Supply,Rate of Profit,Rate of Surplus Value,Organic Composition of Capital\n")
    file.close()

def write_to_log(turnnum,planets,filepath="log.csv"):
    file=open(filepath,"a")

    writeString=str(turnnum)+","
    population=0
    fulfillavg=0
    fulfill=0
    money=0
    GDP=0
    companySize=0
    for planet in planets:
        for pop in planet.pops:
            population+=pop.population
            fulfill+=sum(pop.needsmet)/len(pop.needsmet)
            money+=pop.savings
            GDP+=pop.income

        fulfillavg+=fulfill/len(planet.pops)
        #GDP+=price_list(planet.supply,planet.prices)


        for ind in planet.industries:
            companySize+=ind.size
            money+=ind.savings
            GDP+=ind.income

    fulfillavg=fulfillavg/len(planets)
    writeString+=str(population)+","+str(fulfillavg)+","+str(GDP)+","+str(money)+","

    #Marxian indicators
    ROP=0
    OOC=0
    ROSV=0
    for planet in planets:
        for ind in planet.industries:
            surplus=(ind.income-(ind.maintenance-ind.labour))
            ROP+=(surplus)/(ind.maintenance+ind.labour)*ind.size/companySize
            OOC+=(ind.maintenance/ind.labour)*ind.size/companySize
            ROSV+=(surplus/(surplus+ind.labour))*ind.size/companySize

    writeString+=str(ROP)+","+str(ROSV)+","+str(OOC)+"\n"

    file.write(writeString)

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


