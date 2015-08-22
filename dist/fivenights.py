from __future__ import division
import pygame
import random
from pygame.locals import *

#TODO: Abilities ? Possibly deferred. Game is fine as-is.
#TODO: On-screen text (clock, bar values, etc.)
#TODO: Special animations (victory, time, etc.)

def game(screen,difficulty,debug):
    #for debugging, if we load directly, we need to initialize
    if not (screen):
        pygame.init()
        screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Five Nights With Us')
    
    
    #initializing helper functions. The definitions are below the code
    
    
    #constant initialization
    
    foxytransitionval = [40, 80, 120, 5]
    #foxytransitionval = [5,5,10,5]
    #the max size of the bar to transition from state N to the next
    
    #variable initialization
    #status bars
    energy = 10
    #if debug: energy = 90
    tension = 0.1
    if debug: tension = 1.0
    power = 100
    attackValue = 5
    
    seconds = 0
    hours = 0
    
    #hourcd = 85
    hourcd = 70
    laughcd = 30
    blackoutcd = 65
    itsmecd = 120
    goldenfreddycd = 360
    #Ability Cooldowns. These should be in seconds.
    #The hours are 1 min 25 seconds, for 8 min 30 seconds for a day
    #All times are in seconds
    
    laughcost = 20
    blackoutcost = 40
    makenoisecost = 30
    itsmecost = 75
    goldenfreddycost = 100
    #Ability costs.
    
    locationToText = ["Show Stage",     #0
                      "Back Stage",     #1
                      "Dining Area",    #2
                      "Pirate Cove",    #3
                      "Restroom",       #4
                      "Kitchen",        #5
                      "East Hall",      #6
                      "E. Hall Corner", #7
                      "West Hall",      #8
                      "W. Hall Corner", #9
                      "Supply Closet",  #10
                      "Attacking East", #11, right
                      "Attacking West"] #12, left
    
    freddyAttacking = 0
    bonnieAttacking = 0
    chicaAttacking = 0
    
    #determines how long a puppet has been in place
    stagnationArray = [0,0,0]
    foxymeter = 0
    #Foxy build up meter to change states. At state 3, he attacks
    
    leftDoorClosed = False
    rightDoorClosed = False
    #These are for the actual doors
    
    #security A.I. variables
    #lastKnownLocations = [freddy,bonnie,chica,foxy]
    lastKnownLocations = [0,0,0,3]
    lastKnownFoxyState = 0
    #When someone's position is not known, he will search for it
    searchMode = False
    #This array will be shuffled to determine his search pattern
    #The "worried" variables determine if the security guard is expect an attack from somewhere
    #When worried, the guard will not enter searchMode and will check lights or cameras to keep an eye on the location
    worriedArray = [False,False,False,False]
    #These variables control when the guard wants to close the door
    toggleLeftDoor = False
    toggleRightDoor = False
    #Here is the routine queue. This queue will determine the order he checks things in.
    routineArray = [-1,-1,-1,0,3]
    #just a quick constant, this array is for when the guard feels safe enough to wait.
    delay = 0
    
    #Music definitions
    
    bgm1 = 'assets/sounds/ambience2.wav'
    bgm2 = 'assets/sounds/darkness music.wav'
    bgm3 = 'assets/sounds/EerieAmbienceLargeSca_MV005.wav'
    pygame.mixer.music.load(bgm1)
    #this will put the song ending onto the event queue
    SONG_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(SONG_END)
    
    #Sound Effect definitions
    cameraStartSound = pygame.mixer.Sound('assets/sounds/CAMERA_VIDEO_LOA_60105303.wav')
    cameraSwitchSound = pygame.mixer.Sound('assets/sounds/blip3.wav')
    cameraStopSound = pygame.mixer.Sound('assets/sounds/putdown.wav')
    lightsOnSound = pygame.mixer.Sound('assets/sounds/BallastHumMedium2.wav')
    foxyRunSound = pygame.mixer.Sound('assets/sounds/run.wav')
    foxyKnockSound = pygame.mixer.Sound('assets/sounds/knock2.wav')
    doorSound = pygame.mixer.Sound('assets/sounds/SFXBible_12478.wav')
    windowSound = pygame.mixer.Sound('assets/sounds/windowscare.wav')
    
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    
    # Initialize Objects
    gameMap = GameMap()
    freddy = Freddy()
    bonnie = Bonnie()
    chica = Chica()
    foxy = Foxy()
    camera = Camera()
    freddyIcon = FreddyIcon()
    freddymove1 = RunGuy1Icon([90,40], freddy.move1cost)
    freddymove2 = RunGuy2Icon([90,60], freddy.move2cost)
    bonnieIcon = BonnieIcon()
    bonniemove1 = RunGuy1Icon([90,140], bonnie.move1cost)
    bonniemove2 = RunGuy2Icon([90,160], bonnie.move2cost)
    chicaIcon = ChicaIcon()
    chicamove1 = RunGuy1Icon([90,240], chica.move1cost)
    chicamove2 = RunGuy2Icon([90,260], chica.move2cost)
    foxyIcon = FoxyIcon()
    foxyTimerBar = BasicRectangle([255,0,0],[90,(404 - 0)],[16,0])
    energyBarBox = StatusBox([0,0],[640,30])
    energyBar = BasicRectangle([255,255,0],[3,3],[round(energy*6.34),24])
    energyBarLabel = TextSquare([320,0], "Energy", True)
    tensionBarBox = StatusBox([320, 40], [200,30])
    tensionBar = BasicRectangle([133,193,212], [323, 43], [round(tension* 194),24])
    tensionBarLabel = TextSquare([420,40], "Tension", True)
    tooltip = Tooltip([0,0])
    leftDoor = LeftDoorClosed()
    rightDoor = RightDoorClosed()
    
    #These bars are for attacking
    freddyTimerBar = BasicRectangle([255,0,0],[90,(104 - 0)],[16,0])
    bonnieTimerBar = BasicRectangle([255,0,0],[90,(204 - 0)],[16,0])
    chicaTimerBar = BasicRectangle([255,0,0],[90,(304 - 0)],[16,0])
    
    timerText = TimerText()
    
    #Defining different object arrays for the different game screens.
    #These will be copied to objects[] for blitting to the screen
    gameObjects = []
    gameObjects.append(gameMap)
    gameObjects.append(freddyIcon)
    gameObjects.append(freddymove1)
    gameObjects.append(freddymove2)
    gameObjects.append(bonnieIcon)
    gameObjects.append(bonniemove1)
    gameObjects.append(bonniemove2)
    gameObjects.append(chicaIcon)
    gameObjects.append(chicamove1)
    gameObjects.append(chicamove2)
    gameObjects.append(energyBarBox)
    gameObjects.append(energyBar)
    gameObjects.append(energyBarLabel)
    gameObjects.append(tensionBarBox)
    gameObjects.append(tensionBar)
    gameObjects.append(tensionBarLabel)
    gameObjects.append(foxyIcon)
    gameObjects.append(foxyTimerBar)
    gameObjects.append(freddy)
    gameObjects.append(bonnie)
    gameObjects.append(chica)
    gameObjects.append(foxy)
    gameObjects.append(camera)
    gameObjects.append(tooltip)
    gameObjects.append(leftDoor)
    gameObjects.append(rightDoor)
    gameObjects.append(timerText)
    
    agentArray = [freddy,bonnie,chica,foxy]
    objects = gameObjects #set the main objects array to the gameObjects array
    
    disabledObjects = []
    disabledObjects.append(freddyTimerBar)
    disabledObjects.append(bonnieTimerBar)
    disabledObjects.append(chicaTimerBar)
    
    time = pygame.time.get_ticks()
    hoverTime = 0
    
    hoveredObject = None    
    
    pygame.mixer.music.play()
    # Event loop
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return -1

            #tooltips
            if event.type == MOUSEMOTION:
                mousepos = pygame.mouse.get_pos()
                tooltip.topleft = [mousepos[0]+10,mousepos[1]]
                hovered_sprites = [s for s in objects if s.rect.collidepoint(mousepos)]
                hovered_sprites = filter(lambda x: x.getTooltip(True) != "",hovered_sprites)
                if hovered_sprites:
                    obj = hovered_sprites.pop()
                    if (obj != hoveredObject):
                        hoverTime = 0
                        hoveredObject = obj
                else:
                    hoveredObject = None
                    hoverTime = 0
                    
            #click actions
            if event.type == MOUSEBUTTONUP:
                mousepos = pygame.mouse.get_pos()
                clicked_sprites = [s for s in objects if s.rect.collidepoint(mousepos)]
                #Python has no case statements. God this makes me feel dirty
                for obj in clicked_sprites:
                    if (obj == freddymove1) or (obj == freddymove2): #if freddy is moving
                        energy = calculateMove(freddy,(obj == freddymove1),energy,camera) #passes True if freddymove1, signaling it to use random
                        if (freddy.loc == 11): #attacking code
                            windowSound.play()
                            freddyAttacking = 1
                            toggleObject(freddymove1,objects,disabledObjects)
                            toggleObject(freddymove2,objects,disabledObjects)
                            toggleObject(freddyTimerBar,disabledObjects,objects)
                    
                    elif (obj == bonniemove1) or (obj == bonniemove2):
                        energy = calculateMove(bonnie,(obj == bonniemove1),energy,camera)
                        if (bonnie.loc == 12):
                            windowSound.play()
                            bonnieAttacking = 1
                            toggleObject(bonniemove1,objects,disabledObjects)
                            toggleObject(bonniemove2,objects,disabledObjects)
                            toggleObject(bonnieTimerBar,disabledObjects,objects)
                            
                    elif (obj == chicamove1) or (obj == chicamove2):
                        energy = calculateMove(chica,(obj == chicamove1),energy,camera)
                        if (chica.loc == 11):
                            windowSound.play()
                            chicaAttacking = 1
                            toggleObject(chicamove1,objects,disabledObjects)
                            toggleObject(chicamove2,objects,disabledObjects)
                            toggleObject(chicaTimerBar,disabledObjects,objects)
            
            if event.type == KEYUP:
                if event.key == pygame.K_ESCAPE:
                    return 5
            
            if event.type == SONG_END:
                if (tension >= .5):
                    pygame.mixer.music.load(bgm3)
                else:
                    pygame.mixer.music.load(bgm2)
                pygame.mixer.music.play()
        if (hoveredObject):
            hoverTime += 1
            #print(hoverTime)
            tip = ""
            if (100 < hoverTime < 300):
                #display tooltip
                tip = hoveredObject.getTooltip(True)
            if (hoverTime >= 300):
                tip = hoveredObject.getTooltip(False)
            if (tip != ""):
                #print(tip)
                tooltip.visible = True
                tooltip.text = tip
        else:
            tooltip.visible = False
                
        
        #Everything that happens each second, instead of each frame, goes in here                    
        if ((pygame.time.get_ticks() - time) >= 1000):
            time = pygame.time.get_ticks()
            #Energy Update
            seconds += 1
            if (seconds == hourcd):
                hours += 1
                timerText.hours = hours
                #print hours, " AM"
                seconds = 0
                if (hours == 6):
                    #print("YOU LOSE! GOOD DAY SIR!")
                    return 0
            
            if (tension < 0.1): #always get energy, even if your tension is low, but not past 40
                if (energy < 40): energy += 0.5
                else: energy += 5 * tension
            else: energy += 5 * tension
            #Attacking Update
            if (freddyAttacking > 0):
                freddy.attack -= 4
                if (freddy.attack <= 0):
                    freddyAttacking = 0
                    freddy.attack = 1
                    toggleObject(freddyTimerBar,objects,disabledObjects)
                    toggleObject(freddymove1,disabledObjects,objects)
                    toggleObject(freddymove2,disabledObjects,objects)
                    
                    rand = random.randint(0,2)
                    #Freddy is twice as likely to only backup one than he is two
                    if (rand != 2): freddy.pathstate -= 1
                    else: freddy.pathstate -= 2
                    freddy.loc = freddy.path[freddy.pathstate]
                elif (rightDoorClosed):
                    freddyAttacking = 1
                else:
                    freddyAttacking += 1
                    if (freddyAttacking >= attackValue):
                        #print("Freddy got him!")
                        #print("YOU WIN THE GAME!")
                        return 1
            else:
                freddy.attack += 1
                if (freddy.attack > freddy.maxAttack): freddy.attack = freddy.maxAttack
            
            if (bonnieAttacking > 0):
                bonnie.attack -= 4
                if (bonnie.attack <= 0):
                    bonnieAttacking = 0
                    bonnie.attack = 1
                    toggleObject(bonnieTimerBar,objects,disabledObjects)
                    toggleObject(bonniemove1,disabledObjects,objects)
                    toggleObject(bonniemove2,disabledObjects,objects)
                    
                    rand = random.randint(0,3)
                    if (rand != 3): bonnie.pathstate -= 1
                    else: bonnie.pathstate -= 2
                    bonnie.loc = bonnie.path[bonnie.pathstate]
                elif (leftDoorClosed):
                    bonnieAttacking = 1
                else:
                    bonnieAttacking += 1
                    if (bonnieAttacking > attackValue):
                        #print("Bonnie got him!")
                        #print("YOU WIN THE GAME!")
                        return 2
            else:
                bonnie.attack += 2
                if (bonnie.attack > bonnie.maxAttack): bonnie.attack = bonnie.maxAttack
            
            if (chicaAttacking > 0):
                chica.attack -= 4
                if (chica.attack <= 0):
                    chicaAttacking = 0
                    chica.attack = 1
                    toggleObject(chicaTimerBar,objects,disabledObjects)
                    toggleObject(chicamove1,disabledObjects,objects)
                    toggleObject(chicamove2,disabledObjects,objects)
                    rand = random.randint(0,2)
                    if (rand != 2): chica.pathstate -= 2
                    else: chica.pathstate -= 1
                    chica.loc = chica.path[chica.pathstate]
                elif (rightDoorClosed):
                    chicaAttacking = 1
                else:
                    chicaAttacking += 1
                    if (chicaAttacking >= attackValue):
                        #print("Chica got him!")
                        #print("YOU WIN THE GAME!")
                        return 3
            else:
                chica.attack += 1
                if (chica.attack > chica.maxAttack): chica.attack = chica.maxAttack
            
            
            #Foxy Update
            foxymeter += 1
            #Increase the bar by the proper percentage. This makes sure that the bar is always at full
            if (foxymeter >= foxytransitionval[foxy.state]):
                foxy.state += 1
                foxymeter = 0
                if (foxy.state == 3): foxyRunSound.play()
                if (foxy.state >= 4):
                    if (leftDoorClosed == False):
                        #print("Foxy got him!")
                        #print("YOU WIN THE GAME!")
                        return 4
                    else:
                        foxyKnockSound.play()
                        foxy.state = 0
                    
                foxyIcon.state = foxy.state
            
            #Camera Update
            
            #if trying to toggle the door
            if (toggleLeftDoor):
                doorSound.play()
                if (leftDoorClosed):
                    leftDoorClosed = False
                    #print("I'm opening the left door")
                else:
                    leftDoorClosed = True
                    #print("I'm closing the left door")
                toggleLeftDoor = False
            if (toggleRightDoor):
                doorSound.play()
                if (rightDoorClosed):
                    rightDoorClosed = False
                    #print("I'm opening the right door")
                else:
                    rightDoorClosed = True
                    #print("I'm closing the right door")
                toggleRightDoor = False
            
            #setting the door icons
            if (leftDoorClosed):  leftDoor.visible = True
            else: leftDoor.visible  = False
            if (rightDoorClosed): rightDoor.visible = True
            else: rightDoor.visible = False
            exitState = camera.loc
            #if delay is set, hold camera where it is
            if (delay > 0):
                enterState = camera.loc
                if enterState == 3: foxymeter -= 2
                delay -= 1
            elif (delay == 0):
                if routineArray: #If we have stuff to do
                    enterState = routineArray.pop(0)
                    #we can't go straight from camera to lights, so this will put a -1 between them
                    if (enterState >= 11) and (exitState != -1):
                        routineArray.insert(0, enterState) #put it back on the queue
                        enterState = -1
                        
                    #If checking a light
                    if (enterState == 11):
                        if (rightDoorClosed): #if the door is closed
                            if (freddy.loc != 11) and (chica.loc != 11): #and neither of them are there
                                delay = 0
                                toggleRightDoor = True
                        else: #if the door is open
                            if (freddy.loc == enterState): #and freddy is there
                                tension += 3
                                delay = 0
                                toggleRightDoor = True
                            if (chica.loc == enterState): #if chica is there
                                tension += .1
                                delay = 0
                                toggleRightDoor = True 
                    if (enterState == 12):
                        if (leftDoorClosed): #if the door is closed
                            if (bonnie.loc != enterState) and (lastKnownFoxyState != 3):
                                delay = 0
                                toggleLeftDoor = True
                        else: #if the door is open
                            if (bonnie.loc == enterState): #we don't check for foxy here because we don't see him at the light
                                tension += .1
                                delay = 0
                                toggleLeftDoor = True
                    
                    #Checking the known locations first, ignoring Foxy for now
                    for a in range(0,3):
                        loc = lastKnownLocations[a]
                        if (loc == enterState): #If we are currently checking one of these states
                            agent = agentArray[a]
                            if (agent.loc != loc) and (loc != -1): #If a puppet SHOULD be here, but isn't
                                tension += .05 #Get spooked
                                if (agent.name() == "Freddy"): tension += .05 #Freddy is spookier than normal. Extra tension for Freddy
                                lastKnownLocations[a] = -1 #Switch their position to unkown
                                delay = 1 #Hold for one more update
                                stagnationArray[a] = 0
                                #print "can't find ",agent.name()
                            elif (agent.loc == loc):
                                stagnationArray[a] += 1
                                if (stagnationArray[a] % 5) == 0: #if someone's been there for five checks
                                    print("He's been there a while...")
                                    tension -= 0.1
                                    
                    if(enterState == 3): #If it IS Foxy
                        if (foxy.state != 3):
                            foxymeter -= 2 #it gained one this tick, so we remove that, and one more
                            if (foxymeter < 0): foxymeter = 0 #can't go below zero
            
                        if (worriedArray[3]): delay = 2 #Keep the camera on him if he's about to come out
                        if (lastKnownFoxyState != foxy.state): #If foxy's moved since we saw him last
                            tension += .05 #Minor spook
                            lastKnownFoxyState = foxy.state #But now we know!
                            if (foxy.state == 2) and (worriedArray[3] == False): #If Foxy's about to move and we're not worried...
                                worriedArray[3] = True #...we should be.
                                #print("I'm worried about Foxy")
                            elif (foxy.state == 3): #If Foxy is MIA
                                tension += .4 #Super spooky, but only for a bit
                                if (leftDoorClosed == False): #If our door is open
                                    delay = 0
                                    routineArray = [-1] #IMMEDIATELY DROP CAMERA
                                    toggleLeftDoor = True #OH GOD CLOSE IT CLOSE IT CLOSE IT
                                    #print("Foxy's attacking!")
                            elif (foxy.state == 0) and (worriedArray[3] == True): #If Foxy's safe at home
                                tension -= .2 #Sight of relief
                                worriedArray[3] = False #No longer worried
                                print("Foxy's gone")
                                if (leftDoorClosed): toggleLeftDoor = True #Open the door, if it isn't already
                                
                    
                    #Begin Block
                    #Puppet found in a different place
                    if (freddy.loc == enterState) and (lastKnownLocations[0] != enterState) and (enterState != -1):
                        if (lastKnownLocations[0] != -1):
                            #print("HI FREDDY. You weren't supposed to be there")
                            tension += .1
                        #else:
                            #print("found freddy")
                        lastKnownLocations[0] = enterState
                        delay = 1 #scared into staying for another tic
                        #A one-line workaround to see if the state is one of these three values
                        if (worriedArray[0] == False) and ([6,7,11].count(enterState) > 0):
                            worriedArray[0] = True
                            #print("I'm worried about Freddy")
                        elif (worriedArray[0] == True) and ([6,7,11].count(enterState) == 0):
                            worriedArray[0] = False
                            #print("Freddy's gone, for now")
                            
                    if (bonnie.loc == enterState) and (lastKnownLocations[1] != enterState):
                        if (lastKnownLocations[1] != -1):
                            #print("HI BONNIE. You weren't supposed to be there")
                            tension += .05
                        #else:
                            #print("found bonnie")
                        lastKnownLocations[1] = enterState
                        delay = 1
                        if (worriedArray[1] == False) and ([9,12].count(enterState) > 0):
                            worriedArray[1] = True
                            #print("I'm worried about Bonnie")
                        elif (worriedArray[1] == True) and (enterState < 9):
                            worriedArray[1] = False
                            #print("Bonnie's gone, for now")
                            
                    if (chica.loc == enterState) and (lastKnownLocations[2] != enterState):
                        if (lastKnownLocations[2] != -1):
                            #print("HI CHICA. You weren't supposed to be there")
                            tension += .05
                        #else:
                            #print("found chica")
                        lastKnownLocations[2] = enterState
                        delay = 1
                        if (worriedArray[2] == False) and ([6,7,11].count(enterState) > 0):
                            worriedArray[2] = True
                            #print("I'm worried about Chica")
                        elif (worriedArray[2] == True) and ([6,7,11].count(enterState) == 0):
                            worriedArray[2] = False
                            #print("Chica's gone, for now")
                    
                    #Begin Block
                    #After each update        
                    if (lastKnownLocations.count(-1) > 0) and (searchMode == False): #If someone's position is unknown but we're not in searchMode yet
                        searchMode = True #Rectify that.
                        if (worriedArray[:2].count(True) != 0):
                            panic = True
                        else:
                            panic = False
                        routineArray = resetRoutine(True,panic,routineArray,worriedArray,lastKnownLocations)
                        
                    if (searchMode == True) and (lastKnownLocations.count(-1) == 0): #If everyone's position is known and we're in searchMode
                        searchMode = False #No need to search any more
                        routineArray = resetRoutine(False,False,routineArray,worriedArray,lastKnownLocations)
                        #print("found everyone")
                
                else: #If we don't have anything left in our routine
                    if (searchMode == False) and (lastKnownLocations.count(-1) == 0): #If we're not searching and we know where everyone is
                        print("All clear")
                        tension -= 0.05
                        enterState = -1
                        routineArray = resetRoutine(False,False,routineArray,worriedArray,lastKnownLocations)
                        
                    else: #If searchMode is on and we're still missing someone
                        #print("still missing someone, oh dang")
                        tension += .15 #Get spooked
                        routineArray = resetRoutine(True,True,routineArray,worriedArray,lastKnownLocations)
                        enterState = routineArray.pop(0)
            
            #sound effect controls
            if (enterState != exitState): #If we're not staying still
                #play the start sound if you are going from OFF to a camera
                if (exitState == -1) and (0 <= enterState <= 10): cameraStartSound.play()
                
                #stop the light sound if no longer looking at a light
                if (exitState == 11): lightsOnSound.stop()
                if (exitState == 12): lightsOnSound.stop()
                
                #start the light sound if looking at a light
                if (enterState == 11): lightsOnSound.play()
                if (enterState == 12): lightsOnSound.play()
                
                #play the camera stop sound if switching from a camera to not a camera
                if (0 <= exitState <= 10) and (enterState == 11 or enterState == 12 or enterState == -1):
                    cameraStartSound.stop()
                    cameraStopSound.play()
                
                #play the switch sound if switching from a camera to a camera
                if (0 <= exitState <= 10) and (0 <= enterState <= 10): cameraSwitchSound.play()
            
            #and finally...
            camera.loc = enterState #...wow, all that buildup and THIS is the payoff?                  
        
        
        #repainting the screen
        #Avoid index out of bounds
        if (tension <   0): tension = 0
        if (energy  <   0): energy  = 0
        if (tension > 1.0): tension = 1.0
        if (foxymeter < 0): foxymeter = 0
        
        maxEnergy = 50
        if (tension > 0.5): maxEnergy = tension*100
        if (energy  > maxEnergy): energy  = maxEnergy
        
        
        #tweaking some strings and sizes and whatnot before painting
        energyBarBox.brieftooltip = str(int(energy)) + "/" + str(int(maxEnergy))
        energyBarBox.fulltooltip = str(int(energy)) + "/" + str(int(maxEnergy)) + "\nUsed to move your characters.\nIncreases based on Tension.\nMaximum value based on Tension."
        energyBarLabel.text = str(int(energy)) + "/" + str(int(maxEnergy)) + " Energy"
        
        tensionBarBox.brieftooltip = str(int(tension*100)) + "%"
        tensionBarBox.fulltooltip = str(int(tension*100)) + "%\nDetermines rate of energy gain.\nIncreases when unexpected things happen.\nDecreases if things stay normal."
        tensionBarLabel.text = str(int(tension*100)) + "% Tension"
        
        if (freddy.attack < 0): freddy.attack = 0
        if (bonnie.attack < 0): bonnie.attack = 0
        if (chica.attack < 0): chica.attack = 0
        barHeight(freddyTimerBar,104,freddy.attack,freddy.maxAttack)
        barHeight(bonnieTimerBar,204,bonnie.attack,bonnie.maxAttack)
        barHeight( chicaTimerBar,304,chica.attack,chica.maxAttack)
        barHeight(  foxyTimerBar,404,foxymeter,foxytransitionval[foxy.state])
        
        energyBar.size = [round(energy*6.34),24] #Update Energy Bar
        tensionBar.size = [round(tension* 194),24] #Update Tension Bar
        
        if (tension < .5):
            toggleObject(freddymove2,objects,disabledObjects)
            toggleObject(bonniemove2,objects,disabledObjects)
            toggleObject(chicamove2,objects,disabledObjects)
        else:
            if (freddyAttacking == 0): toggleObject(freddymove2,disabledObjects,objects)
            if (bonnieAttacking == 0): toggleObject(bonniemove2,disabledObjects,objects)
            if ( chicaAttacking == 0): toggleObject(chicamove2,disabledObjects,objects)
            
        screen.fill([0, 0, 0])
        for obj in objects:
            #try:
            obj.update()
            #except pygame.error:
                #print obj
                #print obj.size
                #print "ERROR, invalid resolution for surface"
                #return -1
            if (obj.visible):
                screen.blit(obj.image,obj.rect)
            
        pygame.display.update()
    
    #end of loop iteration
     

