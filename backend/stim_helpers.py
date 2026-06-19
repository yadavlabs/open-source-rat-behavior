import math
import xipppy as xp


def defaultChannelMap():
    array_chans = list(range(1,17)) # labelling convention of electrode array being used 
    ripple_chans = [1, 6, 9, 15, 2, 5, 10, 16, 3, 7, 12, 13, 4, 8, 11, 14] # ripple channels that map to electrodes on the array (based on connection/wiring/routing)
    return(dict(zip(array_chans, ripple_chans)))


def quantizeAmplitude(amplitude, Nc, Na, s):
    """
    Translates quantizeAmplitude.m feature-for-feature.
    Ensures absolute charge balancing across multipolar combinations.
    """
    # q = number of cathodes * number of anodes * step size (uA)
    q = Nc * Na * s
    
    # Round off to guarantee configuration factors align with hardware steps
    m = int(round(amplitude / q))
    I_valid = m * q  # Corrected total valid current
    
    kc = m * Na  # Quantized steps for cathodes
    ka = m * Nc  # Quantized steps for anodes
    
    Ic = kc * s  # Total cathode current payload (uA)
    Ia = ka * s  # Total anode current payload (uA)
    
    return kc, ka, I_valid, Ic, Ia


def buildSchedule(params, Nc, Na):
    """
    Translates buildSchedule layout rules, coordinating sequential vs concurrent 
    stimulation repetition cycles over the specified train length.
    """
    # Check your parameters dictionary flags; defaults to sequential true if missing
    seq_flag = params.get("sequential", True)
    
    schedule = []
    
    if seq_flag:
        # Electrodes shift configurations dynamically across the train length duration
        repeats = int((params["frequency"] * params["train_length"]) / Nc)
        
        # Action mappings: First loop cycle defaults to 'curcyc' (0), subsequent ones to 'allcyc' (1)
        # Action mapping codes inside xipppy: 0 = immediate/current cycle, 1 = subsequent cycles
        actions = [0] + [1] * (Nc - 1)
        
        if Na == 1 and Nc > 1: # Multiple cathodes, single tracking anode
            for i in range(Nc):
                schedule.append({
                    "anodes": [params["anode"]],
                    "cathodes": [params["cathode"][i]],
                    "repeats": repeats,
                    "action": actions[i]
                })
                
        elif Na == Nc and Na > 1: # Multiple discrete anode-cathode pairs
            for i in range(Nc):
                schedule.append({
                    "anodes": [params["anode"][i]],
                    "cathodes": [params["cathode"][i]],
                    "repeats": repeats,
                    "action": actions[i]
                })
                
        else: # Single standard baseline pair configuration fallback
            schedule.append({
                "anodes": [params["anode"]],
                "cathodes": [params["cathode"]],
                "repeats": repeats,
                "action": actions[0]
            })
            
    else:
        # Simultaneous concurrent multipolar stimulation delivery mode
        total_repeats = int(params["frequency"] * params["train_length"])
        schedule.append({
            "anodes": params["anode"] if isinstance(params["anode"], list) else [params["anode"]],
            "cathodes": params["cathode"] if isinstance(params["cathode"], list) else [params["cathode"]],
            "repeats": total_repeats,
            "action": 0  # Immediate 'curcyc' execution flag
        })
        
    return schedule


def buildBiphasicSequence(pw, amp, leading_pol, fast_settle):
    """
    Translates buildBiphasicSequence array creation into a list of 
    native xipppy StimSegment objects matching clock-cycle rules.
    """
    # Leading Phase Segment: Polarity maps -1 for Cathodic leading, 1 for Anodic leading
    pol1 = -1 if leading_pol == 0 else 1
    seg1 = xp.StimSegment(length=int(pw), ampl=int(amp), pol=pol1, fast_settle=False, current_enable=True)
    
    # Inter-Pulse Interval (IPI): Forced to 2 clock-cycles (66.66 microseconds)
    seg2 = xp.StimSegment(length=2, ampl=0, pol=0, fast_settle=False, current_enable=False)
    
    # Trailing Phase Segment: Inverse polarity to balance total charge delivery
    pol3 = 1 if leading_pol == 0 else -1
    seg3 = xp.StimSegment(length=int(pw), ampl=int(amp), pol=pol3, fast_settle=False, current_enable=True)
    
    segments = [seg1, seg2, seg3]
    
    # Append passive fast discharge dump line if flag toggle is engaged
    if fast_settle:
        seg4 = xp.StimSegment(length=6, ampl=0, pol=pol3, fast_settle=True, current_enable=True)
        segments.append(seg4)
        
    return segments


