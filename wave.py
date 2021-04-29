
import pygame, time, math
from pygame.locals import QUIT
import threading as t


"""Algorithm :

problem : To create a sinusodial wave flowing in real time (animation in 2D using pygame)

Breakdown into : 
1. Wavefronts (different wavefronts having different phase angles)
2. Motion of Wavefronts
3. Production of wavefronts
4. Sense of Amplitude(s)
5. Realism

1. Wavefronts :
Each wavefront is a circle of finite initial radius, thickness, color that enlarges as the wave travels.
Every wavefront (with amplitudes of same sign) constituting a wave will have same color (with different alpha values).

2. Motion of wavefronts :
Every wavefront will travel (enlarge its radius) with same speed related to its wavelength

3. Production of wavefronts :
The wavefront just produced may be called initial wavefront.
As soon as it leaves the source, another wavefront must be produced from the production point.
To keep it ideal (maybe made real by applying inverse square law in future) the wavefronts destruct when they reach a certain distance
that can be called as destruction distance (defined only when the wave is ideal otherwise it would eventually die out)

4.Sense of Amplitude(s):
Amplitude of a wavefront can be represented using a color with different alpha value corresponding to the sin of phase
Formula of color opacity : abs(255*(sin(phase)))
for sin(phase) >= 0: color can be red
for sin(phase) < 0: color can be blue (/light blue)

5.Realism:
Wave will obey inverse square law i.e., the intensity of the wave decreases as the square of distance


Implementation:

"""

#globals
pi = math.pi
INITIATE_EXIT = False

def compute_opacity(phase=pi/2):
    sinus_value = math.sin(phase)
    if sinus_value >= 0:
        positive = True
    else:
        positive = False
    return abs(int(255*(sinus_value))), positive

class Wavefront:
    
    def __init__(self, phase=pi/2):
        
        self.phase = phase
        
        self.opacity, sign = compute_opacity(self.phase)
        if sign:
            self.color = (255, 0, 0, self.opacity)
        else:
            self.color = (0, 0, 255, self.opacity)

        self.initial_color = tuple(self.color)
        self.radius = 1
        self.thickness = 2 #px
        
    def draw(self, dis):
        pygame.draw.circle(dis, self.color, (255, 255), self.radius, self.thickness)
    
    def inverse_square(self):

        opacity = int((self.opacity*10000)/(self.radius**2))
        ic = self.initial_color
        if opacity > 255:
            opacity = 255
        if self.radius > 100:
            self.color = (ic[0], ic[1], ic[2], opacity)
            #approximation that the wave has almost same intensity from 0 to 100px
            #after 100px that it varies considerably
        

class Wave:
    
    def __init__(self, initial_phase=pi/2, velocity=30, wavelength=5):
        
        self.velocity, self.wavelength = velocity, wavelength
        self.initial_phase = initial_phase

        frequency = self.velocity/self.wavelength
        self.angular_frequency = 2*pi*frequency
        
        self.phase = self.initial_phase
        
        self.wave_fronts = []
        self.time = 0
        self.destruction_check = False
        
        self.is_flowing = False
        self.destroy = False
        
    def initiate_propagation(self):
        
        t.Thread(target=self.travel).start()
        self.is_flowing = True
        
    def destroy_wavefronts(self):
        
        self.destruction_check = True
        to_remove = []
        
        for i in range(len(self.wave_fronts)):
            j = self.wave_fronts[i]
            if j.radius > 500:
                to_remove.append(j)
        for i in to_remove:
            self.wave_fronts.remove(i)
            
        self.destruction_check = False
        
    def travel(self):

        global INITIATE_EXIT
        
        while not(INITIATE_EXIT):
            
            s = time.time()
            
            #destroying wave_fronts:
            if not(self.destruction_check):
                t.Thread(target=self.destroy_wavefronts).start()
            
            #producing wavefronts
            if not(self.wave_fronts):
                self.wave_fronts.append(Wavefront(phase=self.phase))
            else:
                last_wavefront = self.wave_fronts[len(self.wave_fronts)-1]
                if last_wavefront.radius > 2:
                    self.wave_fronts.append(Wavefront(phase=self.phase))
            
            #moving wavefronts
            for i in self.wave_fronts:
                i.radius += int(self.velocity)
                #decreasing intensity of wavefronts obeying inverse square law
                i.inverse_square()
            
            self.time += 1/60
            self.phase = self.angular_frequency*self.time + self.initial_phase
            
            e = time.time()
            if e-s < 1/60:
                time.sleep((1/60) - (e-s))
            
    def draw(self, dis):
        
        for i in self.wave_fronts:
            i.draw(dis)
            

main_dis = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Progressive Wave Animation", "Made in pygame")

wave_surface = pygame.Surface((500, 500), pygame.SRCALPHA)
main_wave = Wave(velocity=1, wavelength=1)
        

while not(INITIATE_EXIT):
    
    for i in pygame.event.get():
        if i.type == QUIT:
            INITIATE_EXIT = True
            
    
    if not(main_wave.is_flowing):
        main_wave.initiate_propagation()
    
    main_dis.fill((0, 0, 0))
    
    wave_surface.fill((0, 0, 0, 255))
    main_wave.draw(wave_surface)
    
    main_dis.blit(wave_surface, (0, 0))
    
    pygame.display.flip()

pygame.quit()
