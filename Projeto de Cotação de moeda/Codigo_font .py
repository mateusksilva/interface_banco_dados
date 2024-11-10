import tkinter as tK 
from tkinter import ttk
from tkcalendar import DateEntry
import requests
from tkinter import filedialog, messagebox
from tkinter.filedialog import askopenfilename
import pandas as pd
import openpyxl
from datetime import datetime, timedelta
import numpy as np
import logging
import locale

# Tenta configurar o locale para português brasileiro
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

logging.basicConfig(filename='app.log', level=logging.DEBUG)
resquisiçao = requests.get('https://economia.awesomeapi.com.br/json/all')
dicionario = resquisiçao.json()
janela = tK.Tk()
def pegar_cotação():
    data = calendario_moeda.get()
    moeda = combobox_selecionarmoeda.get()
    

    try:
        data_formatada = datetime.strptime(data, '%d/%m/%Y').strftime('%d/%m/%Y')
    except ValueError:
        # Caso ocorra algum erro no formato da datan
        messagebox.showerror('Erro', 'Formato de data iválido.')
        return

    ano = data_formatada[-4:]
    mes = data_formatada[3:5]
    dias = data_formatada[:2]
    link = f'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/?start_date={ano}{mes}{dias}&end_date={ano}{mes}{dias}'

    valor_moeda = requests.get(link)
    cotaçao = valor_moeda.json()
    if cotaçao and isinstance(cotaçao, list) and len(cotaçao) > 0:
        valor_moeda = cotaçao[0]['bid']
        labem_texto['text'] = f'A cotação de {moeda} no dia {data_formatada} foi de R$ {valor_moeda}'
    else:
        labem_texto['text'] = f'Não foi possível obter a cotação para {moeda} no dia {data_formatada}.'

    moeda =combobox_selecionarmoeda.get()
    data = calendario_moeda.get()
    ano = data[-4:]
    mes = data[3:5]
    dias = data[:2]
    link = f'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/?start_date={ano}{dias}{mes}&end_date={ano}{dias}{mes}'
    valor_moeda = requests.get(link)
    cotaçao = valor_moeda.json()
    if cotaçao and isinstance(cotaçao, list) and len(cotaçao) > 0:
        valor_moeda = cotaçao[0]['bid']
        labem_texto  ['text'] =f'A cotação de {moeda} no dia {data} foi de R$ {valor_moeda}'
    else:
        labem_texto ['text'] =  f'Não foi possível obter a cotação para {moeda} no dia {data}.'


def selecionar_arquivo():
    caminho = askopenfilename(title='selecione  o Arquivo Moeda')
    var_caminho_arquivo.set(caminho)
    if caminho:
        labe_arquivo_selecinado['text'] = f'Arquivo selecionado {caminho}'


def atualizar_cotacao():
    try:
        # Ler o DataFrame do arquivo Excel
        df = pd.read_excel(var_caminho_arquivo.get())
        
        # Extrair moedas e datas
        moedas = df.iloc[:, 0].unique()  # Extrair moedas únicas para evitar duplicações
        data_inicial_var = data_inicial.get()

        
        # Extrair ano, mês e dia da data inicial
        ano_inicial = data_inicial_var[-4:]
        mes_inicial = data_inicial_var[3:5]
        dia_inicial = data_inicial_var[:2]
        for moeda in moedas:
            try:
                # Montar a URL com as datas no formato necessário
                link = f'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/?start_date={ano_inicial}{mes_inicial}{dia_inicial}&end_date={ano_inicial}{mes_inicial}{dia_inicial}'
                resposta = requests.get(link)
                
                # Verificar se a resposta foi bem-sucedida
                if resposta.status_code == 200:
                    cotações = resposta.json()
                    
                    # Verificar se há cotações na resposta
                    if cotações:
                        for cotacao in cotações:
                            # Converter timestamp para datetime
                            timestamp = cotacao.get('timestamp')
                            bid = float(cotacao['bid'])
                            
                            # Converter o timestamp (segundos) para uma data legível
                            data = datetime.fromtimestamp(int(timestamp)).strftime('%d/%m/%Y')
                            
                            # Adicionar a coluna da data, se não existir
                            if data not in df.columns:
                                df[data] = np.nan
                            
                            # Atualizar o valor da moeda na data correspondente
                            df.loc[df.iloc[:, 0] == moeda, data] = bid
                    else:
                        messagebox.showinfo(f"Não há cotações para {moeda} nas datas selecionadas.")
                else:
                    messagebox.showerror( f"Erro ao obter dados para {moeda}. Código de status: {resposta.status_code}")
            except Exception as e:
                messagebox.showinfo('Ocorreu um erro:')
        
        # Salvar o DataFrame atualizado para verificar
        df.to_excel("cotações_atualizadas.xlsx", index=False)
        
    except ValueError:
        messagebox.showinfo("Selecione um arquivo no formato correto!")
    except Exception as e:
        messagebox.showinfo('"Selecione um arquivo no formato correto!"')
