from Prediction.data_analyzes import DataAnalyzes
from Prediction.sender import Sender
from .terra_brasilis import TerraBrasilis

#    [
#        "2018-12-21T16:06:00.000Z",    weather e Hora
#       "NPP-375",                      Satelite
#       "Brasil",                       Pais
#       "CEARÁ",                        Estado do pais
#       "ARARIPE",                      Municipio
#       "Caatinga",                     Bioma
#       2,                              Dias sem chuva
#       1.7,                            Precipitação
#       0.2,                            Risco de Fogo
#       -7.18889,                       Latitude
#       -39.94255,                      Longitude
#       null,                           Area Industrial
#       2.8                             FRP
#   ]

def main():

    tbApi = TerraBrasilis()
    tbApi.initialize()              # Baixa o token e cookie do BD Queimadas para uso posterior nos downloads dos datasets
    #cookie = tbApi.getCookie()
    #print(f'cookie = {cookie}')
    #csrfCookie = tbApi.getCsrf()
    #print(f'csrf = {csrfCookie}')

    tbApi.retrieveCities()          # Baixa e analiza os Datasets de 2014 ate o ano anterior ao atual (LEVA DEZENAS DE MINUTOS)
    tbApi.updateCurrentData()       # Baixa e analiza os Datasets do ano atual (PODE LEVAR UNS 10 MINUTOS)
    tbApi.removeDuplicities()       # Remove duplicidades dos Datasets (Mesmo foco de queimada resgistrado por satelites diferentes)
    #tbApi.generateCustomData()     # Gerar um JSON costumizado para teste

    dataAnalyzes = DataAnalyzes()   # Cria as variaveis onde serao armazenados os dados referentes aos focos e ao envio ao back-end
    dataAnalyzes.analyze()          # Analiza os datasets e preenche as variaveis com os dados
    #dataAnalyzes.cityModels...
    #dataAnalyzes.totalCurrentYear...

    sender = Sender(dataAnalyzes.dataChapadaAraripe, dataAnalyzes.dataCities)
    sender.sendData()               # Envio dos dados referentes aos focos previstos e ocorridos por cidade e totais (Chapada inteira)

if __name__ == '__main__':
    print("start")
    main()
    print("finish")