def inactive_cathode_sequence(pw):
    """
    Translates inactive_cathode_sequence mapping window lengths for auxiliary channels.
    """
    total_len = int(2 * pw + 2)
    # Generate an un-energized placeholder pass block
    seg = xp.StimSegment(length=total_len, ampl=0, pol=0, fast_settle=False, current_enable=False)
    return [seg]


def generateStimulationCommand(params, fast_settle=False, trig_chan=None):
    """
    Translates generateStimulationCommand.m into Python.
    Iterates across the behavioral schedule arrays to compile structural command sequences.
    """
    # 30,000 Hz clock cycle definition -> 33.33 microseconds per tick unit conversion
    period = int(math.floor(30000 / params["frequency"]))
    durCC = round(params["duration"] / 33.33, 1)
    
    # Clean and flatten input streams to list tracking structures explicitly
    cathodes = params["cathode"] if isinstance(params["cathode"], list) else [params["cathode"]]
    anodes = params["anode"] if isinstance(params["anode"], list) else [params["anode"]]
    
    Nc = len(cathodes)
    Na = len(anodes)
    
    schedule = buildSchedule(params, Nc, Na)
    
    cmd_out = []
    trig_adj = 1 if trig_chan is not None else 0
    
    # Iterate across scheduled execution profiles
    for i in range(len(schedule)):
        active_cathodes = schedule[i]["cathodes"]
        active_anodes = schedule[i]["anodes"]
        
        aNc = len(active_cathodes)
        aNa = len(active_anodes)
        
        # Calculate balanced step variables for current loop
        kc, ka, amp_valid, amp_c, amp_a = quantizeAmplitude(params["amplitude"], aNc, aNa, params["step"])
        
        repeats = schedule[i]["repeats"]
        action = schedule[i]["action"]
        
        # List context to aggregate StimSeq definitions
        step_sequences = []
        
        # 1. Compile Cathodic Electrodes Sequences
        for n in range(aNc):
            seq_list = buildBiphasicSequence(durCC, kc, leading_pol=0, fast_settle=fast_settle)
            stim_seq = xp.StimSeq(elec=active_cathodes[n], period=period, repeats=repeats, seq=seq_list, action=action)
            step_sequences.append(stim_seq)
            
        # 2. Compile Anodic Electrodes Sequences
        for n in range(aNa):
            seq_list = buildBiphasicSequence(durCC, ka, leading_pol=1, fast_settle=fast_settle)
            stim_seq = xp.StimSeq(elec=active_anodes[n], period=period, repeats=repeats, seq=seq_list, action=action)
            step_sequences.append(stim_seq)
            
        # 3. Handle Auxiliary Input Trigger Channel Lines if defined
        if trig_adj:
            seq_list = inactive_cathode_sequence(durCC)
            stim_seq = xp.StimSeq(elec=trig_chan, period=period, repeats=repeats, seq=seq_list, action=action)
            step_sequences.append(stim_seq)
            
        cmd_out.append(step_sequences)
        
    # Generate structural verification meta-dictionaries mimicking your ampInfo payload fields
    amp_info = {
        "validInput": isequal_fallback(params["amplitude"], amp_valid),
        "ampValid": amp_valid,
        "ampCathode": amp_c,
        "ampAnode": amp_a
    }
    
    return cmd_out, amp_info

def isequal_fallback(val1, val2):
    return abs(val1 - val2) < 1e-5
