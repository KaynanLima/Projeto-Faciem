import sys
import cv2
import numpy as np
import os
import shutil
import time
import threading
from PySide6.QtGui import QFont, QAction, QDesktopServices
from PySide6.QtCore import Qt, QThread, Slot, Signal, QObject, QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QWidgetAction, QListWidget, QListWidgetItem
from qdarktheme import load_stylesheet
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing import image_dataset_from_directory, image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tkinter import filedialog
from tkinter import Tk
from PIL import Image
from functools import partial

#Define uma váriavel global para garantir funcionamento da função em segundo plano
marca = 0

#Executando a classe de execução em segundo plano
class Worker(QObject):
    finished = Signal(str)
    #Função de execuções em segundo plano do Reconhecimento Facial
    def executar_reconhecimento_facial(self):
        #Garantia da segurança da função
        self._mutex = threading.Lock()
        with self._mutex:
            #Puxa váriaveis globais
            global marca
            global cancelado
            cancelado = False
            while not cancelado:
                print('teste')
                try:
                    model = tf.keras.models.load_model('Faciem 1-2.h5')

                    #Solicitação do caminho da imagem
                    image_path = filedialog.askopenfilename()

                    #Processamento da imagem no sistema
                    img = image.load_img(image_path, target_size=(250, 250))

                    #Converção da imagem em array
                    img_array = image.img_to_array(img)
                    img_array = tf.expand_dims(img_array, 0)

                    #Definição do diretório no banco de dados
                    data_dir = 'lfw2'

                    #Criação de "Dicionário" para conter os nomes de cada pessoa
                    class_index_to_name = {}

                    #Definição dos nomes de cada pessoa no dicionário, na ordem da pasta
                    for class_index, class_name in enumerate(sorted(os.listdir(data_dir))):
                        if os.path.isdir(os.path.join(data_dir, class_name)):
                            class_index_to_name[class_index] = class_name

                    #Predição feita pela IA
                    predictions = model.predict(img_array)

                    #Verificação da pessoa com maior probabilidade
                    predicted_class = np.argmax(predictions[0])
                    max_probability = np.max(predictions[0])

                    # Definição um limite de confiança no reconhecimento
                    confidence_threshold = 15

                    #Definição da previsão e nome
                    try:
                        #Verificação do limite de confiança
                        if max_probability > confidence_threshold:
                            # Dar nome para a classe
                            class_name = class_index_to_name.get(predicted_class, 'Classe Desconhecida')
                        else:
                            class_name = 'Rosto_não_reconhecido'

                        #Finalização, devolução do nome
                        self.finished.emit(f"Nome: {class_name}")

                    #Definição de erro de processamento na imagem
                    except Exception as e:
                        self.finished.emit(f"Erro ao processar a imagem: {str(e)}")
                        cancelado = True
                        return

                    #Garante que o sistema vá esperar o botão ser apertado para se executar novamente
                    marca = marca - 1
                    while marca == 0:
                        time.sleep(1)

                #Definição de erro de execução no reconhecimento em si
                except Exception as e:
                    self.finished.emit(f"Erro ao executar o reconhecimento facial: {str(e)}")
                    cancelado = True
                    return



