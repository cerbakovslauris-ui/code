import viz
import vizshape
import vizcam
import vizact
import vizmat
import os
import random

viz.go()

# -----------------------------------
# PAMATA ZEME
# -----------------------------------
ground = vizshape.addPlane(size=(200, 200))
ground.texture(viz.addTexture('grida.jpg'))
ground.enable(viz.LIGHTING)

# -----------------------------------
# PLATFORMAS SIENA (griesti)
# -----------------------------------
platform = vizshape.addPlane(size=(200, 200), axis=vizshape.AXIS_Y)
platform.setPosition([0, 100, 0])
platform.color(viz.WHITE)
platform.alpha(0.15)
platform.disable(viz.LIGHTING)
platform.collidePlane()

# -----------------------------------
# GAISMA
# -----------------------------------
viz.setOption('viz.lightModel.ambient', [0.7, 0.7, 0.7])

sun = viz.addLight()
sun.position(0, 50, 0)
sun.direction(0, -1, 0)
sun.color([1, 1, 1])
sun.intensity(1.5)

# -----------------------------------
# LABIRINTS
# -----------------------------------
maze_path = 'mazefix.glb'
viz.MainView.collision(True)

if os.path.exists(maze_path):
    maze = viz.addChild(maze_path)
    maze.setPosition([0, 0, 50])
    maze.setScale([5, 5, 5])

# -----------------------------------
# INVENTĀRS (ekrāna teksts)
# -----------------------------------
inventory = []
inventory_text = viz.addText("Inventārs: 0 atslēgas", parent=viz.SCREEN, pos=[0.02, 0.95, 0])
inventory_text.setScale([0.8, 0.8, 0.8])

# -----------------------------------
# ATSLĒGU IZVEIDE — AR SPIN ANIMĀCIJU
# -----------------------------------
def spawn_random_object():
    x = random.uniform(-40, 40)
    z = random.uniform(10, 100)

    atslega_path = "atslega.glb"

    # Konteiners rotācijai
    container = viz.addGroup()
    container.setPosition([x, 3, z])

    # Modelis iekš konteinera
    obj = viz.addChild(atslega_path, parent=container)
    obj.setScale([0.6, 0.6, 0.6])
    obj.setEuler([90, 90, 0])

    # Spin animācija ap Y asi
    spin = vizact.spin(0,1,0,20)  # (X,Y,Z,ātrums)
    container.addAction(spin)

    # Kolīzija savākšanai
    container.collideSphere(radius=1)

    return container


# ģenerē 3 atslēgas
objects = []
for i in range(3):
    new_obj = spawn_random_object()
    if new_obj:
        objects.append(new_obj)

# -----------------------------------
# ATSLĒGU SAVĀKŠANA (ROTĀCIJA VĀR TO NAV VAJADZĪGA)
# -----------------------------------
def updateKeys():
    global inventory
    player_pos = viz.MainView.getPosition()

    for obj in objects[:]:
        key_pos = obj.getPosition()
        dist = vizmat.Distance(player_pos, key_pos)

        # Ja spēlētājs pietuvojas
        if dist < 2:
            inventory.append("atslega")
            inventory_text.message("Inventārs: {} atslēgas".format(len(inventory)))
            obj.remove()
            objects.remove(obj)

# update cikls
vizact.ontimer(0, updateKeys)

# -----------------------------------
# CAMERA / WALK MODE
# -----------------------------------
walkNav = vizcam.WalkNavigate()
walkNav.speed = 15.0
viz.cam.setHandler(walkNav)

def lift_camera():
    platform.disable(viz.COLLISION)
    pos = viz.MainView.getPosition()

    if int(pos[1]) == 101:
        viz.MainView.setPosition([pos[0], 1.82, pos[2]])
    else:
        viz.MainView.setPosition([pos[0], 100, pos[2]])

    platform.enable(viz.COLLISION)

def onKeyDown(key):
    if key == 'b':
        lift_camera()
    if key == 'p':
        print(viz.MainView.getPosition())

viz.callback(viz.KEYDOWN_EVENT, onKeyDown)

# sākuma pozīcija
viz.MainView.setPosition([2.5, 3.0, -5])

viz.mouse.setVisible(False)
