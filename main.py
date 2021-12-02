from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import sys
import time
import ctypes
import logging
import requests
from enum import Enum
import logging.handlers
from packaging import version
from functools import partial
from pdfProcess import filepathToImage

CURRENT_VERSION = "0.1.0"
LATEST_VERSION = requests.get(url="https://raw.githubusercontent.com/201710396/PDFPY/main/version.json").json()['version']

class DrawingMode(Enum):
	BRUSH = 1
	RECT = 2
	CIRCLE = 3
	LINE = 4
	TEXT = 5
	ERASER = 6

class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.setWindowTitle("PDFPY")
		self.setWindowIcon(QIcon("./dependencies/image/logo.jpg"))
		self.checkUpdate()

		self.statusBar()
		self.defaultWidget = DefaultWidget(self)
		self.ctrlPressed = False
		self.imgPixmap = None
		self.imageLoadFlag = False
		self.isPresentationMode = False
		self.fillColor = QColor(0, 0, 0)
		self.lineColor = QColor(0, 0, 0)
		self.initMenu()
		self.initToolbar()
		
		self.setStyleSheet("QMainWindow { background: #282C34; }")
		self.statusBar().setVisible(False)
		self.addToolBar(Qt.LeftToolBarArea, self.lftToolbar)
		self.move(300, 50)
		self.resize(1080, 900)
		self.setCentralWidget(self.defaultWidget)
		self.show()
		rootLogger.info("MainWindow 초기화 완료")
	
	def checkUpdate(self):
		try:
			msg = QMessageBox()
			msg.setWindowIcon(QIcon(resourcePath("dependencies/image/logo.ico")))
			if version.parse(CURRENT_VERSION) < version.parse(LATEST_VERSION):
				rootLogger.info("업데이트 발견")
				msg.setWindowTitle("업데이트 알림")
				msg.setText("업데이트가 가능합니다. (%s -> %s)" % (CURRENT_VERSION, LATEST_VERSION))
				msg.addButton(QPushButton("&Update"), QMessageBox.YesRole)
				msg.setStandardButtons(QMessageBox.Cancel)
				answer = msg.exec_()

				if answer == QMessageBox.Cancel:
					rootLogger.info("업데이트 취소")
				else:
					rootLogger.info("업데이트 시작")
			else:
				rootLogger.info("업데이트 없음")
				msg.setWindowTitle("업데이트 알림")
				msg.setText("최신버전(%s)입니다." % CURRENT_VERSION)
				msg.addButton(QPushButton("&Ok"), QMessageBox.YesRole)
				msg.exec_()
		
		except Exception as e:
			rootLogger.error(e)
	
	def initMenu(self):
		self.menu = self.menuBar()

		fileMenu = self.menu.addMenu("&File")
		newFileMenu = QAction("새 파일", self)
		newFileMenu.setShortcut("Ctrl+N")
		newFileMenu.triggered.connect(self.newFile)
		newWinMenu = QAction("새 창", self)
		newWinMenu.setShortcut("Ctrl+Shift+N")
		newWinMenu.triggered.connect(self.runPDFPY)
		openFileMenu = QAction("파일 열기...", self)
		openFileMenu.setShortcut("Ctrl+O")
		openFileMenu.triggered.connect(self.defaultWidget.view.openFile)
		saveFileMenu = QAction("저장", self)
		saveFileMenu.setShortcut("Ctrl+S")
		saveFileMenu.triggered.connect(self.saveFile)
		exportMenu = QAction("내보내기", self)
		exportMenu.setShortcut("Ctrl+Shift+E")
		exportMenu.triggered.connect(self.export)
		exitMenu = QAction("종료", self)
		exitMenu.setShortcut("Ctrl+Q")
		exitMenu.triggered.connect(self.customCloseEvent)
		fileMenu.addAction(newFileMenu)
		fileMenu.addAction(newWinMenu)
		fileMenu.addAction(openFileMenu)
		fileMenu.addAction(saveFileMenu)
		fileMenu.addAction(exportMenu)
		fileMenu.addAction(exitMenu)

		editMenu = self.menu.addMenu("&Edit")
		undoMenu = QAction("되돌리기", self)
		undoMenu.setShortcut("Ctrl+Z")
		undoMenu.triggered.connect(self.defaultWidget.view.undo)
		editMenu.addAction(undoMenu)

		viewMenu = self.menu.addMenu("&View")
		self.presMenu = QAction("프레젠테이션 모드", self)
		self.presMenu.setShortcut("Ctrl+R")
		self.presMenu.triggered.connect(self.setPresMode)
		viewMenu.addAction(self.presMenu)

		helpMenu = self.menu.addMenu("&Help")
		progInfoMenu = QAction("프로그램 정보", self)
		progInfoMenu.setShortcut("Ctrl+I")
		progInfoMenu.triggered.connect(self.showProgInfo)
		updateCheckMenu = QAction("업데이트 확인", self)
		updateCheckMenu.setShortcut("Ctrl+U")
		updateCheckMenu.triggered.connect(self.checkUpdate)
		helpMenu.addAction(progInfoMenu)
		helpMenu.addAction(updateCheckMenu)

		rootLogger.info("menuBar 설정 완료")
	
	def newFile(self):
		self.defaultWidget().__init__()
	
	def runPDFPY(self):
		ctypes.windll.shell32.ShellExecuteW(None, "open", sys.executable, __file__, None, 1)
	
	def saveFile(self):
		img = QPixmap(self.defaultWidget.view.grab(self.defaultWidget.view.sceneRect().toRect()))
		
		rootLogger.info("파일 저장하기 메뉴 열림")
		filename, _ = QFileDialog.getSaveFileName(self, "파일 저장", "", "PNG (*.png)")
		print(_)
		if filename:
			img.save(filename)
	
	def export(self):
		self.defaultWidget.view.scene.clearSelection()
		self.defaultWidget.view.scene.setSceneRect(self.defaultWidget.view.scene.itemsBoundingRect())
		img = QImage(self.defaultWidget.view.scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
		img.fill(Qt.transparent)

		painter = QPainter(img)
		self.defaultWidget.view.scene.render(painter)
		painter.end()

		rootLogger.info("파일 내보내기 메뉴 열림")
		filename, _ = QFileDialog.getSaveFileName(self, "파일 내보내기", "", "PNG (*.png)")
		if filename:
			img.save(filename)
	
	def showProgInfo(self):
		infoBox = QMessageBox()
		infoBox.setIconPixmap(QPixmap(resourcePath("dependencies/image/logo.ico")))
		infoBox.setWindowTitle("정보")
		infoBox.setWindowIcon(QIcon(resourcePath("dependencies/image/logo.ico")))
		infoBox.setText("제작자 : 김진혁<br>깃허브 : <a href='https://github.com/201710396'>https://github.com/201710396</a><br>이메일 : 201710396@office.seowon.ac.kr")
		infoBox.addButton(QPushButton("&Ok"), QMessageBox.YesRole)
		infoBox.exec_()
	
	def setPresMode(self):
		self.presMenu.setText("일반 모드")
		self.presMenu.disconnect()
		self.presMenu.triggered.connect(self.setDefaultMode)
		self.lftToolbar.setVisible(False)
		self.defaultWidget.frame.setVisible(False)
		self.showMaximized()
		
		rootLogger.info("프레젠테이션 모드로 변경")
	
	def setDefaultMode(self):
		self.presMenu.setText("프레젠테이션 모드")
		self.presMenu.disconnect()
		self.presMenu.triggered.connect(self.setPresMode)
		self.lftToolbar.setVisible(True)
		self.defaultWidget.frame.setVisible(True)
		self.showNormal()

		rootLogger.info("일반 모드로 변경")
	
	def initToolbar(self):
		self.lftToolbar = QToolBar("Menu", self)
		self.lftToolbar.setMovable(False)
		self.lftToolbar.setStyleSheet("""
		padding: 5px 0px 5px 0px;
		border: 1px #707070;
		margin: 10px; background: #21252B;
		""")
		brushTool = QAction(QIcon(resourcePath("dependencies/image/whiteBrush.png")), "브러시", self)
		brushTool.triggered.connect(self.brushMode)
		eraserTool = QAction(QIcon(resourcePath("dependencies/image/whiteEraser.png")), "지우개", self)
		eraserTool.triggered.connect(self.eraserMode)
		rectTool = QAction(QIcon(resourcePath("dependencies/image/whiteRect.png")), "사각형", self)
		rectTool.triggered.connect(self.rectMode)
		ellipseTool = QAction(QIcon(resourcePath("dependencies/image/whiteEllipse.png")), "타원형", self)
		ellipseTool.triggered.connect(self.ellipseMode)
		lineTool = QAction(QIcon(resourcePath("dependencies/image/whiteLine.png")), "선", self)
		lineTool.triggered.connect(self.lineMode)
		textTool = QAction(QIcon(resourcePath("dependencies/image/whiteText.png")), "텍스트", self)
		textTool.triggered.connect(self.textMode)
		self.fillColorTool = QToolButton(self)
		self.fillColorTool.setStyleSheet('background-color: rgb(0,0,0)')
		self.fillColorTool.clicked.connect(partial(self.showColorDlg, "fill"))
		self.lineColorTool = QToolButton(self)
		self.lineColorTool.setStyleSheet('background-color: rgb(0,0,0)')
		self.lineColorTool.clicked.connect(partial(self.showColorDlg, "line"))
		self.lineThickTool = QSlider(Qt.Vertical, self)
		self.lineThickTool.setRange(1, 50)
		self.lineThickTool.setValue(3)
		self.lineThickTool.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.lineThickTool.valueChanged.connect(self.changeLblLineThick)
		self.lblLineThick = QLabel(self)
		self.lblLineThick.setText(str(self.lineThickTool.value()))
		self.lblLineThick.setStyleSheet('color: #FFFFFF;')

		self.lftToolbar.addAction(brushTool)
		self.lftToolbar.addAction(eraserTool)
		self.lftToolbar.addAction(rectTool)
		self.lftToolbar.addAction(ellipseTool)
		self.lftToolbar.addAction(lineTool)
		self.lftToolbar.addAction(textTool)
		self.lftToolbar.addWidget(self.fillColorTool)
		self.lftToolbar.addWidget(self.lineColorTool)
		self.lftToolbar.addWidget(self.lineThickTool)
		self.lftToolbar.addWidget(self.lblLineThick)

		rootLogger.info("lftToolbar 설정 완료")
	
	def changeLblLineThick(self):
		self.lblLineThick.setText(str(self.lineThickTool.value()))

		rootLogger.info("선 굵기 %d로 변경" % self.lineThickTool.value())
	
	def showColorDlg(self, mode):
		color = QColorDialog.getColor()
		if color.isValid():
			if mode == "fill":
				self.fillColor = color
				self.fillColorTool.setStyleSheet('background-color: {}'.format(color.name()))
			elif mode == "line":
				self.lineColor = color
				self.lineColorTool.setStyleSheet('background-color: {}'.format(color.name()))
		
		rootLogger.info("ColorDialog 실행")
	
	def lineMode(self):
		self.defaultWidget.drawType = DrawingMode.LINE
		rootLogger.info("선분 모드로 변경")
	
	def rectMode(self):
		self.defaultWidget.drawType = DrawingMode.RECT
		rootLogger.info("사각형 모드로 변경")
	
	def ellipseMode(self):
		self.defaultWidget.drawType = DrawingMode.CIRCLE
		rootLogger.info("타원형 모드로 변경")
	
	def textMode(self):
		self.defaultWidget.drawType = DrawingMode.TEXT
		rootLogger.info("텍스트 모드로 변경")

	def brushMode(self):
		self.defaultWidget.drawType = DrawingMode.BRUSH
		rootLogger.info("브러시 모드로 변경")
	
	def eraserMode(self):
		self.defaultWidget.drawType = DrawingMode.ERASER
		rootLogger.info("지우개 모드로 변경")
	
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Control:
			self.ctrlPressed = True
			super(MainWindow, self).keyPressEvent(event)
	
	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Control:
			self.ctrlPressed = False
			super(MainWindow, self).keyReleaseEvent(event)

	def closeEvent(self, e):
		close = QMessageBox.question(self, "프로그램 종료", "PDFPY를 종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
		if close == QMessageBox.Yes:
			rootLogger.info("closeEvent 수락")
			e.accept()
		else:
			rootLogger.info("closeEvent 무시")
			e.ignore()

	def customCloseEvent(self):
		close = QMessageBox.question(self, "프로그램 종료", "PDFPY를 종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
		if close == QMessageBox.Yes:
			rootLogger.info("customCloseEvent 수락")
			QCoreApplication.instance().quit()

class DefaultWidget(QWidget):
	def __init__(self, parent):
		super(DefaultWidget, self).__init__(parent)

		self.view = GraphicsView(self)
		self.drawType = DrawingMode.LINE
		self.drawingLink = {}

		self.setDefaultLayout()

		rootLogger.info("DefaultWidget 초기화 완료")
	
	def setDefaultLayout(self):
		self.defaultLayout = QHBoxLayout()
		
		mainLayout = QHBoxLayout()
		mainLayout.addWidget(self.view)

		self.sideLayout = QVBoxLayout()
		self.drawedCombo = QComboBox(self)
		
		self.drawedCombo.setFixedWidth(200)
		self.colorChangeBtn = QPushButton(self)
		self.colorChangeBtn.setText("색 바꾸기")
		self.colorChangeBtn.clicked.connect(partial(self.view.changeAttribute, self.drawingLink, self.drawedCombo))
		self.frame = QFrame()
		self.sideLayout.addWidget(self.drawedCombo)
		self.sideLayout.addWidget(self.colorChangeBtn)
		self.frame.setLayout(self.sideLayout)

		self.defaultLayout.addLayout(mainLayout)
		self.defaultLayout.addWidget(self.frame)

		self.setLayout(self.defaultLayout)

		rootLogger.info("defaultLayout으로 설정")
	
	def refreshCombo(self):
		count = [1, 1, 1, 1, 1]
		self.drawedCombo.clear()
		tempList = self.view.drawedItems[:]
		id = 0
		while(id < len(tempList)):
			i = tempList[id]
			if type(i) == int:
				# start = tempList.index(i)
				end = tempList.index("END%d" % i)
				id = end + 1
				self.drawedCombo.addItem("Brush %d" % count[0])
				count[0] += 1

			elif type(i) == type(QGraphicsLineItem()):
				self.drawedCombo.addItem("Line %d" % count[1])
				self.drawingLink["Line %d" % count[1]] = i
				id += 1
				count[1] += 1

			elif type(i) == type(QGraphicsRectItem()):
				self.drawedCombo.addItem("Rect %d" % count[2])
				self.drawingLink["Rect %d" % count[2]] = i
				id += 1
				count[2] += 1

			elif type(i) == type(QGraphicsEllipseItem()):
				self.drawedCombo.addItem("Circle %d" % count[3])
				self.drawingLink["Circle %d" % count[3]] = i
				id += 1
				count[3] += 1

			elif type(i) == type(QGraphicsTextItem()):
				self.drawedCombo.addItem("Text %d" % count[4])
				self.drawingLink["Text %d" % count[4]] = i
				id += 1
				count[4] += 1

		rootLogger.info("drawedCombo 갱신")

class GraphicsView(QGraphicsView):
	def __init__(self, parent):
		super().__init__(parent)

		self.scene = QGraphicsScene(self)
		self.setScene(self.scene)
		self.temp = []
		self.brushFlag = []
		self.imgPixmap = None
		self.fontDB = QFontDatabase()
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.fontDB.addApplicationFont(resourcePath("dependencies/font/D2Coding.ttf"))
		self.setRenderHint(QPainter.HighQualityAntialiasing)
		self.setAlignment(Qt.AlignCenter)
		# shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
		# shortcut.activated.connect(self.changeColor)
		self.background = QGraphicsPixmapItem()
		self.scene.addItem(self.background)
		self.prevItems = []
		self.drawedItems = []
		 
		self.start = QPointF()
		self.end = QPointF()

		# shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
		# shortcut.activated.connect(self.undo)

		rootLogger.info("QGraphicsView 초기화 완료")
	
	def changeAttribute(self, dict, cbx):
		try:
			obj = dict[cbx.currentText()]
			if type(obj) == type(QGraphicsLineItem()):
				obj.setPen(QPen(ex.lineColor, int(ex.lineThickTool.value())))
			elif type(obj) == type(QGraphicsTextItem()):
				obj.setDefaultTextColor(ex.lineColor)
			elif type(obj) == type(QGraphicsRectItem()) or type(obj) == type(QGraphicsEllipseItem()):
				obj.setBrush(QBrush(ex.fillColor))
		except Exception as e:
			rootLogger.error(e)

	def openFile(self):
		rootLogger.info("파일 열기 메뉴 열림")
		fileName, _ = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
		if fileName == "":
			return
		if fileName.split(".")[-1].lower() != "pdf":
			self.imgPixmap = QPixmap(fileName)
			if self.imgPixmap.isNull():
				self.imageLoadFlag = False
				QMessageBox.information(self, "PDFPY",
						"파일 %s을 불러올 수 없습니다." % fileName)

				rootLogger.info("파일을 불러오지 못함")
				return
			else:
				self.imageLoadFlag = True
				self.imgPixmap = self.imgPixmap.scaledToHeight(850)
				self.setImage(self.imgPixmap, self.imgPixmap.width(), self.imgPixmap.height())

				rootLogger.info("이미지를 이미지 파일로부터 불러옴")
		else:
			self.convertedImage = filepathToImage(fileName)
			self.imgPixmap = QPixmap(self.convertedImage[0])
			self.imgPixmap = self.imgPixmap.scaledToHeight(850)
			self.setImage(self.imgPixmap, self.imgPixmap.width(), self.imgPixmap.height())

			rootLogger.info("이미지를 PDF로부터 불러옴")
	
	def setImage(self, image, w, h):
		self.scene.setSceneRect(0, 0, w, h)
		self.resize(w, h)
		self.background.setPixmap(image)
		
		rootLogger.info("QGraphicsScene을 불러온 이미지에 맞춤")

	def moveEvent(self, e):
		rect = QRectF(self.rect())
		rect.adjust(0,0,-2,-2)
		self.scene.setSceneRect(rect)

	def mousePressEvent(self, e):
		if e.button() == Qt.LeftButton:
			self.start = e.pos()
			self.end = e.pos()

	def mouseMoveEvent(self, e):
		if e.buttons() & Qt.LeftButton:
			self.end = e.pos()
			# if self.parent().checkbox.isChecked():
			#     pen = QPen(QColor(255,255,255), 10)
			#     path = QPainterPath()
			#     path.moveTo(self.start)
			#     path.lineTo(self.end)
			#     self.scene.addPath(path, pen)
			#     self.start = e.pos()
			#     return None

			if self.parent().drawType == DrawingMode.LINE:
				pen = QPen(ex.lineColor, int(ex.lineThickTool.value()))
				if len(self.prevItems) > 0:
					self.scene.removeItem(self.prevItems[-1])
					del(self.prevItems[-1])

				line = QGraphicsLineItem(self.start.x(), self.start.y(), self.end.x(), self.end.y())
				line.setPen(pen)
				self.scene.addItem(line)
				self.prevItems.append(line)
			
			elif self.parent().drawType == DrawingMode.RECT:
				pen = QPen(Qt.transparent, 0)
				brush = QBrush(ex.fillColor)
				if len(self.prevItems) > 0:
					self.scene.removeItem(self.prevItems[-1])
					del(self.prevItems[-1])
				
				rect = QGraphicsRectItem(QRectF(self.start, self.end))
				rect.setPen(pen)
				rect.setBrush(brush)
				self.scene.addItem(rect)
				self.prevItems.append(rect)
			
			elif self.parent().drawType == DrawingMode.CIRCLE:
				pen = QPen(Qt.transparent, 0)
				brush = QBrush(ex.fillColor)
				if len(self.prevItems) > 0:
					self.scene.removeItem(self.prevItems[-1])
					del(self.prevItems[-1])
				
				ellipse = QGraphicsEllipseItem(QRectF(self.start, self.end))
				ellipse.setPen(pen)
				ellipse.setBrush(brush)
				self.scene.addItem(ellipse)
				self.prevItems.append(ellipse)
			
			elif self.parent().drawType == DrawingMode.BRUSH:
				pen = QPen(ex.lineColor, int(ex.lineThickTool.value()))
				brushLine = QGraphicsLineItem(self.start.x(), self.start.y(), self.end.x(), self.end.y())
				brushLine.setPen(pen)
				self.scene.addItem(brushLine)
				self.temp.append(brushLine)
				self.start = e.pos()

		super().mouseMoveEvent(e)

	def mouseReleaseEvent(self, e):
		if e.button() == Qt.LeftButton:
			# if self.parent().checkbox.isChecked():
			#     return None
			if self.parent().drawType == DrawingMode.LINE:
				pen = QPen(ex.lineColor, int(ex.lineThickTool.value()))
				line = QGraphicsLineItem(self.start.x(), self.start.y(), self.end.x(), self.end.y())
				line.setPen(pen)
				self.scene.addItem(line)
				self.drawedItems.append(line)

				rootLogger.info("(%d, %d)->(%d, %d) 선분 그림" % (self.start.x(), self.start.y(), self.end.x(), self.end.y()))

			elif self.parent().drawType == DrawingMode.RECT:
				pen = QPen(Qt.transparent, 0)
				brush = QBrush(ex.fillColor)
				rect = QGraphicsRectItem(QRectF(self.start, self.end))
				rect.setPen(pen)
				rect.setBrush(brush)
				self.scene.addItem(rect)
				self.drawedItems.append(rect)

				rootLogger.info("(%d, %d)->(%d, %d) 사각형 그림" % (self.start.x(), self.start.y(), self.end.x(), self.end.y()))
			
			elif self.parent().drawType == DrawingMode.CIRCLE:
				pen = QPen(Qt.transparent, 0)
				brush = QBrush(ex.fillColor)
				ellipse = QGraphicsEllipseItem(QRectF(self.start, self.end))
				ellipse.setPen(pen)
				ellipse.setBrush(brush)
				self.scene.addItem(ellipse)
				self.drawedItems.append(ellipse)

				rootLogger.info("(%d, %d)->(%d, %d) 타원형 그림" % (self.start.x(), self.start.y(), self.end.x(), self.end.y()))
			
			elif self.parent().drawType == DrawingMode.TEXT:
				inputTxt, answer = QInputDialog.getText(self, "Input", "입력할 텍스트")

				if answer:
					text = QGraphicsTextItem(inputTxt)
					text.setPos(self.end)
					text.setDefaultTextColor(ex.fillColor)
					text.setFont(QFont("D2Coding", ex.lineThickTool.value()))
					self.scene.addItem(text)
					self.drawedItems.append(text)
				
				rootLogger.info("(%d, %d) 텍스트 그림" % (self.end.x(), self.end.y()))
			
			elif self.parent().drawType == DrawingMode.BRUSH:
				self.brushFlag.append(len(self.brushFlag))
				self.drawedItems.append(self.brushFlag[-1])
				self.drawedItems.extend(self.temp)
				self.drawedItems.append("END%d" % self.brushFlag[-1])
				self.temp = []

				rootLogger.info("브러시 그림")
			
			elif self.parent().drawType == DrawingMode.ERASER:
				item = self.itemAt(QPoint(self.end))
				self.drawedItems.remove(item)
				self.scene.removeItem(item)

				rootLogger.info("객체(%s) 지움" % str(item))

		# print(self.drawedItems)
		self.parent().refreshCombo()

		for i in self.prevItems:
			self.scene.removeItem(i)
			self.prevItems.remove(i)

		super().mouseReleaseEvent(e)

	def undo(self):
		if self.drawedItems:
			if type(self.drawedItems[-1]) == str:
				found = self.drawedItems.index(self.brushFlag.pop())
				for i in self.drawedItems[found+1:-1]:
					self.scene.removeItem(i)
				del self.drawedItems[found:-1]
				self.drawedItems.pop()
			else:
				poped = self.drawedItems.pop()
				self.scene.removeItem(poped)
				del poped
			
			rootLogger.info("뒤로가기 실행함")
		else:
			rootLogger.info("취소할 객체 없음")
		# print(self.drawedItems)
		self.parent().refreshCombo()

def resourcePath(relativePath):
	try:
		basePath = sys._MEIPASS
	except Exception:
		basePath = os.path.abspath(".")
	return os.path.join(basePath, relativePath)

if __name__ == "__main__":
	os.makedirs("./logs", exist_ok=True)
	rootLogger = logging.getLogger("PDFPY")
	rootLogger.setLevel(logging.DEBUG)
	formatter = logging.Formatter("[%(asctime)s | %(levelname)s | %(name)s | Line %(lineno)s] > %(message)s", "%Y-%m-%d %H:%M:%S")
	now = time.localtime()
	fileHandler = logging.FileHandler("./logs/PDFPY_%d_%d_%d_%d_%d_%d.log" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
	fileHandler.setFormatter(formatter)
	fileHandler.setLevel(logging.NOTSET)
	streamHandler = logging.StreamHandler()
	streamHandler.setFormatter(formatter)
	rootLogger.addHandler(fileHandler)
	rootLogger.addHandler(streamHandler)
	app = QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())