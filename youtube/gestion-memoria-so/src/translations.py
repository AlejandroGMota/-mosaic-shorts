"""Cue-by-cue translations of gestion-memoria-so.es (same order/timing as the Spanish cues)."""
EN = """Memory management by the operating system.
The goal of this video is to understand how an operating system frees and allocates
memory space to the different programs.
To do this, we need to understand that there are two types of memory:
main memory and secondary memory.
Main memory is made up of RAM and ROM.
RAM stores the information a program needs
while it runs.
It accesses data regardless of the order in which it is stored.
This memory loses its data when it stops receiving power.
ROM is read-only;
it stores the essential software the computer needs
to boot. It checks that the components are working correctly,
and it keeps its information whether it receives power
or not. Secondary memory, on the other hand, is where
programs and files are stored permanently.
For example, a solid-state drive or a hard disk drive.
When a program runs,
its files are sent to main memory.
The Memory Management Unit tells main memory the position on disk
of the program's data.
Main memory retrieves the data from the physical addresses,
which is where the data is located on the hard drive,
creating a base address, which is where the data will be located in main
memory. Each byte on the hard drive has its own physical address.
Once in main memory,
data belonging to the same process is stored according to its base register,
which serves as a reference to locate a particular address, and the limit
register, which helps determine the offset within an address.
There are different ways to allocate process space in main
memory. The main ones are static partitions.
Memory is divided so that each partition holds one process.
Partitions can each be a different size.
The operating system creates a table of partitions and processes, indicating whether
the partition is occupied or free.
And which process occupies the partition?
Dynamic partitions.
The operating system places processes consecutively in memory,
making more efficient use of memory.
The operating system creates a process table with the identifier,
the base address, the size,
the process state, the control block address;
likewise, it creates a table of the free memory fragments, indicating
their base address and size.
When data is added or grows,
the tables are updated.
Memory management by segmentation
In this approach, memory is divided according to the existing segments.
Processes are divided into different segments.
There are code segments, stack segments, and data segments.
Each segment is smaller than a partition,
because if a partition held a process,
that partition could be divided into different,
smaller segments, which can be freed without affecting the whole process.
This makes freeing memory easier,
because when a process isn't using a segment,
it can be removed from memory
to make room for another waiting segment."""

PT = """Gerenciamento de memória pelo sistema operacional.
O objetivo deste vídeo é entender como um sistema operacional libera e aloca
espaços na memória para os diferentes programas.
Para isso, precisamos entender que existem dois tipos de memória:
a memória principal e a memória secundária.
A memória principal é formada pela memória RAM e pela memória ROM.
A memória RAM armazena as informações de que um programa precisa
enquanto é executado.
Ela acessa os dados sem importar a ordem em que estão.
Essa memória perde os dados quando deixa de receber energia.
A memória ROM é somente leitura;
é onde fica o software essencial para que o computador
inicie. Ela verifica se os componentes estão funcionando corretamente,
e mantém as informações independentemente de receber energia
ou não. Por outro lado, a memória secundária é onde são armazenados
os programas e arquivos de forma permanente.
Por exemplo, um SSD ou um disco rígido.
Quando um programa é executado,
os arquivos são enviados para a memória principal.
A Memory Management Unit informa à memória principal a posição no disco
dos dados do programa.
A memória principal obtém os dados dos endereços físicos,
que é onde os dados estão no disco rígido,
criando um endereço base, que é onde os dados ficarão na memória
principal. Cada byte no disco rígido tem seu próprio endereço físico.
Uma vez na memória principal,
os dados do mesmo processo são armazenados de acordo com seu registrador base,
que serve como referência para localizar um endereço específico, e o registrador
limite, que ajuda a determinar o deslocamento em um endereço.
Existem diferentes formas de alocar o espaço dos processos na memória
principal. As principais são as partições estáticas.
A memória é dividida para conter um processo em cada partição.
As partições podem ter tamanhos diferentes.
O sistema operacional cria uma tabela com as partições e processos, indicando se
a partição está ocupada ou livre.
E qual processo ocupa a partição?
Partições dinâmicas.
O sistema operacional coloca os processos de forma consecutiva na memória,
organizando de forma mais eficiente o uso da memória.
O sistema operacional cria uma tabela de processos com o identificador,
o endereço base, a capacidade,
o estado do processo, o endereço do bloco de controle;
da mesma forma, cria uma tabela com os fragmentos livres da memória, indicando
o endereço base e a capacidade.
Quando dados são incluídos ou aumentam,
as tabelas são atualizadas.
Gerenciamento de memória por segmentação
Nessa forma, a memória é dividida de acordo com os segmentos existentes.
Os processos são divididos em diferentes segmentos.
Existem segmentos de código, de pilha e de dados.
Cada segmento é menor que as partições,
pois, se houvesse uma partição com um processo,
essa partição poderia ser dividida em diferentes segmentos,
menores, que podem ser liberados sem afetar todo o processo.
Isso facilita a liberação da memória,
pois quando um processo não usa um segmento,
ele pode ser retirado da memória
para dar lugar a outro segmento em espera."""

