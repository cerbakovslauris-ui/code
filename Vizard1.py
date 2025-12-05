import viz
import vizshape
import vizcam
import vizact
import vizmat
import os
import random
import math

viz.go()

# ===== GAISMA =====
flashlight = viz.addLight()
flashlight.enable()
flashlight.intensity(3.0)
flashlight.color(1,1,1)
flashlight.ambient(0.1,0.1,0.1)

def updateFlashlight():
    pos = viz.MainView.getPosition()
    flashlight.position(pos[0], pos[1], pos[2])

vizact.ontimer(0, updateFlashlight)

# ===== SKAŅA =====
pickup_sound = viz.addAudio('pop.mp3')

scary_sounds = [
    viz.addAudio('scary-sound-effect-359877.mp3'),
    viz.addAudio('scary-transition-401717.mp3'),
    viz.addAudio('scary-sound-410559.mp3')
]

def playRandomScarySound():
    sound = random.choice(scary_sounds)
    volume = random.uniform(0.4, 1.0)
    sound.volume(volume)
    sound.play()
    next_time = random.uniform(10.0, 60.0)
    vizact.ontimer2(next_time, 1, playRandomScarySound)

vizact.ontimer2(10.0, 1, playRandomScarySound)

# ===== HUD =====
key_icon = viz.addTexQuad(parent=viz.SCREEN)
key_icon.texture(viz.addTexture('2datslega.png'))
key_icon.setPosition([0.08, 0.90, 0])
key_icon.setScale([1.5, 1.5, 1])

key_counter = viz.addText("0", parent=viz.SCREEN)
key_counter.setPosition([0.17, 0.85, 0])
key_counter.setScale([1.2, 1.2, 1])

# ===== STAMINA TEXT =====
stamina_text = viz.addText("Stamina: 100%", parent=viz.SCREEN)
stamina_text.setPosition([0.01, 0.80, 0])
stamina_text.setScale([0.5,0.5,0.5])
stamina_text.color(viz.WHITE)

# ===== PLATFORMAS =====
ground = vizshape.addPlane(size=(200, 200))
ground.texture(viz.addTexture('grida.jpg'))
ground.enable(viz.LIGHTING)

platform = vizshape.addPlane(size=(200, 200), axis=vizshape.AXIS_Y)
platform.setPosition([0, 100, 0])
platform.color(viz.WHITE)
platform.alpha(0.15)
platform.disable(viz.LIGHTING)
platform.collidePlane()

# ===== LABIRINTS =====
maze_path = 'mazefix (2).osgb'
viz.MainView.collision(True)
maze = viz.addChild(maze_path)
maze.setPosition([0, 0, 120])
maze.setScale([5, 5, 5])
maze.enable(viz.LIGHTING)

# ===== DURVIS =====
door = maze.getChild('Door')
DOOR_SCALE = [0.75, 1, 0.75]
DOOR_OFFSET = [-4.3, -2.5, -0.07]
orig_pos = door.getPosition(viz.ABS_GLOBAL)
orig_euler = door.getEuler(viz.ABS_GLOBAL)
final_pos = [
    orig_pos[0] + DOOR_OFFSET[0],
    orig_pos[1] + DOOR_OFFSET[1],
    orig_pos[2] + DOOR_OFFSET[2]
]
door.setPosition(final_pos, viz.ABS_GLOBAL)
door.setEuler(orig_euler, viz.ABS_GLOBAL)
door.setScale(DOOR_SCALE)
door_removed = False

def removeDoor():
    global door_removed
    if door_removed: return
    door.remove()
    door_removed = True

# ===== ATSLĒGU SISTĒMA =====
inventory = []

key_positions = [
    [43.2983, 1.82, 12.8770],
    [34.0662, 1.82, 25.5270],
    [34.9661, 1.82, 48.6848],
    [35.1175, 1.82, 69.1208],
    [43.2681, 1.82, 70.6941],
    [12.4041, 1.82, 75.6498],
    [2.4852, 1.82, 57.3607],
    [-0.6159, 1.82, 26.0106],
    [-24.6561, 1.82, 11.7162],
    [-42.6306, 1.82, 48.9335],
    [-37.9733, 1.82, 76.6581],
    [-15.6070, 1.82, 93.3492]
]

