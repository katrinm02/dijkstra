from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
    QWidget, QMessageBox, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMenuBar, QFileDialog, QPushButton, QAction,
    QVBoxLayout, QListWidget ,QTableWidget, QHeaderView, QTableWidgetItem,
    QStyledItemDelegate, QMessageBox)
from PyQt5.QtGui import QIntValidator, QPixmap
import createGraph
import json

class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        print("NO!")
        return

class QComboBoxEdge(QComboBox):
    boxInstances = []

    def __init__(self):
        super(QComboBox, self).__init__()
        QComboBoxEdge.boxInstances.append(self)

    @classmethod
    def addNode(QComboBoxEdge, value):
        for box in QComboBoxEdge.boxInstances:
            box.addItem(value)

    @classmethod
    def deleteEdge(QComboBoxEdge, index):
        for box in QComboBoxEdge.boxInstances:
            box.removeItem(index)
    
    @classmethod
    def reset(QComboBoxEdge):
        for box in QComboBoxEdge.boxInstances:
            box.clear()

class AskUserWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Hello World')
        self.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def showMessage(message):
    msg = QMessageBox()
    msg.setWindowTitle("Информация")
    msg.setText(message)
    msg.setIcon(QMessageBox.Warning)

    msg.exec_()

class Dialog(QDialog):
    # NumGridRows = 3
    # NumButtons  = 4

    def __init__(self):
        super(Dialog, self).__init__()

        self.setWindowTitle("Поиск кратчайшего пути")

        self.createMenu()

        self.createAddingVertex()
        self.createAddingEdge()

        mainLayout = QGridLayout()
        mainLayout.setMenuBar(self.menu)
        mainLayout.addWidget(self.gridVertexBox, 1, 1)
        mainLayout.addWidget(self.gridEdgeBox, 2, 1)

        btnCreateGraph = QPushButton("Построить граф")
        btnCreateGraph.clicked.connect(self.pressButtonCreateGraph)
        mainLayout.addWidget(btnCreateGraph, 3, 1)

        self.createFindingPath()

        img_label = QLabel()
        mainLayout.addWidget(self.gridFindPathBox, 4, 1)

        mainLayout.addWidget(img_label, 1, 2, 3, 1)

        self.setLayout(mainLayout)

    def createMenu(self):
        self.menu = QMenuBar()
        self.parse = QAction("Upload file")
        self.menu.addAction(self.parse)
        self.parse.triggered.connect(self.parseFileGraph)

        self.save = QAction("Save file")
        self.menu.addAction(self.save)
        self.save.triggered.connect(self.saveToFileGraph)

    def createAddingVertex(self):
        self.gridVertexBox = QGroupBox("Вершины графа")
        layout = QGridLayout()

        label = QLabel("Название вершины:")
        vertexName = QLineEdit()
        buttonAddVertex = QPushButton("Добавить")
        buttonAddVertex.clicked.connect(self.pressButtonAddVertex)

        buttonDeleteVertex = QPushButton("Удалить")
        buttonDeleteVertex.clicked.connect(self.pressButtonDeleteVertex)

        VertexList = QListWidget()

        layout.addWidget(label,    1, 0)
        layout.addWidget(vertexName, 1, 1)
        layout.addWidget(buttonAddVertex, 1, 2)
        layout.addWidget(buttonDeleteVertex, 2, 2)
        layout.addWidget(VertexList, 1, 3, 5, 2)

        # self.smallEditor = QTextEdit()
        # self.smallEditor.setPlainText(
        #     "Этот виджет занимает около двух третей "
        #     "макета сетки. \n Смотрим соотношение `setColumnStretch`!"
        # )

        # layout.addWidget(self.smallEditor, 0, 2, 5, 1)   # 0, 2, 4, 1

        # # QGridLayout.setColumnStretch(column, stretch)
        # # Устанавливает растягивающий коэффициент столбца столбца для растягивания. 
        # # Первый столбец - номер 0.
        # layout.setColumnStretch(0, 1)      # label
        # layout.setColumnStretch(1, 10)      # lineEdit
        # layout.setColumnStretch(2, 30)      # smallEditor
        self.gridVertexBox.setLayout(layout)

    def pressButtonAddVertex(self):
        lineEditW = self.gridVertexBox.findChild(QLineEdit)
        listW = self.gridVertexBox.findChild(QListWidget)
        vertexName = lineEditW.text()
        if vertexName != "" :
            list_item = [listW.item(row).text() for row in  range(listW.count())]
            if vertexName in list_item:
                showMessage("Данная вершина уже добавлена")
            else:
                lineEditW.setText("")
                listW.addItem(vertexName)
                QComboBoxEdge.addNode(vertexName)

    def pressButtonDeleteVertex(self):
        listW = self.gridVertexBox.findChild(QListWidget)
        listItems = listW.selectedItems()
        if not listItems: return        
        for item in listItems:
            index = listW.row(item)
            name = item.text()
            listW.takeItem(index)
            QComboBoxEdge.deleteEdge(index)

            #удаление ребер
            tablewidget= self.gridEdgeBox.findChild(QTableWidget)
            deleted = 0
            for row in range(tablewidget.rowCount()):
                row -= deleted
                if tablewidget.item(row, 0).text() == name or tablewidget.item(row, 1).text() == name:
                    tablewidget.removeRow(row)
                    deleted+= 1

    def createAddingEdge(self):
        self.gridEdgeBox = QGroupBox("Ребра графа")
        layout = QGridLayout()

        labelEdge1 = QLabel("Первая вершина:")
        fromEdge = QComboBoxEdge()

        labelEdge2 = QLabel("Вторая вершина:")
        toEdge = QComboBoxEdge()

        labelWeight = QLabel("Вес ребра:")
        weightValue = QLineEdit()
        onlyInt = QIntValidator()
        onlyInt.setRange(1, 1000)
        weightValue.setValidator(onlyInt)

        buttonAddEdge = QPushButton("Добавить")
        buttonDeleteEdge = QPushButton("Удалить")

        tableEdges = QTableWidget()
        tableEdges.setColumnCount(3)
        headers = ['Вершина 1', 'Вершина 2', 'Вес']
        tableEdges.setHorizontalHeaderLabels(headers)
        tableEdges.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        delegate = ReadOnlyDelegate(self)
        tableEdges.setItemDelegateForColumn(0, delegate)
        tableEdges.setItemDelegateForColumn(1, delegate)
        # tableEdges.setEditTriggers(QTableWidget.NoEditTriggers)
        buttonDeleteEdge = QPushButton("Удалить")
        buttonAddEdge.clicked.connect(self.pressButtonAddEdge)
        buttonDeleteEdge.clicked.connect(self.pressButtonDeleteEdge)

        layout.addWidget(labelEdge1,    1, 0)
        layout.addWidget(fromEdge,    1, 1)
        layout.addWidget(labelEdge2,    2, 0)
        layout.addWidget(toEdge,    2, 1)
        layout.addWidget(labelWeight, 3, 0)
        layout.addWidget(weightValue, 3, 1)
        layout.addWidget(buttonAddEdge, 4, 0, 1, 2)
        layout.addWidget(tableEdges, 5, 1, 1, 2)
        layout.addWidget(buttonDeleteEdge, 5, 0)

        self.gridEdgeBox.setLayout(layout)

    def createFindingPath(self):
        self.gridFindPathBox = QGroupBox("Алгоритм поиска пути")
        layout = QGridLayout()

        labelEdge1 = QLabel("Начало:")
        fromEdge = QComboBoxEdge()

        labelEdge2 = QLabel("Конец:")
        toEdge = QComboBoxEdge()

        btnFindPath = QPushButton("Найти кратчайший путь")
        btnFindPath.clicked.connect(self.pressButtonFindPath)

        labelAnswer = QLabel()

        layout.addWidget(labelEdge1,    1, 0)
        layout.addWidget(fromEdge,    1, 1)
        layout.addWidget(labelEdge2,    2, 0)
        layout.addWidget(toEdge,    2, 1)
        layout.addWidget(btnFindPath,    3, 0, 1, 2)
        layout.addWidget(labelAnswer,    4, 0, 1, 2)

        self.gridFindPathBox.setLayout(layout)

    def pressButtonFindPath(self):
        tableW = self.gridEdgeBox.findChild(QTableWidget)
        listW = self.gridVertexBox.findChild(QListWidget)
        ComboBoxEdgeFromW = self.gridFindPathBox.findChildren(QComboBox)[0]
        edgeValueFrom = ComboBoxEdgeFromW.currentText()
        ComboBoxEdgeToW = self.gridFindPathBox.findChildren(QComboBox)[1]
        edgeValueTo = ComboBoxEdgeToW.currentText()
        rowsCount = tableW.rowCount()
        if rowsCount != 0:
            init_graph = {}
            edges = []
            nodes = [listW.item(row).text() for row in  range(listW.count())]
            for node in nodes:
                init_graph[node] = {}
            for row in range(rowsCount):
                node1 = tableW.item(row, 0).text()
                node2 = tableW.item(row, 1).text()
                try:
                    weight = int(tableW.item(row, 2).text())
                    init_graph[node1][node2] = weight
                    edges.append({"node1":node1, "node2":node2, "weight":weight})
                except:
                    showMessage("Вес должен быть числом")
            graph = createGraph.Graph(nodes, init_graph)
            previous_nodes, shortest_path = createGraph.dijkstra_algorithm(graph=graph, start_node=edgeValueFrom)
            nodesIterator, weightPath = createGraph.get_result(previous_nodes, shortest_path, start_node=edgeValueFrom, target_node=edgeValueTo)
            if nodesIterator is None:
                showMessage("Невозможно найти путь")
                return
            text = createGraph.get_answer(nodesIterator, weightPath)
            self.gridFindPathBox.findChildren(QLabel)[2].setText(text)
            path = "simpple_path_answer.png"
            createGraph.save_image_graph(nodes, edges, path, nodesIterator)
            pixmap = QPixmap(path)
            # pixmap.scaled(50, 50, Qt.KeepAspectRatio)
            self.findChild(QLabel).setPixmap(pixmap)
            # self.img_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        else:
            showMessage("Добавьте ребра графа")

    def pressButtonAddEdge(self):
        ComboBoxEdgeFromW = self.gridEdgeBox.findChildren(QComboBox)[0]
        edgeValue1 = ComboBoxEdgeFromW.currentText()
        ComboBoxEdgeToW = self.gridEdgeBox.findChildren(QComboBox)[1]
        edgeValue2 = ComboBoxEdgeToW.currentText()
        LabelW = self.gridEdgeBox.findChild(QLineEdit)
        weightValue = LabelW.text()
        tableW = self.gridEdgeBox.findChild(QTableWidget)
        rowPosition = tableW.rowCount()
        if edgeValue1 != '' and edgeValue2 != '' and weightValue != '':
            exists = False
            for row in range(tableW.rowCount()):
                if not bool({tableW.item(row, 0).text(), tableW.item(row, 1).text()} ^ {edgeValue1, edgeValue2}):
                    exists = True
            if not exists:
                tableW.insertRow(rowPosition)
                tableW.setItem(rowPosition, 0, QTableWidgetItem(edgeValue1))
                tableW.setItem(rowPosition, 1, QTableWidgetItem(edgeValue2))
                tableW.setItem(rowPosition, 2, QTableWidgetItem(weightValue))
                LabelW.setText("")
            else:
                showMessage("Данное ребро уже добавлено")

    def pressButtonDeleteEdge(self):
        tableW = self.gridEdgeBox.findChild(QTableWidget)
        tableW.removeRow(tableW.currentRow())

    def pressButtonCreateGraph(self):
        tableW = self.gridEdgeBox.findChild(QTableWidget)
        listW = self.gridVertexBox.findChild(QListWidget)
        if listW.count() != 0:
            nodes = [listW.item(row).text() for row in  range(listW.count())]
            edges = []
            for row in range(tableW.rowCount()):
                node1 = tableW.item(row, 0).text()
                node2 = tableW.item(row, 1).text()
                try:
                    weight = int(tableW.item(row, 2).text())
                    edges.append({"node1":node1, "node2":node2, "weight":weight})
                except:
                    showMessage("Вес должен быть числом")
            path = 'simple_path.png'
            createGraph.save_image_graph(nodes, edges, path)
            pixmap = QPixmap(path)
            # pixmap.scaled(50, 50, Qt.KeepAspectRatio)
            self.findChild(QLabel).setPixmap(pixmap)
            # self.img_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        else:
            showMessage("Добавьте ребра графа")

    def parseFileGraph(self):
        reply = QMessageBox.question(self, 'Загрузить файл', 'При загрузке все веденные данные удаляться. Вы уверены, что хотите загрузить',                                                           
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            wb_patch = QFileDialog.getOpenFileName()
            lineEditW = self.gridVertexBox.findChild(QLineEdit)
            try:
                with open(rf"{wb_patch[0]}") as json_file:
                    json_data = json.load(json_file)

                listW = self.gridVertexBox.findChild(QListWidget)
                listW.clear()
                QComboBoxEdge.reset()
                for vertexName in json_data["nodes"]:
                    list_item = [listW.item(row).text() for row in  range(listW.count())]
                    if vertexName in list_item:
                        pass# showMessage("Данная вершина уже добавлена")
                    else:
                        lineEditW.setText("")
                        listW.addItem(vertexName)
                        QComboBoxEdge.addNode(vertexName)
                tableW = self.gridEdgeBox.findChild(QTableWidget)
                for _ in range(tableW.rowCount()):
                    tableW.removeRow(0)
                rowPosition = 0
                for node_edge in json_data["edges"].keys():
                    for node2_edge in json_data["edges"][node_edge].keys():
                        if node_edge != '' and node2_edge != '' and json_data["edges"][node_edge][node2_edge] != '':
                            exists = False
                            for row in range(tableW.rowCount()):
                                if not bool({tableW.item(row, 0).text(), tableW.item(row, 1).text()} ^ {node_edge, node2_edge}):
                                    exists = True
                            if not exists:
                                tableW.insertRow(rowPosition)
                                tableW.setItem(rowPosition, 0, QTableWidgetItem(node_edge))
                                tableW.setItem(rowPosition, 1, QTableWidgetItem(node2_edge))
                                tableW.setItem(rowPosition, 2, QTableWidgetItem(json_data["edges"][node_edge][node2_edge]))
                            else:
                                pass# showMessage("Данное ребро уже добавлено")
            except:
                showMessage("Проверьте исходный файл")
        else:
            pass

    def saveToFileGraph(self):
        tableW = self.gridEdgeBox.findChild(QTableWidget)
        listW = self.gridVertexBox.findChild(QListWidget)
        data = {}
        if listW.count() != 0:
            wb_patch = QFileDialog.getSaveFileName()
            data["nodes"] = [listW.item(row).text() for row in  range(listW.count())]
            edges = {}
            for row in range(tableW.rowCount()):
                node1 = tableW.item(row, 0).text()
                node2 = tableW.item(row, 1).text()
                if node1 not in edges.keys():
                    edges[node1] = {}
                edges[node1][node2] = tableW.item(row, 2).text()
            data['edges'] = edges
            if ".json" not in wb_patch[0]:
                pathFile = rf"{wb_patch[0]}.json"
            with open(pathFile, 'w') as fp:
                json.dump(data, fp)
        else:
            showMessage("Граф не создан")

if __name__ == '__main__':
    import sys
    app    = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())