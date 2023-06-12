'''
Treadmill Animal Tracking and Feedback Control
(c) Andrew J. Spence
Structure and Motion Lab
Royal Veterinary College
11 Mar 2013
aspence at rvc dot ac dot uk
www.spencelab.com
$ Revision 0.5 Alpha $

The code is released under the GNU GPL Version 3. You should have recieved a copy of this license with this code, in the file `LICENSE.TXT`.

*If you build this system or use this code, please cite the following paper*::

  Spence, A. J., Nicholson-Thomas, G., and Lampe, R. (2013 (in press)).
  "Closing the loop in legged neuromechanics: an open-source computer vision
  controlled treadmill." Journal of Neuroscience Methods.
  http://dx.doi.org/10.1016/j.jneumeth.2013.03.009

We hope that you find this code useful, and we welcome suggestions to improve the code at

http://github.com/aspence/tmilltracker

This code is pre-Alpha and very unstable. No warranty is implied or given on it's performance.

==============================================
Usage:

Tracking from FireWire camera using fast camiface library, and requiring user input of metadata:
    python tmilltracker.py

Ignore metadata and leave at defaults, but can be overriden later with input commands from the menu:
    python tmilltracker.py -I
    
Use slower 12Hz OpenCV highgui for acuisition (does not require import of motmot.pycamiface module):
    python tmilltracker.py --noci

Use a directory full of png images of following format fr00001_20130215_154312p232123.png for video stream:
    python tmilltracker.py -I --imgs ~/mydirectory/fr20130206_165921p382628/
    python tmilltracker.py -I --imgs '/Users/aspence/Documents/work/treadmill/harriet/30hz mouse with without overlay/fr20130205_115303p154501_noover'
'''

import numpy as np, matplotlib as mpl, pylab as pl
import tty, termios, select, sys, os, serial, threading, time, socket, re
import cv
import shelve

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

