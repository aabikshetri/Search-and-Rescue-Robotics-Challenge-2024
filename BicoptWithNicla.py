from comm.Serial import SerialController, DataType_Int, DataType_Float, DataType_Boolean
from joystick.JoystickManager import JoystickManager
from gui.simpleGUI import SimpleGUI
from gui.niclaGUI import NiclaBox
import time
from user_parameters import ROBOT_MAC,SERIAL_PORT, PRINT_JOYSTICK



if __name__ == "__main__":
    # Communication
    serial = SerialController(SERIAL_PORT, timeout=.5)  # 5-second timeout
    serial.manage_peer("A", ROBOT_MAC)
    serial.manage_peer("G", ROBOT_MAC)
    time.sleep(.05)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "zEn", True)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "rollEn", False)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "rotateEn", False)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "pitchEn", False)
    serial.send_preference(ROBOT_MAC, DataType_Boolean, "yawEn", True)

    
    # // PID terms
    serial.send_preference(ROBOT_MAC, DataType_Float, "kpyaw", 0) #2
    serial.send_preference(ROBOT_MAC, DataType_Float, "kppyaw", 0.10) #2
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdyaw", 0)#.1
    serial.send_preference(ROBOT_MAC, DataType_Float, "kddyaw", 0.1)#.1
    serial.send_preference(ROBOT_MAC, DataType_Float, "kiyaw", 0)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kiyawrate", 0)

    serial.send_preference(ROBOT_MAC, DataType_Float, "yawrate_gamma", 0.5)
    serial.send_preference(ROBOT_MAC, DataType_Float, "rollrate_gamma", 0.85)
    serial.send_preference(ROBOT_MAC, DataType_Float, "pitchrate_gamma", 0.7)
    

    serial.send_preference(ROBOT_MAC, DataType_Float, "kpz", 0.3)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdz", 0.6)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kiz", 0.05)

    serial.send_preference(ROBOT_MAC, DataType_Float, "kproll", 0)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdroll", 0)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kppitch", 0)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdpitch", 0)

    # // Range terms for the integrals
    serial.send_preference(ROBOT_MAC, DataType_Float, "z_int_low", 0.0)
    serial.send_preference(ROBOT_MAC, DataType_Float, "z_int_high", 0.15)
    serial.send_preference(ROBOT_MAC, DataType_Float, "yawRateIntRange", 0)

    # // radius of the blimp
    serial.send_preference(ROBOT_MAC, DataType_Float, "lx", 0.15)

    serial.send_preference(ROBOT_MAC, DataType_Float, "servoRange", 180) #degrees
    serial.send_preference(ROBOT_MAC, DataType_Float, "servoBeta", 0) #degrees
    serial.send_preference(ROBOT_MAC, DataType_Float, "servo_move_min",0) #degrees

    serial.send_preference(ROBOT_MAC, DataType_Float, "botZlim", -1)
    serial.send_preference(ROBOT_MAC, DataType_Float, "pitchOffset", 0) #degrees
    serial.send_preference(ROBOT_MAC, DataType_Float, "pitchInvert", -1) #degrees

    # nicla parameters
    serial.send_preference(ROBOT_MAC, DataType_Float, "y_thresh", 0.5)
    serial.send_preference(ROBOT_MAC, DataType_Float, "y_strength", 1)
    serial.send_preference(ROBOT_MAC, DataType_Float, "x_strength", 1)

    serial.send_preference(ROBOT_MAC, DataType_Float, "fx_togoal", 0.15)
    serial.send_preference(ROBOT_MAC, DataType_Float, "fx_charge", 0.3)
    serial.send_preference(ROBOT_MAC, DataType_Float, "fx_levy", 0.1)

    serial.send_preference(ROBOT_MAC, DataType_Int, "n_max_x", 240)
    serial.send_preference(ROBOT_MAC, DataType_Int, "n_max_y", 160)
    serial.send_preference(ROBOT_MAC, DataType_Float, "h_ratio", 0.8)
    serial.send_control_params(ROBOT_MAC, (0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0))
    time.sleep(.2)

    # Joystick
    joystick = JoystickManager()
    mygui = SimpleGUI()
    niclaGUI = NiclaBox(max_x=240, max_y=160, x=120, y=80, width=120, height=80)
    
    sensors = serial.getSensorData()
    height = 0
    tz = 0
    nicla_x = 0
    nicla_y = 0
    nicla_w = 0
    nicla_h = 0
    if (sensors) :
        tz = sensors[1]
        height = sensors[0]
        nicla_x= sensors[2]
        nicla_y = sensors[3]
        nicla_w = sensors[4]
        nicla_h = sensors[5]
    ready = 0
    old_b = 0
    old_x = 0
    fx_ave = 0
    dt = .1
    
    servos = 75
