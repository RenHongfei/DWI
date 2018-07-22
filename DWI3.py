
import sys
from PyQt5.QtCore import (QByteArray, QPoint, QRectF, Qt, QPointF, QLineF)
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QGraphicsItem,
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView,
                             QHBoxLayout, QLabel, QPushButton,
                             QStyle, QVBoxLayout, QLineEdit, QGraphicsLineItem)
from PyQt5.QtGui import QFontMetrics,QTransform, QPainter, QPen, QPixmap, QImage, QBrush, QPolygonF, QPainterPath
from PyQt5.QtPrintSupport import QPrinter
import pymysql


MAC = True
try:
    from PyQt5.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False


PageSize = (1250, 893) # US Letter in points
PointSize = 10
database = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rhf950123',
    'database': 'DWI_test',
    'charset': 'utf8'
}

def get_db(setting):
    return pymysql.connect(**setting)

class GraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)


        """label = QLabel(self)
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        pixmap = QPixmap('Factory_map.png')
        pixmap = img
        """
    """
    def wheelEvent(self, event):
        #factor = 1.41 ** (-event.delta() / 240.0)
        factor = event.angleDelta().y()/120.0
        if event.angleDelta().y()/120.0 > 0:
            factor=2
        else:
            factor=0.5
        self.scale(factor, factor)"""

class BoxItem(QGraphicsItem):

    def __init__(self, position, scene, row,  style=Qt.SolidLine,
                 rect=None, matrix=QTransform()):
        super(BoxItem, self).__init__()
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable|
                      QGraphicsItem.ItemIsFocusable)
        x = position.x()
        y = position.y()
        Width = row["Width"]
        Height = row["Height"]
        #print(row["Item"])

        if rect is None:
            rect = QRectF(-10 * PointSize, -PointSize, Width, Height)
        self.rect = rect
        self.style = style

        self.setPos(x + 100, y+10)
        #self.setTransform(matrix)
        text = QGraphicsTextItem()
        text.setPlainText(row["Bin"])
        text.setPos(x, y)
        scene.addItem(self)
        scene.addItem(text)
        # self.setSelected(True)
        # self.setFocus()


    def parentWidget(self):
        return self.scene().views()[0]

    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget):
        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(2)
        brush = QBrush()
        brush.setColor(Qt.yellow)
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
        if option.state & QStyle.State_Selected:
            pen.setColor(Qt.blue)
        painter.setPen(pen)
        painter.drawRect(self.rect)


class MyArrow(QGraphicsLineItem):
    def __init__(self, scene, Source, Dest):
        super(MyArrow, self).__init__()
        Source_x = Source[0]
        Source_y = Source[1]
        Dest_x = Dest[0]
        Dest_y = Dest[1]
        self.source = QPointF(Source_x, Source_y)
        self.dest = QPointF(Dest_x, Dest_y)
        self.line = QLineF(self.source, self.dest)
        self.line.setLength(self.line.length() - 20)
        scene.addItem(self)

    def prepareGeometryChange(self):
        self.update()

    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):

        # setPen
        pen = QPen()
        pen.setWidth(2)
        pen.setJoinStyle(Qt.MiterJoin)
        QPainter.setPen(pen)

        # setBrush
        brush = QBrush()
        brush.setColor(Qt.black)
        brush.setStyle(Qt.SolidPattern)
        QPainter.setBrush(brush)

        v = self.line.unitVector()
        v.setLength(10)
        v.translate(QPointF(self.line.dx(), self.line.dy()))

        n = v.normalVector()
        n.setLength(n.length() * 0.5)
        n2 = n.normalVector().normalVector()

        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()

        QPainter.drawLine(self.line)
        QPainter.drawPolygon(p1, p2, p3)


