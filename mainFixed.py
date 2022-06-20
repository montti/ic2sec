import random, copy
import matplotlib.pyplot as plt
import operator
import pickle

## PARÁMETROS DE LA EVOLUCIÓN
contadorIndividuos = 0 #Contador de individuos para ID
margenChoose = 0.1 #Margen de choosePackets() del individuo
mutacion = 0.05 # Porcentaje de mutacion del inviduo
initialPop = 100 #Cantidad de individuos, poblacion inicial
umbralPackets = 50 #umbral de minimos paquetes para agregarlos a diccionario  
percentageElitism = 0.4 #Porcentaje de elitismo a realizar
newMemory = 10 #Cantidad de ciclos para actualizar celula de memoria
cycles = 10 #Cantidad de paquetes para evaluar la población
attackThreshold = 30 #Cantidad de feromona para declarar un ataque
evaporationRate = 1 #Velocidad de evaporacion de la feromona
feromoneAdded = 10 #Cantidad de feromona a agregar en cada evaluacion que indica ataque
porcentajeAtaque = 0.3 #Porcentaje de baja del fitness para detectar un ataque
grafico = "promedio"
## FIN PARÁMETROS DE LA EVOLUCIÓN

## Parametros Grupo 5
activatePurge = True # Si la modificacion del modelo esta activa. 
topElementos = 3 # Los elementos que sobreviven a la purga.
pesoDiversidad = 10 # Cuanto peso tiene la diversidad en el score de la purga. 
diversityCutoff = 0 # El valor de la diversidad promedio para que se congele el modelo de ataque. 
purgePoint = 200 # Si no se utliza un cutoff de diversidad, utlizamos un punto manual para congelar el modelo. 
loadPickle = True # Carga un modelo guardado con pickle en vez de generar un modelo de ataque.
pickleFilename = "purge.pkl" # Nombre del archivo pickle. 
##

#Contador para tipos de paquetes, para actualizar los genes de los agentes y el comodín
packetList = {}