lista_moeda=list(dicionario.keys())
janela.title('Janela de Cotação De Moeda ')

laber_cotaçao  = tK.Label(text='Cotação de 1 moeda especifica ',borderwidth=2,relief='solid')
laber_moedas  = tK.Label(text='Cotação de varias  moeda especifica ',borderwidth=2,relief='solid')
labe_selecionar = tK.Label(text='Selecionar Moeda:',anchor='e')
labe_selecionar_arquivo =tK.Label(text='Selecionar Um arquivo em excel Com Moeda Na Coluna A:')
combobox_selecionarmoeda = ttk.Combobox(values=lista_moeda)


var_caminho_arquivo = tK.StringVar()
butao =tK.Button(text='click para selecionar',command=selecionar_arquivo)
botao_pegarcotaçao=tK.Button(text='Pegar cotação',command=pegar_cotação)
labe_arquivo_selecinado= tK.Label(text='Nehum Arquivo Selecionador',anchor='e')
laber_dia = tK.Label(text='Selecionar Dia Que Deija Pegar a Cotação:',anchor='e')
labe_data_inicial = tK.Label(text='Data :',anchor='e')
labem_texto=tK.Label(text='')

butao_atuliazar_cotaçao = tK.Button(text='Atualizar Cotação:',command=atualizar_cotacao)
laber_atuliazar_cotaçao = tK.Label(text='')
butao_fechar = tK.Button(text='Fechar',command=janela.quit)
# cotaçao de varias moedas 
calendario_moeda = DateEntry(year=2024, locale='pt_BR', date_pattern='dd/mm/yyyy')
data_inicial  = DateEntry(year=2024,locale='pt_br')
# adicionando width
labe_selecionar.grid(row=1,column=0,padx=10,pady=10,sticky='NESW',columnspan=2)
laber_moedas.grid(row=4,column=0,padx=10,pady=10,sticky='NESW', columnspan=6)
laber_cotaçao.grid(row=0,column=0,padx=10,pady=10,sticky='NESW', columnspan=6)
combobox_selecionarmoeda.grid(row=1,column=2,padx=10,pady=10,sticky='NESW',columnspan=3)
laber_dia.grid(row=2,column=0,sticky='e',padx=10,pady=10,columnspan=2)
calendario_moeda.grid(row=2,column=2,padx=10,pady=10,sticky='NEWS',columnspan=3)
botao_pegarcotaçao.grid(row=3,column=2,sticky='NEWS',padx=10,pady=10,columnspan=3)
labe_selecionar_arquivo.grid(row=5,column=0,sticky='NEWS',columnspan=2,padx=10,pady=10)
butao.grid(row=5,column=3,sticky='nsew',padx=10,pady=10,columnspan=6)
labe_arquivo_selecinado.grid(row=6,column=0,columnspan=6,padx=10,pady=10,sticky='e')
data_inicial.grid(row=7,column=1,padx=10,pady=10,sticky='ensw')
labe_data_inicial.grid(row=7,column=0,padx=10,pady=10,sticky='ensw')
butao_atuliazar_cotaçao.grid(row=9,column=0,padx=10,pady=10,sticky='enws')
laber_atuliazar_cotaçao.grid(row=9,column=2,columnspan=5,padx=10,pady=10,sticky='nsew')
butao_fechar.grid(row=10,column=3,columnspan=5,padx=10,pady=10,sticky='nsew')
labem_texto.grid(row=3,column=1,padx=10,pady=10,sticky='NEWS')
janela.mainloop()