# Gesture Control Specifications

This document defines the hand gesture recognition system for the HandsFree-Gaming project. All gestures are calibrated for right-hand detection only and are designed for gaming control applications.

> [!WARNING]
> This gesture recognition system was developed as a personal research project. The gestures and thresholds are specifically calibrated for the original developer's hand anatomy, camera setup, and hardware configuration. Performance may vary significantly for other users.

> [!IMPORTANT]
> This system relies solely on camera input for 3D gesture translation to 2D input commands. No additional sensors (IMU, range finder, etc.) are available. All calculations and gesture selections are critical for system functionality.

## Technical Limitations

> [!NOTE]
> **Camera Dependency**: Performance depends heavily on camera quality, lighting conditions, and positioning. Requires consistent camera angle and distance for reliable detection.

> [!CAUTION]
> **Hand Anatomy Variations**: Gesture definitions assume specific finger length ratios and joint flexibility. May not function properly for users with different hand proportions or limited finger mobility.
>   - Hand tremors or involuntary movements
> - Children's hands may be too small for accurate detection of defined distances

> **💻 HARDWARE REQUIREMENTS:**
> - Requires sufficient processing power for real-time MediaPipe processing
> - May cause system lag or overheating on older hardware
> - Memory usage increases with gesture complexity validation
> - Not optimized for mobile devices or low-power systems

## USABILITY AND COMFORT WARNINGS

> **🕐 FATIGUE FACTOR:**
> - Extended use may cause hand, wrist, and arm fatigue
> - Complex gestures require sustained muscle tension
> - Camera pan gestures especially demanding on wrist rotation
> - Not recommended for sessions longer than 30-45 minutes without breaks

> **🎯 LEARNING CURVE:**
> - Gestures require significant practice to perform consistently
> - Initial setup may take hours to calibrate properly
> - Muscle memory development needed for fluid interaction
> - Frustration likely during initial learning phase

> **🔄 CALIBRATION DEPENDENCY:**
> - May require recalibration when:
>   - Changing camera position or angle
>   - Different lighting conditions
>   - Wearing different clothing (sleeves affecting wrist detection)
>   - Using different backgrounds
> - No automatic adaptation to user variations

## ENVIRONMENTAL CONSIDERATIONS

> **🌡️ ENVIRONMENTAL FACTORS:**
> - Optimal performance requires:
>   - Consistent, diffused lighting
>   - Plain, contrasting background
>   - Stable camera mounting
>   - Minimal background movement
> - Performance degrades with:
>   - Moving shadows
>   - Reflective surfaces in background
>   - Multiple people in frame
>   - Cluttered or hand-colored backgrounds

> **👥 SINGLE-USER OPTIMIZATION:**
> - Gestures calibrated for one specific user
> - No multi-user support or user switching
> - Sharing system requires complete recalibration
> - Not suitable for public or shared use scenarios

## HEALTH AND SAFETY CONSIDERATIONS

> **⚠️ REPETITIVE STRAIN WARNING:**
> - Repeated complex finger positions may cause strain
> - Monitor for signs of discomfort or pain
> - Take regular breaks to stretch hands and wrists
> - Discontinue use if experiencing persistent discomfort

> **👁️ EYE STRAIN CONSIDERATION:**
> - Constant visual feedback monitoring may cause eye fatigue
> - Ensure proper screen distance and brightness
> - Follow 20-20-20 rule during extended sessions

> **🧠 COGNITIVE LOAD:**
> - Learning and executing complex gestures requires mental effort
> - May interfere with game focus and enjoyment initially
> - Consider simplified gesture sets for casual gaming

## TECHNICAL IMPLEMENTATION WARNINGS

> **🔧 MEDIAPIPE LIMITATIONS:**
> - MediaPipe hand tracking has inherent accuracy limitations (~2-5mm)
> - Finger occlusion can cause tracking failures
> - Model may struggle with unusual hand positions
> - No guarantee of consistent landmark detection

> **⚡ PERFORMANCE IMPACT:**
> - Real-time gesture validation is computationally expensive
> - Complex distance calculations may impact frame rate
> - Validation requirements scale exponentially with gesture complexity
> - May require hardware upgrades for smooth operation

> **🐛 ERROR HANDLING:**
> - System may fail silently with invalid hand positions
> - No built-in recovery mechanisms for tracking loss
> - Gesture conflicts may cause unexpected behavior
> - Limited debugging information for troubleshooting

