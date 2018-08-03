
import sys
from PyQt5.QtCore import (QByteArray, QPoint, QRectF, Qt, QPointF, QLineF, QThread, pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QGraphicsItem,
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView,
                             QHBoxLayout, QLabel, QPushButton,
                             QStyle, QVBoxLayout, QLineEdit, QGraphicsLineItem, QTableWidget,QTableWidgetItem)
from PyQt5.QtGui import QFontMetrics,QTransform, QPainter, QPen, QPixmap,QBrush
from PyQt5.QtGui import QFont
from PyQt5.QtPrintSupport import QPrinter
import pymysql
import os
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import matplotlib.pyplot as plt
import numpy as np

MAC = True
try:
    from PyQt5.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False

prefix = ''
logpath = os.getcwd() + '/mysql.log'

PageSize = (1250, 893) # US Letter in points
PointSize = 10
database = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rhf950123',
    'database': 'DWI',
    'charset': 'utf8'
} #数据库连接信息




#连接数据库
def get_db(setting):
    return pymysql.connect(**setting)

#绘图区
class GraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)

#Summary表格
class MyTable(QTableWidget):
    def __init__(self, parent=None):
        super(MyTable, self).__init__(parent)
        db = get_db(database)
        #获取Summary数据库信息
        sql = "SELECT * FROM Summary"
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        #计算获取的条数
        n = cursor.rowcount
        self.setWindowTitle("Summary") #设置表头
        self.setFont(QFont( "Times", 25)) #设置字体
        self.resize(500, 700) #设置表格大小
        self.setColumnCount(2) #设置两列
        self.setRowCount(n) #设置行数为数据库行数
        self.setColumnWidth(0, 200) #设置宽度
        i = 0
        while i < n:
            print(i)
            self.setRowHeight(i, 80) #设置每行宽度
            i +=1

        row_n =0
        # 添加表格的文字内容.
        for row in cursor:
            RPO = row["RPO"]
            Status = row["Status"]
            self.setItem(row_n, 0, QTableWidgetItem(RPO))
            self.setItem(row_n, 1, QTableWidgetItem(Status))
            row_n +=1
        self.setHorizontalHeaderLabels([ "RPO", "Status"]) #设置每一列标题
        cursor.close()
        db.close()

#Location方块
class BoxItem(QGraphicsItem):

    def __init__(self, position, scene, row,  style=Qt.SolidLine,
                 rect=None, matrix=QTransform()):
        super(BoxItem, self).__init__()
        self.setFlags(QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsMovable|
                      QGraphicsItem.ItemIsFocusable)
        #设置方块横纵坐标
        x = position.x()
        y = position.y()
        #设置方块长宽
        Width = row["Width"]
        Height = row["Height"]
        #print(row["Item"])

        if rect is None:
            rect = QRectF(-10 * PointSize, -PointSize, Width, Height)
        self.rect = rect
        self.style = style

        #绘制方块位置
        self.setPos(x + 100, y+10)
        #self.setTransform(matrix)

        #设置label信息
        text = QGraphicsTextItem()
        text.setPlainText(row["Bin"])
        text.setPos(x, y)
        scene.addItem(self)
        scene.addItem(text)


    def parentWidget(self):
        return self.scene().views()[0]

    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    #绘制方块属性设置
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

#绘制箭头连线
class MyArrow(QGraphicsLineItem):
    def __init__(self, scene, Source, Dest):
        super(MyArrow, self).__init__()
        #设置起点x，y
        Source_x = Source[0]
        Source_y = Source[1]
        #设置终点x，y
        Dest_x = Dest[0]
        Dest_y = Dest[1]
        #绘制连线
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

        #绘制终点箭头
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

#监控mysql日志更新
class Monitor(QThread):
    update = pyqtSignal()
    def __init__(self, event, rpo):
        QThread.__init__(self)
        #连接数据库日志文件
        self.popen = subprocess.Popen('tail -f /Users/hongfeiren/PycharmProjects/DWI/mysql.log', stdout=subprocess.PIPE,
                                 shell=True)
        self.rpo = rpo
    def run(self):
        nt = 0
        try:
            while self.popen.poll() == None:
                #对日志文件内容进行筛选
                insert = "INSERT INTO"
                line = str(self.popen.stdout.readline().strip())

                if insert in line:
                    if self.rpo in line:
                        print(line)
                        line = line.split()
                        line = str(line[10:])
                        line = line.replace('(', '')
                        line = line.replace(')', '')
                        line = line.replace(',', '')
                        line = line.replace("'", "")
                        line = line.replace('\\', '')
                        line = line.replace('[', '')
                        line = line.replace(']', '')
                        line = line.replace('"', '')
                        line = line.split()
                        print(line)
                        print(type(line))
                        #当获取到需要信息后，更新绘图，下边这里可能有Bug
                        nt+=1
                        if nt > 1:
                            self.update.emit()

        except KeyboardInterrupt:
            os.remove('/Users/hongfeiren/PycharmProjects/DWI/mysql.log')


