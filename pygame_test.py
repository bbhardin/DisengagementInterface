import time
import pygame
pygame.init()

size = [500, 700]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

#Loop until the user clicks the close button.
done = False
# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

# Used to manage how fast the screen updates
clock = pygame.time.Clock()
gamepad = pygame.joystick.Joystick(0)

gamepad.init()
print("Initialised? ", gamepad.get_name())
print("Axis are: ", gamepad.get_numaxes())
done = False

# -------- Main Program Loop -----------
while not done:
    # EVENT PROCESSING STEP
    pygame.event.pump()

    for event in pygame.event.get(): # User did something
        print(event)
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        
        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        elif event.type == pygame.JOYAXISMOTION:
            axis = [ 'X', 'Y' ]
            print( "joystick: %d, movement: %4.2f in the %s-axis" % ( event.joy, event.value, axis[event.axis] ) )
        elif event.type == pygame.JOYBUTTONDOWN and event.button == 7:
            print( "Joystick button pressed." )
            #pass
        elif event.type == pygame.JOYBUTTONUP:
            print( 'joystick: %d, button: %d' % ( event.joy, event.button ) )

    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill( WHITE )

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second
    clock.tick( 20 )

# exit
pygame.quit()