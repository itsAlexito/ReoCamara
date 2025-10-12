# ReoCamara

Bot de telegram encargado de gestionar la cámara de seguridad de Euri. A continuación se explican algunos detalles de funcionamiento, instalación, y mantenimiento para que en el futuro no haya que gastar infinitas horas intentando que vuelva a funcionar

## Funcionamiento

El funcionamiento del bot no es especialmente complicado, pero si es tu primera experiencia con un bot de telegram, o si llevas 1 año sin mirar el repositorio porque la cámara funcionaba sin problemas hasta ayer (o porque no había wifi con la que pudiera funcionar), estas de suerte, porque aquí se explica todo lo necesario para configurar la cámara y el bot antes de instalarlos en el servidor.

**CÁMARA**

El bot está configurado para usarse con una Reolink E1 Zoom. Si pretendes usarlo con otra cámara, te tocará estudiarte la API y cambiar la sintaxis necesaria. Asumiendo que no es el caso, la cámara no tiene mucho misterio:

- Primera conexión: Para conectar la cámara a la Wifi, se puede hacer desde la aplicación de Reolink. La IP que aparezca asignada a la cámara es la que se tendrá que añadir en el .env y con la que se podrá acceder a los ajustes de esta desde cualquier ordenador conectado a la wifi. El usuario y contraseña que configures también tendrás que meterlos en el .env.


- Presets: La mayoría de comandos de la cámara funcionan con presets. Estos son posiciones predeterminadas de la cámara que puedes configurar desde la app y que valen para que al momento de grabar la cámara se mueva por un camino preestablecido y no grabe siempre la misma esquina. Para acceder a los presets en el código, referirse a la variable ROUTES de config.py


- Otras configuraciones: La cámara permite, entre otras cosas, grabar audio, emitir sonidos, etc. Actualmente estas no se usan, pero si en un futuro el que está leyendo esto tiene ganas de innovar le animo a que al menos lo documente para futuras generaciones.

**BOT**

Aquí es donde está toda la chicha (y las fuentes de mi sufrimiento). En los diferentes archivos que componen este bot se encuentran configuradas la gestión de los mensajes recibidos por el grupo, la grabación y procesado de los videos, y el envío de mensajes al grupo. Los archivos que lo componen son: 

*main.py*

Nombre bastante autodescriptivo, lo más interesante que hay aquí son los handlers de los comandos permitidos

*config.py*

En este archivo se definen las macros que usa el bot en su funcionamiento: los comandos existentes, las rutas de la cámara, los chats permitidos, y el tiempo de vida de los mensajes.

*handlers.py*

Aquí se encuentra la parte de procesado de los mensajes recibidos por el grupo. Si la cámara lleva tiempo sin usarse, es posible que haya que modificar la variable url en la función *getImage*. Por lo demás, todo debería funcionar sin problemas.

*camera.py*

Este es el archivo que procesa toda la grabación de la cámara antes de enviarla, y suele ser el más problemático a la hora de configurar el bot después de un tiempo. Ante la duda tras un error, revisar si la API ha sido modificada. Si no es el caso y sigue sin funcionar, buena suerte.  
<br>
En esta parte lo más personalizable es la función *execute_route*, en la cual se puede ajustar cuanto tiempo tarda la cámara en empezar a girar y cuanto tiempo dura el vídeo en total. Por lo demás, todo debería funcionar correctamente tal y como está

*delete.py*

Este archivo es el que gestiona el envío y borrado de los mensajes después de un tiempo. En principio no debería ser necesaria ninguna modificación, puesto que si se quiere modificar el tiempo de vida de los mensajes, se puede hacer desde config.py.


## Instalación

El servidor en el que tiene que correr el bot ya está configurado, por lo que aqui solo se detalla el como iniciar el bot para que empiece a funcionar.

**PASOS PARA LA INSTALACIÓN**

 1. Asumiendo que se está instalando de 0, clonar en el servidor el repositorio haciendo git clone. Si el repositorio ya se encuentra instalado y lo que se quiere es actualizar la versión, basta con ejecutar git pull

 2. Una vez instalado el bot, ajustar los contenidos del .env y el .env.chats asegurandose de que los datos sean válidos. A la hora de configurar la cámara, elegir con cuidado la contraseña ya que algunos carácteres especiales pueden interferir con el procesamiento de la url de las peticiones a la API.

 3. Por último, ejecutar en la carpeta generada con el git clone/git pull: 
```
 docker compose build
 docker compose up -d
```

En el caso de que el bot se encuentre corriendo y se quiera actualizar por cualquier motivo, se deberá ejecutar docker compose down para tumbarlo, y a partir de ahí actualizar el código como se detalla anteriormente.

## Tips & Tricks

Este bot ya me ha tocado montarlo varias veces, y cuando llevas un montón de tiempo sin manejar el código, se puede hacer muy cuesta arriba volver a entenderlo y sobretodo entender qué hay que tocar para que funcione como antes. Entre los consejos que puedo dar (por desgracia basados en mi experiencia personal) están:

- Documentar TODO. Si no, las horas que vas a estar haciendo reverse engineering para recordar donde había que poner cada cosa se te van a hacer largas.

- Tener mucho cuidado con la contraseña que le pones a la cámara. Algunos carácteres especiales pueden hacer que las peticiones a la API no funcionen correctamente.

- Comprobar que en el servidor que va a hostear el bot están todos los requirements instalados. Como digo, en el actual lo están, pero si en un futuro se cambia a otro, no hagas como yo y verifica que tiene ffmpeg y demás antes de desplegar el bot.

- Usa el canal 0 en todas las urls. Aunque desde la interfaz del ordenador aparezca que es el canal 1, la desgraciada indexa en 0. Si no lo usas luego no te extrañes cuando la cámara no gire al grabar.

Espero que en un futuro esto le resulte tan útil a alguien como a mi me hubiera resultado las 2 veces que tuve que levantarlo.