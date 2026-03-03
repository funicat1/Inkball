from tkinter import *
from PIL import Image,ImageTk

class Ball:
    def __init__(self,color,x=100,y=100,vx=5,vy=5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
    def update(self,level):
        self.x += self.vx
        self.y += self.vy
        return level # the ball modifies the level
    def image(self):
        if self.color == "green":
            return greenball

ballsleft = []
balls = [
    Ball("green")
]

root = Tk()
root.title("InkBall")
menu = Menu()
img = ImageTk.PhotoImage(file='.rsrc/ICON/7.ico') # we assume the data from original inkball is here.
spritesheet = Image.open(".rsrc/BITMAP/501.bmp")
def gettile(x,y,x2,y2):
    return spritesheet.crop((x,y,x2+x,y2+y))
def filtercol(img: Image.Image,color=(255,0,255)): # filters out color pixel by pixel. BMPs are not transparent!
    img = img.convert("RGBA")
    for y in range(24):
        for x in range(24):
            # idk if its not compatible with images on different sizes.
            r,g,b,a = img.getpixel((x,y))
            if (r,g,b) == color:
                img.putpixel((x,y),(0,0,0,0))
    return img
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

greenball = ImageTk.PhotoImage(image=filtercol(gettile(1,229,24,24)))

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
        atx += 9 # letters have 2 letter spacing in inkball's spritesheet.
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
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0100000000000000000000000000000001",
    "0101010101010101010101010101010101",
    
]

root.config(menu=menu)

root.geometry("544x586")
root.resizable(False,False)
canvas = Canvas(root,width=17*32,height=586, bd=0,highlightthickness=0,background="red")
canvas.pack()
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
    for i in balls: # topbar is 42 pixels in height.
        canvas.create_image(i.x,i.y+42,anchor=NW,image=i.image())
    root.after(500,update)
    # ow my balls owch
update()
root.mainloop()