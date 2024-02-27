from spot_helper import SpotRobotController
import time
import threading

# Shared variable to signal when to stop
stop_requested = False

def listen_for_enter(controller):
    input("Press Enter to stop...")
    controller.request_stop()
    print("Stop requested. Halting robot operations.")

def main():
    config_path = 'config.json'
    controller = SpotRobotController(config_path)

    # Initialize the robot and acquire necessary resources
    controller.initialize_robot()
    controller.acquire_resources()

    # Start listening for the Enter key in a background thread
    threading.Thread(target=listen_for_enter, args=(controller,), daemon=True).start()

    # Ensure the robot is powered on before sending any commands
    controller.power_on_robot()

    ## code here

    time.sleep(4)
    controller.stand()
    time.sleep(4)
    controller.sit()
    time.sleep(4)
    controller.move_direction("forward", 1)
    time.sleep(1.5)
    controller.rotate("left",2)
    time.sleep(2.5)
    controller.move_direction("backward", 1)
    time.sleep(1.5)
    controller.turn_body_pitch_yaw(0.5, 0.5)
    time.sleep(4)

    ## Code ends here

    
if __name__ == '__main__':
    main()
