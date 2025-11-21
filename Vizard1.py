import viz
import vizshape
import vizcam
import os

viz.go()

# --- Pamata zeme
ground = vizshape.addPlane(size=(200, 200))
ground.texture(viz.addTexture('grida.jpg'))
ground.enable(viz.LIGHTING)

# --- Gaisma no augšas
sun = viz.addDirectionalLight(euler=(90, 0, 0))
sun.color(viz.WHITE)
sun.intensity(1.0)

# --- Ielādēt labirintu, ja tas eksistē
maze_path = 'mazefix.glb'
viz.MainView.collision(True)
if os.path.exists(maze_path):
    maze = viz.addChild(maze_path)
    maze.setPosition([0, 0, 50])
    maze.setScale([5, 5, 5])

# --- Kamera / pārvietošanās
walkNav = vizcam.WalkNavigate()
walkNav.speed = 15.0
walkNav.jumpHeight = 5.0
walkNav.gravity = 9.8
viz.cam.setHandler(walkNav)

# --- Novieto kameru augstāk
viz.MainView.setPosition([2.5, 3.0, -5])

# --- Paslēpt peli
viz.mouse.setVisible(False)
