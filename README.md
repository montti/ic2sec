# ic2sec - Seleccion de los mejores r-agentes en una poblacion

El siguiente respositorio contiene el codigo desarollado para el proyecto final de IC2SEC del Grupo 5.

## Parametros
```
activatePurge = True  # Si las modificaciones estan activas, con False actua como CyES normal. 
topElementos = 3      # La cantidad de elementos que sobreviven a la purga y son selecionados
pesoDiversidad = 5    # El peso de la diversidad en el score de la purga. 
maturityWindow = 400  # El tamaño de la ventana de fitnessHistory que se utiliza para
                      # identificar si la fitness es estable y ver si ya esta madura la poblacion.
                      
maturityLimit = 0.6   # El valor de desviacion estandar minima permitida, bajo este valor se activa la purga. 
purgePoint = 450      # El punto manual para la purga, solo se utiliza si maturityWindow = 0.
loadPickle = False    # Si es verdadero carga un modelo guardado con pickle en vez de generar un modelo de ataque.
pickleFilename = "purge.pkl" # Nombre del archivo pickle a cargar. 
```

## Uso
