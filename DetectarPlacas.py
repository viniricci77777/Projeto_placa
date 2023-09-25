import cv2
import pytesseract
import threading
import pymysql
import logging

class database:
    _host:str
    _user:str
    _password:str
    _database:str

    def __init__(self):
        self._host = None
        self._user = None
        self._password = None
        self._database = None
    
    @classmethod
    def _connect(cls):
        try:
            connection = pymysql.connect(
                host=cls._host,
                user=cls._user,
                password=cls._password,
                database=cls._database
            )
            cursor = connection.cursor()
            return cursor
        except:
            print('Não foi possivel estabelecer a conexão com o banco de dados')
    
class imagem:
    
    # Captura o frame da webcam
    def _ImageCapture(self):
        try:
        # parâmetro passado se refere a qual webcam será capturada a imagem
            cap = cv2.VideoCapture(0)
            validation, frame = cap.read()
            while validation:
                validation, frame = cap.read()
                cv2.imshow('Webcam', frame)
                # parâmetro passado se refere ao tempo em milisegundos entre cada captura
                k = cv2.waitKey(2000)
                # caso o botão com valor 113 (F2) seja apertado, o código é interrompido
                if k == 113:
                    cap.release()
                    cv2.destroyAllWindows()
                    break
                # chama função com o frame capturado
                self._contorno_imagem(frame)
                self._preProcessamentoRoi()
                self._ocrImagePlate()
        except:
            print('Não foi possivel capturar a imagem da webcam')

    def _contorno_imagem(self, frame):
        if frame is not None:
            # parâmetros são o frame passado para o método e o tamanho a ser redimensionalizado
            image_resized = cv2.resize(frame, (800, 400))
            # imagem a ser convertida e a função presente na biblioteca de conversão para cinza
            gray_image = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
            # função para binarizar a imagem
            _, binary_image = cv2.threshold(gray_image, 90, 255, 0)
            # função para borrar a imagem levemente
            blur_img = cv2.GaussianBlur(binary_image, (3, 3), 0)
            # função para fazer os contornos na imagem com base em árvore de hierarquia e todos os contornos são mantidos sem qualquer simplificação
            contours, _ = cv2.findContours(blur_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

            for contour in contours:
                # calcula o comprimento de cada contorno, caso este seja fechado (True)
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 300: 
                    # aproxima o contorno simplificando-o, caso o valor seja menor no segundo parâmetro, mais proximo ficara do contorno original e True indica que é fechado
                    aprox_retangulo = cv2.approxPolyDP(contour, 0.03 * perimeter, True)
                    # caso a variavel tenha 4 lados (retangulo)
                    if len(aprox_retangulo) == 4:
                        # pega as coordenadas do contorno
                        x, y, height, width = cv2.boundingRect(contour)
                        # pinta um retangulo com essas coordenadas em cima da imagem passada, os dois ultimos parâmetros são a cor RGB e a grossura da linha
                        cv2.rectangle(image_resized, (x, y), (x + height, y + width), (90, 255, 35), 3)
                        roi = image_resized[y:y + width, x:x +height]
                        cv2.imwrite('D:/VSCODE_PY/Projeto_placas/roi.png', roi)
    
    def _preProcessamentoRoi(self):
        max_width = 800
        max_height = 400    
        roi = cv2.imread('D:/VSCODE_PY/Projeto_placas/roi.png')
        if roi is None:
            return 
        
        # pega o valor em pixels da imagem
        current_height, current_width = roi.shape[:2]
        # se for maior que o definido é redimensionado
        if current_width > max_width or current_height > max_height:
            roi = cv2.resize(roi, (max_width, max_height), interpolation=cv2.INTER_CUBIC)
        roi_risezed = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray_roi = cv2.cvtColor(roi_risezed, cv2.COLOR_BGR2GRAY)   
        n, binary_roi = cv2.threshold(gray_roi, 70, 255, cv2.THRESH_BINARY)
        blur_roi = cv2.GaussianBlur(binary_roi, (5, 5), 0)
        cv2.imwrite('D:/VSCODE_PY/Projeto_placas/roi.png', blur_roi)

    def _ocrImagePlate(self):
        roi = cv2.imread('D:/VSCODE_PY/Projeto_placas/roi.png')
        if roi is not None:
            roi_resized = cv2.resize(roi, (800, 400))
            # configuração de caracteres que o pytessetact irá analisar
            config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6'
            # imagem a ser analisada as letras,a linguagem e a configuração passada acima
            saida = pytesseract.image_to_string(roi_resized, lang='eng', config=config)
            
            saida = saida.strip().upper()

            db = database
            db._host = 'localhost'
            db._user = 'root'
            db._password = '.VINxBLOw[JfTdo-'
            db._database = 'cadastros'
            cursor = db._connect()
            # consulta do banco de dados em SQL
            cursor.execute(f"select placa_automovel from pessoas where placa_automovel = '{saida}';")
            placa = cursor.fetchall()
            
            if len(placa) > 0:
                placa = placa[0][0]
                placa = placa.strip().upper()
            
            
            if saida == placa:
                # geração de log com path do arquivo, o nivel de importância e a formatação das informações saidas
                logging.basicConfig(filename='D:/VSCODE_PY/Projeto_placas/retorno.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
                logging.debug(f'A placa "{placa}" está presente no database: %s', True) 
            else:
                print(saida)

if __name__ == "__main__":
    img = imagem()
    # processamento do método imagecapture não atrapalha os outros métodos, rodam ao mesmo tempo diminuindo o processamento
    thread_processamnto = threading.Thread(target=img._ImageCapture(), daemon=True)
    thread_processamnto.start()
    
