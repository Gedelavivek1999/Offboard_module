
**Deterministic control loop with RT Watchdog Mechanism**

Issue: If the Flight controller(Pixhawk) goes offboard mode/manually controlled it requires continuous heartbeat Tx sig to Flight controller if not it could drift away or crash land, before the flight controller takes charge
Minimum frequency required is 50hz - 2ms 

Method: Deterministic control loop to generate the pulses up to 50hz for 1.5 sec 
Watchdog timer which is set for 10 seconds waits for the feed if not received will generate hard fault error and safely lands.

Resolves: Runaway Drift, Managing Safe Pilot Takeover, Handles Ros2 node crashes 
/
/
/
/
/
starting commits- I have done this project to control the drone model without the GCS.
Offboard Mode - integrated the control feature with keyboard.
