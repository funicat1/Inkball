from tkinter import *
from PIL import Image,ImageTk
import math

def unit(x, y):
    length = math.sqrt(x*x + y*y)
    if length == 0:
        raise ValueError("zero vector has no direction")
    return (x / length, y / length)

def scale(vec,by):
    return tuple([i*by for i in vec])
class Ball:
    def __init__(self,color,x=100,y=100,vx=2,vy=2):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = 12
    def update_tiles(self, level):
        # move ball
        self.x += self.vx
        self.y += self.vy

        # tiles ball could be overlapping
        min_tx = int((self.x - self.radius) // 32)
        max_tx = int((self.x + self.radius) // 32)
        min_ty = int((self.y - self.radius) // 32)
        max_ty = int((self.y + self.radius) // 32)

        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                if level[ty][tx] == 1:
                    # tile rectangle
                    rx, ry, rw, rh = tx*32, ty*32, 32, 32
                    cx, cy = self.closest_point_on_rect(rx, ry, rw, rh)
                    dx = self.x - cx
                    dy = self.y - cy
                    dist2 = dx*dx + dy*dy
                    if dist2 < self.radius*self.radius:
                        dist = math.sqrt(dist2) or 0.001
                        nx = dx / dist
                        ny = dy / dist
                        dot = self.vx*nx + self.vy*ny
                        self.vx -= 2*dot*nx
                        self.vy -= 2*dot*ny
                        overlap = self.radius - dist
                        self.x += nx * overlap
                        self.y += ny * overlap

    # helper: closest point on a rectangle
    def closest_point_on_rect(self, rx, ry, rw, rh):
        closest_x = min(max(self.x, rx), rx + rw)
        closest_y = min(max(self.y, ry), ry + rh)
        return closest_x, closest_y

    # ball-ball collision
    def collide_with(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dist2 = dx*dx + dy*dy
        radius_sum = self.radius + other.radius
        if dist2 < radius_sum*radius_sum:
            dist = math.sqrt(dist2) or 0.001
            nx = dx / dist
            ny = dy / dist
            # velocity along normal
            p = 2 * ((self.vx*nx + self.vy*ny) - (other.vx*nx + other.vy*ny)) / 2
            self.vx -= p * nx
            self.vy -= p * ny
            other.vx += p * nx
            other.vy += p * ny
            # push apart
            overlap = (radius_sum - dist) / 2
            self.x -= nx * overlap
            self.y -= ny * overlap
            other.x += nx * overlap
            other.y += ny * overlap
    def update(self, level, balls):
        self.update_tiles(level)
        for other in balls:
            if other is not self:
                self.collide_with(other)
    def image(self):
        return balldict[self.color]

spritesheet = Image.open(".rsrc/BITMAP/501.bmp")
def gettile(x,y,x2,y2):
    return spritesheet.crop((x,y,x2+x,y2+y))
def filtercol(img: Image.Image): # filters out color pixel by pixel. BMPs are not transparent! Only for balls.
    img = img.convert("RGBA")
    for y in range(24):
        for x in range(24):
            r,g,b,a = img.getpixel((x,y))
            _,a,_ = spritesheet.getpixel((x+1,y+277))
            img.putpixel((x,y),(r,g,b,a))
    return img

root = Tk()

balldict = {}

# THE BALL DICTIONARY
for c,i in enumerate(["white", "orange", "blue", "green", "yellow"]):
    y = 157 + (c*24)
    balldict[i] = ImageTk.PhotoImage(image=filtercol(gettile(1,y,24,24)))

ballsleft = []
balls = [
    Ball("white",100,100+i)
    for i in range(0,64,24)
]

root.title("InkBall")
menu = Menu()
img = ImageTk.PhotoImage(file='.rsrc/ICON/7.ico') # we assume the data from original inkball is here.

blanktile = ImageTk.PhotoImage(image=gettile(1,1,32,32))
whitetile = ImageTk.PhotoImage(image=gettile(99,1,32,32))
topbarpart1 = ImageTk.PhotoImage(image=gettile(264,236,104,42))
topbarpart2 = ImageTk.PhotoImage(image=gettile(1,332,341,42))
topbarpart3 = ImageTk.PhotoImage(image=gettile(264,279,101,42))

fieldleftpart = gettile(264,176,2,19) # Isnt used in canvas bliting, so no photoimage
fieldmiddlepart = gettile(268,176,1,19)
fieldrightpart = gettile(370,176,2,19)

redfieldleftpart = gettile(264,216,2,19)
redfieldmiddlepart = gettile(268,216,1,19)
redfieldrightpart = gettile(378,216,3,19)

root.iconphoto(False, img)
menu.add_cascade(label="Game")
menu.add_cascade(label="Difficulty")
menu.add_cascade(label="Help")

def hextolist(l):
    out = []
    for i in range(0,len(l),2):
        out.append(int(l[i]+l[i+1],16))
    return out

def createtextsheet(atx,aty,reference):
    # Creates a text spritesheet 
    out = {}
    for i in reference:
        letter = ImageTk.PhotoImage(image=gettile(atx,aty,9,9))
        out[i] = letter
        atx += 9 # yeah i was shocked too
    return out

def rendertext(canvas: Canvas,x,y,text,sheet,textdir="left"): # i hate vscode
    # textdir can be "left", "right", or "center".
    text = str(text)
    if textdir == "right":
        text = text[::-1]
    if textdir == "center":
        x -= int((len(text) * 9)/2)
    for i in text:
        canvas.create_image(x,y,anchor=W,image=sheet[i],tag="erase") # the erase tag gets erased on every update (not frame), good for things that need updates when a value gets changed
        if textdir == "right":
            x -= 9
        else:
            x += 9

def getcenter(x,y,w,h):
    return int(x+w/2),int(y+h/2)


def createfield(width,red=False):
    # This creates a static image of a field. The method im using here is really resource intensive, but it does its job, it doesnt redraw every frame anyway
    width = width - 4 # account for left and right part being 2 pixels in width.
    field = Image.new("RGB",(4+width,19))
    if not red:
        field.paste(fieldleftpart,(0,0))
        for x in range(width): # Oh boy...
            field.paste(fieldmiddlepart,(2+x,0))
        field.paste(fieldrightpart,(2+width,0))
    else:
        field.paste(redfieldleftpart,(0,0))
        for x in range(width): # Oh boy...
            field.paste(redfieldmiddlepart,(2+x,0))
        field.paste(redfieldrightpart,(1+width,0)) # theres like a little shade on the bottom right, so we are overlapping
    return field # Never again.
    

def hextolist2d(leveldat):
    out = []
    for y,line in enumerate(leveldat):
        out.append(hextolist(line))
    return out

levelfield = ImageTk.PhotoImage(image=createfield(27)) # ?
scorefield = ImageTk.PhotoImage(image=createfield(63)) # not sure
timefield = ImageTk.PhotoImage(image=createfield(45,red=True)) # surenot
fieldtextsheet =      createtextsheet(273,181,"0123456789")
greenfieldtextsheet = createtextsheet(273,201,"0123456789") 
redfieldtextsheet =   createtextsheet(273,221,"0123456789-") # theres a - in the spritesheet, idk why. 
bartextsheet =        createtextsheet(273,166,"0123456789+") # a plus. really?


level = 0
score = 55555
time = 98
blocks = 0

# grid size - 17x17
# objects are HEX digits, why hex? having 00-99 is awkward.
leveldata = [
    "0101010101010101010101010101010101",
    "0100000000000000000000000000010001",
    "0100000000000000000000000000010001",
    "0100000000000000000000000000010001",
    "0100000000000000000000000000010001",
    "0100000000000000000000000000010001",
    "0100000000000000000000000000010001",
    "0100000000000000000000000000010001",
    "0100000000000000000000010000000001",
    "0100000000000000000000010000000001",
    "0100000000000000000000010000000001",
    "0101010101010000000000010000000001",
    "0100000000000000000000010000000001",
    "0100000000000000000000010000000001",
    "0100000000000000000000010000000001",
    "0100000000000000000000010000000001",
    "0101010101010101010101010101010101",
    
]

root.config(menu=menu)

root.geometry("544x586")
root.resizable(False,False)
canvas = Canvas(root,width=17*32,height=586, bd=0,highlightthickness=0,background="red")
canvas.pack(fill=X)
canvas.create_image(0,0,anchor=NW,image=topbarpart1)
canvas.create_image(104,0,anchor=NW,image=topbarpart2)
canvas.create_image(104+341,0,anchor=NW,image=topbarpart3)
canvas.create_image(341,13,anchor=NW,image=levelfield)
canvas.create_image(379,13,anchor=NW,image=scorefield)
canvas.create_image(496,13,anchor=NW,image=timefield)

levelfieldcenter = getcenter(341,13,27,19)
scorefieldcenter = getcenter(379,13,63,19)
timefieldcenter  = getcenter(496,13,45,19)
blockcenter      = getcenter(460,18,7,9) # ???

rendertext(canvas,*levelfieldcenter, level,fieldtextsheet,"center")
rendertext(canvas,*scorefieldcenter,str(score).zfill(5),greenfieldtextsheet,"center")
rendertext(canvas,*timefieldcenter,str(time).zfill(3),redfieldtextsheet,"center")
rendertext(canvas,*blockcenter,str(blocks),bartextsheet,"center")

for y,line in enumerate(leveldata):
    for x,col in enumerate(hextolist(line)):
        if col == 0:
            canvas.create_image(x*32,(y*32)+42,anchor=NW,image=blanktile)
        elif col == 1:
            canvas.create_image(x*32,(y*32)+42,anchor=NW,image=whitetile)

def update():
    global level
    canvas.delete("upd")
    for i in balls: # topbar is 42 pixels in height.
        canvas.create_image(i.x-12,i.y-12+42,anchor=NW,image=i.image(),tag="upd")
        level2d = hextolist2d(leveldata)
        i.update(level2d, balls)
    root.after(10,update)
    # ow my balls owch
update()
root.mainloop()