def floatObject(obj, amplitude=0.3, speed=2):
    base_y = obj.getPosition()[1]
    time = 0
    def updateFloat():
        nonlocal time
        time += viz.getFrameElapsed()
        new_y = base_y + math.sin(time * speed) * amplitude
        obj.setPosition(obj.getPosition()[0], new_y, obj.getPosition()[2])
    vizact.ontimer(0, updateFloat)

def spawn_object_at(position):
    atslega_path = "atslega.glb"
    container = viz.addGroup()
    container.setPosition(position)
    obj = viz.addChild(atslega_path, parent=container)
    obj.setScale([0.6, 0.6, 0.6])
    obj.setEuler([90, 90, 0])
    obj.setPosition([0, 2, 0])
    obj.enable(viz.LIGHTING)
    spin = vizact.spin(0, 1, 0, 20)
    container.addAction(spin)
    floatObject(container, amplitude=0.3, speed=2.0)
    container.collideSphere(radius=1)
    return container

objects = []
chosen_positions = random.sample(key_positions, 3)
for pos in chosen_positions:
    objects.append(spawn_object_at(pos))

def updateKeys():
    global inventory
    player_pos = viz.MainView.getPosition()
    for obj in objects[:]:
        key_pos = obj.getPosition()
        dist = vizmat.Distance(player_pos, key_pos)
        if dist < 2:
            pickup_sound.play()
            inventory.append("atslega")
            key_counter.message(str(len(inventory)))
            obj.remove()
            objects.remove(obj)

            if len(inventory) == 3:
                removeDoor()
                gate_text = viz.addText("Varti ir atvērt! Vari doties uz izeju!", parent=viz.SCREEN)
                gate_text.setPosition([0.5,0.5,0])
                gate_text.alignment(viz.ALIGN_CENTER)
                gate_text.setScale([0.5,0.5,0.5])
                gate_text.color(viz.WHITE)
                def removeGateText():
                    gate_text.remove()
                vizact.ontimer2(5.0, 1, removeGateText)

vizact.ontimer(0, updateKeys)

# ===== SPRINT / STAMINA =====
MOVE_SPEED = 0.03
MAX_STAMINA = 100
stamina = MAX_STAMINA
STAMINA_DRAIN = 22
STAMINA_REGEN = 10
SPRINT_MULT = 2.0
low_stamina_sound_playing = False
low_stamina_sound = viz.addAudio("elsosana.mp3")
low_stamina_sound.loop(True)

def onUpdate():
    global stamina, low_stamina_sound_playing
    yaw = viz.MainView.getEuler()[0]
    yaw_rad = math.radians(yaw)
    move_x = 0
    move_z = 0
    shift_down = viz.key.isDown(viz.KEY_SHIFT_L) or viz.key.isDown(viz.KEY_SHIFT_R)
    sprinting = shift_down and stamina > 0
    speed = MOVE_SPEED * (SPRINT_MULT if sprinting else 1)

    # movement
    if viz.key.isDown('w'):
        move_x += math.sin(yaw_rad) * speed
        move_z += math.cos(yaw_rad) * speed
    if viz.key.isDown('s'):
        move_x -= math.sin(yaw_rad) * speed
        move_z -= math.cos(yaw_rad) * speed
    if viz.key.isDown('d'):
        move_x += math.cos(yaw_rad) * speed
        move_z -= math.sin(yaw_rad) * speed
    if viz.key.isDown('a'):
        move_x -= math.cos(yaw_rad) * speed
        move_z += math.sin(yaw_rad) * speed

    pos = viz.MainView.getPosition()
    viz.MainView.setPosition([pos[0] + move_x, 1.82, pos[2] + move_z])

    stamina_percent = int((stamina / MAX_STAMINA) * 100)
    stamina_text.message(f"Stamina: {stamina_percent}%")

    if sprinting:
        stamina -= STAMINA_DRAIN * viz.getFrameElapsed()
        stamina = max(0, stamina)
    else:
        stamina += STAMINA_REGEN * viz.getFrameElapsed()
        stamina = min(MAX_STAMINA, stamina)

    # Low stamina breathing
    if stamina_percent < 10:
        if not low_stamina_sound_playing:
            low_stamina_sound.play()
            low_stamina_sound_playing = True
    else:
        if low_stamina_sound_playing:
            low_stamina_sound.stop()
            low_stamina_sound_playing = False

vizact.ontimer(0, onUpdate)

# ===== CAMERA =====
viz.mouse.setVisible(False)
yaw = 0.0
pitch = 0.0
SENS = 0.15