class individual:
    #El diccionario "genes" tiene la forma:
    # {
    #   packetID: [[packetID, probability], ..., [packetID, probability]], 
    #   .
    #   .
    #   .
    #   packetID: [[packetID, probability], ..., [packetID, probability]]
    # }
    # packetID es el string resultante del hash (o lo que sea que se vaya a usar) de identificación de cada tipo de paquete
    def __init__(self, i = -1, g = {}, e = 0, f = 0, fM = 0, d = 0):
        self.id = i
        self.genes = g
        self.energy = e
        self.fitness = f
        self.fitnessMemory = fM

        # Añadido Grupo 5

        self.diversity = d

    def __repr__(self):
        g = ""
        for i in self.genes:
            g = g + str(i) + ": " + str(self.genes[i]) + "\n"
        return "ID: " + str(self.id) + "\nGenes:\n" + g +  "\nEnergy: " + str(self.energy) + "\nFitness: " + str(self.fitness) + "\nDiversity: " + str(self.diversity) + "\n--------------------\n"

    # Añadido Grupo 5 

    def setDiversity(self, d = 0):
        self.diversity = d

    #Felipe/Alan
    def eatPacket(self, packet = None, packetAnt = None):
        """Alimentar a individuo con packet.

        Args:
            packet: El paquete parseado para alimentar a la población (def = None)
            packetAnt: El paquete parseado anteriormente (def = None)
        """
        #print(packetAnt)
        if(packetAnt == None or packetAnt not in self.genes.keys()):
            packetAnt = "*"
        fMarkov = self.genes[packetAnt]
        packets = self.choosePackets(fMarkov)
        if packet in packets or (packet not in self.genes.keys() and "*" in packets):
            self.fitness = self.fitness + 1

    

    def choosePackets(self, fMarkov = []):
        """Elegir apuesta individuo.
        
        Args:
            fMarkov: Fila en la matriz de markov del agente, que corresponde al paquete anteriormente llegado

        Returns:
            packets: Paquetes a los cuales se le apuesta.
        """
        packets = [] # Se guardaran las mejores opciones
        #margenChoose = 0.1
        max = [None, 0]
        for i in fMarkov:
            if max[1] <= i[1]:
                max = i
        packets.append(max[0])

        for i in fMarkov:
            if i[1] >= max[1]-(max[1]*margenChoose) and max != i:
                packets.append(i[0])
        
        return packets
    
    #Felipe/Alan CAMBIAR ESTO
    def mutate2(self):
        """Mutar el individuo."""
        #mutacion = 0.05
        for i in self.genes.keys():
            rand = random.random()
            if rand <= mutacion:
                n1 = random.randint(0,len(self.genes[i])-1)
                n2 = random.randint(0,len(self.genes[i])-1)
                temp = self.genes[i][n1][1]*0.5
                self.genes[i][n1][1] = self.genes[i][n1][1]-temp
                self.genes[i][n2][1] = self.genes[i][n2][1]+temp
    
    def mutate(self):
        """Mutar el individuo."""
        #mutacion = 0.05
        for i in self.genes.keys():
            rand = random.random()
            if rand <= mutacion:
                n1 = random.randint(0,len(self.genes[i])-1)
                n2 = random.randint(0,len(self.genes[i])-1)
                temp = self.genes[i][n1][1]
                self.genes[i][n1][1] = self.genes[i][n2][1]
                self.genes[i][n2][1] = temp 
    
    # mutacion es el porcentaje de mutacion para cada gen del individuo. Escogiendo
    # dos random se logra intercambiar las probabilidades de cada packet    

    def updateGenesWithPacket(self, packet = None):
        """Actualizar los genes de los individuos para incluir el paquete 'packet', visto muchas veces.

        Args:
            packet: El paquete que se quiere agregar a los genes de la poblacion (def = None)
        """
        for i in self.genes:
            newPacketChance = round(self.genes[i][0][1] / 2, 2)
            newJchance = self.genes[i][0][1] - newPacketChance
            self.genes[i].append([packet, newPacketChance])
            self.genes[i][0][1] = newJchance
        #print(selfModel)

        self.genes[packet] = []    
        geneLine = []
        m = 100
        for i in self.genes:
            val = random.randint(0, m)
            m = m - val
            geneLine.append([i, val / 100])
        geneLine[-1][1] = (val + m) / 100
        self.genes[packet] = geneLine
        #print("Post update:")
        #print(self)
        #input()