class TmillSerialInterface:
    '''
    This class handles control of a Panlab treadmill over the serial port.
    It is based on a description of the protocol provided by Panlab s.e.
    '''
    def __init__(self, port, baudrate, parity, rtscts, xonxoff, echo=False):
        try:
            self.serial = serial.serial_for_url(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        except AttributeError:
            # This can happen when pyserial is older than 2.5. 
            # We use the serial class directly in that case
            self.serial = serial.Serial(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        self.verbose=False
        
    def start(self):
        self.buf = ''
        self.alive = True
        self.starttime = time.time()
        # Start recieving thread
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(1)
        self.receiver_thread.start()

    def stop(self):
        self.alive = False

    def join(self):
        self.receiver_thread.join()

    def reader(self):
        """
        This thread loops, parsing any incoming velocity messages 
        and storing them locally. These could be time stamped and
        logged for timing purposes, but at present are not used.
        """
        try:
            while self.alive:
                data = self.serial.read(1)
                # When we get XON, start saving data, when we get XOFF, check for proper format,
                # if so extract speed and store with timestamp.
                if data == '\x11':
                    # Start of packet: clear buffer
                    self.buf = ''
                elif data == '\x13':
                    # End of packet: parse and append to log file:
                    if self.buf[0:6] == 'VELOCI' and len(self.buf)==9:
                        self.spd = int(self.buf[7:9])
                        if self.verbose:
                            sys.stderr.write("VELOCI MSG: " +self.buf+"\n")
                            sys.stderr.flush()
                    else:
                        # Presently unparsed message:
                        if self.verbose:
                            sys.stderr.write("UNKNOWN MSG: " +self.buf+"\n")
                            sys.stderr.flush()
                        self.buf = ''
                else:
                    # Add character to buffer:
                    self.buf = self.buf + data                
        except serial.SerialException, e:
            self.alive = False
            raise
            
    def tcontrol(self,onoff,verbose=False):
        # Set PC control of treadmill on/off
        if onoff:
            # Send on message
            if verbose:
                sys.stderr.write('Sending PC OONN message ...\n')        
                sys.stderr.flush()
            self.serial.write('\x11PC OONN\x13')
            return True # should check here
        else:
            if verbose:
                sys.stderr.write('Sending PC OOFF message ...\n')        
                sys.stderr.flush()
            self.serial.write('\x11PC OOFF\x13')

    def runstop(self,runstop,verbose=False):
        # Set treadmill to RUN or STOP
        if runstop:
            if verbose:
                sys.stderr.write('Sending RUN**** message ...\n')
                sys.stderr.flush()
            self.serial.write('\x11RUN****\x13')
        else:
            if verbose:
                sys.stderr.write('Sending STOP*** message ...\n')
                sys.stderr.flush()
            self.serial.write('\x11STOP***\x13')
    
    def setspd(self,spd,verbose=False):
        # Set treadmill speed:
        msg = '\x11VELOCID%03d\x13' % spd
        if verbose:
            sys.stderr.write('Sending ' + msg + ' message ...\n')
            sys.stderr.flush()
        self.serial.write(msg)

class TmillTracker():
    '''
    This class handles the majority of tracking the animal and controlling the
    treadmill.
    '''
    def __init__(self, haveserial=True, noci=False, imgs="",debug=False ):
        # Store options
        self.debug=debug
        self.host = 'crunch2' #remote host
        self.port = 50002 # must match open port on host        
        self.useci = not noci
        self.state = "idle"
        self.roiinput = False
        self.measureinput = False
        self.drawline = False
        self.drawroi = False
        self.usekalman = True        
        self.imgs = imgs
        self.roipt1 = (27, 279)
        self.roipt2 = (618, 409)
        d = shelve.open("shelf")
        if (d.has_key("roipt1") and d.has_key("roipt2")):
            self.roipt1 = d["roipt1"]
            self.roipt2 = d["roipt2"]
        self.roirect = (self.roipt1[0],self.roipt1[1],self.roipt2[0]-self.roipt1[0],self.roipt2[1]-self.roipt1[1])
        self.setpt = 0.5 # Set point for controller -- 50% of treadmill
        self.areapct = 0.7 # Take contours with area +- 70% around given value e.g. 2200. High value for robustness.       
        self.area = 2200
        self.thresh = 70 # Threshold for contour finding, out of 255 for 8 bit images.
        if d.has_key("thresh"):
            self.thresh=d["thresh"]
        # BETTER SETTINGS FOR MOUSE 09/05/2013 kp = 0.35, kd=20
        # at kp=0.5, kd=10, mouse was getting far up belt before it caught them
        # at kp = 0.35, kd=15, better, smooth ramp up with mouse, still getting far forward though and then fast catch
        # Previous PD settings were driving current mouse to back of treadmill, reducing p gait slightly to compensate. Previous settings kp=0.35, kd=15
        # Just lower p gain to 0.25 and leave d gain at 15 and see how we do.
        self.kp = 0.25 # Position gain at 15 fps. Not that will be scaled by actual framerate used. Works well at 30 fps with gui on. Jumpy at 150 fps.
        self.kd = 15 # See below
        self.tmillwidth = 410*0.001 # 41 cm belt, see specs of Panlab.
        if(d.has_key("tmillwidth")):
            self.tmillwidth = d["tmillwidth"]
        self.updaterates = { "guioff":{"video":150.0,"serial":50.0}, "guion":{"video":30.0,"serial":30.0}, "noci":{"video":12,"serial":12} }
        self.logging = False
        self.logstarttime = np.nan
        self.keyinput = False
        self.camcap = None
        self.cvwindow = False
        self.alive = True
        self.verbose = False
        self.prevwn = "Tracker preview image"
        self.tcontrol = False
        self.trunning = False
        self.vidwriting = False
        self.framewriting = False
        self.behavtrig = False
        self.perturb = False
        self.applyingpert = False
        self.pertdur = 0.2          # Perturbation lasts 200ms, down and up ramps
        self.pertfrac = 0.5         # Perturbation loses 100% of current speed
        self.pertresponsedur = 0.75  # Seconds to record after perturbation finishes.
        self.pertvidsavetime = -1
        self.pertwait = 10.0
        self.pertendtime = -np.Inf
        self.guion = True
        self.tmspd = 0
        # Load left and right bracket key speeds if stored
        if(d.has_key("lbrk_spd")):
            self.lbrk_spd = d["lbrk_spd"]
        else:
            self.lbrk_spd = 15
        if(d.has_key("rbrk_spd")):
            self.rbrk_spd = d["rbrk_spd"]
        else:
            self.rbrk_spd = 30
        self.pa = cv.CreateMat(1,1, cv.CV_32FC2)
        self.haveserial = haveserial
        self.fliplr = False
        self.overlay = True
        self.lasttracktime = time.time()
        self.lastserial = time.time()
        self.grabstop = -np.inf
        self.lastsercmdtime = -np.inf
        self.trackdata = np.empty((150*3600,18,)) # at 150 FPS buffer for 1 hour data, 18 columns.
        self.framenum = 0
        self.animalnum = -1
        self.trialnum = 1
        self.weight = -1
        self.notes = ''
        self.startBehavior = -1
        self.endBehavior = -1
        self.animspd = 0.0
        self.invert = False
        self.capsecs = 1.0
        # Give lastgoodtracktime a value because np.nan implies have a good track.
        # Setting to a time will cause slowdown if we have no track.
        self.lastgoodtracktime = time.time()
        self.timesincetrack = time.time() - self.lastgoodtracktime
        d.close()
        if self.usekalman:
            self.setupKalman()
        self.setUpdateRates()

    def get_help_text(self):
        return """=== TmillTracker 0.5 alpha - help ===
---
--- Escape or 'q' - Exit program
--- h             - Print this help menu
--- s             - Display settings
--- v             - Toggle verbosity
--- p             - Toggle single preview image capture from camera
--- u             - Update preview image
--- o             - Set ROI for treadmill video tracker on preview image
                  - NOTE: Click top left first then drag to bottom right and release
--- H             - Set threshold for finding contours: default = 70; range 0-255
--- d             - Display live video feed
--- c             - Toggle control treadmill
--- r             - Toggle treadmill run/stop
--- 0-9           - Set treadmill speed 0 - 90 cm/s
--- [, ]          - Set speed to preset values. Default [=15 cm/s, ]=30 cm/s
--- shift-[, -]   - Set the preset speed value of these keys.  
--- C             - Calibrate length scale
--- a             - Calibrate animal size ellipse
--- M             - Measure and set ellipse area
--- n             - Set animal ID number
--- N             - Input notes string for trial
--- T             - Set trial number
--- l             - Toggle data logging (autostarts with feedback mode)
---               - Toggle belt speed polling (not implemented yet)
---               - Toggle digital trigger time stamp (req AD board and comedi) (not implemented)
--- t             - Toggle video tracking of animal (number keys 0-9 work to manually set belt speed)
--- f             - Toggle belt feedback control mode
--- V             - Log video to file
--- F             - Log video Frames
--- b             - Behaviour trigger (High speed video record)
--- <return>      - Store last 2 seconds of HSV (in tracking mode only)
--- e             - Tell HS camera code to Exit
--- S             - Save current trackdata to shelf
--- O             - Toggle Overlay on images on screen and disk: speed, FPS, etc.
--- g             - Toggle GUI display of video on/off
--- P             - Toggle Perturbation mode on/off
--- i             - Toggle invert image (use for white mice)
"""
    
    def getSettings(self):
        return """
--- Settings ---
ROI: (top: %d, left: %d, width %d, height %d)
Video rate: %d
Serial rate: %d
Elipse area: %d
Threshold for contour detection: %d
Treadmill width calibration (meters): %f
Overlay: %d
Animal num: %d
Trial num: %d
Weight: %3.3f
Notes: %s
Left bracket key speed: %d
Right bracket key speed: %d
""" % (self.roirect + (self.vidrate,self.serialrate,self.area,self.thresh,self.tmillwidth,self.overlay,self.animalnum,self.trialnum,self.weight,self.notes,self.lbrk_spd,self.rbrk_spd))
        
    def mouseHandler(self,event,x,y,flags,param):
        if self.roiinput:
            if event == cv.CV_EVENT_LBUTTONDOWN:
                # Store click
                self.roipt1 = (x, y)
                self.drawroi = True
            elif event == cv.CV_EVENT_MOUSEMOVE:
                # Draw a rectangle
                if self.drawroi:
                    img1 = cv.CloneImage(self.prevfr);
                    cv.Rectangle(img1, (self.roipt1[0], self.roipt1[1]), (x,y), cv.Scalar(0, 0, 255, 0), 2, 8, 0)
                    cv.ShowImage(self.prevwn,img1)
            elif event == cv.CV_EVENT_LBUTTONUP:
                self.drawroi = False
                self.roiinput = False
                self.roipt2 = (x,y)
                self.roirect = (self.roipt1[0],self.roipt1[1],self.roipt2[0]-self.roipt1[0],self.roipt2[1]-self.roipt1[1])
                print "ROI set to x1 %d y1 %d x2 %d y2 %d" % (self.roipt1[0], self.roipt1[1],self.roipt2[0],self.roipt2[1])
                self.prevfr = self.getGrayImage()
                # Overlay new ROI
                cv.Rectangle(self.prevfr, (self.roipt1[0], self.roipt1[1]), (self.roipt2[0],self.roipt2[1]), cv.Scalar(0, 0, 255, 0), 2, 8, 0)
                cv.ShowImage(self.prevwn,self.prevfr)
                # Save new ROI
                d = shelve.open("shelf")
                d["roipt1"] = self.roipt1
                d["roipt2"] = self.roipt2
                d.close()

        if self.measureinput:
            if event == cv.CV_EVENT_LBUTTONDOWN:
                # Store click
                self.mpt1 = (x, y)
                self.drawline = True
            elif event == cv.CV_EVENT_MOUSEMOVE:
                # Draw line
                if self.drawline:
                    img1 = cv.CloneImage(self.prevfr);
                    cv.Line(img1, (self.mpt1[0], self.mpt1[1]), (x,y), cv.Scalar(0, 0, 255, 0), 2, 8, 0)
                    cv.ShowImage(self.prevwn,img1)
            elif event == cv.CV_EVENT_LBUTTONUP:
                self.drawline = False
                self.measureinput = False
                self.mpt2 = (x,y)
                measlength = np.sqrt((self.mpt1[0]-self.mpt2[0])**2.0 + (self.mpt1[1]-self.mpt2[1])**2.0 )
                print "Line length: %f\n" % measlength
                self.prevfr = self.getGrayImage()
                # Overlay new ROI
                cv.Line(self.prevfr, (self.mpt1[0], self.mpt1[1]), (x,y), cv.Scalar(0, 0, 255, 0), 2, 8, 0)
                cv.ShowImage(self.prevwn,self.prevfr)
                print "Ellipse area based on this length (width=1.8x length) = %f\n" % (np.pi*measlength*measlength/(1.8*4.0))
                print "Setting area to this value.\n"
                self.area = np.pi*measlength*measlength/(1.8*4.0)

    def openCam(self):
        # Start a capture using opencv_highgui or libcamiface
        if self.imgs == "":
            if self.useci:
                mode_num = 6
                device_num = 0
                num_buffers = 1
                self.camcap = cam_iface.Camera(device_num,num_buffers,mode_num)
                self.camcap.start_camera()
                self.camcap.set_framerate(420)
            else:
                # Handle roi manually: grab whole frame then copy sub
                self.camcap = cv.CaptureFromCAM(0)
        else:
            # Make camcap the list of image files in the dir given in imgs
            # fr08096_20130206_170005p540540.png
            pat="fr\d\d\d\d\d_.*\.png$"
            self.camcap=list()
            for root, dirs, files in os.walk(self.imgs):
                for f in files:
                    if re.search(pat,f):
                        self.camcap.append(os.path.join(root,f))
                        # Keep following code snippet in case we want frame loading speed test function.
                        if 0:
                            now=time.time()
                            im=cv2.imread(fullfile)
                            done=time.time()
                            print "%.3f FPS reading %s with cv2 imread" % (1.0/(done-now),fullfile)
                            now=time.time()
                            im=cv2.cv.LoadImage(fullfile)
                            done=time.time()
                            print "%.3f FPS reading %s with cv LoadImage" % (1.0/(done-now),fullfile)
            print "Found %d images of type frXXXXX_XX_XXpXX.png in dir %s" % (len(self.camcap),self.imgs)
            self.currfr = 0
            # Need to set ROI size to that of these images:
            testfr=self.getGrayImage()
            self.roipt1 = (1, 1)
            self.roipt2 = (testfr.width+1,testfr.height+1)
            self.roirect = (self.roipt1[0],self.roipt1[1],self.roipt2[0]-self.roipt1[0],self.roipt2[1]-self.roipt1[1])
            self.currfr = 0
            
    def makeROIimage(self):
        # Uses ROI pts to allocate roiimage:
        self.roisize = (self.roipt2[0]-self.roipt1[0],self.roipt2[1]-self.roipt1[1])
        self.roirect = (self.roipt1[0],self.roipt1[1],self.roipt2[0]-self.roipt1[0],self.roipt2[1]-self.roipt1[1])
        self.roiimg = cv.CreateImage(self.roisize, 8, 1)        
        if self.debug:
            print "roipt1",self.roipt1
            print "roipt2",self.roipt2
            print "roisize",self.roisize
            print "roimg getsize",cv.GetSize(self.roiimg)
    
    def getGrayImage(self):
        if type(self.camcap) is list:
            if self.currfr == (len(self.camcap)-1):
                self.currfr = 0
            #print "Loading frame %s" % self.camcap[self.currfr]
            newfr = cv.LoadImage(self.camcap[self.currfr])
            self.grabstop=time.time()
            self.currfr=self.currfr+1
        elif type(self.camcap) is not None:
            if self.useci:
                if self.verbose:
                    print "Processing time: %f\n" % (time.time()-self.grabstop)
                self.grabstart=time.time()
                newfr = cv.fromarray(np.asarray(self.camcap.grab_next_frame_blocking()))
                self.grabstop=time.time()
                if self.verbose:
                    print "Grab time: %f\n" % (self.grabstop-self.grabstart)      
            else:
                newfr = cv.QueryFrame(self.camcap)
                self.grabstop=time.time()
        else:
            print "ERROR! No valid camera capture object or directory of images found!"
        if self.fliplr:
            cv.Flip( newfr, None, 1 );
        if newfr.channels is not 1:
            newbgfr = cv.CreateImage(cv.GetSize(newfr),8,1)
            cv.CvtColor(newfr,newbgfr,cv.CV_RGB2GRAY)
            if self.invert:
                cv.SubRS(newbgfr,cv.Scalar(255),newbgfr)
            return newbgfr
        else:
            if self.invert:
                cv.SubRS(newfr,cv.Scalar(255),newfr)
            return newfr
    
    def setupKalman(self):
        # Setup Kalman:
        A = [ [1, 1], [0, 1] ]
        # CreateKalman(dynam_params, measure_params, control_params=0)
        #Allocates the Kalman filter structure.
        #Parameters:	
        #    dynam_params (int) dimensionality of the state vector
        #    measure_params (int) dimensionality of the measurement vector
        #    control_params (int) dimensionality of the control vector
        # state: 4D: x,y,vx,vy measure: 2D: x,y 
        self.kalman = cv.CreateKalman(4, 2, 0)
        self.kalmanstate = cv.CreateMat(4, 1, cv.CV_32FC1)  # (x,y,vx,vy)
        # Not currently used -> this is for generated data
        self.process_noise = cv.CreateMat(2, 1, cv.CV_32FC1)
        self.measurement = cv.CreateMat(2, 1, cv.CV_32FC1)
        self.prediction = cv.CreateMat(4, 1, cv.CV_32FC1)
        # Not currently used -> range for random generated
        rng = cv.RNG(-1)
        code = -1L
        cv.Zero(self.measurement)
        # Fills with normal values mean zero sigma 0.1. Uses rng random generator object with state
        cv.RandArr(rng, self.kalmanstate, cv.CV_RAND_NORMAL, cv.RealScalar(0), cv.RealScalar(0.1))
        # What does our matrix look like? 4x4, x = x0 + vx dt
        # [1 0 dt 0][x]
        # [0 1 0 dt][y]
        # [0 0 1  0][vx]
        # [0 0 0  1][vy]
        # [row, col]
        tm = np.array([[ 1.,  0.,  1.,  0.,],\
                       [ 0.,  1.,  0.,  1.,],\
                       [ 0.,  0.,  1.,  0.,],\
                       [ 0.,  0.,  0.,  1.]])
        # The following assignment doens't work. Setting each element seems ridiculous -- but can't find
        # workaround. Migrating to cv2 in the future should help.
        #self.kalman.transition_matrix=cv.fromarray(tm)
        self.kalman.transition_matrix[0,0] = 1
        self.kalman.transition_matrix[0,1] = 0
        self.kalman.transition_matrix[0,2] = 1 # pixels/frame
        self.kalman.transition_matrix[0,3] = 0
        self.kalman.transition_matrix[1,0] = 0
        self.kalman.transition_matrix[1,1] = 1
        self.kalman.transition_matrix[1,2] = 0
        self.kalman.transition_matrix[1,3] = 1
        self.kalman.transition_matrix[2,0] = 0
        self.kalman.transition_matrix[2,1] = 0
        self.kalman.transition_matrix[2,2] = 1
        self.kalman.transition_matrix[2,3] = 0
        self.kalman.transition_matrix[3,0] = 0
        self.kalman.transition_matrix[3,1] = 0
        self.kalman.transition_matrix[3,2] = 0
        self.kalman.transition_matrix[3,3] = 1
        #print np.asarray(self.kalman.transition_matrix)
        # Measurement matrix - we only see positions:
        # MxN X NxJ
        # [1 0 0 0][x]
        # [0 1 0 0][y]
        #          [vx]
        #          [vy]
        self.kalman.measurement_matrix[0,0] = 1
        self.kalman.measurement_matrix[0,1] = 0
        self.kalman.measurement_matrix[0,2] = 0
        self.kalman.measurement_matrix[0,3] = 0
        self.kalman.measurement_matrix[1,0] = 0
        self.kalman.measurement_matrix[1,1] = 1
        self.kalman.measurement_matrix[1,2] = 0
        self.kalman.measurement_matrix[1,3] = 0
        #print np.asarray(self.kalman.transition_matrix)
        # Process noise incorporates animal dynamics.
        # Measurement noise may be interpreted as just that: 0.1 pixels for x, y. This could be higher.
        # Value here are 30 Hz, default starting point for tracker:
        cv.SetIdentity(self.kalman.process_noise_cov, cv.RealScalar(5e-2))
        #print np.asarray(self.kalman.process_noise_cov)
        cv.SetIdentity(self.kalman.measurement_noise_cov, cv.RealScalar(1e-1))
        #print np.asarray(self.kalman.measurement_noise_cov)
        cv.SetIdentity(self.kalman.error_cov_post, cv.RealScalar(1))
        #print np.asarray(self.kalman.error_cov_post)
        cv.Set(self.kalman.state_pre,cv.Scalar(0))
        cv.RandArr(rng, self.kalman.state_post, cv.CV_RAND_NORMAL, cv.RealScalar(0), cv.RealScalar(0.1))
        #print np.asarray(self.kalman.state_post)

    def setUpdateRates(self):
        if self.useci:
            if self.guion:
                self.vidrate = self.updaterates["guion"]["video"]
                self.serialrate = self.updaterates["guion"]["serial"]
                if self.usekalman:
                    # Set Kalman gains for 30 Hz:
                    cv.SetIdentity(self.kalman.process_noise_cov, cv.RealScalar(5e-2))
                    cv.SetIdentity(self.kalman.measurement_noise_cov, cv.RealScalar(1e-1))
            else:
                self.vidrate = self.updaterates["guioff"]["video"]
                self.serialrate = self.updaterates["guioff"]["serial"]
                if self.usekalman:
                    # Set Kalman gains for 150 Hz:
                    # 21-02-2013: These values too fast at 150 Hz, need more smoothing. Factor five decrease in proc noise to 1e-3?
                    # 21-02-2013: Above was better, could still be smoother. Another factor of two.
                    cv.SetIdentity(self.kalman.process_noise_cov, cv.RealScalar(5e-4))
                    cv.SetIdentity(self.kalman.measurement_noise_cov, cv.RealScalar(1e-1))
        else:
            self.vidrate = self.updaterates["noci"]["video"]
            self.serialrate = self.updaterates["noci"]["serial"]
            if self.usekalman:
                cv.SetIdentity(self.kalman.process_noise_cov, cv.RealScalar(1e-1))
                cv.SetIdentity(self.kalman.measurement_noise_cov, cv.RealScalar(1e-1))
        # We multiply by this, e.g. 15.0/30.0 factor, to slow feedback.
        # Feedback gains tuned for 15 Hz update rate, base future rates off of this.
        self.rateadjust = 15.0 / self.serialrate

    def storeLengthCal(self):
        self.tmillwidth = float(self.keybuf)
        sys.stderr.write('\nSetting treadmill width calibration to %f meters\n' % self.tmillwidth )
        # Save new length calibration
        d = shelve.open("shelf")
        d["tmillwidth"] = self.tmillwidth
        d.close()

    def storeArea(self):
        self.area = float(self.keybuf)
        sys.stderr.write('\nSetting animal ellipse target area to %f\n' % self.area )

    def storeThresh(self):
        self.thresh = float(self.keybuf)
        sys.stderr.write('\nSetting threshold for countour detection to %d\n' % self.thresh )
        # Save new threshold
        d = shelve.open("shelf")
        d["thresh"] = self.thresh
        d.close()

    def storeAnimalNum(self):
        self.animalnum = int(self.keybuf)
        sys.stderr.write('\nSetting animal number to %d\n' % self.animalnum )

    def storeTrialNum(self):
        self.trialnum = int(self.keybuf)
        sys.stderr.write('\nSetting trial number to %d\n' % self.trialnum )

    def storeWeight(self):
        self.weight = int(self.keybuf)
        sys.stderr.write('\nSetting weight to %3.3f\n' % self.weight )

    def storeNotes(self):
        self.notes = str(self.keybuf)
        sys.stderr.write('\nSetting notes to %s\n' % self.notes )

    def storeLeftBrkSpd(self):
        self.lbrk_spd = int(self.keybuf)
        sys.stderr.write('\nSetting left bracket key speed to %d, and saving settings.\n' % self.lbrk_spd )
        d = shelve.open("shelf")
        d["lbrk_spd"] = self.lbrk_spd
        d.close()

    def storeRightBrkSpd(self):
        self.rbrk_spd = int(self.keybuf)
        sys.stderr.write('\nSetting right bracket key speed to %d, and saving this setting.\n' % self.rbrk_spd )
        d = shelve.open("shelf")
        d["rbrk_spd"] = self.rbrk_spd
        d.close()
    
    def makeTimeStampStr(self,epochtime):
        return time.strftime("%Y%m%d_%H%M%Sp",time.localtime(epochtime)) + ("%0.6f" % (epochtime % 1))[2:]
        
    def getLengthCal(self):
        sys.stderr.write('Old treadmill width: %f meters\n' % self.tmillwidth )
        sys.stderr.write("New width of treadmill belt (ROI) in meters:")
        self.keycallback = self.storeLengthCal
        self.keybuf = ""
        self.keyinput = True

    def getThresh(self):
        sys.stderr.write('Old threshold: %d\n' % self.thresh )
        sys.stderr.write("New threshold (0-255; default 70 for black mice on white bg): ")
        self.keycallback = self.storeThresh
        self.keybuf = ""
        self.keyinput = True
        
    def getanimalnum(self):
        sys.stderr.write('Old animal num: %d\n' % self.animalnum )
        sys.stderr.write("Enter new animal ID number:")
        self.keycallback = self.storeAnimalNum
        self.keybuf = ""
        self.keyinput = True

    def getTrialNum(self):
        sys.stderr.write('Old trial num: %d\n' % self.trialnum )
        sys.stderr.write("Enter new trial number:")
        self.keycallback = self.storeTrialNum
        self.keybuf = ""
        self.keyinput = True

    def getWeight(self):
        sys.stderr.write("Enter new weight:")
        self.keycallback = self.storeWeight
        self.keybuf = ""
        self.keyinput = True
       
    def getNotes(self):
        sys.stderr.write('Old notes: %s\n' % self.notes )
        sys.stderr.write("Enter new trial notes: ")
        self.keycallback = self.storeNotes
        self.keybuf = ""
        self.keyinput = True

    def getLbrkSpd(self):
        sys.stderr.write('Old left bracket speed (cm/s): %d\n' % self.lbrk_spd )
        sys.stderr.write("Enter new speed setting for left bracket key: ")
        self.keycallback = self.storeLeftBrkSpd
        self.keybuf = ""
        self.keyinput = True

    def getRbrkSpd(self):
        sys.stderr.write('Old right bracket speed (cm/s): %d\n' % self.rbrk_spd )
        sys.stderr.write("Enter new speed setting for right bracket key: ")
        self.keycallback = self.storeRightBrkSpd
        self.keybuf = ""
        self.keyinput = True
        
    def getInitial(self):
        self.animalnum = int(raw_input('Enter animal number: '))
        self.weight = float(raw_input('Enter weight: '))
        self.trialnum = int(raw_input('Enter trial number: '))
        self.notes = raw_input('Enter notes for trial: ')
        
    def handleInput(self,c):
        if self.verbose:
            sys.stderr.write('Got char: ordinal %d\n' % ord(c) )
        if c == '\x1b': # x1b is ESC - Always check this first for quick exit
            self.alive = False
        elif self.keyinput == True:
            if c == '\x0A': # This is ordinal 10 = Line Feed. Get these from terminal carriage return input.
                # Then call the function stored in self.keycallback to process the buffer
                self.keycallback()
                self.keyinput = False
                self.keybuf = ""
            else:
                # Store chars in a buffer until return
                sys.stderr.write( c )
                self.keybuf = self.keybuf + c
        elif c == 's': # Display settings
            sys.stderr.write(self.getSettings())
        elif c == 'C': # Get length calibration.
            self.getLengthCal()
        elif c == 'n': # Get animal number
            self.getanimalnum()
        elif c == 'T': # Input trial number for this trial
            self.getTrialNum()
        elif c == 'w': # Input weight for this trial
            self.getWeight()
        elif c == 'N': # Input notes for this trial
            self.getNotes()
        elif c =='{':
            if self.state=="idle":
                self.getLbrkSpd()
        elif c =='}':
            if self.state=="idle":
                self.getRbrkSpd()
        elif c == 'a': # New animal ellipse area:
            sys.stderr.write('Old animal ellipse area: %f\n' % self.area )
            sys.stderr.write("New ellipse area:")
            self.keycallback = self.storeArea
            self.keybuf = ""
            self.keyinput = True
        elif c == 'H': # Threshold:
            if self.state=="idle":
                self.getThresh()
            else:
                sys.stderr.write("Can only set threshold in idle mode")
        elif c == 'M': # Measure new animal area:
            if self.state == 'preview':
                self.measureinput = not self.measureinput
            else:
                sys.stderr.write('  CAN ONLY MEASURE IN PREVIEW MODE: hit p\n' )
        elif c == 'q':         # also quit on q if not in keyboard input mode:
            self.alive = False
        elif c == 'h':
            sys.stderr.write(self.get_help_text())
        elif c == 'v':
            self.verbose = not self.verbose
            if self.haveserial:
                self.tsinter.verbose = not self.tsinter.verbose
            if self.verbose:
                sys.stderr.write('Verbosity: ON\n' )
            else:
                sys.stderr.write('Verbosity: OFF\n' )
        elif c == 'g':
            self.guion = not self.guion
            self.setUpdateRates()             
        elif c == 'p':
            # Make p toggle the preview - can only go into from idle
            if self.state == 'idle':                
                try:
                    if self.camcap is None:
                        self.openCam()
                    # Not in useci mode, will grab full frame
                    self.prevfr = self.getGrayImage() 
                    # Overlay current ROI
                    cv.Rectangle(self.prevfr, (self.roipt1[0], self.roipt1[1]), (self.roipt2[0],self.roipt2[1]), cv.Scalar(0, 0, 255, 0), 2, 8, 0)
                    cv.NamedWindow(self.prevwn, cv.CV_WINDOW_AUTOSIZE)
                    cv.ShowImage(self.prevwn,self.prevfr)
                    cv.SetMouseCallback(self.prevwn, self.mouseHandler, None)
                    self.cvwindow = True
                    self.state = 'preview'
                except:
                    sys.stderr.write('Unable to open camera with cv.CaptureFromCAM(0).\n')
            elif self.state == 'preview':
                # Close down the preview
                # Switch back to idle
                cv.DestroyWindow(self.prevwn)
                self.cvwindow = False
                # Give opencv a few chances to close the window
                for k in range(10):                
                    c = cv.WaitKey(10)
                del(self.camcap)
                self.camcap = None
                self.state = "idle"
        elif c == 'u':
            if self.verbose:
                sys.stderr.write('Updating preview\n')
            try:
                self.prevfr = self.getGrayImage()
                # Overlay current ROI
                cv.Rectangle(self.prevfr, (self.roipt1[0], self.roipt1[1]), (self.roipt2[0],self.roipt2[1]), cv.Scalar(0, 0, 255, 0), 2, 8, 0)
                cv.ShowImage(self.prevwn,self.prevfr)
            except:
                std.stderr.write('Unable to get new frame.\n')
        elif c == 'o':
            if self.state == 'preview':
                self.roiinput = not self.roiinput
        elif c == 'd':
            # First check if we are given image sequence input, cannot display as only have ROIs
            if self.imgs != "":
                print "Cannot go into display mode given image sequence, only have ROIs"
                return
            # if we are in idle go into display
            # if we are in other modes, ignore
            if self.state == "idle":
                self.makeROIimage()
                if self.camcap is None:
                    self.openCam()
                # Not in useci mode, will grab full frame
                self.prevfr = self.getGrayImage()                      
                cv.Copy(cv.GetSubRect(self.prevfr,self.roirect),self.roiimg)
                print "Got Image"                     
                cv.NamedWindow(self.prevwn, cv.CV_WINDOW_AUTOSIZE)
                cv.ShowImage(self.prevwn,self.prevfr)
                self.cvwindow = True
                self.state = "display"
            elif self.state == "display":
                # Switch back to idle
                cv.DestroyWindow(self.prevwn)
                self.cvwindow = False
                # Give opencv a few chances to close the window
                for k in range(10):                
                    c = cv.WaitKey(10)
                del(self.camcap)
                self.camcap = None
                self.state = "idle"
        elif c == 't':
            # Go into tracking mode
            if self.state == "idle":
                # Difference order from display!
                if self.camcap is None:
                    self.openCam() # This also adjusts ROI if in files mode
                self.makeROIimage()
                self.filtimg = cv.CreateImage(self.roisize, 8, 1)
                self.storage = cv.CreateMemStorage(0)
                #print cv.GetSize(self.roiimg)
                #print self.roirect
                # Frame should be roi size, copy to cv image:
                self.prevfr = self.getGrayImage()
                #print self.camcap.get_frame_roi()
                print "Prevfr size:"
                print cv.GetSize(self.prevfr)
                print "ROI Size:"
                print cv.GetSize(self.roiimg)
                if self.imgs != "":
                    cv.Copy(self.prevfr,self.roiimg)
                else:
                    cv.Copy(cv.GetSubRect(self.prevfr,self.roirect),self.roiimg)
                cv.NamedWindow(self.prevwn, cv.CV_WINDOW_AUTOSIZE)
                self.cvwindow = True               
                cv.ShowImage(self.prevwn,self.roiimg)
                self.trackstarttime = time.time()
                self.lasttrack=-np.inf
                self.state = "tracking"
                if sys.platform == 'darwin':
                    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
            elif self.state == "tracking":
                # Switch back to idle
                cv.DestroyWindow(self.prevwn)
                self.cvwindow = False
                # Give opencv a few chances to close the window
                for k in range(10):                
                    c = cv.WaitKey(10)
                del(self.camcap)
                self.camcap = None
                self.state = "idle"
                if self.logging:
                    self.stopLogging()
                    self.logging = False
        elif c == 'f':
            # Go into feedback control mode
            if self.state == "idle":              
                # Get tracking setup
                self.makeROIimage()
                self.filtimg = cv.CreateImage(self.roisize, 8, 1)
                self.storage = cv.CreateMemStorage(0)
                # Start camera
                if self.camcap is None:
                    self.openCam()
                # Setup windows, grab and display
                cv.NamedWindow(self.prevwn, cv.CV_WINDOW_AUTOSIZE)
                self.cvwindow = True
                self.prevfr = self.getGrayImage()                      
                cv.Copy(cv.GetSubRect(self.prevfr,self.roirect),self.roiimg)
                cv.ShowImage(self.prevwn,self.roiimg)
                # Setup serial
                if self.haveserial:
                    # Get control of belt:
                    self.tcontrol = self.tsinter.tcontrol(True,self.verbose)
                    time.sleep(0.2)
                    if not self.tcontrol:
                        print "UNABLE TO GET CONTROL OF TMILL"
                    # Set speed to zero, then run:
                    self.tsinter.setspd(0,self.verbose)
                    time.sleep(0.2)
                    self.tmspd = 0
                    self.tsinter.runstop(True,self.verbose)
                    time.sleep(0.2)
                    self.trunning = True
                self.trackstarttime = time.time() 
                self.lastfeedback = -np.inf
                self.lastserial=-np.inf               
                self.state = "feedback"
                sys.stderr.write("Feedback mode ON\n")
            elif self.state == "feedback":
                # Stop the treadmill
                if self.haveserial:
                    self.tsinter.runstop(False,self.verbose)
                    self.tsinter.setspd(0,self.verbose)
                # Switch back to idle
                cv.DestroyWindow(self.prevwn)
                self.cvwindow = False
                # Give opencv a few chances to close the window
                for k in range(10):                
                    c = cv.WaitKey(10)
                del(self.camcap)
                self.camcap = None
                self.state = "idle"
                sys.stderr.write("Feedback mode OFF\n")
                # Shut down vidwriter if on
                if self.vidwriting:
                    del(self.vidwriter)
                    self.vidwriter = None
                    self.vidwriting = False
                if self.logging:
                    self.stopLogging()
                    self.logging = False
                    sys.stderr.write("Logging mode OFF\n")                    
        elif c == 'b':
            if self.state == "feedback" or self.state == "tracking":
                self.behavtrig = not self.behavtrig
                print "Behavioural trigger set to %s." % self.behavtrig
            else:
                print "Cant turn off or off behavioural trigger except in feedback or tracking mode."
        elif c == '\x0D' or c == '\x0A': # Carriage return = 0x0D = 13: note that these come from OpenCV window on hitting enter, whereasa 0x0A == 10 comes from terminal enter. User may hit enter into either.
            # If we are in tracking mode, and user hits carriage return, save X secs of high speed video
            if self.state == "tracking" or self.state == "feedback":
                #send packet to trigger camera to capture last capsecs seconds
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    now = time.time()
                    print "Sending request to HSV machine store %d seconds up to present time." % (self.capsecs)
                    s.connect((self.host, self.port))
                    s.send("%.6f %.6f" % (now-self.capsecs,now) )
                except:
                    print "Error connecting"
                finally:
                    print 'closing socket!'
                    s.close()
            else:
                print "<enter> stores high speed video in tracking mode only"
        elif c == 'i':
            if not self.invert:
                self.invert = True
                print "Invert image set to True"
            else:
                self.invert = False
                print "Invert image set to False"
        elif c == 'P':
            if self.state == "feedback":
                self.perturb = not self.perturb
                print "PERTURBATION set to %s." % self.perturb
            else:
                print "Cant turn off or off PERTURBATION mode except in feedback mode."                        
        elif c == 'e':
            # send packet to tell hsv camera code to exit
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((self.host, self.port))
                s.send("exit")
                data = s.recv(1024)
                print 'Received', repr(data)
            except:
                print "Error connecting"
            finally:
                s.close()            
        # =========== NEW CODE HERE ===========
        elif c == 'm':
            # send packet to tell hsv camera code to toggle streaming to disk
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((self.host, self.port))
                s.send("togglestreaming")
                data = s.recv(1024)
                print 'Received', repr(data)
            except:
                print "Error connecting"
            finally:
                s.close()          
        elif c == 'V':
            if self.state == "feedback":
                if not self.vidwriting:
                    # Try IYUV or I420 for uncompressed in AVI container
                    # CreateVideoWriter(filename, fourcc, fps, frame_size [, is_color])
                    # Sort file name + placement as below
                    self.vidwriter = cv.CreateVideoWriter('vid.avi', cv.CV_FOURCC('I','4','2','0'), self.vidrate, self.roisize)
                    self.vidwriting = True
                else:
                    del(self.vidwriter)
                    self.vidwriter = None
                    self.vidwriting = False
        elif c == 'F':
            if not self.framewriting:
                self.framedir = "data/raw/fr" + self.makeTimeStampStr(self.trackstarttime)
                if not os.path.exists(self.framedir):
                    os.makedirs(self.framedir)
                self.framewriting = True
            else:
                self.framewriting = False
        elif c == 'O':
            self.overlay = not self.overlay
        elif c == 'l':
            if self.logging:
                self.stopLogging()
            else:
                self.startLogging()
        elif c == 'c':
            if self.tcontrol:
                self.tsinter.tcontrol(False,self.verbose)
                self.tcontrol = False
            else:
                self.tcontrol = self.tsinter.tcontrol(True,self.verbose)
        elif c == 'r':
            if not self.tcontrol:
                self.tcontrol = self.tsinter.tcontrol(True,self.verbose)
            if self.trunning:
                self.tsinter.runstop(False,self.verbose)
                self.trunning = False
            else:
                self.tsinter.runstop(True,self.verbose)
                self.trunning = True
        elif c in '0123456789':
            # Note this does zero checking of state! Will work in tracking mode.
            if self.haveserial:
                self.tsinter.setspd(int(c)*10,self.verbose)
            self.lastsercmdtime=time.time()
            self.tmspd = int(c)*10
            if self.logging:
                self.logSerCmd((self.lastsercmdtime-self.logstarttime,self.lastsercmdtime,self.tmspd))
        elif c in '['+']':
            if c=='[':
                spdset=self.lbrk_spd
            else:
                spdset=self.rbrk_spd
            # Note this does zero checking of state! Will work in tracking mode.
            if self.haveserial:
                self.tsinter.setspd(int(spdset),self.verbose)
            self.lastsercmdtime=time.time()
            self.tmspd = int(spdset)
            if self.logging:
                self.logSerCmd((self.lastsercmdtime-self.logstarttime,self.lastsercmdtime,self.tmspd))
        elif c == 'S':
            d = shelve.open("shelf")
            d["trackdata"] = self.trackdata[0:self.framenum,:]
            d.close()
        else:
            sys.stdout.write('Unknown command: %c\n' % c)

    def draw_cross(self,img,center, color, d):                                 
        cv.Line(img, (center[0] - d, center[1] - d),                
                     (center[0] + d, center[1] + d), color, 1, cv.CV_AA, 0) 
        cv.Line(img, (center[0] + d, center[1] - d),                
                     (center[0] - d, center[1] + d), color, 1, cv.CV_AA, 0)

    def traverse(self,seq):
        # Traverses all contours found, returns that with area closes to animal area
        # setting. 
        self.currmin = float("inf")
        while seq:
            # print cv.ContourArea(seq)
            contarea = cv.ContourArea(seq)
            if (np.abs(self.area-contarea) < self.currmin):
                self.currmin = np.abs(self.area-contarea)
                self.closestarea = contarea
                # print "set curring to %f" % self.currmin
                self.pa = cv.CreateMat(1,len(seq), cv.CV_32FC2)
                for (i,(x,y)) in enumerate(seq):
                    self.pa[0,i]=(x,y)
            # Returned contours as a list -- so no children            
            #self.traverse(seq.v_next()) # Recurse on children
            if seq.v_next() is not None:
                sys.stdout.write('ERROR: Given sequence with children.\n')
            seq = seq.h_next() # Next sibling

    def updateTracker(self):
        # Done analyzing the video, store track time.        
        self.trackdt = time.time() - self.lasttracktime
        self.lasttracktime = time.time()
        self.fps = 1.0 / self.trackdt
        self.prevfr = self.getGrayImage()
        if self.imgs == "":
            cv.Copy(cv.GetSubRect(self.prevfr,self.roirect),self.roiimg)
        else:
            cv.Copy(self.prevfr,self.roiimg)
        cv.Dilate(self.roiimg,self.filtimg,None,2)
        # Threshold for mouse with no shadow?
        cv.Threshold(self.filtimg, self.filtimg, self.thresh, self.thresh, cv.CV_THRESH_BINARY_INV)
        #cv.Threshold(self.filtimg, self.filtimg, 150, 150, cv.CV_THRESH_BINARY)
        contours = cv.FindContours(self.filtimg,self.storage,cv.CV_RETR_LIST,cv.CV_CHAIN_APPROX_SIMPLE,(0,0))
        #gray = cv.CV_RGB(100, 0, 0)
        if self.overlay:
            cv.DrawContours(self.roiimg,contours,cv.CV_RGB(255, 255, 255),cv.CV_RGB(255, 255, 255),200)
        self.traverse(contours)
        #if self.verbose:
        #    if self.closestarea in locals():
        #        print "Closest contour area: %f" % self.closestarea
        if (self.pa.cols > 5) and ((self.currmin/self.area) < self.areapct):
        #if (self.pa.cols > 5):
            (center, size, angle) = cv.FitEllipse2(self.pa)
            self.center = center
            if self.usekalman:
                self.prediction = cv.KalmanPredict(self.kalman)
                self.measurement[0,0]=center[0]
                self.measurement[1,0]=center[1]
                cv.KalmanCorrect(self.kalman, self.measurement) 
            self.rcenter = (cv.Round(center[0]), cv.Round(center[1]))
            size = (cv.Round(size[0] * 0.5), cv.Round(size[1] * 0.5))
            color = cv.CV_RGB(255,255,255) # white
            self.perr = -(self.roirect[2]*self.setpt - self.center[0]) * (self.tmillwidth/self.roirect[2])
            if self.overlay:
                cv.Ellipse(self.roiimg, self.rcenter, size, angle, 0, 360, color, 1, cv.CV_AA, 0)
                font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5, 0, 1, 8)
                self.draw_cross(self.roiimg, self.rcenter, cv.CV_RGB(255, 255,255), 10)
                cv.PutText(self.roiimg,"spd %3.2f FPS %2.1f area %.0f perr %f" % \
                    ((self.animspd,)+(self.fps,)+(self.closestarea,)+(self.perr,)),(3,18),font, 0)
                if self.usekalman:
                    cv.Circle(self.roiimg, (cv.Round(np.asarray(self.prediction[0])),cv.Round(np.asarray(self.prediction[1]))), 10, cv.CV_RGB(255, 255,255) )
                    cv.Circle(self.roiimg, (cv.Round(np.asarray(self.kalman.state_post[0])),cv.Round(np.asarray(self.kalman.state_post[1]))), 5, cv.CV_RGB(255, 255,255) )
            self.lastgoodtracktime = time.time()
            # if timesincetrack = nan, then we have track. otherwise time since a good track.
            self.timesincetrack = np.nan
        else:
            self.center = (np.nan,np.nan)
            self.rcenter = (np.nan,np.nan)
            size = (np.nan,np.nan)
            angle = np.nan
            # Don't have track. compute time since last track.
            self.timesincetrack = time.time() - self.lastgoodtracktime

        # Compute derived quantities.        
        # [  0          1    2          3          4        5        6         7     8     9     10     11           12          13    14   15  16   17]
        # [ ANIMALNUM FRNUM LOGTIME   ANIMSPD ANIMLABSPD BELTSPEED ANIMANGLE ANIMX ANIMY ANIMVX ANIMVY  UTCTIME  LASTGRABTIME    FPS kalmanx ky kvx kvy]
        # Fliping sign of X here, to make right positive on video.
        self.x = -(float(self.roirect[2])*float(self.setpt) - self.center[0]) * (float(self.tmillwidth)/float(self.roirect[2]))
        self.y = (float(self.roirect[3])*float(self.setpt) - self.center[1]) * (float(self.tmillwidth)/float(self.roirect[2]))
        if self.framenum > 0:
            # Compute a crude speed based on differencing
            self.vx = (self.x - self.trackdata[self.framenum-1,7]) / self.trackdt
            self.vy = (self.y - self.trackdata[self.framenum-1,8]) / self.trackdt
            self.animlabspd = np.sqrt( self.vx**2 + self.vy**2 )
            self.animspd = np.sqrt( (self.vx + self.tmspd/100.0)**2.0 + self.vy**2.0 )
        else:
            self.vx = 0.0
            self.vy = 0.0
            self.animspd = 0.0
            self.animlabspd = 0.0
        self.animangle = angle
        # Get kalman data and put in same units
        sp = np.asarray(self.kalman.state_post)
        self.kx = -(float(self.roirect[2])*float(self.setpt) - sp[0]) * (float(self.tmillwidth)/float(self.roirect[2]))
        self.ky = (float(self.roirect[3])*float(self.setpt) - sp[1]) * (float(self.tmillwidth)/float(self.roirect[2]))
        self.kvx = sp[2] * (float(self.tmillwidth)/float(self.roirect[2])) / self.trackdt
        self.kvy = -sp[3] * (float(self.tmillwidth)/float(self.roirect[2])) / self.trackdt
        # print sp, sp[0],sp[1]
        self.trackdata[self.framenum,] = [self.animalnum,self.framenum,self.lasttracktime-self.trackstarttime, self.animspd,self.animlabspd,self.tmspd/100.0,self.animangle,self.x,self.y,self.vx,self.vy,self.lasttracktime,self.grabstop,1.0/self.trackdt,self.kx,self.ky,self.kvx,self.kvy]      
        if self.logging:
            # Unify this time stamp!
            self.logTrack()
        if self.vidwriting:
            #newcroifr = cv.CreateImage(cv.GetSize(self.roiimg),8,3)
            #cv.CvtColor(self.roiimg,newcroifr,cv.CV_GRAY2RGB)
            cv.WriteFrame(self.vidwriter, self.roiimg)
        if self.framewriting:
            cv.SaveImage( os.path.join(self.framedir,("fr%05d_" % self.framenum) + self.makeTimeStampStr(self.grabstop) + ".png"), self.roiimg )
        self.framenum = self.framenum + 1
        cv.ShowImage(self.prevwn,self.roiimg)
        
    def behaviorTriggerHS(self):
        # If animal is within right range, track length of range, 
        # then send trigger over tcp
        # FIXME: Use Kalman speed!
        if(self.animspd > 0.25 and self.animspd < 0.95):
            if(self.startBehavior == -1):
                self.startBehavior = self.lasttracktime
            else:
                self.endBehavior = self.lasttracktime
        else:
            if(self.startBehavior != -1 and self.endBehavior != -1):
                print 'end of good speed! for:', self.endBehavior - self.startBehavior, 'seconds' 
                if((self.endBehavior - self.startBehavior) > 1.0 ): #10 seconds?            
                    #send packet to trigger camera (should this be its own method?)
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        s.connect((self.host, self.port))
                        s.send("%.6f %.6f" % (self.startBehavior,self.endBehavior) )
                        #data = s.recv(1024)
                        #print 'Received', repr(data)
                    except:
                        print "Error connecting"
                    finally:
                        print 'closing socket!'
                        s.close()
            self.startBehavior = -1
            self.endBehavior = -1
    
    def perturbVidHandler(self):
        '''
        How will perturbations work? Handle separate vid/feedback loops.
        
        Vid handler looks for valid behaviour as in behavioural trigger.
        When valid behaviour occurs, trigger speed perturbation, which:
            Sets flag to hand over serial control to perturbSerialHandler
        Vid handler then runs until serial pert finished, at which point it
        Tells HSV camera to store all vid from beginning of good behaviour,
        through the perturbation.
        
        Store perturbation time in a log file.
        
        Relies on constants:
          - self.pertdur:  Perturbation duraction. Say: 200 ms (10 samples at 50Hz serial.
          - self.pertfrac:  Fraction of speed to lose and regain, e.g. 0.5 for 50%
            - Can tweak if just want to set to zero and back again.
        '''
        # If not applying perturbation, look for trigger of perturbation:
        if not self.applyingpert:
            # If animal is within right range, for required time span, 
            # then apply speed perturbation.
            # FIXME: Should be based on Kalman speed!
            if(self.animspd > 0.25 and self.animspd < 0.5):
                # Did we just enter good speed? If so note this:
                if(self.startBehavior == -1):
                    # Just transitioned into valid speed range
                    self.startBehavior = self.lasttracktime
                # Have we been in good behaviour long enough to trigger?
                if( ((self.lasttracktime - self.startBehavior) > 1.0) and ((self.lasttracktime-(self.pertendtime+self.pertresponsedur))>self.pertwait) ): # seconds
                    print 'PERTURBING: Valid behaviour sequence for:', self.lasttracktime - self.startBehavior, 'seconds'
                    self.perttime=self.lasttracktime
                    # Compute slope of speed drop reqd to drop X pct of speed in pertdur/2
                    self.pertslope= -(self.pertfrac * float(self.tmspd))/(self.pertdur/2.0)
                    self.pertstartspeed = self.tmspd
                    self.applyingpert=True
            else:
                # We are not in valid speed range. Note valid behaviour not started.
                self.startBehavior = -1
        else:
            # We ARE applyingpert: check if finished, if done, send command to save video
            if (self.pertvidsavetime == -1):
                if ((self.lasttracktime - self.perttime) > self.pertdur):
                    # Perturbation should have finished.
                    # Set end time:
                    self.pertendtime=self.lasttracktime
                    self.pertvidsavetime = self.pertendtime + self.pertresponsedur
                    # Log pert to file. Start behav, pert start time, pert end time
                    print "Perturbation duration complete: would log to file here. Sending VID LOG COMMAND:"
                    if self.logging:
                        self.logPert()
                    # Put treadmill speed back:
                    self.tmspd = self.pertstartspeed
            else:
                if (self.lasttracktime-self.pertendtime) > self.pertresponsedur:
                    # Reset state then send logging command to HSV:
                    self.applyingpert=False
                    #send packet to trigger camera (this should be its own method)
                    print "Response duration elapsed, sending save command"
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        s.connect((self.host, self.port))
                        s.send("%.6f %.6f" % (self.startBehavior, self.pertvidsavetime) )
                        #data = s.recv(1024)
                        #print 'Received', repr(data)
                    except:
                        print "Error connecting"
                    finally:
                        print 'Closing socket!'
                        s.close()
                    self.pertvidsavetime = -1
                    self.startBehavior = -1
            
    def perturbSerialHandler(self):
        '''
        Take over serial handling from feedback control. Drop speed down linearly by
        pct percent in t secs, then back up.
        
        Requirements: Log all changes to the serial commands log file.
        Allow emergency stopping.
        '''
        if 0:
            # Only called if self.applypert:
            if (self.lasttracktime-self.perttime)<(self.pertdur/2.0):
                # In the down time region: (pertslope is negative)
                newspd = self.pertstartspeed + (self.lasttracktime - self.perttime)*self.pertslope
            elif (self.lasttracktime-self.perttime)>(self.pertdur):
                # Done - pert mode will be cancelled soon.
                newspd = self.pertstartspeed
            else:
                # In the back up region:
                newspd = self.pertstartspeed - (self.lasttracktime - (self.perttime+(self.pertdur/2.0)))*self.pertslope
                if newspd > self.pertstartspeed:
                    newspd = self.pertstartspeed
        else:
            if (self.lasttracktime-self.perttime)<=self.pertdur:
                newspd = self.pertstartspeed * self.pertfrac
                if self.verbose:
                    print "perturb setting spd to -1 shoudl be ten? of these"
            else:
                if self.verbose:
                    print "Out of perturb dur back to start speed"
                newspd = self.pertstartspeed
        # Bounds checking done below
        return newspd
        
    def startLogging(self):
        # Open the log write, write initial time stamp
        try:
            sys.stderr.write("Starting logging.\n")
            self.logstarttime = time.time()
            if not os.path.isdir('data'):
                os.mkdir('data')
            if not os.path.isdir('data/raw'):
                os.mkdir('data/raw')
            # Write metadata file:
            self.metafname = time.strftime("data/raw/tmilltrackerlog_%Y%m%d_%H%M%S_metadata.txt",time.localtime(self.logstarttime))
            self.metaf = open( self.metafname, 'w' )
            self.metaf.write( self.getSettings()  )
            self.metaf.close()
            
            # Open and start tracker data file:
            self.logfname = time.strftime("data/raw/tmilltrackerlog_%Y%m%d_%H%M%S.csv",time.localtime(self.logstarttime))
            self.logf = open( self.logfname, 'w' )
            # Write the header:
            self.logf.write( "LOG START: %f seconds since epoch\n" % self.logstarttime  )
            self.logf.write( 'animnum,framenum,time,animspd,animlabspd,beltspeed,animangle,animx,animy,animvx,animvy,utctime,grabtime,vidfps,kalmanx,kalmany,kalmanvx,kalmanvy\n' )
            self.logging=True

            # Open and start the serial command timestamp file:
            self.serfname = time.strftime("data/raw/tmilltrackerlog_%Y%m%d_%H%M%S_serial.csv",time.localtime(self.logstarttime))
            self.serf = open( self.serfname, 'w' )
            self.serf.write( 'time,utctime,tmspdcmd\n' )
        except IOError:
            print "ERROR: Unable to open log file for writing: " + logfname + ". EXITING.\n"
        
    def logTrack(self):
        # Store latest track in log file:
        # [ANIMNUM FRNUM TIME ANIMSPD ANIMLABSPD BELTSPEED ANIMANGLE ANIMX ANIMY ANIMVX ANIMVY UTCTIME GRABTIME FPS KX KY KVX KVY] 
        self.logf.write( '%d,%d,%05.6f,%0.5f,%0.5f,%0.3f,%3.3f,%0.6f,%0.6f,%0.6f,%0.6f,%.6f,%.6f,%.3f,%0.6f,%0.6f,%0.6f,%0.6f\n' \
            % tuple(self.trackdata[self.framenum,]) )
        # print "Logging new track"

    def logSerCmd(self,data):
        # Store latest serial command in log file: 'time','utctime','tmspdcmd'
        self.serf.write( '%.6f,%05.6f,%0.3f\n' % data )

    def logPert(self):
        # Store latest serial command in log file: 'time','utctime','startbehav','perttime','pertendtime'
        self.pertfname = time.strftime("data/raw/tmilltrackerlog_%Y%m%d_%H%M%S_pert.csv",time.localtime(self.logstarttime))
        self.pertf = open( self.pertfname, 'a' )
        self.pertf.write( '%.6f,%05.6f,%05.6f,%05.6f,%05.6f\n' % (self.lasttracktime-self.logstarttime, self.lasttracktime,self.startBehavior, self.perttime, self.pertendtime) )
        self.pertf.close()

    def stopLogging(self):
        self.logging=False
        # Close the log file
        print "Closing log files"
        self.logf.close()
        self.serf.close()

    def run(self):
        if self.haveserial:
            self.tsinter.start()
        
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            fd = sys.stdin.fileno()    
            stime = time.time()
            dt=-np.inf
            while self.alive:
                if self.guion:
                    if self.cvwindow:
                        c = cv.WaitKey(1) % 0x100
                        if self.verbose:
                            print "Got key %s from window" % chr(c)
                        if c is not 255:
                            self.handleInput(chr(c))
                if self.state == "display":
                    self.prevfr = self.getGrayImage()
                    cv.Rectangle(self.prevfr, (self.roipt1[0], self.roipt1[1]), \
                        (self.roipt2[0],self.roipt2[1]), cv.Scalar(0, 0, 255, 0), 2, 8, 0)  
                    cv.ShowImage(self.prevwn,self.prevfr)
                elif self.state == "tracking":
                    now=time.time()
                    dt=now-self.lasttrack
                    if dt > (1.0/self.vidrate):
                        self.lasttrack=now
                        if self.verbose:
                            print 1.0/dt
                        self.updateTracker()
                        if self.behavtrig:
                            self.behaviorTriggerHS()
                elif self.state == "feedback":
                    now=time.time()
                    dt=now-self.lastfeedback
                    if dt > (1.0/self.vidrate):
                        self.lastfeedback=now
                        if self.verbose:
                            print (1.0/dt)
                        self.updateTracker()
                        if self.behavtrig:
                            self.behaviorTriggerHS()
                        if self.perturb:
                            self.perturbVidHandler()
                    now=time.time()
                    dt=now-self.lastserial
                    if dt > (1.0/self.serialrate):
                        self.lastserial=now
                        if self.verbose:
                            print "Serial rate: %.3f" % (1.0/dt)
                        if self.applyingpert:
                            # Compute speed with pert handler
                            newspd = self.perturbSerialHandler()
                        else:
                            # Take self.center, convert to m offset from 0.5 setpt, adjust belt speed
                            if not np.any(np.isnan(self.center)):
                                if not np.isnan(self.kvx):
                                    newspd = self.tmspd + np.round(float(self.perr)*self.kp*100.0*self.rateadjust) + np.round(float(self.kvx)*self.kd*self.rateadjust)
                                    if self.verbose:
                                        print "Velocity x is: %f" % self.kvx
                                        print "increase due to p: %2.3f" % np.round(float(self.perr)*self.kp*100.0*self.rateadjust)
                                        print "increase due to v: %2.3f" % np.round(float(self.kvx)*self.kd*self.rateadjust)                
                                else:
                                    newspd = self.tmspd + np.round(float(self.perr)*self.kp*100.0*self.rateadjust) # e.g. 0.1 * 0.2 * 100     
                            else:
                                if self.timesincetrack > 0.5:
                                    newspd = self.tmspd - 4 # TODO: Adjust for update rate.
                        # Have computed new speed. Now bounds check before serial.
                        if newspd >= 0 and newspd <= 100:
                            self.tmspd = newspd
                            if self.verbose:
                                print "Setting speed to: %d" % self.tmspd
                            if self.haveserial and newspd >= 5:
                                #print "setting speed to %d" % newspd
                                self.tsinter.setspd( newspd, self.verbose )
                                self.lastsercmdtime=time.time()
                        elif newspd < 0:
                            self.tmspd = 0
                            if self.verbose:
                                print "Setting speed to: %d" % self.tmspd
                            if self.haveserial:
                                self.tsinter.setspd( 0, self.verbose )
                                self.lastsercmdtime=time.time()
                        elif newspd > 100:
                            self.tmspd = 100
                            if self.verbose:
                                print "Setting speed to: 100 cm/s"
                            if self.haveserial:
                                self.tsinter.setspd( 100, self.verbose )    
                                self.lastsercmdtime=time.time()
                    if self.logging:
                        self.logSerCmd((self.lastsercmdtime-self.logstarttime,self.lastsercmdtime,self.tmspd))
                if isData():
                    c = sys.stdin.read(1)
                    self.handleInput(c)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            if self.haveserial:
                self.tsinter.runstop(False,self.verbose)
                self.tsinter.tcontrol(False,self.verbose)
                self.tsinter.stop()
                
def main():
    import optparse

    parser = optparse.OptionParser(
        usage = "%prog [options]",
        description = "TmillTracker - A real-time animal tracking system and treadmill controller for closed loop neuromechanics."
    )

    parser.add_option("-q", "--quiet",
        dest = "quiet",
        action = "store_true",
        help = "suppress non error messages",
        default = False
    )

    parser.add_option("-d", "--debug",
        dest = "debug",
        action = "store_true",
        help = "If set outputs diagnostic and debug messages",
        default = False
    )

    parser.add_option("--noci",
        dest = "noci",
        action = "store_true",
        help = "do not use libcamiface",
        default = False
    )

    parser.add_option("-I",
        dest = "initial",
        action = "store_false",
        help = "do not ask for initial settings: default animalnum=-1, trial=1, notes=''",
        default = True
    )

    parser.add_option("--imgs",
        dest = "imgs",
        action = "store",
        help = "use a directly of images in format fr%d.png as video feed. assumes 150 Hz.",
        default = ""
    )

    (options, args) = parser.parse_args()

    try:
        # Expect a Panlab LE8700 treadmill on the default serial port.
        # Use settings 9600 baud, parity N, no RTS, no XON/XOFF, no echo
        # 8 bit size, 1 stop bit for treadmill: these are typical defaults of serial port object and will match treadmill -- update if necessary.
        tsinter = TmillSerialInterface(0,9600,'N',False,False,False)
        haveserial = True
    except serial.SerialException, e:
        sys.stderr.write("Could not open port %r: %s\n" % (0, e))
        haveserial = False
    except:
        sys.stderr.write("Non-serial exception in creating serial interface.\n")
        print "Unexpected error:", sys.exc_info()[0]
        haveserial = False

    if haveserial and not options.quiet:
        sys.stderr.write('=== TmillSerialInterface on %s: %d,%s,%s,%s ===\n' % (
            tsinter.serial.portstr,
            tsinter.serial.baudrate,
            tsinter.serial.bytesize,
            tsinter.serial.parity,
            tsinter.serial.stopbits,
        ))
    
    # Parse tmilltracker options:
    # Check for camera versus img sequence:
    if options.imgs == "":
        # Import cam_iface unless told not to:
        if not options.noci:
            #import motmot.cam_iface.cam_iface_ctypes as cam_iface
            exec("import motmot.cam_iface.cam_iface_ctypes as cam_iface") in globals()
    
    # Create the tmilltracker, and run it
    tt = TmillTracker(haveserial,options.noci,options.imgs,options.debug)
    if options.initial:
        tt.getInitial()
    sys.stderr.write(tt.get_help_text())
    sys.stderr.write(tt.getSettings())
    if haveserial:
        tt.tsinter = tsinter
    tt.run()

    if not options.quiet:
        sys.stderr.write("\n=== exit ===\n")

if __name__ == '__main__':
    main()