def onMouseMove(e):
    global yaw, pitch
    dx = e.dx
    dy = e.dy
    yaw += dx * SENS
    pitch -= dy * SENS
    pitch = max(-89, min(89, pitch))
    viz.MainView.setEuler([yaw, pitch, 0])

viz.callback(viz.MOUSE_MOVE_EVENT, onMouseMove)

# ===== CAMERA LIFT =====
def lift_camera():
    platform.disable(viz.COLLISION)
    pos = viz.MainView.getPosition()
    if int(pos[1]) == 101:
        viz.MainView.setPosition([pos[0], 1.82, pos[2]])
    else:
        viz.MainView.setPosition([pos[0], 100, pos[2]])
    platform.enable(viz.COLLISION)

def onKeyDown2(key):
    if key == 'b':
        lift_camera()
    if key == 'p':
        print(viz.MainView.getPosition())

viz.callback(viz.KEYDOWN_EVENT, onKeyDown2)
viz.MainView.setPosition([2.5, 1.82, -5])

# ===== JUMPSCARE =====
jumpscare_image_path = 'jumpscare.jpg'
jumpscare_sound = viz.addAudio('jumpscare.mp3')
jumpscare_trigger_distance = 2.0
jumpscare_active = False

jumpscare_positions = [
    [-39.4, 1.82, 15.63], [-38.77, 1.82, 37.93], [-21.68, 1.82, 39.77],
    [-17.45, 1.82, 35.49], [5.0, 1.82, 44.47], [0.36, 1.82, 52.54],
    [-5.05, 1.82, 64.09], [23.41, 1.82, 16.56], [16.5, 1.82, 9.9],
    [33.4, 1.82, 14.86], [32.11, 1.82, 29.65], [38.89, 1.82, 50.42],
    [12.34, 1.82, 78.92], [-20.12, 1.82, 50.34], [40.23, 1.82, 10.45],
    [-10.55, 1.82, 65.12], [5.67, 1.82, 25.78], [-30.12, 1.82, 90.34],
    [35.44, 1.82, 55.67], [-5.23, 1.82, 15.89], [22.34, 1.82, 80.12],
    [-40.11, 1.82, 20.45], [10.89, 1.82, 70.23], [-25.78, 1.82, 35.56],
    [30.12, 1.82, 60.78], [-15.45, 1.82, 12.34], [0.23, 1.82, 90.67]
]

jumpscare_triggered_flags = [False] * len(jumpscare_positions)

def triggerJumpscare():
    global jumpscare_active
    if jumpscare_active: return
    jumpscare_active = True
    js = viz.addTexQuad(parent=viz.SCREEN)
    js.texture(viz.addTexture(jumpscare_image_path))
    js.setPosition([0.5,0.5,0])
    js.alignment = viz.ALIGN_CENTER
    js.setScale([15,10,10])
    jumpscare_sound.play()
    def removeJumpscare():
        js.remove()
        global jumpscare_active
        jumpscare_active = False
    vizact.ontimer2(1.0,1,removeJumpscare)

def checkJumpscare():
    player_pos = viz.MainView.getPosition()
    for i, pos in enumerate(jumpscare_positions):
        if not jumpscare_triggered_flags[i]:
            dist = vizmat.Distance(player_pos, pos)
            if dist <= jumpscare_trigger_distance:
                triggerJumpscare()
                jumpscare_triggered_flags[i] = True

vizact.ontimer(0, checkJumpscare)

# ===== GAME FINISH / CHECKPOINT =====
finish_position = [-1.8382, 1.82, 98.5153]
finish_radius = 3.0
game_finished = False

# Victory sound
victory_sound = viz.addAudio("Victory.mp3")

def checkFinish():
    global game_finished
    if game_finished:
        return
    player_pos = viz.MainView.getPosition()
    dist = vizmat.Distance(player_pos, finish_position)
    
    if dist <= finish_radius and len(inventory) == 3:
        game_finished = True
        victory_sound.play()
        end_text = viz.addText("Spēle pabeigta, paldies par spēlēšanu!", parent=viz.SCREEN)
        end_text.setPosition([0.2, 0.5, 0])
        end_text.alignment = viz.ALIGN_CENTER
        end_text.setScale([0.5, 0.5, 0.5])
        end_text.color(viz.WHITE)

vizact.ontimer(0, checkFinish)