#Helper Functions:

     
#toggleObject - move an object from the Object list and put it into the disabledObject list
#
#obj - object - the object to be disabled 
def toggleObject(obj,objects1, objects2):
    if (objects1.count(obj) > 0): #make sure the object is enabled
        objects1.remove(obj)
        objects2.append(obj)
    

#calculateMove - determine where the animatronics should move
#
#agent - object  - the animatronic that is moving. Use the actual object for this, not the icon
#rand  - boolean - whether or not to randomly determine forward or backward movement
def calculateMove(agent, rand, energy, camera):
    errorSound = pygame.mixer.Sound('assets/sounds/error.wav')
    if (rand):
        if (energy >= agent.move1cost):
            if (camera.loc != agent.loc):
                randomnum = random.randint(0,len(agent.path)+1)
                #more likely to go forward when not very far in, and more likely to go backward when far
                if (randomnum >= agent.pathstate):
                    agent.pathstate += 1
                    if (agent.pathstate == len(agent.path)):
                        agent.pathstate = 0
                    agent.loc = agent.path[agent.pathstate]
                else:
                    agent.pathstate -= 1
                    if (agent.pathstate < 0):
                        agent.pathstate = 0
                    agent.loc = agent.path[agent.pathstate]
                energy -= agent.move1cost
            else: #can't move when being looked at
                errorSound.play()
        else: #not enough energy
            errorSound.play()
    else:
        if (energy >= agent.move2cost):
            if (camera.loc != agent.loc):
                agent.pathstate += 1
                if (agent.pathstate == len(agent.path)):
                    agent.pathstate = 0
                agent.loc = agent.path[agent.pathstate]
                energy -= agent.move2cost
            else:
                errorSound.play()
        else:
            errorSound.play()
    return energy            
