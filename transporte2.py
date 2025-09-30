class Transporte:
    def __init__(self, capacidade, velocidade_maxima):
        self.__capacidade = capacidade      # Atributo privado
        self.__velocidade_maxima = velocidade_maxima  # Atributo privado
        

    # Getters

    def getCapacidade(self):
        return self.__capacidade

    def get_velocidade_maxima(self):
        return self.__velocidade_maxima
    

    # Setters

    def set_capacidade(self, capacidade):
        if capacidade > 0 and capacidade < 50:
            self.__capacidade = capacidade

    def set_velocidade_maxima(self, velocidade):
        if velocidade > 0:
            self.__velocidade_maxima = velocidade

    # Método para exibir informações
    def descricao(self):
        print(f"Capacidade: {self.__getCapacidade()}")

    def mover(self):
        print('O transporte esta em movimento')    
        

class Onibus(Transporte):
    def __init__(self,capacidade, velocidade_maxima ):
        super().__init__(capacidade, velocidade_maxima) 

class Bicicleta(Transporte):
    def __init__(self,capacidade, velocidade_maxima ):
        super().__init__(capacidade, velocidade_maxima)

onibus1 = Onibus(30, '80 km/h')
bike1 = Bicicleta(1, '40 km/h')       

onibus1.descricao()
onibus1.mover()

bike1.descricao()
bike1.mover()
             

    
 
carro.descricao()        