class model:
    def __init__(self, pop = [], modelType = "normal"):
        self.population = pop
        self.memory = None
        self.type = modelType
        self.alertLevel = 0
        self.repose = False
        self.timeActive = 0
        self.fitnessHistory = []

        # Añadido Grupo 5
        # Evita que se ejecute, el crossover y mutacion. Sirve para un modelo que
        # ya se selccionaron sus mejores agentes.

        self.freeze = False

    def __repr__(self):
        return str(self.population)

    #Matias
    def initializePop(self, num = 100):
        """Generar población inicial.
    
        Args:
            num: Tamaño de la población (def = 100)
        """
        for i in range(num):
            gene = {
                "*" : [["*", 1]]
            }
            self.population.append(individual(i, gene, 0, 0))
        contadorIndividuos = num

    # Añadido Grupo 5

    def calculateDiversity(self):
        """ Calcula la diversidad de cada agente.
        """

        for i in self.population:
            # Incializamos la diversidad
            div = 0

            # Obtenemos las probabilidades de los genes
            listProb = self.flatGenes(i.genes)
            for j in self.population:
                listProbAux = self.flatGenes(j.genes)

                # Restamos las probablidades.
                aux = list(map(operator.sub, listProb, listProbAux))

                # Sacamos sus valores absolutos.
                aux = list(map(abs, aux))

                # Sumamos todos los valores.
                div += sum(aux) 

            # Guardamos la diversidad del agente como su diversidad absoluta dividida por la poblacion.
            # Esto asume que la poblacion es constante. 

            # print(div / initialPop)
            i.setDiversity(div / initialPop)

    def flatGenes(self, genes = {}):
        """ Transforma los genes de un agente a una lista solamente con sus probabilidades.

         Args:
            genes: Los genes del agente.
        """

        # Debe existir una manera mas eficiente y legible de hacer esto. Es temporal.

        # Pasa los valores del diccionario a una lista. 
        aux = list(genes.values())

        # Transforma la lista de 2D a 1D
        aux = [x for sub in aux for x in sub]

        # Solo guarda las probabilidades. 
        aux = [x[1] for x in aux]

        return aux


    #---
    def feedPop(self, packet = None, lastPacket = None):
        """Alimentar a la poblacion de este modelo.

        Args:
            packet: El paquete con que se va a alimentar (def = None)
            lastPacket: Paquete anteriormente recibido
        """
        for i in self.population:
            i.eatPacket(packet, lastPacket)
        if(self.memory != None):
            self.memory.eatPacket(packet, lastPacket)

    def memoryUpdate(self):
        """Darle un punto de fitnessMemory a los individuos de la poblacion con mayor fitness despues de un ciclo.
        """
        maxFitness = self.population[0]
        i = 0
        while self.population[i] == maxFitness and len(self.population)<i:
            self.population[i].fitnessMemory+1
            i+1
    
    def memoryChange(self):
        """Cambiar la memoria de la poblacion, eligiendo al con mayor fitnessMemory
        """
        sorted(self.population, key = orderByMemoryFitness, reverse = True)
        self.memory = copy.deepcopy(self.population[0])
        for i in self.population:
            i.fitnessMemory = 0


    #Felipe/Alan
    def selectParents(self, num = 2):
        """Seleccionar num padres (usando torneo) y retornarlos como lista.
        
        Returns:
            p: Lista de padres
        """
        p = []
        for i in range(num):
            p.append(self.torneoSelect(2))
        
        return p

    def torneoSelect(self, size = 2):
        """ Seleccionar mejor opcion, retornandola. Si ambos son iguales, se retorna uno al azar.

        Returns:
            o1 o o2: Mejor opcion.
        """
        #popCopy = copy.deepcopy(self.population)
        #random.shuffle(popCopy)
        #participants = popCopy[0:size]
        #participants.sort(key = orderByFitness, reverse = True)
        #return participants[0]

        popIDs = []
        for i in range(size):
            popIDs.append(1)
        for i in range(len(self.population) - size):
            popIDs.append(0)

        random.shuffle(popIDs)
        participants = [i for i, j in zip(self.population, popIDs) if j]
        participants.sort(key = orderByFitness, reverse = True)
        return copy.deepcopy(participants[0])

        #o1 = random.choice(self.population)
        #o2 = random.choice(self.population)
        #if o1.fitness > o2.fitness:
        #    return o1
        #elif o1.fitness < o2.fitness:
        #    return o2
        #else:
        #    return random.choice([o1,o2])

    def checkDictionaryUpdate(self, models):
        """Revisar si hay algun paquete nuevo que agregar a su matriz de markov
        """
        commonPackets = list(dict(filter(lambda p: int(p[1]) >= umbralPackets, packetList.items())).keys())
        for i in commonPackets:
            agente = self.population[0]
            if i not in agente.genes:
                for j in models:
                    for k in j.population:
                        k.updateGenesWithPacket(i)
                
    
    def evaporate(self, amount = 1):
        """Evaporar la cantidad de feromona/señal.

        Args:
            amount: Cantidad de feromona/señal a evaporar
        """
        self.alertLevel = max(self.alertLevel - amount, 0)

    def addFeromone(self, amount = 1):
        """Agregar la cantidad de feromona/señal.

        Args:
            amount: Cantidad de feromona/señal a agregar
        """
        self.alertLevel = self.alertLevel + amount

def elitism(population,news):
    """Ordenar segun fitness y eliminar a los peores reemplazandolos por los hijos creados.
        
    Args:
        population: Poblacion que va a conservar a los mejores
        news: Hijos creados que se agregaran a la poblacion (population)
    """
    population = sorted(population, key = orderByFitness, reverse = True)
    population = population[:(len(population)-len(news))]
    population.extend(news)
    return population

