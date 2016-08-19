import json
import tkinter
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename, asksaveasfilename
import requests as r
from bs4 import BeautifulSoup


class Rest(ttk.Frame):

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

    def __init__(self, root, *args, **kwargs):
        super(Rest, self).__init__(*args, **kwargs)
        self.pack()

        menubar = tkinter.Menu(root)
        menu_arquivo = tkinter.Menu(menubar, tearoff=0)
        
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Novo", command=self.novo_arquivo)
        menu_arquivo.add_command(label="Abrir", command=self.abrir_arquivo)
        menu_arquivo.add_command(label="Salvar", command=self.salvar_arquivo)
        menu_arquivo.add_command(label="Sair",command=root.quit)

        root.config(menu=menubar)

        self.url = tkinter.StringVar()

        self.frame_url = ttk.Frame(self)
        self.frame_url.pack()
        self.lbl_url_entry = tkinter.Label(self.frame_url,text='URL')
        self.lbl_url_entry.pack(side=tkinter.LEFT)
        self.url_entry = tkinter.Entry(self.frame_url,textvariable=self.url, width=80)
        self.url_entry.pack(side=tkinter.LEFT)
        
        
        self.metodo = tkinter.StringVar()
        self.metodos_combo = ttk.Combobox(self.frame_url, textvariable=self.metodo, width=8)
        self.metodos_combo.bind("<<ComboboxSelected>>", self.metodo_select)
        self.metodos_combo['values'] = (Rest.GET, Rest.POST,Rest.PUT, Rest.DELETE)
        self.metodos_combo.pack(side=tkinter.LEFT)
        self.metodos_combo.state(['readonly'])
        self.metodo.set( self.metodos_combo['values'][0] )
        

        self.botao_ir = ttk.Button( self.frame_url, text='IR', command=self.request)
        self.botao_ir.pack(side=tkinter.LEFT)

        self.frame_header = ttk.Frame(self)
        self.frame_header.pack(fill=tkinter.X, padx=5, pady=2)
        self.lbl_headers = tkinter.Label(self.frame_header,text='Headers')
        self.lbl_headers.pack(side=tkinter.LEFT)
        self.botao_addheader = ttk.Button( self.frame_header, text='+', command=self.add_header)
        self.botao_addheader.pack(side=tkinter.RIGHT)

        self.headers_canvas = tkinter.Canvas(self, borderwidth=0, height=100)

        self.frame_headers = ttk.Frame(self.headers_canvas)
        self.frame_headers.pack()

        #Scrollbar
        self.scroll_bar_y = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.headers_canvas.yview)
        self.headers_canvas.configure(yscrollcommand=self.scroll_bar_y.set)
        self.scroll_bar_y.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        self.scroll_bar_x = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL, command=self.headers_canvas.xview)
        self.headers_canvas.configure(xscrollcommand=self.scroll_bar_x.set)
        self.scroll_bar_x.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        self.headers_canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.headers_canvas.create_window((1,1), window=self.frame_headers, anchor="nw", tags="self.frame_headers")
        self.frame_headers.bind("<Configure>", self.on_frame_configure)

        self.lista_headers = []

        frame_keyvalue = tkinter.Frame(self.frame_headers)
        frame_keyvalue.pack()
        header1 = tkinter.Label(frame_keyvalue, text='Header')
        header1.pack(side=tkinter.LEFT)
        value_header1 = tkinter.Label(frame_keyvalue, text='Valor')
        value_header1.pack(side=tkinter.LEFT)


        lbl_body = tkinter.Label(root, text='Body')
        lbl_body.pack()

        self.body = ScrolledText(root, height=10, width=100)
        self.body.pack()

        lbl_retorno = tkinter.Label(root, text='Retorno')
        lbl_retorno.pack()

        self.retorno = ScrolledText(root, height=18, width=100)
        self.retorno.pack()

        self.metodo_select()#Bloqueando o Body para edição

        self.lbl_request = tkinter.Label(root,text='')
        self.lbl_request.pack()

    def metodo_select(self, value=None):
        metodo = self.metodo.get()
        if metodo == Rest.POST or metodo == Rest.PUT:
            self.body.config(state=tkinter.NORMAL)
        elif metodo == Rest.GET or metodo == Rest.DELETE:
            self.body.config(state=tkinter.DISABLED)

    def remove_header(self, chave, frame):
        for item in self.lista_headers:
            if item[0] == chave:
                self.lista_headers.remove(item)
                frame.destroy()

    def add_header(self, key='', value=''):
        chave = tkinter.StringVar()
        chave.set(key)
        valor = tkinter.StringVar()
        valor.set(value)
        frame_keyvalue = tkinter.Frame(self.frame_headers)
        frame_keyvalue.pack()
        header1 = tkinter.Entry(frame_keyvalue,textvariable=chave)
        header1.pack(side=tkinter.LEFT)
        value_header1 = tkinter.Entry(frame_keyvalue,textvariable=valor)
        value_header1.pack(side=tkinter.LEFT)
        botao_remover = tkinter.Button(frame_keyvalue, text='-',command=lambda: self.remove_header(chave, frame_keyvalue))
        botao_remover.pack(side=tkinter.LEFT)

        self.lista_headers.append( (chave, valor, frame_keyvalue) )

    def on_frame_configure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.headers_canvas.configure(scrollregion=self.headers_canvas.bbox("all"))

    def get_headers(self):
        headers = {}
        for keyValue in self.lista_headers:
            headers[ keyValue[0].get() ] = keyValue[1].get()
        return headers

    def get_data(self):
        return self.body.get(0.0,tkinter.END)

    def request(self):
        resposta = ''
        try:
            metodo = self.metodo.get()
            headers = self.get_headers()
            if metodo == Rest.POST:
                data = self.get_data()
                resposta = r.post(self.url.get(), headers=headers, data=data)
            elif metodo == Rest.GET:
                resposta = r.get(self.url.get(), headers=headers)
            elif metodo == Rest.PUT:
                data = self.get_data()
                resposta = r.put(self.url.get(), headers=headers, data=data)
            elif metodo == Rest.DELETE:
                resposta = r.delete(self.url.get(), headers=headers)
        except Exception as ex:
            print(ex)
            resposta = ex.message
        self.tratar_resposta(resposta)

        self.retorno.delete(0.0,tkinter.END)
        try:
            load = json.loads(resposta.text)
            self.retorno.insert(tkinter.END, json.dumps(load, indent=4, sort_keys=True) )
        except:
            soup = BeautifulSoup(resposta.text)
            self.retorno.insert(tkinter.END, soup.prettify() )

    def tratar_resposta(self, resposta):
        try:
            texto = 'Status: {0}\n'.format(resposta.status_code)
            texto += 'Headers:\n'
            for key in resposta.headers.keys():
                texto += '\t {0}:{1}\n'.format(key, resposta.headers[key])
            texto += 'Encoding:{0}\n'.format(resposta.encoding)
            self.lbl_request['text'] = texto
        except Exception as ex:
            print(ex)
            self.lbl_request['text'] = 'Erro'

    def abrir_arquivo(self):
        arquivo = askopenfilename(title='Escolher arquivo',filetypes=( ("JSON File", "*.json"), )  )
        if arquivo:
            self.novo_arquivo() # Limpa os campos
            arquivo_json = None
            with open(arquivo, 'r') as configuracao:
                arquivo_json = configuracao.read()
            arquivo_json = json.loads(arquivo_json)
            self.url.set( arquivo_json['url'] )
            if arquivo_json['method']:
                if arquivo_json['method'] == Rest.GET:
                    self.metodo.set( Rest.GET )
                elif arquivo_json['method'] == Rest.POST:
                    self.metodo.set( Rest.POST )
                elif arquivo_json['method'] == Rest.PUT:
                    self.metodo.set( Rest.PUT )
                elif arquivo_json['method'] == Rest.DELETE:
                    self.metodo.set( Rest.DELETE )
            self.metodo_select()
            if arquivo_json['data']:
                self.body.delete(0.0,tkinter.END)
                self.body.insert(tkinter.END, arquivo_json['data'])
            if 'headers' in arquivo_json:
                for key in arquivo_json['headers'].keys():
                    self.add_header(key=key, value=arquivo_json['headers'][key])

    def novo_arquivo(self):
        self.url.set('')
        self.body.delete(0.0,tkinter.END)
        self.retorno.delete(0.0,tkinter.END)
        self.lbl_request['text'] = ''
        self.metodo.set( Rest.GET )
        while True:
            if self.lista_headers:
                item = self.lista_headers[0]
                key = item[0]
                frame = item[2]
                self.remove_header( key, frame )
            else:
                break

    def salvar_arquivo(self):
        arquivo_destino = asksaveasfilename(title='Salvar JSON do Request', filetypes=[('JSON File','*.json')])
        if arquivo_destino:
            dicionario = {}
            dicionario['headers'] = self.get_headers()
            dicionario['data'] = self.get_data()
            dicionario['method'] = self.metodo.get()
            dicionario['url'] = self.url.get()
            with open(arquivo_destino, 'w') as destino:
                destino.write( json.dumps(dicionario) )
                messagebox.showinfo('Rest', 'Arquivos salvo com sucesso')

root = tkinter.Tk()
root.title( 'Rest' )
root.geometry('800x640')
aplicacao = Rest(root)
tkinter.mainloop()