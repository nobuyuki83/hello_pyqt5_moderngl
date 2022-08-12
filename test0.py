import moderngl
from PyQt5 import QtOpenGL, QtWidgets, QtCore
import numpy as np

class QGLControllerWidget(QtOpenGL.QGLWidget):

    def __init__(self, parent=None):
        self.parent = parent        
        #super(QGLControllerWidget, self).__init__(parent)
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super(QGLControllerWidget, self).__init__(fmt, None)        

    def initializeGL(self):
        self.ctx = moderngl.create_context()

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 Mvp;
                in vec3 in_position;
                in vec3 in_normal;
                out vec3 v_vert;
                out vec3 v_norm;
                void main() {
                    v_vert = in_position;
                    v_norm = in_normal;
                    gl_Position = Mvp * vec4(in_position, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform vec4 Color;
                in vec3 v_vert;
                in vec3 v_norm;
                out vec4 f_color;
                void main() {
                    vec3 color = Color.rgb * Color.a;
                    f_color = vec4(color * v_norm.z, 1.0);
                }
            '''
        )

        self.color = self.prog['Color']
        self.mvp = self.prog['Mvp']
        self.mesh = None
        self.center = np.zeros(3)
        self.scale = 1.0

        index_buffer = self.ctx.buffer(
            np.array([0,1,2], dtype="u4").tobytes())
        vao_content = [
            (self.ctx.buffer(
                np.array([-1,-1,0, +1,-1,0, +1,+1,0], dtype="f4").tobytes()),
                '3f', 'in_position'),
            (self.ctx.buffer(
                np.array([0,0,+1, 0,0,+1, 0,0,+1], dtype="f4").tobytes()),
                '3f', 'in_normal')
        ]
        self.vao = self.ctx.vertex_array(
                self.prog, vao_content, index_buffer, 4,
            )

    def paintGL(self):
        self.ctx.clear(1.0, 0.0, 1.0)
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.color.value = (0.0, 0.0, 1.0, 1.0)
        self.mvp.value = (
            1., 0., 0., 0., 
            0., 1., 0., 0.,
            0., 0., 1., 0.,
            0., 0., 0., 1.)
        self.vao.render()

    def resizeGL(self, width, height):
        width = max(2, width)
        height = max(2, height)
        self.ctx.viewport = (0, 0, width, height)
        return

    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            pass

    def mouseReleaseEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            pass

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            pass


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.resize(640, 480)
        self.setWindowTitle('Mesh Viewer')
        self.gl = QGLControllerWidget(self)

        self.setCentralWidget(self.gl)
        self.menu = self.menuBar().addMenu("&File")
        self.menu.addAction('&Open', self.openFile)

        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # period, in milliseconds
        timer.timeout.connect(self.gl.updateGL)
        timer.start()

    def openFile(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open file', '', "Mesh files (*.obj *.off *.stl *.ply)")
        self.gl.set_mesh(mesh)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = MainWindow()

    win.show()
    app.exec()