def orderByFitness(x):
    return x.fitness

def orderByMemoryFitness(x):
    return x.fitnessMemory

def purgeElitism(population, top = 3):
    """ Seleciona los mejores agentes.
    Args:
        population: poblacion del modelo.
        top: El numero que quedaran en modelo
        k: Parametro que indica cuanto vale la diversidad para el score de cada agente.
            Score(Agente) = fitness(Agente) + k * diversity(Agente)
    """

    population = sorted(population, key = orderByScore, reverse=True)
    population = population[:top]

    return population

def orderByScore(x, k = pesoDiversidad):
    return x.fitness + k * x.diversity

#Martin
def makeUsableList(inputList = None):
    """Recibir una lista con todos los elementos de la entrada, retornar una lista con solo los elementos relevantes.
    Esto depende mucho de la entrada y su formato, de momento se trabaja igual como se hacia en CyES, quedando abierto a cambios una vez que se sepa como van a llegar los datos que nos van a entregar
    
    Args:
        inputList: Lista completa (def = None)

    Returns:
        usableList: Lista con solo los elementos relevantes
    """
    usableList = []
    usableList.append(inputList[7])
    usableList.append(inputList[8])
    usableList.append(inputList[9])
    
    for i in range(11,19):
        usableList.append(inputList[i])
    
    for i in range(25,54):
        usableList.append(inputList[i])
            
    return usableList
    
def parsePacket(file = None):
    """Interpretar 1 linea del archivo de entrada, retornar el resultado.

    Args:
        file: Archivo a leer (def = None)
    
    Returns:
        p: Paquete procesado, en forma de string
    """
    p = []
    line = file.readline()
    #for elem in line.split():
    #    p.append(int(elem))
    #p = ''.join(map(str, makeUsableList(p)))
    p = line
    return p
    
#Felipe/Alan PROMEDIAR PADRES
def crossIndividuals2(parent1 = {}, parent2 = {}):
    """Hacer 2 hijos a partir de los genes de los padres y retornarlos.

    Args:
        parent1: Genes del padre 1 para crear un hijo (def = None)
        parent2: Genes del padre 2 para crear un hijo (def = None)
    
    Returns:
        h1: Hijo generado
    """
    d1 = {}
    c = 0
    for i in parent1.keys():
        lista = []
        for j in range(len(parent1.get(i))):
           probability = ((parent1.get(i))[j][1]+(parent2.get(i))[j][1])/2
           lista.append([parent1.get(i)[j][0],probability])
        d1[i] = lista
    global contadorIndividuos
    contadorIndividuos = contadorIndividuos + 1
    return individual(contadorIndividuos-1,d1,0,0)

def crossIndividuals(parent1 = {}, parent2 = {}):
    """Hacer 2 hijos a partir de los genes de los padres y retornarlos.

    Args:
        parent1: Genes del padre 1 para crear un hijo (def = None)
        parent2: Genes del padre 2 para crear un hijo (def = None)
    
    Returns:
        h1, h2: Los 2 hijos
    """
    d1 = {}
    d2 = {}
    c = 0
    for i in parent1.keys():
        if c % 2 == 0:
            d1[i] = parent1[i]
            d2[i] = parent2[i]
        else:
            d1[i] = parent2[i]
            d2[i] = parent1[i]
        print(str(type(parent1.get(i)))+" "+ str(len(parent1.get(i)))+" "+ str(parent1.get(i)[0][1]))
        c = c + 1
    global contadorIndividuos
    contadorIndividuos = contadorIndividuos + 2
    return individual(contadorIndividuos-1,d1,0,0),individual(contadorIndividuos,d2,0,0)

