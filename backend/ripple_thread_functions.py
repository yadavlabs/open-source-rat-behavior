import time
import threading
import array
import xipppy as xp
from stim_helpers import generateStimulationCommand, quantizeAmplitude, defaultChannelMap

def testConnection():
    
    # Connect to processor (Try UDP then TCP) and then print the processor time.
    try:
        print("[Xipppy] Attempting to connect over UDP...")
        with xp.xipppy_open():
            print(f"[Xipppy] Processor time: {xp.time()}")
    except:
        try:
            print("[Xipppy] Attempting to connect over TCP...")
            with xp.xipppy_open(use_tcp=True):
                print(f"[Xipppy] Processor time: {xp.time()}")
        except:
            print("[Xipppy] Failed to connect to processor.")
        else:
            print("[Xipppy] Connected over TCP")
    else:
        print("[Xipppy] Connected over UDP")
    
    time.sleep(0.001)

class XipppyStimulator:
    def __init__(self, channel_map=defaultChannelMap(), front_end_type="Pico"):
        self.is_initialized = False
        self.mode = "TCP"
        self.address = '192.168.42.129'
        self.status_message = "Disconnected"
        
        # Channel allocation profiles
        self.stimulation_channels = []
        self.selected_channels = []
        self.gnd_ref_channel = None
        self.gnd_channel = None
        self.ref_channel = None
        self.trig_channel = None
        self.stimulus_event_handler = None  # Placeholder for external callback registration

        # Configuration and mapping constraints
        self.channel_map = channel_map if channel_map is not None else {}
        self.apply_map = True if channel_map is not None else False
        self.fast_settle = True
        
        # Default parameter fields matching your MATLAB structure
        self.stimulation_parameters = {
            "anode": 16, "cathode": 1, "sequential": False,
            "frequency": 50, "duration": 200, "amplitude": 200,
            "train_length": 2, "step": 5, "amplitude_cathode": 200,
            "amplitude_anode": 200
        }
        
        # Hardcoded configuration constants matching front-end type selections
        if front_end_type == "Macro":
            self.amp_res_val_list = [10, 20, 50, 100, 200]
            self.max_steps_list = [100, 100, 100, 100, 75]
        else:  # Defaults cleanly to "Pico" front-end profiles
            self.amp_res_val_list = [1, 2, 5, 10, 20]
            self.max_steps_list = [100, 100, 100, 100, 75]

        self.amp_res_val = None
        self.amp_res = None
        self.max_amp = None
        self.stimulation_command = None
        self.clear_cmd = []
        
        # Recording and runtime execution handlers
        self.recording_enabled = False
        self.is_recording = False
        self.operator_address = None
        self.stim_timer = None
        self._ctx = None  # Holds the persistent context manager reference

    def log_status(self, msg):
        """Replicates your displayStatusMessage callback method style."""
        self.status_message = msg
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[XipppyStimulator {timestamp}] {msg}")

    # ====================================================
    # NATIVE PYTHON CONTEXT MANAGER HOOKS
    # ====================================================
    '''
    def __enter__(self):
        """Allows usage like: 'with XipppyStimulator() as stimulator:'"""
        self.log_status("Top of __enter__.")
        self.initialize()
        return self
    '''
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Safely tears down hardware when exiting a code block or crashing."""
        if exc_type is not None:
            self.log_status(f"Crash detected inside code loop! Exception: {exc_val}")
        self.cleanup()

    def initialize(self, mode="TCP", address="192.168.42.129"):
        self.log_status("Top of initialize.")
        if self.is_initialized:
            self.log_status("Stimulator already initialized.")
            return True
            
        self.mode = mode
        self.address = address
        
        try:
            # Leverage the documentation's context manager safely
            # We instantiate and enter it programmatically to keep the channel open
            print("At xipppy_open")
            tcpMode = xp._open(use_tcp=(self.mode == "TCP"))
            #self._ctx = xp.xipppy_open(use_tcp=(self.mode == "TCP"))
            #self._ctx.__enter__()
            self.log_status("Xipppy TCP session active.")
        except Exception as e:
            self.log_status(f"Xipppy Context Manager did not initialize: {e}")
            return False

        # Query available stimulation electrodes from connected front-ends
        stim_chans = xp.list_elec('stim')
        if len(stim_chans) == 0:
            self.log_status("Warning: No stimulation hardware detected on the bus network.")
            return False
        
        # See comment in defaultChannelMap() in stim_helpers.py but to call xipppy functions with multiplitple electrodes,
        # the variable that holds the list of electrodes must be an array.array('I', [elecs])
        self.stimulation_channels = list(stim_chans)
        
        # Map channels if an active lead dictionary is present
        if self.apply_map:
            self.selected_channels = array.array('I', [c for c in self.stimulation_channels if c in self.channel_map.values()])
        else:
            self.selected_channels = array.array('I', self.stimulation_channels)

        self.is_initialized = True
        self.log_status("Stimulator initialized successfully.")
        
        # Launch startup hardware configurations
        self.generate_clear_cmd()
        self.enable_recording()
        self.update_amplitude_resolution(self.stimulation_parameters["step"])
        self.update_parameters(parameters=self.stimulation_parameters)

        return True

    def is_connected(self):
        return self.is_initialized

    def update_parameters(self, parameters):
        if not self.is_initialized:
            self.log_status("Xipppy not initialized.")
            return

        for field, new_param in parameters.items():
            if field in self.stimulation_parameters:
                if field in ["anode", "cathode"] and self.apply_map:
                    self.stimulation_parameters[field] = self.channel_map.get(new_param, new_param)
                elif field == "step":
                    self.update_amplitude_resolution(new_param)
                else:
                    self.stimulation_parameters[field] = new_param
                self.log_status(f"Parameter '{field}' updated to: {self.stimulation_parameters[field]}")
        
        self.stimulation_command, amp_info = generateStimulationCommand(
            params=self.stimulation_parameters,
            max_amp=self.max_amp,
            fast_settle=self.fast_settle,
            trig_chan=self.trig_channel
        )
        if not amp_info["validInput"]:
            self.stimulation_parameters["amplitude"] = amp_info["ampValid"]
            self.log_status(f"Amplitude corrected to: {amp_info['ampValid']} uA")

        if not self.stimulation_parameters["sequential"]:
            self.stimulation_parameters["amplitude_cathode"] = amp_info["ampCathode"]
            self.log_status(f"Cathode amplitude set to {amp_info['ampCathode']} uA")

            self.stimulation_parameters["amplitude_anode"] = amp_info["ampAnode"]
            self.log_status(f"Anode amplitude set to {amp_info['ampAnode']} uA")
        else:
            self.stimulation_parameters["amplitude_cathode"] = amp_info["ampValid"]
            self.stimulation_parameters["amplitude_anode"] = amp_info["ampValid"]
        

        self.log_status("Parameters updated.")

    def deliver_stimulus(self):
        if not self.is_initialized:
            self.log_status("Xipppy not initialized.")
            return

        self.log_status("Delivering stimulation train...")
        
        # Because the context manager is reentrant, wrapping specific critical sections 
        # inside an explicit 'with' block is highly reliable and prevents side-channel drift
        #with xp.xipppy_open(use_tcp=(self.mode == "TCP")):
        xp.stim_enable_set(True)
        for step_sequence_list in self.stimulation_command:
            #for stim_seq_obj in step_sequence_list:
            xp.StimSeq.send_stim_seqs(step_sequence_list)
                #xp.StimSeq.send(stim_seq_obj)
            # Convert durations into clock cycle ticks (33.33 microseconds per tick)
            '''
            pulse_ticks = int(round(self.stimulation_parameters["duration"] / 33.33))
            interphase_ticks = int(round(pulse_ticks / 2))
            
            # Map frequency targets to loop repetition intervals
            period_ticks = int(round(30000 / self.stimulation_parameters["frequency"]))
            total_repeats = int(self.stimulation_parameters["frequency"] * self.stimulation_parameters["train_length"])

            # Construct raw StimSegment arrays mirroring your pulse sequences
            pseg = xp.StimSegment(pulse_ticks, self.stimulation_parameters["amplitude"], -1, fast_settle=self.fast_settle)
            ipi = xp.StimSegment(interphase_ticks, 0, 1, current_enable=False, fast_settle=self.fast_settle)
            nseg = xp.StimSegment(pulse_ticks, self.stimulation_parameters["amplitude"], 1, fast_settle=self.fast_settle)

            # Build sequence header and dispatch down network card
            seq = xp.StimSeq(self.stimulation_parameters["cathode"], period_ticks, total_repeats, [pseg, ipi, nseg], action=0)
            xp.StimSeq.send(seq)
            '''

        # Trigger your non-blocking asynchronous timer thread loop
        if self.stim_timer and self.stim_timer.is_alive():
            pass
        self.stim_timer = threading.Thread(target=self._handle_stimulus_timer, args=(self.stimulation_parameters["train_length"],), daemon=True)
        self.stim_timer.start()
        return True

    def _handle_stimulus_timer(self, delay_seconds):
        time.sleep(delay_seconds)
        self.stimulus_event_handler() if hasattr(self, 'stimulus_event_handler') else None
        self.log_status("Stimulation complete. StimulusDelivered event handled.")

    def assign_stimulus_event_handler(self, event_handler):
            """Allows external code to register a callback for stimulus delivery events."""
            self.stimulus_event_handler = event_handler
            self.log_status("External stimulus event handler registered.")

    def deliver_stimulus_external(self, stimulus_timer_fcn):
        # passed to arduino manager. Difference is that the "handle_stimulus_timer" returns a value that can be written to the arduino
        # via the arduino manager to indicate that the stimulus has been delivered to progress the trial. This might not be a good idea.
        if not self.is_initialized:
            self.log_status("Xipppy not initialized.")
            return
        
        self.log_status("Delivering stimulation train...")
        xp.stim_enable_set(True)
        for step_sequence_list in self.stimulation_command:
            xp.StimSeq.send_stim_seqs(step_sequence_list)
        if self.stim_timer and self.stim_timer.is_alive():
            pass
        self.stim_timer = threading.Thread(target=stimulus_timer_fcn, args=(self.stimulation_parameters["train_length"],), daemon=True)
        self.stim_timer.start()
        return True

    
    def stop_stimulus(self):
        if not self.is_initialized:
            return
        with xp.xipppy_open(use_tcp=(self.mode == "TCP")):
            xp.stim_enable_set(False)
        self.log_status("Stimulation safely halted via global enable override.")

    def generate_clear_cmd(self):
        if not self.is_initialized:
            return
        self.clear_cmd = []
        for chan in self.selected_channels:
            #print(f"Selected channel: {chan}")
            clear_seg = xp.StimSegment(3, 0, -1, enable=False)
            clear_seq = xp.StimSeq(chan, 20, 1, clear_seg, action=0)
            self.clear_cmd.append(clear_seq)

    def update_amplitude_resolution(self, new_res_val):
        if not self.is_initialized:
            self.log_status("Xipppy not initialized.")
            return
            
        if new_res_val == self.amp_res_val:
            self.log_status("Amplitude resolution already applied.")
            return

        if new_res_val not in self.amp_res_val_list:
            self.log_status("Invalid amplitude resolution selection parameters.")
            return

        new_res_idx = self.amp_res_val_list.index(new_res_val)
        
        with xp.xipppy_open(use_tcp=(self.mode == "TCP")):
            xp.stim_enable_set(False)
            time.sleep(0.05)
            # Adjust the resolution step size on selected electrodes
            # Only need to set for one electrode as all other electrodes on the same Front End will
            # also be set. (So this assumes that the selected channels are on the same Front End.)
            xp.stim_set_res(min(self.selected_channels), new_res_idx)
            time.sleep(0.05)
            xp.stim_enable_set(True)

        self.amp_res = new_res_idx
        self.amp_res_val = new_res_val
        self.max_amp = self.max_steps_list[new_res_idx] * new_res_val
        print(self.max_amp)
        self.stimulation_parameters["step"] = new_res_val
        self.log_status(f"Amplitude resolution set to: {self.amp_res_val} uA")
        #self.update_stimulation_parameters(parameters=self.stimulation_parameters)
        '''
        [self.stimulation_command, amp_info] = generateStimulationCommand(
            params=self.stimulation_parameters,
            fast_settle=self.fast_settle, 
            trig_chan=self.trig_channel
        )
        if not amp_info["validInput"]:
            self.stimulation_parameters["amplitude"] = amp_info["ampValid"]
            self.log_status(f"Amplitude corrected to: {amp_info['ampValid']} uA")

        if not self.stimulation_parameters["sequential"]:
            self.stimulation_parameters["amplitude_cathode"] = amp_info["ampCathode"]
            self.log_status(f"Cathode amplitude set to {amp_info['ampCathode']} uA")

            self.stimulation_parameters["amplitude_anode"] = amp_info["ampAnode"]
            self.log_status(f"Anode amplitude set to {amp_info['ampAnode']} uA")
        else:
            self.stimulation_parameters["amplitude_cathode"] = amp_info["ampValid"]
            self.stimulation_parameters["amplitude_anode"] = amp_info["ampValid"]
        self.log_status("Parameters updated.")
        self.log_status(f"Amplitude resolution set to: {self.amp_res_val} uA")
        '''
    def set_gnd_ref(self, chan):
        if not self.is_initialized:
            return
        target = self.channel_map.get(chan, chan) if self.apply_map else chan
        self.gnd_ref_channel = target
        self.log_status(f"Ground/reference configuration mapped for channel: {target}")

    def remove_gnd_ref(self):
        if not self.is_initialized or self.gnd_ref_channel is None:
            return
        self.log_status(f"Ground/reference removed from channel: {self.gnd_ref_channel}")
        self.gnd_ref_channel = None

    def enable_recording(self):
        if not self.is_initialized or self.mode != "TCP":
            return
        try:
            last_octet = int(self.address.split('.')[-1])
            with xp.xipppy_open(use_tcp=True):
                xp.add_operator(last_octet)
            self.recording_enabled = True
            self.operator_address = last_octet
            self.log_status(f"Operator registration added successfully at final ID: {last_octet}")
        except Exception as e:
            self.log_status(f"Warning: Operator ID authentication registration issue: {e}")
            self.recording_enabled = False

    def start_recording(self, save_file_path):
        if not self.recording_enabled:
            return
        try:
            with xp.xipppy_open(use_tcp=True):
                xp.trial(oper=self.operator_address, status='recording', file_name_base=save_file_path, auto_incr=False)
            self.is_recording = True
            self.log_status(f"Recording started on Grapevine Trek hardware disk paths: {save_file_path}")
        except Exception as e:
            self.log_status(f"Failed to initialize file recording loops: {e}")

    def stop_recording(self):
        if not self.is_recording:
            return
        try:
            with xp.xipppy_open(use_tcp=True):
                xp.trial(oper=self.operator_address, status='stopped')
            self.is_recording = False
            self.log_status("Recording stopped successfully.")
        except Exception as e:
            self.log_status(f"Catching file locking errors calmly: {e}")
            self.is_recording = False


    def cleanup(self):
        """Teardown method to safely disconnect hardware lines."""
        if not self.is_initialized:
            return
        try:
            # 1. Clear any active front-end current drivers safely
            if xp.stim_enable():
                xp.stim_enable_set(False)
            # 2. Programmatically close out the underlying context wrapper tracking hooks
            flag = xp._close()
            if flag == 0:
                self.log_status("Xipppy connections detached cleanly.")
            else:
                self.log_status("Xipppy may have encountered an issue during disconnection.")
            #if self._ctx is not None:
            #    self._ctx.exit(None, None, None)
            self._ctx = None
            self.is_initialized = False
            #self.log_status("Xipppy connections detached cleanly.")
        except Exception as e:
            self.is_initialized = False
            self.log_status(f"Error packing library context down: {e}")

    def __del__(self):
        """Ensures cleanup fires if the Python garbage collector deletes the object instance."""
        self.cleanup()