#resetRoutine - Empties the routine array and rebuilds it based on parameters
#
#search - boolean - True if the new routine should contain the shuffled search array
#panic  - boolean - True if the new routine should start with checking lights
def resetRoutine(search, panic, routineArray, worriedArray, lastKnownLocations):
    routineArray = [] #Dump the routineArray
    searchModeArray = [0,1,2,3,4,5,6,7,8,9,10]
    waitArray = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    
    if (panic): #if we're panicking, check both lights
        routineArray = [-1,11,12]
    else: #otherwise check more methodically
        if (worriedArray[1] and (lastKnownLocations.count(12) == 0)): routineArray.append(12) #Check for Bonnie if we're worried
        if ((worriedArray[0] or worriedArray[2]) and (lastKnownLocations.count(11) == 0)): routineArray.append(11) #Check for Chica and Freddy if we're worried
        #if (worriedArray[3]): routineArray.append(3)
    
    if (search):
        random.shuffle(searchModeArray)
        if (worriedArray[3]):
            searchModeArray.remove(3)
            searchModeArray.insert(0, 3)
        routineArray.extend(searchModeArray[:])
    else:
        if (worriedArray.count(True) == 0):
            routineArray.extend(waitArray[:]) #This [:] is to pass by value instead of reference. Stupid Python.
        routineArray.extend(list(set(lastKnownLocations)))
    return routineArray