def evaluatePop(model = None):
    """Obtener una evaluación de la población del modelo "model".

    Args:
        model: El modelo a evaluar (def = None)

    Returns:
        totalFitness: La suma de las fitness de toda la población.
    """
    
    if grafico=="promedio":
        totalFitness = 0
        for i in model.population:
            totalFitness = totalFitness + i.fitness
        totalFitness = totalFitness/len(model.population)
    
    elif grafico=="elite":
        totalFitness = 0
        for i in range(int(len(model.population)*percentageElitism)):
            totalFitness = totalFitness + model.population[i].fitness
        totalFitness = totalFitness/int(len(model.population)*percentageElitism)
    
    else:
        totalFitness = -1    
        if(model.memory != None):
            totalFitness = model.memory.fitness

    return totalFitness

def attack(listFitness,models = None):
    """Evaluar posible ataque".

    Args:
        listFitness: lista del fitness historico

    Returns:
        booleano que determina si está en ataque
    """
    if models == None:
        if len(listFitness) > 11:
            for i in range(len(listFitness)-10,len(listFitness)):
                if listFitness[i]!= 0:
                    porcentaje = 1-(listFitness[-1]/listFitness[i])
                    if porcentaje >= porcentajeAtaque:
                        return True

        if bool(listFitness) and listFitness[-1] <= 5:
            return True
    else:
        for i in models:
            if i.repose:
                if i.fitnessHistory[-1]>=listFitness[-1]:
                    return True 
    return False 


#Creamos los modelos
selfModel = model()
selfModels = [selfModel]
nonSelfModels = []
selfModel.repose = False
ataqueModel = None
#ataqueModel = model(pop = selfModel.population, signal = True, modelType = "ataque")
#nonSelfModels.append(ataqueModel)

#Inicializamos la poblacion
selfModel.initializePop(initialPop)

#print(selfModel)

file1 = open("data/normal+ataque_parsed.txt", "rt")
file2 = open("data/incidente_parsed.txt", "rt")

if loadPickle:
    filePickle = open(pickleFilename, 'rb')

currentFile = file1

ticks = 0 

fitnessHistory = []

lastPacket = None