## USAGE RECOMMENDATIONS

> **📋 BEFORE STARTING:**
> - Test all gestures thoroughly before gaming sessions
> - Document your personal calibration settings
> - Have backup input methods available
> - Start with short sessions to assess comfort

> **🎮 GAMING CONSIDERATIONS:**
> - Best suited for turn-based or slow-paced games
> - May not be suitable for competitive gaming
> - Consider game genres that benefit from gesture control
> - Some games may require gesture mapping modifications

> **🔄 MAINTENANCE:**
> - Regular recalibration may be necessary
> - Keep gesture definitions documentation updated
> - Monitor system performance over time
> - Be prepared to adjust thresholds based on usage patterns

---

**Remember: This system represents one person's exploration of touchless gaming interaction. Your experience will likely differ significantly, and extensive customization will probably be necessary for your specific use case, hand anatomy, and gaming preferences.**

---

## General Rules
- **Right Hand Only**: All controls are valid only for the right hand. Left-hand gestures are ignored to prevent unintended triggers.
- **Gesture Duration**: A gesture must be held for at least 0.3 seconds to trigger, preventing misfires from rapid hand movements.
- **Priority Hierarchy**: If multiple gestures are detected simultaneously, priority is: Navigation Control > Camera Control > Movement Control > Action Control. Higher-priority gestures override lower-priority ones.
- **Re-engagement**: For gestures with "Hold" or "Repeating" properties, re-engagement requires the gesture to be released (return to a neutral state or break the gesture condition) for at least 0.2 seconds before triggering again.
- **Tolerances**: Axis length changes (Camera Control) and ROI overlaps have a 10% tolerance to account for tracking noise, except for Action Control, which requires 50% Fingertip ROI overlap with Joint ROI. Bounding box and ROI sizes are normalized relative to the hand’s size.
- **Action vs. Movement Separation**: Action Control gestures are triggered when a Fingertip ROI overlaps with the corresponding Joint ROI by ≥50%. If the fingertip moves into the Palm Bounding Box, Movement Control logic takes precedence.

## Visualizer
- **Palm Bounding Box**: Defined by 5 points: 4 metacarpal points (MCP2: Index, MCP3: Middle, MCP4: Ring, MCP5: Pinky) and 1 wrist point (Wrist 0). Labeled with sides: TOP, BOTTOM, LEFT, RIGHT.
- **Joint ROI**: Circular ROIs centered on the proximal phalanges of Index (PIP2), Middle (PIP3), Ring (PIP4), and Pinky (PIP5). Radius is 10% of the Palm Bounding Box width.
- **Fingertip ROI**: Circular ROIs centered on the 5 fingertip points: Thumb (TIP1), Index (TIP2), Middle (TIP3), Ring (TIP4), Pinky (TIP5). Radius is 5% of the Palm Bounding Box width.
- **3-Axis ROI**: Defined by:
  - X-axis: Middle finger fingertip (TIP3) to N-axis point (near Index MCP2).
  - Y-axis: Index finger fingertip (TIP2) to N-axis point.
  - Z-axis: Thumb fingertip (TIP1) to N-axis point.
  - N-axis point: Centered near Index MCP2, with a circular ROI (radius 5% of Palm Bounding Box width). Labeled with X, Y, Z, and N axes.
- **Wrist Anchor Point**: Wrist point (Wrist 0), used for Peace Sign and F Sign gestures.
- **Dynamic 3-Axis Graph**: Connects Middle TIP3 (X-axis), Index TIP2 (Y-axis), and Thumb TIP1 (Z-axis) to the N-axis point, forming straight lines. Used for Camera Control.
- **Tilt Anchor Point**: Line from the center of the Palm Bounding Box (midpoint of MCP2–5 and Wrist 0) to the Middle finger proximal phalanges (PIP3). Used for Jump and F Sign gestures.

## Gesture Validation

### Action Control
Controls for triggering actions (e.g., attacks, skills). Requires an open palm gesture (all fingers extended, palm facing camera) unless specified. Triggers when the specified Fingertip ROI overlaps with the corresponding Joint ROI by ≥50%. If the fingertip moves into the Palm Bounding Box, Movement Control logic takes precedence.

