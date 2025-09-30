class Conta:
    # Primeiro metodo sempre é : contrutor
    # primeiro "atributo" deve ser: self
    
    def __init__(self, numConta, titular, saldo = 0):
        self.numConta = numConta
        self.titular = titular
        self.saldo = saldo
        inicio = '\nExtrato do(a)' + self.titular + '\
            ' com saldo inicial de: R$ ' + str(self.saldo)
        self.extrato = [inicio]
    
    def realizarDeposito(self,valor):
        if valor > 0:
            self.saldo = self.saldo + valor
            saida = 'Deposito realizado com'+ \
                  'sucesso no valor de :R$ ' + str(valor)+ \
                  '\nSaldo Atual:' + str(saldo)
            self.extrato.append(saida)
        else:
            print('Digite um vaor válido')    
            #igual a isso saldo += valor
    def realizarSaque(self, valor):
            if self.saldo >= valor and valor > 0:
                # tudo certo, pode sacar
                self.saldo = self.saldo - valor
                saida = 'Saque realizado com sucesso'+ \
                    'no valor de:' + str(valor)+\
                    '\nSaldo Atual:'+ str(self.saldo)
            elif valor <= 0: # else if -> elif
                 print('Digite um valor válido')
            else:
                 print('Não há saldo suficiente')

    def realizarTransferencia(self, destinatario, valor):
        saida = 'Transferria para a conta '+|
        self.realizarSaque(valor)
        destinatario.realizarDeposito(valor) 

    def retirarExtrato(self):
                                


conta1 = Conta('00001', 'Renan')
conta1.realizarDeposito(100)
conta1.realizarSaque(50)
print("saldo:", conta1.saldo)
conta2 = Conta('00002', 'Raphael', 2)

conta2.realizarTransferencia(conta1, 1.99)
print(f'R$ {conta2.saldo:.2f}')