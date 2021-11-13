import random
import struct

from collections import namedtuple # es para nombrar cada elemento de un array 



# esto lo hace mas legible
V2 = namedtuple('Point2D', ['x', 'y'])
V3 = namedtuple('Point3D', ['x', 'y', 'z'])


def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    # short
    return struct.pack('=h', w)

def dword(w):
    # long
    return struct.pack('=l', w)



def color(r, g, b):
    return bytes([b, g, r])

BLACK =  color(0, 0, 0)
WHITE =  color(255, 255, 255)

class Renderer(object):
    def glinit():
        r =  Renderer(1024, 768)

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Esta variable le da color al punto
        self.current_color = WHITE

        self.clear()

    def clear(self):
        self.framebuffer = [
            [BLACK for x in range(self.width)]
            for y in range(self.height)
        ]

    def write(self, filename):
        f = open(filename, 'bw')

        # File header (14)
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + 3*(self.width*self.height)))
        f.write(dword(0))
        f.write(dword(14 + 40))

        # Info header (40)
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(3*(self.width*self.height)))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        # Bitmap (se recorre el framebuffer completo, para meter los bytes en un array de 4)
        for y in range(self.height):
            for x in range(self.width):
                f.write(self.framebuffer[y][x])

        f.close()
        
    # --------------- LINE ---------------
      # ALGORITMO DE DIXTRA, VER BRESENHAM ALGORITHM 
    def line(self, x0, y0, x1, y1):
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        # en el caso que no funcione la linea, steep hace que se cambien los valores de y a x. Le da la vuelta
        steep = dy > dx
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        # ahora se reemplatea la pendiente.
            dy = abs(y1 - y0)
            dx = abs(x1 - x0)
    
        offset = 0 # offset = 0 * 2 * dx
        
        threshold = dx # threshold = 0.5 * 2 * dx
        y = y0

        points = []
        for x in range(x0, x1):
            #se agrega esto para que este en la direccion correcta
            if steep:
                points.append((y, x))
            else:
                points.append((x, y))
            
            offset += 2 * dy # offset += (dy/dx) * 2 * dx
            
            if offset >= threshold:
                y += 1 if y0 < y1 else -1
                threshold += 2 * dx # threshold += 1 * 2 * dx

        for point in points:
            r.point(*point)

    # --------------- LINE ---------------        

    def render(self):
        self.write('a.bmp')

    # Se agregara un punto 
    def point(self, x, y, color = None):
        self.framebuffer[y][x] = color or self.current_color

    # esta es una funcion que reciba un vertice como parametro que se transforma en X y Y
    def transform(self, v, translate, scale):
        # se tiene que retornar V2 (uno de los objetos de antes)
        return V2(
            round((v[0] + translate[0]) * scale[0]),
            round((v[1] + translate[1]) * scale[1])
        )
        
# este es un triangle wirefram
    def triangle_wireframe(self, A, B, C):
        self.line(A, B)
        self.line(B, C)
        self.line(C, A)

# funcion que recibe 3 vertices y dibuja un triangulo
    def triangle(self, A, B, C, color = None):
        '''
        self.line(A, B)
        self.line(B, C)
        self.line(C, A)
        '''
        # agarra y reordenar los puntos
        # hay que intentar que en A se encuentre el valor mas pequeño

        if A.y > B.y :
            A, B = B, A
            # si A es mayor que C, se cambian uno a otro
            # el cambio de vertices garantiza que A se quede con el menor valor
        if A.y > B.y :
            A, B = B, A
        if A.y > C.y :
            A, C = C, A
        if B.y > C.y :
            B, C = C, B


        dx_ac = C.x - A.x
        dy_ac = C.y - A.y

        # que pasa si el triangulo es plano??
        if dy_ac == 0:
            return
        # pendiente inversa
        mi_ac = dx_ac/dy_ac


        dx_ab = B.x - A.x
        dy_ab = B.y - A.y

        # que pasa si el triangulo es plano??
        if dy_ab != 0:
            # pendiente inversa
            mi_ab = dx_ab/dy_ab

    # todos los rangos no incluyem el ultimo valor, entonces para incluirlo se agrega el +1
            for y in range(A.y, B.y + 1):
                xi = round(A.x - mi_ac *(A.y - y))
                xf = round(A.x - mi_ab *(A.y - y))
                # el verde no funciona porque el inicial debe ser de A a C, se voltea
                if xi > xf:
                    xi, xf = xf, xi
                #se recorre verticalmente la linea desde el xi
                for x in range(xi, xf + 1):
                    self.point(x, y, color)
                # Se hace un xf en base a la linea de A a B

        # Ahora solo hace falta llenar lo que va de B a C  
        dx_bc = C.x - B.x
        dy_bc = C.y - B.y
        # que pasa si el triangulo es plano??
        if dy_bc:
            # pendiente inversa
            mi_bc = dx_bc/dy_bc

            for y in range(B.y, C.y + 1):
                # xi sigue siendo la misma porque va de A a C
                xi = round(A.x - mi_ac *(A.y - y))
                # xf si cambia porque ahora va de B a C
                xf = round(B.x - mi_bc *(B.y - y))
            
            # ahora se hace la linea horizontal 
                if xi > xf:
                    xi, xf = xf, xi
                for x in range(xi, xf + 1):
                    self.point(x, y, color)


    def pol_fill(self, vertex):
        self.points = []
        for i in range(len(vertex) - 1):
            self.line(vertex[i][0], vertex[i][1], vertex[i+1][0], vertex[i + 1][1])
            i += 1
        lin = self.line(vertex[i][0], vertex[i][1], vertex[0][0], vertex[0][1])
        
        for i in self.points:
            if lin < range(self.height) and lin >= range(self.height):
                    if lin < range(self.width) and lin >= range(self.width):
                        self.point(self.x, self.y, color)

                        

poligono1 = [(165, 380), (185, 360), (180, 330), (207, 345), (233, 330), (230, 360), (250, 380), (220, 385), (205, 410), (193, 383)]
poligono2 = [(321, 335), (288, 286), (339, 251), (374, 302)]
poligono3 = [(377, 249), (411, 197), (436, 249)]
poligono4 = [(413, 177), (448, 159), (502, 88), (553, 53), (535, 36), (676, 37), (660, 52),
(750, 145), (761, 179), (672, 192), (659, 214), (615, 214), (632, 230), (580, 230),
(597, 215), (552, 214), (517, 144), (466, 180)]
poligono5 = [(682, 175), (708, 120), (735, 148), (739, 170)]






r =  Renderer(800, 600)

r.current_color = color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) )

r.pol_fill(poligono1)
r.pol_fill(poligono2)
r.pol_fill(poligono3)
r.pol_fill(poligono4)
r.pol_fill(poligono5)

# r.triangle(V2(10,70), V2(50, 160), V2(70, 80))
# r.current_color = color(255, 255, 255)
# r.triangle(V2(180, 50), V2(150, 1), V2(70, 180))
# r.current_color = color(0, 255, 0)
# r.triangle(V2(180, 150), V2(120, 160), V2(130, 180))
# r.current_color = color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) )
# r.load('./models/cube2.obj', [5, 2], [100, 100])

r.render()

# se puede empezar desde abajo, llenandolo con lineas de lado a lado