#Classe de interface
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        global marca
        global worker_thread
        worker_thread = QThread()

        # Definação do título da janela
        self.setWindowTitle("Projeto Faciem")

        # Definação de um tamanho fixo para a janela
        self.setFixedSize(800, 600)

        # Criação de um widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Criação de  um layout vertical para o widget central
        layout = QVBoxLayout(central_widget)
        central_widget.setLayout(layout)

        #Definição de detalhes da fonte
        font = QFont()
        font.setPixelSize(18)

        #Definição de Fonte de Título
        titulo = QFont()
        titulo.setPixelSize(36)
        titulo.setFamily('Verdana')
        titulo.setBold(True)  # Deixa o texto em negrito
        titulo.setUnderline(True)  # Sublinha o texto

        #Definição da Label de Titulo
        titulo_label = QLabel("Projeto Faciem")
        titulo_label.setAlignment(Qt.AlignCenter)
        titulo_label.setFont(titulo)
        titulo_label.setFixedHeight(50)

        #Definição da label para texto padrão
        mensagem_label = QLabel("Para iniciar o sistema, clique no botão abaixo")
        mensagem_label.setAlignment(Qt.AlignCenter)
        mensagem_label.setFont(font)
        mensagem_label.setFixedHeight(20)

        #Criação de botão
        self.button = QPushButton("Executar Reconhecimento Facial")
        self.button.setFont(font)  # Defina a fonte para o botão

        # Criação de um rótulo para exibir o nome da pessoa reconhecida
        self.nome_label = QLabel("Nome: N/A")
        self.nome_label.setAlignment(Qt.AlignCenter)
        self.nome_label.setFont(font)  # Defina a fonte para o rótulo do nome
        self.nome_label.setFixedHeight(75)

        # Conecção do botão ao slot (função) que executa o reconhecimento facial
        self.button.clicked.connect(self.executar_reconhecimento_facial)

        # Adição dos rótulos, do botão e do rótulo do nome ao layout
        layout.addWidget(titulo_label)
        layout.addWidget(mensagem_label)
        layout.addWidget(self.button)
        layout.addWidget(self.nome_label)

        # Criação do Menu Superior e seus botões
        action = QAction('Adicionar Imagens', self)
        action.triggered.connect(self.interface_update)
        ajuda = QAction('Ajuda', self)
        ajuda.triggered.connect(self.ajuda)
        sair = QAction('Sair', self)
        sair.triggered.connect(self.sair)
        menu = self.menuBar()
        menu_geral = menu.addMenu('Menu')
        menu_geral.addAction(action)
        menu_geral.addAction(ajuda)
        menu_geral.addAction(sair)

        #Preparação para mudar a Label Nome quando o rosto for reconhecido
        self.worker = Worker()
        self.worker.finished.connect(self.update_nome_label)

    #Função de alteração da Label de Nome, para quando o rosto for reconhecido
    @Slot(str)
    def update_nome_label(self, nome):
        self.nome_label.setText(nome)

    #Função para iniciar o reconhecimento facial em segundo plano.
    def executar_reconhecimento_facial(self):
        #self.button.setEnabled(False)
        global marca

        #Na segunda vez que o botão for apertado,
        #aumenta o valor de marca para fazer o Reconhecimento rodar novamente
        if 'garantia' in globals():
            marca = marca + 1

        #Na primeira vez que o botão for apertado, executa o sistema em segundo plano
        elif 'worker_thread' in globals() and not 'garantia' in globals():
            self.worker.moveToThread(worker_thread)
            worker_thread.started.connect(self.worker.executar_reconhecimento_facial)
            worker_thread.start()

            #Criação da varíavel garantia para garantir que a função não será criada novamente.
            global garantia
            garantia = 1

            # Adição do valor de marca em 1 para permitir a execução do sistema em segundo plano.
            marca = marca + 1


    #Função de Interface do Update
    def interface_update(self, folder):
        # Definição de título e Layout
        self.setWindowTitle('Update no Sistema')
        self.setGeometry(300, 300, 300, 200)
        layout = QVBoxLayout()

        # Definição de fonte padrão
        font = QFont()
        font.setPixelSize(18)
        mensagem_Label = QLabel(
            'Escolha uma pessoa para adicionar novas imagens')
        mensagem_Label.setAlignment(Qt.AlignCenter)
        mensagem_Label.setFont(font)  # Defina a fonte para o rótulo do nome
        mensagem_Label.setFixedHeight(25)
        layout.addWidget(mensagem_Label)

        # Adição de um QListWidget
        self.listWidget = QListWidget(self)
        layout.addWidget(self.listWidget)

        # Definição de lista dos nomes das pastas em um diretório
        data_dir = 'lfw2'
        folders = [name for name in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, name))]

        # Adiciona um Botão (QPushButton) para cada pessoa/pasta
        for index, folder in enumerate(folders):
            item = QListWidgetItem(folder)
            self.listWidget.addItem(item)
            button = QPushButton('Clique', self)

            #Definação do nome dos botões para diferencia-los
            button.setObjectName(f'{folder}')

            button.clicked.connect(partial(self.colocando_imagem, folder))
            self.listWidget.setItemWidget(item, button)

        # Aplicação da interface já definida
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    # Função de execução do modelo de Update
    def colocando_imagem(self, folder):
        # Adição da tela enquanto o update é feito
        self.setWindowTitle('Fazendo Update')
        self.setGeometry(300, 300, 300, 200)
        layout = QVBoxLayout()

        # Definição da fonte
        font = QFont()
        font.setPixelSize(18)

        # Preparação das Labels
        self.mensagem_Label = QLabel(
            'Insira as imagens e espere enquanto o sistema é retreinado.')
        self.mensagem_Label.setAlignment(Qt.AlignCenter)
        self.mensagem_Label.setFont(font)  # Defina a fonte para o rótulo do nome
        self.mensagem_Label.setFixedHeight(25)
        self.submensagem_Label = QLabel('Isso pode demorar alguns minutos. É comum que o sistema deixe de responder por um tempo.')
        self.submensagem_Label.setAlignment(Qt.AlignCenter)
        self.submensagem_Label.setFixedHeight(15)
        layout.addWidget(self.mensagem_Label)
        layout.addWidget(self.submensagem_Label)

        # Aplicação da interface já definida
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # Execução do Update
        try:
            #Definindo o nome da pasta de acordo com o botão clicado na interface anterior
            self.folder_name = folder
            print (self.folder_name)
            data_dir = 'lfw2'


            root = Tk()
            root.withdraw()  # linha para não mostrar uma janela Tk vazia
            file_path = filedialog.askopenfilenames()  # Execução de caixa de diálogo Open File, retorna o caminho para o(s) arquivo(s) selecionado(s)

            # Seleção da pasta correta
            person_dir = os.path.join(data_dir, self.folder_name)

            # Verificação de existência da pasta
            if not os.path.exists(person_dir):
                print(f"A pessoa {self.folder_name} não existe no sistema.")
                self.finished.emit(f"A pessoa {self.folder_name} não existe no sistema.")

            # Movimentação das imagens para a pasta "lfw2" e para a pasta da pessoa
            for file in root.tk.splitlist(file_path):
                img = Image.open(file)
                img_resized = img.resize((250, 250))
                base_name = os.path.basename(file)  # Obter o nome base do arquivo
                save_path = os.path.join(person_dir, base_name)  # Criar o caminho completo para salvar
                img_resized.save(save_path)  # Copia os arquivos para o diretório da pessoa

            # Carregamento do modelo existente
            model = keras.models.load_model('Faciem 1-2.h5')

            # Definição do treinamento com os novos dados
            train_ds = image_dataset_from_directory(
                data_dir,
                validation_split=0.2,
                subset="training",
                seed=123,
                image_size=(250, 250),
                batch_size=32
            )

            val_ds = image_dataset_from_directory(
                data_dir,
                validation_split=0.2,
                subset="validation",
                seed=123,
                image_size=(250, 250),
                batch_size=32
            )

            # Continuação do treinamento
            model.fit(train_ds, validation_data=val_ds, batch_size=32, epochs=2)

            # Atualização do modelo com novas imagens
            model.save('Salvando.h5')

            # Apagamento da versão antiga da IA
            antigo = 'Faciem 1-2.h5'
            os.remove(antigo)

            # Renomeiamento da nova versão para o nome correto
            novo = 'Salvando.h5'
            os.rename(novo, 'Faciem 1-2.h5')

        except Exception as e:
            print('Algo deu errado :(')

        python = sys.executable
        os.execl(python, python, *sys.argv)


    #função de "ajuda", localizado no menu
    def ajuda(self):
        #Abre o arquivo html do site
        caminho_atual = os.getcwd()
        caminho_site = os.path.join(caminho_atual, 'Site/PagTutorial/index.html')
        url = QUrl.fromLocalFile(caminho_site)
        QDesktopServices.openUrl(QUrl(url))

    #função para sair do aplicativo
    def sair(self):
        QApplication.instance().quit()




#Execução do aplicativo
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