class MainForm(QDialog):

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.filename = ""
        self.copiedItem = QByteArray()
        self.pasteOffset = 5
        self.prevPoint = QPoint()
        self.addOffset = 5
        self.borders = []

        self.printer = QPrinter(QPrinter.HighResolution)
        self.printer.setPageSize(QPrinter.Letter)

        self.view = GraphicsView()
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, PageSize[0], PageSize[1])
        self.view.setScene(self.scene)

        pixmap = QPixmap("Bin_Map_25%_59%.png")
        self.scene.addPixmap(pixmap)
        #self.view.fitInView(gfxPixItem)


        self.wrapped = [] # Needed to keep wrappers alive
        buttonLayout = QVBoxLayout()
        rpo = QLabel('RPO#', self)
        self.lineEdit = QLineEdit(self)
        buttonLayout.addWidget(rpo)
        buttonLayout.addWidget(self.lineEdit)
        for text, slot in (
                ("Add Box", self.addBox),
                ("Clear", self.clear),
                ("Quit", self.accept)):
            button = QPushButton(text)
            if not MAC:
                button.setFocusPolicy(Qt.NoFocus)
            if slot is not None:
                button.clicked.connect(slot)
            if text == "Quit":
                buttonLayout.addStretch(1)
            buttonLayout.addWidget(button)
        buttonLayout.addStretch()

        layout = QHBoxLayout()
        layout.addLayout(buttonLayout)
        layout.addWidget(self.view, 1)

        self.setLayout(layout)
        #MyArrow(self.scene)
        fm = QFontMetrics(self.font())
        self.resize(self.scene.width() + fm.width(" Delete... ") + 50,
                    self.scene.height() + 50)
        self.setWindowTitle("DWI")


    def accept(self):
        QDialog.accept(self)

    def clear(self):
        self.scene.clear()
        pixmap = QPixmap("Bin_Map_25%_59%.png")
        self.scene.addPixmap(pixmap)


    def position(self,x, y):
        return QPoint(x, y)

    def addBox(self):
        # Connect Database
        db = get_db(database)
        rpo = self.lineEdit.text()
        sql = "SELECT * FROM Compounding where RPO = %s"
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, rpo)
        count = 0
        Source = []
        Dest = None
        Out = None
        for row in cursor:
            Bin = row["Bin"]
            sql_Bin = "SELECT * FROM Location where Bin = %s"
            cursor_Bin = db.cursor(pymysql.cursors.DictCursor)
            cursor_Bin.execute(sql_Bin, Bin)
            for row_Bin in cursor_Bin:
                x = row_Bin["x"]
                y = row_Bin["y"]
                Source.append((x, y))
                BoxItem(self.position(x, y), self.scene, row_Bin)


            # Machine Bin only draw Once
            if count == 1:
                continue
            Machine = row["Machine"]
            sql_Mac = "SELECT * FROM Location where Bin = %s"
            cursor_Mac = db.cursor(pymysql.cursors.DictCursor)
            cursor_Mac.execute(sql_Mac, Machine)
            for row_Mac in cursor_Mac:
                x = row_Mac["x"]
                y = row_Mac["y"]
                Dest = (x, y)
                BoxItem(self.position(x, y), self.scene, row_Mac)
                count += 1
            Output = row["Output"]
            sql_Out = "SELECT * FROM Location where Bin = %s"
            cursor_Out = db.cursor(pymysql.cursors.DictCursor)
            cursor_Out.execute(sql_Out, Output)
            for row_Out in cursor_Out:
                x = row_Out["x"]
                y = row_Out["y"]
                Out = (x, y)
                BoxItem(self.position(x, y), self.scene, row_Out)

        for row in Source:
            MyArrow(self.scene, row, Dest)
        MyArrow(self.scene, Dest, Out)
        cursor.close()

app = QApplication(sys.argv)
form = MainForm()
rect = QApplication.desktop().availableGeometry()
form.resize(int(rect.width()), int(rect.height()))
#form.resize(2000, 1800)
form.show()
app.exec_()