FR = """Gestion de la mémoire par le système d'exploitation.
Le but de cette vidéo est de comprendre comment un système d'exploitation libère et alloue
l'espace mémoire aux différents programmes.
Pour cela, il faut comprendre qu'il existe deux types de mémoire :
la mémoire principale et la mémoire secondaire.
La mémoire principale est composée de la RAM et de la ROM.
La RAM stocke les informations dont un programme a besoin
pendant son exécution.
Elle accède aux données quel que soit leur ordre.
Cette mémoire perd ses données lorsqu'elle n'est plus alimentée.
La ROM est en lecture seule ;
elle contient le logiciel essentiel pour que l'ordinateur
démarre. Elle vérifie que les composants fonctionnent correctement,
et conserve les informations, qu'elle soit alimentée
ou non. La mémoire secondaire, elle, est l'endroit où sont stockés
les programmes et les fichiers de façon permanente.
Par exemple, un SSD ou un disque dur.
Lorsqu'un programme s'exécute,
ses fichiers sont envoyés vers la mémoire principale.
La Memory Management Unit indique à la mémoire principale la position sur le disque
des données du programme.
La mémoire principale récupère les données aux adresses physiques,
c'est-à-dire là où se trouvent les données sur le disque dur,
en créant une adresse de base, là où les données seront placées en mémoire
principale. Chaque octet du disque dur possède sa propre adresse physique.
Une fois en mémoire principale,
les données d'un même processus sont stockées selon leur registre de base,
qui sert de référence pour localiser une adresse précise, et le registre
limite, qui aide à déterminer le décalage dans une adresse.
Il existe plusieurs façons d'attribuer l'espace des processus en mémoire
principale. Les principales sont les partitions statiques.
La mémoire est divisée pour contenir un processus par partition.
Les partitions peuvent avoir des tailles différentes.
Le système d'exploitation crée une table des partitions et des processus, indiquant si
la partition est occupée ou libre.
Et quel processus occupe la partition ?
Partitions dynamiques.
Le système d'exploitation place les processus de façon consécutive en mémoire,
ce qui optimise l'utilisation de la mémoire.
Le système d'exploitation crée une table des processus avec l'identifiant,
l'adresse de base, la capacité,
l'état du processus, l'adresse du bloc de contrôle ;
de même, il crée une table des fragments libres de la mémoire, indiquant
l'adresse de base et la capacité.
Lorsque des données sont ajoutées ou augmentent,
les tables sont mises à jour.
Gestion de la mémoire par segmentation
Dans cette approche, la mémoire est divisée selon les segments existants.
Les processus sont divisés en différents segments.
Il existe des segments de code, de pile et de données.
Chaque segment est plus petit qu'une partition,
car si une partition contenait un processus,
cette partition pourrait être divisée en différents segments,
plus petits, qui peuvent être libérés sans affecter tout le processus.
Cela facilite la libération de la mémoire,
car lorsqu'un processus n'utilise pas un segment,
celui-ci peut être retiré de la mémoire
pour laisser la place à un autre segment en attente."""

LANGS = {"en": EN, "pt-BR": PT, "fr": FR}