- **Palm Neutral**:
  - **Trigger**: When the palm is in a neutral position.
  - **Valid if**: All fingertips (TIP1–TIP5) are extended outward and not within the Palm Bounding Box or any Joint ROI. At least 4 fingertips must be detected outside the Palm Bounding Box for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward, Left, Right, Jump), Navigation Neutral (both use open palm gestures, compatible if no other Navigation gestures are triggered).
    - **Cannot Coexist With**: Other Action Controls (LMB, Skill #1, Skill #2, Skill #3, Utility) due to conflicting fingertip positions; Camera Control (Neutral, Pan Up/Down/Left/Right, Camera Lock) due to Ring and Pinky TIPs in Palm Bounding Box; Navigation Control (OK, F, ESC) due to higher priority and conflicting finger positions.
- **Attack/Tap/LMB**:
  - **Trigger**: Once when detected. Optional properties: **Hold** (continuous trigger while held), **Repeating** (triggers every 0.5 seconds if held).
  - **Valid if**: Thumb TIP1 is within the Palm Bounding Box for 0.3 seconds. Other fingertips (TIP2–TIP5) must be outside the Palm Bounding Box and their respective Joint ROIs.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward, Shift) if Ring TIP4 is in the Palm Bounding Box and other conditions are met; Navigation Neutral (if open palm is maintained).
    - **Cannot Coexist With**: Other Action Controls (Neutral, Skill #1, Skill #2, Skill #3, Utility) due to conflicting fingertip positions; Camera Control (Neutral, Pan Up/Down/Left/Right, Camera Lock) due to Ring and Pinky TIPs in Palm Bounding Box; Movement Control (Left, Right, Jump) due to conflicting Thumb TIP1 positions; Navigation Control (OK, F, ESC) due to higher priority and conflicting finger positions.
- **Skill #1/Key 1/Key E**:
  - **Trigger**: Once when detected. Optional properties: **Hold**, **Repeating** (every 0.5 seconds).
  - **Valid if**: Index Fingertip ROI (TIP2) overlaps with Index Joint ROI (PIP2) by ≥50% for 0.3 seconds, and TIP2 is not within the Palm Bounding Box. Other fingertips (TIP1, TIP3–TIP5) must be outside the Palm Bounding Box and their respective Joint ROIs.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward) if Ring TIP4 is in the Palm Bounding Box; Navigation Neutral (if open palm is maintained).
    - **Cannot Coexist With**: Other Action Controls (Neutral, LMB, Skill #2, Skill #3, Utility) due to conflicting fingertip positions; Camera Control (Neutral, Pan Up/Down/Left/Right, Camera Lock) due to Ring and Pinky TIPs in Palm Bounding Box; Movement Control (Left, Right, Shift, Jump) due to conflicting Index TIP2 positions or exclusivity rules; Navigation Control (OK, F, ESC) due to higher priority and conflicting finger positions.
- **Skill #2/Key 2/Key R**:
  - **Trigger**: Once when detected. Optional properties: **Hold**, **Repeating** (every 0.5 seconds).
  - **Valid if**: Middle Fingertip ROI (TIP3) overlaps with Middle Joint ROI (PIP3) by ≥50% for 0.3 seconds, and TIP3 is not within the Palm Bounding Box. Other fingertips (TIP1–TIP2, TIP4–TIP5) must be outside the Palm Bounding Box and their respective Joint ROIs.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward) if Ring TIP4 is in the Palm Bounding Box; Navigation Neutral (if open palm is maintained).
    - **Cannot Coexist With**: Other Action Controls (Neutral, LMB, Skill #1, Skill #3, Utility) due to conflicting fingertip positions; Camera Control (Neutral, Pan Up/Down/Left/Right, Camera Lock) due to Ring and Pinky TIPs in Palm Bounding Box; Movement Control (Left, Right, Shift, Jump) due to conflicting Middle TIP3 positions or exclusivity rules; Navigation Control (OK, F, ESC) due to higher priority and conflicting finger positions.
- **Skill #3/Key 3/Key Q**:
  - **Trigger**: Once when detected. Optional properties: **Hold**, **Repeating** (every 0.5 seconds).
  - **Valid if**: Ring Fingertip ROI (TIP4) overlaps with Ring Joint ROI (PIP4) by ≥50% for 0.3 seconds, and TIP4 is not within the Palm Bounding Box. Other fingertips (TIP1–TIP3, TIP5) must be outside the Palm Bounding Box and their respective Joint ROIs.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward) if Ring TIP4 is in the Palm Bounding Box; Navigation Neutral (if open palm is maintained).
    - **Cannot Coexist With**: Other Action Controls (Neutral, LMB, Skill #1, Skill #2, Utility) due to conflicting fingertip positions; Camera Control (Neutral, Pan Up/Down/Left/Right, Camera Lock) due to Ring and Pinky TIPs in Palm Bounding Box; Movement Control (Left, Right, Shift, Jump) due to conflicting Ring TIP4 positions or exclusivity rules; Navigation Control (OK, F, ESC) due to higher priority and conflicting finger positions.
- **Utility/Key 4/Key T**:
  - **Trigger**: Once when detected. Optional properties: **Hold**, **Repeating** (every 0.5 seconds).
  - **Valid if**: Pinky Fingertip ROI (TIP5) overlaps with Pinky Joint ROI (PIP5) by ≥50% for 0.3 seconds, and TIP5 is not within the Palm Bounding Box. Other fingertips (TIP1–TIP4) must be outside the Palm Bounding Box and their respective Joint ROIs.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward) if Ring TIP4 is in the Palm Bounding Box; Navigation Neutral (if open palm is maintained).
    - **Cannot Coexist With**: Other Action Controls (Neutral, LMB, Skill #1, Skill #2, Skill #3) due to conflicting fingertip positions; Camera Control (Neutral, Pan Up/Down/Left/Right, Camera Lock) due to Ring and Pinky TIPs in Palm Bounding Box; Movement Control (Left, Right, Shift, Jump) due to conflicting Pinky TIP5 positions or exclusivity rules; Navigation Control (OK, F, ESC) due to higher priority and conflicting finger positions.

### Camera Control
Controls for camera panning and locking. Requires a 3-axis formation with fingers spread outward, triggered by wrist movements that change axis lengths.

- **Camera Neutral**:
  - **Trigger**: When the camera is in a neutral position.
  - **Valid if**: Index TIP2 (Y-axis), Middle TIP3 (X-axis), and Thumb TIP1 (Z-axis) are extended outward and not within the Palm Bounding Box, with all three fingertips forming the 3-axis formation relative to the N-axis point (near Index MCP2). Ring TIP4 and Pinky TIP5 are within the Palm Bounding Box. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward) if Ring TIP4 is in the Palm Bounding Box.
    - **Cannot Coexist With**: Other Camera Controls (Pan Up, Pan Down, Pan Left, Pan Right, Camera Lock) due to conflicting axis length changes or ROI overlaps; Action Control (Neutral, LMB, Skill #1, Skill #2, Skill #3, Utility) due to conflicting fingertip positions (Index, Middle, Thumb extended vs. Joint ROI/Palm Bounding Box); Movement Control (Left, Right, Shift, Jump) due to conflicting fingertip positions or exclusivity rules; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.
- **Pan Up**:
  - **Trigger**: When the 3-axis formation changes to indicate upward panning.
  - **Valid if**: Y-axis length (Index TIP2 to N-axis point) decreases by >10%, X-axis length (Middle TIP3 to N-axis point) increases by >10%, Z-axis length (Thumb TIP1 to N-axis point) remains within ±10% of neutral length. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward) if Ring TIP4 is in the Palm Bounding Box.
    - **Cannot Coexist With**: Other Camera Controls (Neutral, Pan Down, Pan Left, Pan Right, Camera Lock) due to conflicting axis length changes or ROI overlaps; Action Control (Neutral, LMB, Skill #1, Skill #2, Skill #3, Utility) due to conflicting fingertip positions; Movement Control (Left, Right, Shift, Jump) due to conflicting fingertip positions or exclusivity rules; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.
- **Pan Down**:
  - **Trigger**: When the 3-axis formation changes to indicate downward panning.
  - **Valid if**: Y-axis length increases by >10%, X-axis length decreases by >10%, Z-axis length remains within ±10%. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward) if Ring TIP4 is in the Palm Bounding Box.
    - **Cannot Coexist With**: Other Camera Controls (Neutral, Pan Up, Pan Left, Pan Right, Camera Lock) due to conflicting axis length changes or ROI overlaps; Action Control (Neutral, LMB, Skill #1, Skill #2, Skill #3, Utility) due to conflicting fingertip positions; Movement Control (Left, Right, Shift, Jump) due to conflicting fingertip positions or exclusivity rules; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.
- **Pan Left**:
  - **Trigger**: When the 3-axis formation changes to indicate leftward panning.
  - **Valid if**: Y-axis length remains within ±10%, X-axis length increases by >10%, Z-axis length decreases by >10%. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward) if Ring TIP4 is in the Palm Bounding Box.
    - **Cannot Coexist With**: Other Camera Controls (Neutral, Pan Up, Pan Down, Pan Right, Camera Lock) due to conflicting axis length changes or ROI overlaps; Action Control (Neutral, LMB, Skill #1, Skill #2, Skill #3, Utility) due to conflicting fingertip positions; Movement Control (Left, Right, Shift, Jump) due to conflicting fingertip positions or exclusivity rules; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.
- **Pan Right**:
  - **Trigger**: When the 3-axis formation changes to indicate rightward panning.
  - **Valid if**: Y-axis length remains within ±10%, X-axis length decreases by >10%, Z-axis length increases by >10%. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Forward, Backward) if Ring TIP4 is in the Palm Bounding Box.
    - **Cannot Coexist With**: Other Camera Controls (Neutral, Pan Up, Pan Down, Pan Left, Camera Lock) due to conflicting axis length changes or ROI overlaps; Action Control (Neutral, LMB, Skill #1, Skill #2, Skill #3, Utility) due to conflicting fingertip positions; Movement Control (Left, Right, Shift, Jump) due to conflicting fingertip positions or exclusivity rules; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.
- **Mouse Middle Click/Camera Lock**:
  - **Trigger**: When the 3-axis formation collapses into overlapping ROIs.
  - **Valid if**: Index TIP2, Middle TIP3, and Thumb TIP1 ROIs overlap (within 10% of Palm Bounding Box width) and are extended toward Palm Bounding Box – LEFT. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: None.
    - **Cannot Coexist With**: All other controls (Action, Camera, Movement, Navigation) due to the unique ROI overlap requirement and explicit exclusivity rule.

### Movement Control
Controls for character movement. Typically involves a fist-like gesture with Ring TIP4 in the Palm Bounding Box, triggered when fingertips move into the Palm Bounding Box (e.g., from Joint ROI or extended position).

- **Movement Neutral**:
  - **Trigger**: When the hand is in a neutral movement position.
  - **Valid if**: Ring TIP4 is within the Palm Bounding Box for 0.3 seconds. Optionally, all fingertips (TIP1–TIP5) are within the Palm Bounding Box (fist gesture).
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Action Control (Neutral, LMB, Skill #1, Skill #2, Skill #3, Utility) if fingertip conditions are met; Navigation Neutral (if open palm is maintained).
    - **Cannot Coexist With**: Movement Control (Forward, Backward) due to conflicting Palm Bounding Box size changes; Movement Control (Left, Right, Shift, Jump) due to conflicting fingertip positions or exclusivity rules; Camera Control (Neutral, Pan Up, Pan Down, Pan Left, Pan Right, Camera Lock) due to Ring and Pinky TIPs in Palm Bounding Box; Navigation Control (OK, F, ESC) due to higher priority and conflicting finger positions.
- **Movement Forward/W**:
  - **Trigger**: When the hand moves closer to the camera.
  - **Valid if**: Ring TIP4 is within the Palm Bounding Box, and the Palm Bounding Box size increases by >10% from its neutral size. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Camera Control (Neutral, Pan Up, Pan Down, Pan Left, Pan Right) if 3-axis formation is maintained; Action Control (LMB, Skill #1, Skill #2, Skill #3, Utility) if fingertip conditions are met.
    - **Cannot Coexist With**: Movement Control (Neutral, Backward) due to conflicting Palm Bounding Box size changes; Movement Control (Left, Right, Shift, Jump) due to conflicting fingertip positions or exclusivity rules; Camera Control (Camera Lock) due to conflicting ROI overlaps; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.
- **Movement Backward/S**:
  - **Trigger**: When the hand moves away from the camera.
  - **Valid if**: Ring TIP4 is within the Palm Bounding Box, and the Palm Bounding Box size decreases by >10% from its neutral size. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Camera Control (Neutral, Pan Up, Pan Down, Pan Left, Pan Right) if 3-axis formation is maintained; Action Control (LMB, Skill #1, Skill #2, Skill #3, Utility) if fingertip conditions are met.
    - **Cannot Coexist With**: Movement Control (Neutral, Forward) due to conflicting Palm Bounding Box size changes; Movement Control (Left, Right, Shift, Jump) due to conflicting fingertip positions or exclusivity rules; Camera Control (Camera Lock) due to conflicting ROI overlaps; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.
- **Movement Left/A**:
  - **Trigger**: When the hand indicates leftward movement.
  - **Valid if**: Thumb TIP1 is extended outward and not within the Palm Bounding Box for 0.3 seconds. Ring TIP4 must be within the Palm Bounding Box.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Shift) if Index TIP2 is in Joint ROI and Ring TIP4 is in Palm Bounding Box; Action Control (Neutral) if open palm is maintained.
    - **Cannot Coexist With**: Movement Control (Right, Jump) due to conflicting Thumb TIP1 positions; Movement Control (Forward, Backward, Neutral) due to conflicting fingertip positions or exclusivity rules; Camera Control (Neutral, Pan Up, Pan Down, Pan Left, Pan Right, Camera Lock) due to conflicting fingertip positions; Action Control (LMB, Skill #1, Skill #2, Skill #3, Utility) due to conflicting fingertip positions; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.
- **Movement Right/D**:
  - **Trigger**: When the hand indicates rightward movement.
  - **Valid if**: Pinky TIP5 is extended outward and not within the Palm Bounding Box for 0.3 seconds. Ring TIP4 must be within the Palm Bounding Box.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Shift) if Index TIP2 is in Joint ROI and Ring TIP4 is in Palm Bounding Box; Action Control (Neutral) if open palm is maintained.
    - **Cannot Coexist With**: Movement Control (Left, Jump) due to conflicting Pinky TIP5 positions; Movement Control (Forward, Backward, Neutral) due to conflicting fingertip positions or exclusivity rules; Camera Control (Neutral, Pan Up, Pan Down, Pan Left, Pan Right, Camera Lock) due to conflicting fingertip positions; Action Control (LMB, Skill #1, Skill #2, Skill #3, Utility) due to conflicting fingertip positions; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.
- **Shift/Sprint/Crouch**:
  - **Trigger**: When the Index finger is raised and curled. Optional properties: **Hold**, **Repeating** (every 0.5 seconds).
  - **Valid if**: Index Fingertip ROI (TIP2) overlaps with Index Joint ROI (PIP2) by ≥50% and not within the Palm Bounding Box for 0.3 seconds. Ring TIP4 must be within the Palm Bounding Box. If Index TIP2 moves into the Palm Bounding Box, Movement Neutral logic takes precedence.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Movement Control (Left, Right) if Thumb TIP1 or Pinky TIP5 is extended and Ring TIP4 is in Palm Bounding Box; Action Control (LMB) if Thumb TIP1 is in Palm Bounding Box.
    - **Cannot Coexist With**: Action Control (Neutral, Skill #1, Skill #2, Skill #3, Utility) due to explicit exclusivity rule and conflicting fingertip positions; Movement Control (Forward, Backward, Neutral, Jump) due to conflicting fingertip positions or exclusivity rules; Camera Control (Neutral, Pan Up, Pan Down, Pan Left, Pan Right, Camera Lock) due to conflicting fingertip positions; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.
- **Jump/Space**:
  - **Trigger**: When the hand indicates a jump. Optional properties: **Hold**, **Repeating** (every 0.5 seconds).
  - **Valid if**: Thumb TIP1 and Pinky TIP5 are extended outward and not within the Palm Bounding Box, and the Tilt anchor point line (Palm Bounding Box center to Middle PIP3) decreases by >10% (palm tilted backward). Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Action Control (Neutral) if open palm is maintained.
    - **Cannot Coexist With**: Movement Control (Forward, Backward, Neutral, Left, Right, Shift) due to conflicting fingertip positions or exclusivity rules; Camera Control (Neutral, Pan Up, Pan Down, Pan Left, Pan Right, Camera Lock) due to conflicting fingertip positions; Action Control (LMB, Skill #1, Skill #2, Skill #3, Utility) due to conflicting fingertip positions; Navigation Control (Neutral, OK, F, ESC) due to higher priority and conflicting finger positions.

### Navigation Control
Controls for navigation actions (e.g., confirmation, interaction, cancellation). Typically involves a fist or specific finger gestures.

- **Navigation Neutral**:
  - **Trigger**: When the hand is in a neutral navigation position.
  - **Valid if**: All fingertips (TIP1–TIP5) are extended outward and not within the Palm Bounding Box or any Joint ROI (open palm) for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: Action Control (Neutral, LMB, Skill #1, Skill #2, Skill #3, Utility) if fingertip conditions are met; Movement Control (Neutral, Left, Right, Jump) if fingertip conditions are met.
    - **Cannot Coexist With**: Navigation Control (OK, F, ESC) due to conflicting finger positions; Camera Control (Neutral, Pan Up, Pan Down, Pan Left, Pan Right, Camera Lock) due to Ring and Pinky TIPs in Palm Bounding Box; Movement Control (Forward, Backward, Shift) due to conflicting fingertip positions or exclusivity rules.
- **Peace Sign/OK/Confirmation/Enter**:
  - **Trigger**: When a Peace Sign gesture is detected. Optional properties: **Hold**, **Repeating** (every 0.5 seconds).
  - **Valid if**: Index TIP2 and Middle TIP3 are extended outward, positioned above Palm Bounding Box – TOP, and spaced apart by >10% of Palm Bounding Box width. Thumb TIP1, Ring TIP4, and Pinky TIP5 are within the Palm Bounding Box. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: None.
    - **Cannot Coexist With**: All other controls (Action, Camera, Movement, other Navigation) due to higher priority and conflicting finger positions (Index and Middle TIPs above Palm Bounding Box, others within).
- **F Sign/Tilted Peace Sign/Interact/Key F**:
  - **Trigger**: When a tilted Peace Sign is detected. Optional properties: **Hold**, **Repeating** (every 0.5 seconds).
  - **Valid if**: Index TIP2 and Middle TIP3 are extended outward, positioned above Palm Bounding Box – TOP, spaced apart by >10% of Palm Bounding Box width, and tilted toward Palm Bounding Box – LEFT or RIGHT (Wrist anchor point to Tilt anchor point line deviates by >15° from vertical). Thumb TIP1, Ring TIP4, and Pinky TIP5 are within the Palm Bounding Box. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: None.
    - **Cannot Coexist With**: All other controls (Action, Camera, Movement, other Navigation) due to higher priority and conflicting finger positions (tilted Peace Sign).
- **Thumbs Down/Cancel/ESC**:
  - **Trigger**: When a Thumbs Down gesture is detected. Optional properties: **Hold**, **Repeating** (every 0.5 seconds).
  - **Valid if**: Thumb TIP1 is extended downward and positioned below Palm Bounding Box – BOTTOM by >10% of Palm Bounding Box height. Index TIP2, Middle TIP3, Ring TIP4, and Pinky TIP5 are within the Palm Bounding Box. Held for 0.3 seconds.
  - **Compatibility and Exclusivity**:
    - **Can Coexist With**: None.
    - **Cannot Coexist With**: All other controls (Action, Camera, Movement, other Navigation) due to higher priority and conflicting finger positions (Thumb TIP1 below Palm Bounding Box).

## Implementation Notes
- **Tracking Precision**: Use normalized coordinates (relative to Palm Bounding Box size) to ensure scalability across hand sizes.
- **ROI Overlap Calculation**: For Action Control (Skill #1–Utility, Shift), compute the overlap percentage between Fingertip ROI and Joint ROI using area intersection over the smaller ROI area. Require ≥50% overlap for trigger.
- **Noise Handling**: Apply a 10% tolerance to axis length changes and ROI overlaps (except Action Control, which uses 50% overlap). Smooth tracking data over a 0.1-second window to reduce jitter.
- **Gesture Transitions**: Enforce a 0.2-second neutral state between gesture triggers to prevent rapid misfires. If a fingertip moves from a Joint ROI to the Palm Bounding Box, switch to Movement Control logic immediately.
- **Debug Visualizer**: Display the Palm Bounding Box, Joint ROIs, Fingertip ROIs, 3-Axis ROI, and Tilt anchor point in real-time to aid debugging and user feedback.