class MainForm(QDialog):

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        #设置数据库日志文件
        db = get_db(database)
        cur = db.cursor()
        cur.execute('set global general_log = on')
        db.commit()
        cur.execute('set global log_output = \'file\'')
        db.commit()
        cur.execute('set global general_log_file=' + '\'' + logpath + '\'')
        db.commit()
        db.close()

        self.Receive_Email = None
        self.m = None
        self.n = None

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



        #设置地图文件
        pixmap = QPixmap("Bin_Map_25%_59%.png")
        self.scene.addPixmap(pixmap)


        self.wrapped = [] # Needed to keep wrappers alive
        buttonLayout = QVBoxLayout()
        #添加输入Email label和输入框
        eml = QLabel('TO Email Address', self)
        self.lineEdit1 = QLineEdit(self)
        buttonLayout.addWidget(eml)
        buttonLayout.addWidget(self.lineEdit1)

        #添加输入RPO label和输入框
        rpo = QLabel('RPO#', self)
        self.lineEdit = QLineEdit(self)
        buttonLayout.addWidget(rpo)
        buttonLayout.addWidget(self.lineEdit)

        #添加Button 和对应的功能
        for text, slot in (
                ("Send Email", self.sendEmail),
                ("Add Box", self.addBox),
                ("Clear", self.clear),
                ("Summary", self.Summary),
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

        #设置接收Pick结果邮箱地址
        rcv = QLabel('Receive Email Address', self)
        self.lineEdit2 = QLineEdit(self)
        self.Confirm = QPushButton("Confirm")

        self.Confirm.clicked.connect(self.setRec)
        buttonLayout.addWidget(rcv)
        buttonLayout.addWidget(self.lineEdit2)
        buttonLayout.addWidget(self.Confirm)

        layout = QHBoxLayout()
        layout.addLayout(buttonLayout)
        layout.addWidget(self.view, 1)

        self.setLayout(layout)
        #MyArrow(self.scene)
        fm = QFontMetrics(self.font())
        self.resize(self.scene.width() + fm.width(" Delete... ") + 50,
                    self.scene.height() + 50)
        self.setWindowTitle("DWI")

    #设置接收邮件地址
    def setRec(self):
        self.Receive_Email = self.lineEdit2.text()

    #显示Summary表格
    def Summary(self):
        self.myTable = MyTable()
        self.myTable.show()

    def accept(self):
        QDialog.accept(self)

    #重制绘图区
    def clear(self):
        self.scene.clear()
        pixmap = QPixmap("Bin_Map_25%_59%.png")
        self.timer_thread.quit()
        self.scene.addPixmap(pixmap)

    #转换x，y为 QPoint
    def position(self, x, y):
        return QPoint(x, y)
    #更新绘图区
    def Update(self):
        self.clear()
        print("update Success")
        self.addBox()

    #发送Pick邮件
    def sendEmail(self):
        #当发送Pick邮件时同时在Summary中新增记录，设置状态为"Waiting"
        db = get_db(database)
        rpo = self.lineEdit.text()
        sql = "INSERT INTO `Summary` (`RPO`, `Status`) VALUES (%s, 'Waiting')"
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql, rpo)
            db.commit()
        except:
            pass
        cursor.close()
        db.close()


        my_sender = 'hongfei.ren@qq.com'  # 发件人邮箱账号
        my_pass = 'qxqkxvltwdzhcahe'  # 发件人邮箱密码
        my_user = self.lineEdit1.text()

        def mail():
            #获取发送邮件内容
            db = get_db(database)
            rpo = self.lineEdit.text()
            sql = "SELECT * FROM Pick where RPO = %s"
            cursor = db.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql, rpo)
            content =''
            for row in cursor:
                RPO = row["RPO"]
                Item = row["Item"]
                Bin = row["Bin"]
                Quantity = row["Quantity"]
                content = content + "RPO:"+ RPO + "  " + "Item:" + Item + "  "+ "Bin:" + Bin + "  "+ "Quantity" + Quantity + "\n"

            ret = True
            try:
                msg = MIMEText(content, 'plain', 'utf-8')
                msg['From'] = formataddr(["Please_Pick", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
                msg['To'] = formataddr(["Warehouse", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
                msg['Subject'] = "Please Pick" + rpo  # 邮件的主题，也可以说是标题

                server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
                server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
                server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
                server.quit()  # 关闭连接
            except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
                ret = False
            return ret
            cursor.close()
            db.close()

        ret = mail()
        if ret:
            print("Success")
        else:
            print("Fail")

    # 发送完成邮件
    def FinishEmail(self, rpo):
        # 当Pick完成时，更新Summary数据库对应状态为 "Done"
        print("FinishEMail")
        db = get_db(database)
        RPO = rpo
        sql = "UPDATE `Summary` SET `Status`='Done' WHERE `RPO`= %s;"
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql, rpo)
            db.commit()
        except:
            pass
        cursor.close()
        db.close()

        my_sender = 'hongfei.ren@qq.com'  # 发件人邮箱账号
        my_pass = 'qxqkxvltwdzhcahe'  # 发件人邮箱密码
        print(self.Receive_Email)
        if self.Receive_Email is not None:
            my_user = self.Receive_Email
        else:
            my_user = "hren008@ucr.edu"


        def mail():
            ret = True
            try:
                msg = MIMEText(RPO + "  Pick Finished", 'plain', 'utf-8')
                msg['From'] = formataddr(["Warehouse", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
                msg['To'] = formataddr(["Supervisor", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
                msg['Subject'] = "Pick Finished" + rpo  # 邮件的主题，也可以说是标题

                server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
                server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
                server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
                server.quit()  # 关闭连接
            except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
                ret = False
            return ret

        ret = mail()
        if ret:
            print("Success")
        else:
            print("Fail")

    #绘制Location方块
    def addBox(self):
        # Connect Database
        print("addbox")
        db = get_db(database)
        rpo = self.lineEdit.text()
        # 获取已经Pick材料个数
        sql = "SELECT * FROM Compounding where RPO = %s"
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, rpo)
        count = 0
        Source = []
        Dest = None
        Out = None
        self.n = str(cursor.rowcount)
        # 获取需要Pick材料个数
        sql1 = "SELECT * FROM Pick where RPO = %s"
        cursor1 = db.cursor(pymysql.cursors.DictCursor)
        cursor1.execute(sql1, rpo)
        self.m = str(cursor1.rowcount)
        print(self.m)
        print(self.n)


        #添加 已经Pick个数与需要Pick个数统计
        CurrentQuantity = QGraphicsTextItem()
        CurrentQuantity.setPlainText(self.n + '/' + self.m)
        CurrentQuantity.setPos(245, 845)

        CurrentQuantity.setFont(QFont("Timers",35))
        self.scene.addItem(CurrentQuantity)


        for row in cursor:
            #对每一行记录绘制方块
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
            #绘制机器方块，只绘制一次
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
            #绘制输出方块，只绘制一次
            Output = row["Output"]
            sql_Out = "SELECT * FROM Location where Bin = %s"
            cursor_Out = db.cursor(pymysql.cursors.DictCursor)
            cursor_Out.execute(sql_Out, Output)
            for row_Out in cursor_Out:
                x = row_Out["x"]
                y = row_Out["y"]
                Out = (x, y)
                BoxItem(self.position(x, y), self.scene, row_Out)
        #绘制对应箭头
        for row in Source:
            MyArrow(self.scene, row, Dest)
        MyArrow(self.scene, Dest, Out)

        #如果已经Pick数量与需要Pick数量相等，发送邮件并更新绘图区
        if self.m == self.n:
            self.FinishEmail(rpo)

        cursor.close()
        cursor1.close()
        db.close()

        #启动监视日志文件线程
        self.timer_thread = Monitor(self, rpo)
        self.timer_thread.update.connect(self.Update)
        self.timer_thread.start()

app = QApplication(sys.argv)
form = MainForm()
rect = QApplication.desktop().availableGeometry()
form.resize(int(rect.width()), int(rect.height()))
#form.resize(2000, 1800)
form.show()
app.exec_()