while(True):
    ticks = ticks + 1
    models = selfModels + nonSelfModels
    if(ticks % 100 == 0):
        for i in models:
            #print(i.type+" "+str(len(i.population[-1].genes)))
            if not i.repose:
                print(str(ticks)+" "+i.type)
    
    #if(ticks == 68634):
    #    currentFile = file2

    #Leemos y procesamos el siguiente paquete
    packet = parsePacket(currentFile)
    if(packet == ""):
        # Testing

        #ataqueModel.calculateDiversity()
        #ataqueModel.population = purgeElitism(ataqueModel.population)
        # Este freeze no hace nada al ejecutar esto al final del programa, pero hay que recordarlo
        # para despues.  
        #ataqueModel.freeze = True
        #print(ataqueModel.population)
        #print(len(ataqueModel.population))

        #print(ataqueModel.population[0].genes)
        #print(ataqueModel.population[1].genes)
        #print(ataqueModel.population[2].genes)
        # Fin Testing

        print("Parece que se terminó el archivo")
        legend = []
        for i in models:
            plt.plot(i.fitnessHistory)
            legend.append(i.type)
            #print(i.fitnessHistory)
        plt.title("Normalidad vs Ataque")
        plt.legend(legend)
        plt.show()
        #print(models)
        exit(0)

    if(packet in packetList):
        packetList[packet] = packetList[packet] + 1
    else:
        packetList[packet] = 1
           

    for i in models:
        #Alimentamos a el/los modelos
        i.feedPop(packet, lastPacket)
        if not i.repose:
            i.timeActive = i.timeActive + 1
        #Vemos si es necesario realizar cambio al modelo de ataque
        if (not i.repose) and i.alertLevel>attackThreshold and i.timeActive>=100:
            if ataqueModel == None:
                if loadPickle:
                    ataqueModel = pickle.load(filePickle)
                    ataqueModel.fitnessHistory = [0] * len(fitnessHistory)
                else:
                    ataqueModel = model(pop = copy.deepcopy(selfModel.population), modelType = "ataque")
                    ataqueModel.fitnessHistory = fitnessHistory

                nonSelfModels.append(ataqueModel)
                models = selfModels + nonSelfModels
            else:
                 for j in models:
                     if j.repose:
                        j.alertLevel = 0
                        j.repose = False
                        j.timeActive = 0
            i.repose = True
            i.alertLevel = 0
            i.timeActive = 0
            print("cambio")

    #Esto controla cada cuantas generaciones se realiza una cruza. (def = 1, osea en todas)
    if(not ticks % cycles):
        #print(ticks)
        #print(selfModel)
        #input()
        for i in models:
            medianFitness = evaluatePop(i)
            if ataqueModel == None:
                fitnessHistory.append(-1)
            #Evaporamos la feromona de las poblaciones
            i.evaporate(evaporationRate)
            i.fitnessHistory.append(medianFitness)
            
            
        
        for i in models:
            if not i.repose and i.timeActive>=100:
                if attack(i.fitnessHistory) and ticks > newMemory*2:
                    print("EN ATAQUE "+str(i.alertLevel)+" "+i.type+" "+str(i.timeActive))
                    i.addFeromone(feromoneAdded)
    
        #Realizamos la seleccion de padres
        for i in models:
            # Añadido Grupo 5 
            # Evitamos que la poblacion cambie para el modelo ya "congelado".
            if (not i.repose) and (not i.freeze):
                parentsSize = int(len(i.population)*(1-percentageElitism))*2
                parents = i.selectParents(parentsSize if parentsSize%2==0 else parentsSize+1)
                #Realizamos la cruza
                new = []
                for j in range(0, len(parents), 2):
                    h1 = crossIndividuals2(parents[j].genes, parents[j + 1].genes)
                    #h2 = crossIndividuals2(parents[j+2].genes, parents[j + 3].genes)
                    h1.mutate2()
                    #h2.mutate()
                    new.append(h1)
                    #new.append(h2)
                i.population = elitism(i.population,new)
                i.memoryUpdate()
                if((not ticks % newMemory) and (ticks !=0)):
                    i.memoryChange()
            for j in i.population:
                j.fitness = 0
            if i.memory != None:
                i.memory.fitness = 0
        #Actualizamos la matriz de todos los agentes si hay un nuevo paquete que agregar a sus genes
        i.checkDictionaryUpdate(models)
        
        # Esto basicamente congela el modelo de ataque cuando la diversidad baja de un punto. 
        # No funciona realmente, si no se me ocurre otra cosa voy a simplemente seleccionar un set de
        # ticks para hacer los tesst vs el modelo normal.

        if (activatePurge == True) and (ataqueModel != None) and (ataqueModel.freeze != True):
            ataqueModel.calculateDiversity()

            aux = 0

            for i in ataqueModel.population:
                aux += i.diversity

            if(ticks % 100 == 0): 
                print(aux / initialPop)

            # Revisamos si tenemos un punto manual o es por diversidad.

            if diversityCutoff == 0:
                if int(ticks / cycles) == purgePoint: 
                    print("FREEZE " + str(ticks / 10))

                    ataqueModel.freeze = True

                    outf = open('normal.pkl', 'wb')

                    pickle.dump(ataqueModel, outf)

                    outf.close()

                    ataqueModel.population = purgeElitism(ataqueModel.population)

                    outf = open('purge.pkl', 'wb')

                    pickle.dump(ataqueModel, outf)

                    outf.close()
            elif ((aux / initialPop) < diversityCutoff):
                    print("FREEZE " + str(ticks / 10))

                    ataqueModel.freeze = True

                    outf = open('normal.pkl', 'wb')

                    pickle.dump(ataqueModel, outf)

                    outf.close()

                    ataqueModel.population = purgeElitism(ataqueModel.population)

                    outf = open('purge.pkl', 'wb')

                    pickle.dump(ataqueModel, outf)

                    outf.close()

    lastPacket = packet


#Este es el ciclo de vida basico para el modelo, le falta la interaccion entre los 2+ modelos
