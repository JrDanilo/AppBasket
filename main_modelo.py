from kivy.app import App #importa a biblioteca kivy
from kivy.uix.boxlayout import BoxLayout #importa a função BoxLayout do kivy
from kivy.uix.widget import Widget  #importa a função Widget do kivy
from kivy.uix.image import Image  #importa a função Image do kivy
from kivy.clock import Clock  #importa a função Clock do kivy
from kivy.core.window import Window  #importa a função Window do kivy
from kivy.vector import Vector as Vec  #importa a função Vector do kivy
from kivy.core.audio import SoundLoader  #importa a função SoundLoader do kivy
from kivy.properties import StringProperty  #importa a função StringProperty do kivy
from math import * #importa a biblioteca math
import random #importa a biblioteca random


#Classe da bola
class Bola(Widget):

    estado = StringProperty("pronta") #atribui o estado da bola como "pronto"
    
    #construtor
    def __init__(self, **kwargs):
        super(Bola, self).__init__(**kwargs) #'super' possibilita a herança
        self.som_quica = SoundLoader.load('./som_quica.wav') #som de lançamento da bola

    #define o estado inicial da bola
    def setEstadoInicial(self, x0, y0, cesta):
        self._x = x0
        self.x0 = x0
        self._y = y0
        self.y0 = y0
        self.v0 = 0
        self.pos = x0,y0
        self.theta = 0
        self.estado = "pronta" #estado inicial (vide diagrama de estado da bola)
        self.cesta = cesta
        self.raio = self.width / 2

    #avisa o root que a bola mudou de estado
    def on_estado(self, instancia, valor):
        App.get_running_app().root.ObservaBola(valor)
        
    #move a bola
    def mover(self, velocidade, theta):
        #define a velocidade inicial e o angulo inicial da bola
        self.v0 = velocidade
        self.theta = theta

        #incremento de tempo (em segundos)
        self.dt = 5/60
        
        #tempo inicial
        self.t = 0

        #Toca o som (quica a bola)
        self.som_quica.play()
        
        #altera o estado da bola para o movimento
        self.estado = "em movimento"
        
        #para a animação, preciso usar o clock
        Clock.schedule_interval(self.moverIncremental, self.dt)          

    #Funcao callback do Clock para atualizar a posicao da bola
    def moverIncremental(self, dt):
        
        #verifica, com a cesta, se devo parar o movimento
        if (self.cesta.verificaBola(self) == False):
            return False
        
        #calcula nova posical de x e y
        self._x = self.x0 + self.v0*cos(self.theta)*self.t
        self._y = self.y0 + self.v0*sin(self.theta)* self.t - 9.81*self.t*self.t/2

        #atribui a nova posição para a bola
        self.pos = Vec(self._x, self._y)
        
        #incrementa o tempo
        self.t = self.t + dt
    
        
#Classe da cesta
class Cesta(Widget):
    
    tolerancia = 20
    offsetX = 50
    offsetY = 100
    hrandom = 0 #a variavel hrandom esta relacionada ao sorteio/manter posicionamento da cesta
    
    def posicao(self, x, y):
        self.pos = x, y
        self.alvo = self.pos[0] + self.offsetX, self.pos[1] + self.offsetY
    
    def verificaBola(self, bola):
        #condições para mudança de estado da bola
        #1. Quando a bola estiver abaixo da posição inicial (_y < y0)
        if bola._y < bola.y0:
            bola.estado = "repouso no chao"
            self.hrandom = 0 #atribuimos '0' a variavel self.hrandom quando a bola esta em "repouso no chao"
            print(bola.estado)
            return False      
        
        #2. Quando a bola estiver sobre a cesta
        if (self.alvo[0] - self.tolerancia < bola._x + bola.raio < self.alvo[0] + self.tolerancia) and (self.alvo[1] - self.tolerancia < bola._y + bola.raio < self.alvo[1] + self.tolerancia):
            bola.estado = "repouso na cesta"
            self.hrandom = 1 #atribuimos '1' a variavel self.hrandom quando a bola esta em "repouso na cesta"
            print(bola.estado)
            return False
        
        
        print("Centro Bola = (", bola._x+bola.raio, ",", bola._y + bola.raio, "), Alvo = ", self.alvo)
        return True
    

