class Veiculo:
    # primeira coisa -> metodo construtor
    def __init__(self, marca, modelo, cor, ano):
        self.__marca = marca
        self.__modelo = modelo
        self.__cor = cor
        self.__ano = ano
        self.__cores = ['Branco','Preto', 'Cinza', 'Vermelho']
    
    def getMarca(self):
        return self.__marca
    def getModelo(self):
        return self.__modelo
    def getAno(sef):
        return sef.__ano
    def getCor(self):
        return self.__cor
    def setCor(self, novaCor):
        controle  = 0
        for cor in self.__cores:
            if cor == novaCor:
                controle = 1
                self.__cor = novaCor
                break
            if controle == 1:
                self.__cor = novaCor
            else:
                print('Cor não alterada')    
    
    
    def detalhes(self):
        print(f' Esse carro é da marca {self.__marca}, do modelo: {self.__modelo}, da cor {self.__cor} e de {self.__ano}')
    def acelerar(self):
        print('Acelerando um veiculo aleatório')     
#v1 = Veiculo ('A', 'B', 'C', '11111', 'vermelho', 2010)

#v1.detalhe()
# herança em python
class Carro(Veiculo):
    def __init__(self, marca, modelo, cor, ano, portas):
        super().__init__(marca, modelo, cor, ano)
        self.__portas = portas
    def getPortas(self):
        return self.__portas
    
    
    def acelerar(self):
        print(f'Andando de {self.getModelo()} por aí') 

carro1 = Carro('BYD', 'Dolphin Mini', 'Cinza', 2025, 4)
carro2 = Carro('VW', 'Gol G3', 'Cinza', 1998, 2)  

carro2.detalhes()
carro2.acelerar()