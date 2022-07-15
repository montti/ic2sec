# ic2sec - Seleccion de los mejores r-agentes en una poblacion

El siguiente respositorio contiene el codigo desarollado para el proyecto final de IC2SEC del Grupo 5.

## Parametros
```
activatePurge = True  # Si las modificaciones están activas, con False actuá como CyES normal. 
topElementos = 3      # La cantidad de elementos que sobreviven a la purga y son seleccionados
pesoDiversidad = 5    # El peso de la diversidad en el score de la purga. 
maturityWindow = 400  # El tamaño de la ventana de fitnessHistory que se utiliza para
                      # identificar si la fitness es estable y ver si ya esta madura la población.
                      
maturityLimit = 0.6   # El valor de desviación estándar mínima permitida, bajo este valor se activa la purga. 
purgePoint = 450      # El punto manual para la purga, solo se utiliza si maturityWindow = 0.
loadPickle = False    # Si es verdadero carga un modelo guardado con pickle en vez de generar un modelo de ataque.
pickleFilename = "purge.pkl" # Nombre del archivo pickle a cargar. 
```

## Uso

Si se quiere correr un modelo de ataque ya purgado loadPickle debe ser verdadero, se debe tener el archivo en la misma carpeta y pickleFilename debe ser igual nombre del archivo. El archivo pickle se obtiene corriendo el programa noramalmente. 

Si se quere poner un punto de purga manualmente maturityWindow debe ser igual a 0 y purgePoint igual al punto deseado.

Para correr el programa solamente se debe correr:

```
python3 mainFixed.py

```
Por default se purga en base a la madurez y no manualmente.