#Classe do jogador
class Jogador():
    def lancarBola(self, bola, velocidade, theta):
        #jogador lanca a bola 
        bola.mover(velocidade, theta)
        

#nova classe, declarada no arquivo Lancador.kv
class Cenario(BoxLayout):
    #Construtor
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #Tamanho da janela
        Window.size = (400, 600)

        #Configura os sons
        self.som_erro = SoundLoader.load('./som_erro.wav')
        self.som_aplauso = SoundLoader.load('./som_aplauso.wav')

        self.cesta.posicao(300, 300 + random.randint(-50,100)) #sorteia a altura da cesta quando o app é executado
        
        
        #verifica se está tudo certo com os sons
        if self.som_erro and self.som_aplauso:
            print("Tamanho: som_erro %.3f segundos" % self.som_erro.length)
            print("Tamanho: som_aplauso %.3f segundos" % self.som_aplauso.length)
        
        #cria um jogador
        self.jogador = Jogador()
        
        #inicializa o jogo
        self.inicializar()
      

    #Funcao para reiniciar o processo
    def inicializar(self):

        #posicao inicial da bola
        self.bola.setEstadoInicial(1, 200, self.cesta)

        
        
        #posicao inicial da cesta
        if self.cesta.hrandom == 1: #caso a variável hrandom da classe cesta é 1 (repouso na cesta):
            self.cesta.posicao(300, 300 + random.randint(-50,100))  #é sorteado uma altura nova para a cesta
        else:
            return False #caso não, nada acontece e a cesta é mantida na mesma altura
    
        self.cesta.hrandom = 0 
        #limpa a mensagem de erro       
        self.ids.mensagem.text = ''
        
    #o cenário fica em suspense, aguardando que o estado final da bola
    def ObservaBola(self, estadoBola):
        if estadoBola == "repouso na cesta":
            self.ids.mensagem.text = '[color=#0000FF]ACERTOU![/color]'
            self.IncrementaAcertos()
            #Toca o som (aplauso)
            self.som_aplauso.play()
            return False
        if estadoBola == "repouso no chao":
            self.ids.mensagem.text = '[color=#FF0000]ERROU[/color]'
            self.IncrementaErros()
            #Toca o som (erro)
            self.som_erro.play()
            return False

    #método audio
    def audio(self):
        if self.ids.audio.active == True: #caso o checkbox do audio esteja marcado:
            self.som_aplauso.volume = 1 #todos os sons são reproduzidos com volume máximo (1)
            self.som_aplauso.volume = 1
            self.bola.som_quica.volume = 1
        
        else: #caso o checkbox do audio não esteja marcado:
            self.som_aplauso.volume = 0 #todos os sons são reproduzidos com volume mínimo/mudo (0)
            self.som_erro.volume = 0
            self.bola.som_quica.volume = 0

            
        
    #método disparado pelo on_release do botao
    def LancarClick(self):
        
       #velocidade e angulo inicial
        if float(self.ids.txVel.text) > 0 and float(self.ids.txAng.text) > 0 \
        and float(self.ids.txAng.text) < 90:
        
            v0 = float(self.ids.txVel.text)
            theta = float(self.ids.txAng.text) * pi/180        
        
            #jogador lanca a bola
            self.jogador.lancarBola(self.bola, v0, theta)
        
    #Funcao para sair do aplicativo
    def Sair(self):
        App.get_running_app().stop()

    #Funcao que incrementa o placar de acertos
    def IncrementaAcertos(self):
        self.ids.txAcertos.text = str(int(self.ids.txAcertos.text) + 1)
    #Funcao que incrementa o placar de erros
    def IncrementaErros(self):
        self.ids.txErros.text = str(int(self.ids.txErros.text) + 1)


        
#Classe da aplicacao
class LancadorApp(App):
    # o método build, herdado da classe App, define quais componentes estarão no quadro
    def build(self):
        self.title = 'Lancador de Bolas de Basquete'
        return Cenario()   

#cria uma instancia da aplicação
meuApp = LancadorApp()

#Abre o quadro da aplicacao
meuApp.run()