#barHeight - sets the height and location of a variable portrait bar
#
#bar     - object - The bar to be manipulated
#bottom  - int    - the start position of the bar in pixels
#current - int    - the current value of the bar numerically
#maximum - int    - the maximum value of the bar numerically
def barHeight(bar,bottom,current,maximum):
    h = (round(64 * (current/maximum)))
    bar.size = [16, h]
    bar.topleft = [90, (bottom - h)]
    return bar
#End of helper functions



#Sprites
       
class GameMap(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/gameMap_.png')
        self.visible = True
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [240,40]
    
    def getTooltip(self,brief):
        return ""
    
class FreddyIcon(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/freddyPortrait.png')
        self.visible = True
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [20,40]
    
    def getTooltip(self,brief):
        string = "Freddy Fazbear\n"
        if brief: return string
        string += "Expensive to move, but effective.\n"
        string += "Raises tension greatly when moving."
        return string

class BonnieIcon(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/bonniePortrait.png')
        self.visible = True
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [20,140]
    
    def getTooltip(self,brief):
        string = "Bonnie the Bunny\n"
        if brief: return string
        string += "Cheap to move, but doesn't attack for long.\n"
        string += "Recharges attack faster."
        return string
    
class ChicaIcon(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/chicaPortrait.png')
        self.visible = True
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [20,240]
    
    def getTooltip(self,brief):
        string = "Chica the Chicken\n"
        if brief: return string
        string += "Expensive to move, but relentless.\n"
        string += "Long attack time."
        return string
    
class FoxyIcon(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image0 = pygame.image.load('assets/sprites/foxyPortrait0.png')
        self.image1 = pygame.image.load('assets/sprites/foxyPortrait1.png')
        self.image2 = pygame.image.load('assets/sprites/foxyPortrait2.png')
        self.image3 = pygame.image.load('assets/sprites/foxyPortrait3.png')
        self.state = 0
        
        self.image = self.image0
        self.visible = True
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [20,340]
    
    
    def getTooltip(self,brief):
        string = "Foxy the Pirate\n"
        if brief: return string
        string += "Cannot be controlled directly.\n"
        string += "Delayed by cameras."
        return string
    
    def update(self):
        if (self.state == 0):
            self.image = self.image0
        elif (self.state == 1):
            self.image = self.image1
        elif (self.state == 2):
            self.image = self.image2
        elif (self.state == 3):
            self.image = self.image3    
            
#Color - the color of the rectangle
#topleft - a 2-element array [x,y]
#size - a 2-element array [x,y]
class BasicRectangle(pygame.sprite.Sprite):
    
    def __init__(self,color,topleft,size):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.visible = True
        self.topleft = topleft
        self.size = size
        self.tooltip = ""
        self.update()
    
    
    def getTooltip(self,brief):
        if brief: return self.tooltip.split("\n").pop(0)
        else: return self.tooltip
    
    def update(self):
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft

class Tooltip(pygame.sprite.Sprite):
    
    def __init__(self,topleft):
        pygame.sprite.Sprite.__init__(self)
        self.visible = False
        self.topleft = topleft
        self.text = ""
        self.font = pygame.font.Font("assets/Courier_New.ttf", 15)
        self.image = self.font.render("",1,[255,255,255])
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft
        self.update()
    
    def getTooltip(self,brief):
        return ""
    
    def update(self):
        if (self.text != ""):
            lines = self.text.split('\n')
            maxlen = max(map(len,lines)) #First order functions. I fucking love python
            if lines.count(''): lines.remove('')
            charwidth = 9
            charheight = 20
            
            self.image = pygame.Surface([20 + (maxlen*charwidth),(5 + ((len(lines))*charheight))])
            
            self.image.fill([128,128,128])
            y = 5
            for line in lines:
                self.image.blit(self.font.render(line, 1,[255,255,255]), [10,y])
                y = y+charheight
            self.image.set_alpha(200)    
            self.rect = self.image.get_rect()
            self.rect.topleft = self.topleft
        else:
            self.visible = False
        
        
class RunGuy1Icon(pygame.sprite.Sprite):
    def __init__(self, topleft, cost):
        pygame.sprite.Sprite.__init__(self)
                
        self.image = pygame.image.load('assets/sprites/runguy1.png')
        self.visible = True
        self.cost = cost
        
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
    
    def getTooltip(self,brief):
        string = "Move ("
        string += str(self.cost)
        string += ")\n"
        if brief: return string
        string += "Move randomly forward or backward.\n"
        string += "More effective when further away."
        return string
        
class RunGuy2Icon(pygame.sprite.Sprite):
    def __init__(self, topleft, cost):
        pygame.sprite.Sprite.__init__(self)
                
        self.image = pygame.image.load('assets/sprites/runguy2.png')
        self.visible = True
        self.cost = cost
        
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
    
    def getTooltip(self,brief):
        string = "Tactical Move ("
        string += str(self.cost)
        string += ")\n"
        if brief: return string
        string += "Move towards the security office.\n"
        string += "More expensive, but guaranteed to move you closer."
        return string
    
class Freddy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/freddyloc_temp.png')
        self.loc = 0
        self.visible = True
        self.path = [0,1,2,3,8,10,4,6,7,11]
        self.pathstate = 0
        self.move1cost = 40
        self.move2cost = 70
        self.maxAttack = 120
        self.attack = 0
        
        self.rect = self.image.get_rect()
        self.update()
        
    def name(self):
        return "Freddy"
    
    def getTooltip(self,brief):
        return ""
    
    def update(self):
        if (self.loc == 0):
            #The map starts at [240,40]. This is positioning it relative to the position of the map.
            #This is to make it easier on me to find the proper place in GIMP
            self.rect.topleft = [(240+170),(40 + 40)]
        elif (self.loc == 1):
            self.rect.topleft = [240+10,40+120]
        elif (self.loc == 2):
            self.rect.topleft = [240+220,40+130]
        elif (self.loc == 3):
            self.rect.topleft = [240+65,40+170]
        elif (self.loc == 8):
            self.rect.topleft = [240+117,40+235]
        elif (self.loc == 10):
            self.rect.topleft = [240+60,40+250]
        elif (self.loc == 4):
            self.rect.topleft = [240+320,40+140]
        elif (self.loc == 6):
            self.rect.topleft = [240+222,40+245]
        elif (self.loc == 7):
            self.rect.topleft = [240+235,40+340]
        elif (self.loc == 11):
            self.rect.topleft = [240+210,40+320]

class Bonnie(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/bonnieloc_temp.png')
        self.loc = 0
        self.visible = True
        self.path = [0,1,2,8,10,9,12]
        self.pathstate = 0
        self.move1cost = 10
        self.move2cost = 50
        self.maxAttack = 40
        self.attack = 0
        
        self.rect = self.image.get_rect()
        self.update()
        
    
    def name(self):
        return "Bonnie"
    
    def getTooltip(self,brief):
        return ""
    
    def update(self):
        if (self.loc == 0):
            #The map starts at [240,40]. This is positioning it relative to the position of the map.
            #This is to make it easier on me to find the proper place in GIMP
            self.rect.topleft = [240+190,40 + 40]
        elif (self.loc == 1):
            self.rect.topleft = [240+10,40+120]
        elif (self.loc == 2):
            self.rect.topleft = [240+140,40+130]
        elif (self.loc == 8):
            self.rect.topleft = [240+117,40+235]
        elif (self.loc == 10):
            self.rect.topleft = [240+60,40+250]
        elif (self.loc == 9):
            self.rect.topleft = [240+105,40+340]
        elif (self.loc == 12):
            self.rect.topleft = [240+130,40+320]

class Chica(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/chicaloc_temp.png')
        self.loc = 0
        self.visible = True
        self.path = [0,2,1,4,5,6,7,11]
        self.pathstate = 0
        self.move1cost = 15
        self.move2cost = 50
        self.maxAttack = 80
        self.attack = 0
        
        self.rect = self.image.get_rect()
        self.update()
        
    def name(self):
        return "Chica"
    
    def getTooltip(self,brief):
        return ""
    
    def update(self):
        if (self.loc == 0):
            #The map starts at [240,40]. This is positioning it relative to the position of the map.
            #This is to make it easier on me to find the proper place in GIMP
            self.rect.topleft = [(240+210),(40 + 40)]
        elif (self.loc == 1):
            self.rect.topleft = [240+10,40+120]
        elif (self.loc == 2):
            self.rect.topleft = [240+180,40+170]
        elif (self.loc == 4):
            self.rect.topleft = [240+315,40+180]
        elif (self.loc == 5):
            self.rect.topleft = [240+280,40+270]
        elif (self.loc == 6):
            self.rect.topleft = [240+222,40+245]
        elif (self.loc == 7):
            self.rect.topleft = [240+235,40+340]
        elif (self.loc == 11):
            self.rect.topleft = [240+210,40+320]

class Foxy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/foxyloc_temp.png')
        self.state = 0
        self.visible = False
        
        self.rect = self.image.get_rect()
        self.update()
        
    def name(self):
        return "Foxy"
    
    def getTooltip(self,brief):
        return ""
    
    def update(self):
        if (self.state == 0):
            #The map starts at [240,40]. This is positioning it relative to the position of the map.
            #This is to make it easier on me to find the proper place in GIMP
            self.visible = False
            self.rect.topleft = [240,40]
        elif (self.state == 1):
            self.visible = True
            self.rect.topleft =  [240+35, 40+180]
        elif (self.state == 2):
            self.rect.topleft =  [240+65, 40+190]
        elif (self.state == 3):
            self.rect.topleft = [240+130,40+320]
            
class Camera(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/camera0.png')
        self.loc = -1
        self.visible = False
        
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [240,40]
        self.update()
    
    
    def getTooltip(self,brief):
        return ""
    
    def update(self):
        if (self.loc == -1):
            self.visible = False
        else:
            self.visible = True
            string = 'assets/sprites/camera'
            string += str(self.loc)
            string += '.png'
            self.image = pygame.image.load(string)

class LeftDoorClosed(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/doorclose.png')
        self.visible = False
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [240+146,40+331]
    
    def getTooltip(self,brief):
        return ""
    
class RightDoorClosed(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/doorclose.png')
        self.visible = False
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [240+198,40+331]
    
    def getTooltip(self,brief):
        return ""
        
class TimerText(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.hours = 12
        self.visible = True
        self.font = pygame.font.SysFont("monospace", 20)
        self.image = self.font.render(str(self.hours) + " AM",1,[255,255,255])
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [560,440]
        
    def update(self):
        self.image = self.font.render(" " + str(self.hours) + " AM",1,[255,255,255])
    
    def getTooltip(self,brief):
        return ""
        
class StatusBox(pygame.sprite.Sprite):
    def __init__(self,topleft,size):
        pygame.sprite.Sprite.__init__(self)
        
        self.visible = True
        self.image = pygame.Surface(size)
        self.rect = pygame.Rect(topleft,size)
        self.brieftooltip = ""
        self.fulltooltip = ""
        
        self.image.fill([128,128,128])
        self.image.set_alpha(128)
        pygame.draw.rect(self.image, [255,255,255], pygame.Rect([0,0],size), 5)
        
    def getTooltip(self,brief):
        if brief: return self.brieftooltip
        else: return self.fulltooltip
    
class TextSquare(pygame.sprite.Sprite):
    def __init__(self,topleft,text,centered=False,color=[0,0,0]):
        pygame.sprite.Sprite.__init__(self)
        
        self.visible = True
        self.text = text
        self.centered = centered
        self.font = pygame.font.Font("assets/Courier_New.ttf", 25)
        self.topleft = topleft
        self.image = self.font.render(self.text,1,[0,0,0])
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft
        self.update()
        
    def getTooltip(self,brief):
        return ""
    
    def update(self):
        blackText = self.font.render(self.text,1,[96,96,96])
        #I'm about to do something weird. Where I come from, it's called cheating.
        self.image = self.font.render(self.text,1,[255,255,255])
        #We need to outline this text:
        self.image.blit(blackText,[-1,-1])
        self.image.blit(blackText,[-1,0])
        self.image.blit(blackText,[-1,1])
        self.image.blit(blackText,[0,-1])
        self.image.blit(blackText,[0,1])
        self.image.blit(blackText,[1,-1])
        self.image.blit(blackText,[1,0])
        self.image.blit(blackText,[1,1])
        
        self.image.blit(self.font.render(self.text,1,[255,255,255]),[0,0])
        
        self.rect = self.image.get_rect()
        x = self.rect.width
        if self.centered: self.rect.topleft = [(self.topleft[0] - (x/2)), self.topleft[1]]
        else: self.rect.topleft = self.topleft
        
if __name__  == '__main__': game(None,1,True)