#def leftservo(joystick_input):
 #   servo_position = 90 + (45*joystick_input) 
  #  return servo_position

#def rightservo(joystick_input):
 #   servo_position = 90 - (45*joystick_input) 
  #  return servo_position
    try:
        while True:
            # Axis input: [left_vert, left_horz, right_vert, right_horz, left_trigger, right_trigger]
            # Button inputs: [A, B, X, Y]
            axis, buttons = joystick.getJoystickInputs()
            
            if buttons[3] == 1: # y stops the program
                break
            if buttons[1] == 1 and old_b == 0: # b pauses the control
                if (sensors) :
                    tz = sensors[1]
                    height = sensors[0]
                    nicla_x= sensors[2]
                    nicla_y = sensors[3]
                    nicla_w = sensors[4]
                    nicla_h = sensors[5]


                if ready != 0:
                    ready = 0
                else:
                    ready = 1
            if buttons[2] == 1 and old_x == 0:
                if ready == 2:
                    if (sensors) :
                        tz = sensors[1]
                        height = sensors[0]
                    ready = 1
                else:
                    ready = 2
            old_x = buttons[2]
            old_b = buttons[1]
            if PRINT_JOYSTICK:
                print(" ".join(["{:.1f}".format(num) for num in axis]), buttons)

            #### CONTROL INPUTS to the robot here #########
            #height controller
            ##while height > 20:


            if abs(axis[0]) < .15:
                axis[0] = 0
            height += -axis[0] * dt 
            if height > 15:
                height = 15
                #s2 = leftservo(axis[3])
                #s1 = rightservo(axis[3])

            elif height < -3:
                height = -3
            fz = height
                
            # roll controller
            # if abs(axis[1]) < .15:
            #     axis[1] = 0
            # tx = axis[1] * .2
            tx = 0

            # yaw controller
            if abs(axis[4]) < .15:
                axis[4] = 0
            tz += -axis[4] *1.2 * dt

           # if tz > 5:


            # tz = -axis[4] * .1
            #print("nicla control", tz)
            print("height", height)
            # fx speed controller
            fx = ( -1*axis[2] + axis[5])
            if (fx < 0):
                fx = fx * .2
            fx_ave = fx_ave * .8 + fx * .2 # smooths the fx for more gradual effects
            led = -buttons[2]
           # print(fx_ave)
            #print(tz, ":", height)
            #print(height)
            
           
            ############# End CONTROL INPUTS ###############
            sensors = serial.getSensorData()
            # print(sensors)
            if (sensors):
                if (sensors[2] < 300):
                    niclaGUI.update(x=sensors[2], y=sensors[3], width=sensors[4], height=sensors[5])
                mygui.update(
                    cur_yaw=sensors[1],
                    des_yaw=tz,
                    cur_height=sensors[0],
                    des_height=height,
                    battery=0,#sensors[2],
                    distance=0,
                    connection_status=True,
                )
                
            # Send through serial port
            serial.send_control_params(ROBOT_MAC, (ready, fx_ave, fz, tx, tz, led, 0, 0, 0, 0, 0, 0, 0))
            time.sleep(dt)
            
    except KeyboardInterrupt:
        print("Stopping!")
        # Send zero input
serial.send_control_params(ROBOT_MAC, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
